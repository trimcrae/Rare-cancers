"""Durable ownership under the existing clone-wide research-run OS lock.

The lock is the arbiter. The state is the recovery record, never an expiring
lease. It cannot fence writers in other clones; the committed disabled-driver
handover and claim.py's remote check cover cooperating legacy workers there.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid


class Refused(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class LocalLock:
    """An OS-held lock; process death releases it without lease expiry guesses."""
    def __init__(self, path):
        self.path, self.handle = Path(path), None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            self.handle = None
            raise Refused("Another local research process owns the coordinator lock.") from exc
        return self

    def __exit__(self, *_):
        if self.handle:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()
            self.handle = None


def cache_for(root):
    result = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=root, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise Refused("Cannot locate the shared Git directory for ownership arbitration.")
    return Path(result.stdout.strip()).resolve().parent / ".cache" / "research-runs"


def handover_disabled(root):
    path = Path(root) / "research/autonomy/codex-handover.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise Refused("Cannot verify the legacy-driver handover record.") from exc
    if value.get("legacy_driver", {}).get("status") != "disabled":
        raise Refused("The handover record does not say the legacy driver is disabled.")
    ledger = Path(root) / "research/autonomy/research-ledger.json"
    if ledger.exists():
        rows = json.loads(ledger.read_text(encoding="utf-8-sig")).get("entries", [])
        owners = [f'{row.get("id")}: {row["owner"]}' for row in rows if row.get("owner")]
        if owners:
            raise Refused("Outstanding legacy research owners must be reconciled: " + ", ".join(owners[:10]))


class Coordinator:
    """All state changes require this context's shared OS lock."""
    def __init__(self, root, cache=None):
        self.root = Path(root)
        self.cache = Path(cache) if cache else cache_for(root)
        self.path = self.cache / "coordinator.json"
        self.lock = LocalLock(self.cache / "coordinator.lock")
        self.state = None

    def __enter__(self):
        self.lock.__enter__()
        try:
            self.state = self.read(self.cache)
        except BaseException:
            self.lock.__exit__()
            raise
        return self

    def __exit__(self, *args):
        self.lock.__exit__(*args)

    @staticmethod
    def read(cache):
        path = Path(cache) / "coordinator.json"
        if not path.exists():
            return {"schema": "emc-local-coordinator/1", "owner": None,
                    "resources": {}, "history": []}
        try:
            state = json.loads(path.read_text(encoding="utf-8-sig"))
            if (state.get("schema") != "emc-local-coordinator/1"
                    or not isinstance(state.get("resources"), dict)
                    or not isinstance(state.get("history"), list)):
                raise ValueError("unknown ownership schema")
            return state
        except (OSError, ValueError, AttributeError) as exc:
            raise Refused("Ownership state is unreadable; preserve it and reconcile explicitly.") from exc

    def save(self, action, **details):
        if self.lock.handle is None:
            raise Refused("Ownership mutation requires the shared coordinator lock.")
        self.state["history"].append({"utc": utc_now(), "action": action, **details})
        write_json(self.path, self.state)

    def require(self, owner):
        if not owner or self.state.get("owner") != owner:
            raise Refused(f"Coordinator is {self.state.get('owner')!r}; claim or explicitly hand off ownership before writing.")

    def claim(self, owner, note):
        if not owner or not note:
            raise Refused("Coordinator identity and a handover note are required.")
        if self.state.get("owner"):
            self.require(owner)
            return
        handover_disabled(self.root)
        self.state["owner"] = owner
        self.save("claim_coordinator", owner=owner, note=note)

    def handoff(self, owner, successor, note):
        self.require(owner)
        if not successor or not note:
            raise Refused("Explicit successor identity and handover note are required.")
        self.state["owner"] = successor
        self.save("handoff_coordinator", previous_owner=owner, owner=successor, note=note)

    def release(self, owner, note):
        self.require(owner)
        if self.state["resources"]:
            raise Refused("Unresolved resource ownership prevents coordinator release; hand off with its evidence instead.")
        if not note:
            raise Refused("A coordinator release note is required.")
        self.state["owner"] = None
        self.save("release_coordinator", owner=owner, note=note)

    def reserve(self, owner, resource, worker_id, worktree=None, receipt=None):
        self.require(owner)
        handover_disabled(self.root)
        if not resource or not worker_id:
            raise Refused("Resource and worker identity are required.")
        if resource in self.state["resources"]:
            existing = self.state["resources"][resource]
            raise Refused(f"Resource {resource} remains owned by {existing['worker_id']}; inspect and resolve retained output before dispatching again.")
        if worktree:
            path = Path(worktree).resolve()
            if path == self.root.resolve() or not (path / ".git").is_file() or cache_for(path) != self.cache:
                raise Refused("A writer must use a separate worktree of this clone.")
            if any(row.get("worktree") == str(path) for row in self.state["resources"].values()):
                raise Refused("Another writer already owns this worktree.")
        self.state["resources"][resource] = {
            "worker_id": worker_id, "reserved_utc": utc_now(), "status": "reserved",
            "worktree": str(Path(worktree).resolve()) if worktree else None,
            "receipt": str(receipt) if receipt else None}
        self.save("reserve_resource", owner=owner, resource=resource, worker_id=worker_id)

    def update_run(self, owner, resource, receipt):
        self.require(owner)
        row = self.state["resources"][resource]
        row["status"] = receipt["status"]
        row["worktree"] = receipt["worktree"]
        self.save("record_run", resource=resource, status=receipt["status"])

    def release_resource(self, owner, resource, resolution, evidence):
        self.require(owner)
        if resolution not in ("integrated", "abandoned"):
            raise Refused("Resource resolution must be integrated or abandoned; output is never deleted.")
        if resource not in self.state["resources"]:
            raise Refused("Resource has no recorded owner.")
        path = Path(evidence).resolve()
        if not path.is_file():
            raise Refused("Resource resolution requires a durable evidence file (integration verification or abandonment reason).")
        row = self.state["resources"].pop(resource)
        self.save("resolve_resource", owner=owner, resource=resource, resolution=resolution,
                  evidence=str(path), evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  retained_output=row)

    def recover(self, owner):
        self.require(owner)
        recovered = []
        # Acquiring the OS lock proves that a preceding runner no longer owns it.
        # Never expire ownership by timestamp; keep manual writers reserved.
        for resource, row in self.state["resources"].items():
            if not row.get("receipt"):
                continue
            path = Path(row["receipt"])
            if not path.is_file():
                row["status"] = "interrupted"
                recovered.append(resource)
                continue
            receipt = json.loads(path.read_text(encoding="utf-8-sig"))
            if receipt.get("status") in ("starting", "running"):
                receipt.update(status="interrupted", recovery_utc=utc_now(),
                               recovery_note="Previous runner no longer holds the OS lock; retained output requires reconciliation.")
                write_json(path, receipt)
                recovered.append(resource)
            row["status"] = receipt["status"]
            row["worktree"] = receipt.get("worktree", row.get("worktree"))
        self.save("recover", owner=owner, interrupted_resources=recovered)
        return recovered
