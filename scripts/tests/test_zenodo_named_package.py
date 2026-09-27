"""Named archive integrity and remote mutation ordering; all remote calls are mocked."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest

SPEC = importlib.util.spec_from_file_location("named_zenodo", Path(__file__).parents[1] / "zenodo_deposit.py")
Z = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(Z)


@pytest.fixture
def package(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(Z, "REPO", str(repo))
    monkeypatch.setenv("ZENODO_TOKEN", "mock-token")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE).decode().strip()
    git("init", "-q")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "core.autocrlf", "false")
    paper = Z.package_configuration("aso", Z.PACKAGE_NAME)
    payload = repo / Z.PACKAGE_ROOT / "evidence/analyze.py"
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"print('fixture')\n")
    git("add", ".")
    git("commit", "-qm", "payload")
    entry = {"path": payload.relative_to(repo).as_posix(), "bytes": payload.stat().st_size,
             "sha256": Z.sha256(payload)}
    manifest = {"_schema": "emc-zenodo-package-manifest/1", "_what_this_is": "Fixture",
                "files": [entry], "n_files": 1, "inventory_limited_to_tracked_files": True,
                "git_revision": git("rev-parse", "HEAD"), "conceptrecid": "22028915",
                "deposition_doi": "10.5281/zenodo.22229096", "how_to_reproduce_offline": ["Run Python"],
                "archive_content_digest": Z.content_digest([entry])}
    path = repo / paper["manifest"]
    path.parent.mkdir(parents=True)
    def save(value=manifest):
        path.write_text(json.dumps(value), encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "manifest", "--allow-empty")
    save()
    return repo, paper, manifest, payload, git, save


def args(package, tmp_path, *extra):
    return ["--paper", "aso", "--package", Z.PACKAGE_NAME,
            "--out-dir", str(tmp_path / "out"), "--receipt", str(tmp_path / "receipt.json"), *extra]


def draft(identifier=22229097):
    return {"id": identifier, "conceptrecid": "22028915", "submitted": False,
            "metadata": {"prereserve_doi": {"doi": f"10.5281/zenodo.{identifier}"}},
            "files": [], "links": {"bucket": "https://zenodo.org/api/files/mock", "html": "mock"}}


def test_build_is_deterministic_and_checks_every_member(package, tmp_path):
    repo, paper, manifest, payload, *_ = package
    Z.validate_package_manifest(manifest, paper)
    Z.verify(manifest)
    a, b = tmp_path / "a.zip", tmp_path / "b.zip"
    Z.build_zip(manifest, paper["manifest"], a, deterministic=True)
    os.utime(payload, (1700000000, 1700000000))
    Z.build_zip(manifest, paper["manifest"], b, deterministic=True)
    assert a.read_bytes() == b.read_bytes()
    Z.verify_built_archive(manifest, paper["manifest"], a)
    with Z.zipfile.ZipFile(a, "a") as archive:
        archive.writestr("extra", b"unexpected")
    with pytest.raises(SystemExit, match="inventory"):
        Z.verify_built_archive(manifest, paper["manifest"], a)


def test_canonical_build_ships_manifest_beside_each_declared_payload(package, tmp_path):
    repo, paper, manifest, *_ = package
    output = tmp_path / "canonical.zip"
    Z.build_zip(manifest, paper["manifest"], output)
    expected = [entry["path"] for entry in manifest["files"]] + [paper["manifest"]]
    with Z.zipfile.ZipFile(output) as archive:
        assert archive.namelist() == expected
        for relative in expected:
            assert archive.read(relative) == (repo / relative).read_bytes()


@pytest.mark.parametrize("change", ["missing", "changed", "uncommitted", "digest", "count", "duplicate", "source", "unsafe", "literature", "manuscript"])
def test_bad_payload_refuses_before_network(package, tmp_path, monkeypatch, change):
    repo, paper, manifest, payload, git, save = package
    value = copy.deepcopy(manifest)
    if change == "missing": payload.unlink()
    elif change == "changed": payload.write_bytes(b"X" * payload.stat().st_size)
    elif change == "uncommitted":
        value["_what_this_is"] = "uncommitted edit"
    elif change == "digest": value["archive_content_digest"] = "0" * 64
    elif change == "count": value["n_files"] = 2
    elif change == "duplicate": value["files"] *= 2
    elif change == "source": value["git_revision"] = "0" * 40
    else:
        relative = {"unsafe": "../outside", "literature": Z.PACKAGE_ROOT + "/evidence/sources/article.pdf",
                    "manuscript": Z.PACKAGE_ROOT + "/manuscript.md"}[change]
        if change != "unsafe":
            p = repo / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(payload.read_bytes())
            git("add", ".")
            git("commit", "-qm", "excluded content")
            value["git_revision"] = git("rev-parse", "HEAD")
        value["files"][0]["path"] = relative
        value["archive_content_digest"] = Z.content_digest(value["files"])
    (repo / paper["manifest"]).write_text(json.dumps(value), encoding="utf-8")
    if change != "uncommitted":
        git("add", ".")
        git("commit", "-qm", "fixture mutation", "--allow-empty")
    calls = []
    monkeypatch.setattr(Z, "api", lambda *a, **kw: calls.append(a))
    with pytest.raises(SystemExit): Z.main(args(package, tmp_path, "--inspect"))
    assert calls == []


@pytest.mark.parametrize("path", ["C:/secret", "\\\\host\\secret", "/secret", "a/../secret", "a//b", "a\\b", "a\nfile"])
def test_unsafe_paths_are_rejected(package, path):
    with pytest.raises(SystemExit): Z._safe_regular_file(path)


@pytest.mark.parametrize("mode", ["inspect", "wrong-concept", "published-refresh", "unowned-refresh", "unowned-adoption", "draft-new-version"])
def test_remote_refusals_never_mutate(package, tmp_path, monkeypatch, mode):
    repo, paper, manifest, payload, git, save = package
    current = draft(22229096)
    if mode in {"published-refresh", "unowned-adoption", "inspect"}: current["submitted"] = True
    if mode == "wrong-concept": current["conceptrecid"] = "wrong"
    calls = []
    def api(base, token, method, path, **kw):
        calls.append((method, path))
        assert method == "GET"
        if "?" in path: return [draft()]
        if path.endswith("22229097"): return draft()
        return current
    monkeypatch.setattr(Z, "api", api)
    extra = ["--inspect"] if mode == "inspect" else ["--new-version"] if mode in {"unowned-adoption", "draft-new-version"} else []
    if mode == "inspect":
        assert Z.main(args(package, tmp_path, *extra)) == 0
        assert json.loads((tmp_path / "receipt.json").read_text())["remote_mutation"] is False
    else:
        with pytest.raises(SystemExit): Z.main(args(package, tmp_path, *extra))
    assert all(method == "GET" for method, _ in calls)


def test_uncommitted_ownership_cannot_authorize_refresh(package):
    repo, paper, manifest, payload, git, save = package
    state = repo / Path(paper["manifest"]).parent / "deposit-state.json"
    pending = {"deposition_id": 22229097, "conceptrecid": "22028915", "doi": "10.5281/zenodo.22229097"}
    state.write_text(json.dumps({"pending": pending}))
    with pytest.raises(SystemExit): Z.require_draft_ownership(paper, draft())
    git("add", ".")
    git("commit", "-qm", "actual ownership fixture")
    Z.require_draft_ownership(paper, draft())
    with pytest.raises(SystemExit): Z.require_draft_ownership(paper, draft(22229098))


def test_explicit_adoption_uploads_only_intended_draft_and_verifies_bytes(package, tmp_path, monkeypatch):
    repo, paper, manifest, payload, git, save = package
    manifest["deposition_doi"] = "10.5281/zenodo.22229097"
    save()
    dep = draft()
    calls = []
    def api(base, token, method, path, payload=None, raw=None, **kw):
        calls.append((method, path))
        if method == "PUT" and raw is not None:
            dep["files"] = [{"filename": paper["zip"], "filesize": len(raw), "checksum": "md5:" + hashlib.md5(raw).hexdigest()}]
            return {}
        if method == "PUT":
            dep["metadata"].update(payload["metadata"])
            dep["metadata"]["prereserve_doi"] = {"doi": manifest["deposition_doi"]}
        return copy.deepcopy(dep)
    monkeypatch.setattr(Z, "api", api)
    assert Z.main(args(package, tmp_path, "--adopt-draft", "22229097")) == 0
    receipt = json.loads((tmp_path / "receipt.json").read_text())
    assert receipt["operation"] == "upload_verified"
    assert receipt["record"]["deposition_id"] == 22229097
    assert receipt["publication_requested"] is False
    assert not any(method in {"POST", "DELETE"} for method, _ in calls)


@pytest.mark.parametrize("defect", ["hash", "size", "name", "extra"])
def test_remote_byte_changes_refuse(package, tmp_path, defect):
    zip_path = tmp_path / "archive.zip"
    zip_path.write_bytes(b"archive")
    file = {"filename": "archive.zip", "filesize": 7, "checksum": hashlib.md5(b"archive").hexdigest()}
    dep = {"files": [file]}
    if defect == "hash": file["checksum"] = "0" * 32
    if defect == "size": file["filesize"] = 8
    if defect == "name": file["filename"] = "wrong.zip"
    if defect == "extra": dep["files"].append(dict(file))
    with pytest.raises(SystemExit): Z.verify_uploaded_archive(dep, zip_path, "archive.zip")


def test_canonical_selection_is_unchanged():
    assert Z.package_configuration("aso") is Z.PAPERS["aso"]


@pytest.mark.parametrize("defect", [None, "stale-digest", "stale-zip", "remote-bytes", "remote-doi", "remote-title", "remote-type", "remote-creator", "remote-license", "remote-access", "remote-description", "published", "wrong-concept"])
def test_publish_requires_exact_committed_upload_and_never_refreshes(package, tmp_path, monkeypatch, defect):
    repo, paper, manifest, payload, git, save = package
    manifest["deposition_doi"] = "10.5281/zenodo.22229097"
    save()
    zip_path = tmp_path / "verified.zip"
    Z.build_zip(manifest, paper["manifest"], zip_path, deterministic=True)
    digest = Z.sha256(repo / paper["manifest"])
    pending = {"deposition_id": 22229097, "conceptrecid": "22028915", "doi": manifest["deposition_doi"],
               "uploaded_manifest_digest": manifest["archive_content_digest"],
               "uploaded_archive_sha256": Z.sha256(zip_path), "uploaded_manifest_sha256": digest}
    if defect == "stale-digest": pending["uploaded_manifest_digest"] = "0" * 64
    if defect == "stale-zip": pending["uploaded_archive_sha256"] = "0" * 64
    (repo / Path(paper["manifest"]).parent / "deposit-state.json").write_text(json.dumps({"pending": pending}))
    authority = repo / "research/autonomy/publication-authority.json"
    authority.parent.mkdir(parents=True)
    authority.write_text(json.dumps({"zenodo_archive_publication": {"standing_grant": True, "approval_is_required_per_publication": False}}))
    git("add", ".")
    git("commit", "-qm", "uploaded receipt fixture")
    dep = draft()
    dep["metadata"].update(Z.named_metadata(paper, manifest, digest))
    dep["metadata"]["license"] = {"id": dep["metadata"]["license"]}
    data = zip_path.read_bytes()
    dep["files"] = [{"filename": paper["zip"], "filesize": len(data), "checksum": hashlib.md5(data).hexdigest()}]
    if defect == "remote-bytes": dep["files"][0]["checksum"] = "0" * 32
    if defect == "remote-doi": dep["metadata"]["prereserve_doi"]["doi"] = "10.5281/zenodo.99999999"
    if defect == "remote-title": dep["metadata"]["title"] = "changed"
    if defect == "remote-type": dep["metadata"]["upload_type"] = "publication"
    if defect == "remote-creator": dep["metadata"]["creators"] = [{"name": "Another author"}]
    if defect == "remote-license": dep["metadata"]["license"] = {"id": "wrong"}
    if defect == "remote-access": dep["metadata"]["access_right"] = "closed"
    if defect == "remote-description": dep["metadata"]["description"] += "Unsupported additional claim."
    if defect == "published": dep["submitted"] = True
    if defect == "wrong-concept": dep["conceptrecid"] = "wrong"
    calls = []
    def api(base, token, method, path, **kw):
        calls.append((method, path))
        assert method in {"GET", "POST"}
        if method == "POST":
            assert defect is None
            assert path == "/deposit/depositions/22229097/actions/publish"
            dep["submitted"] = True
        return copy.deepcopy(dep)
    monkeypatch.setattr(Z, "api", api)
    command = args(package, tmp_path, "--publish", "--approved-by", "Existing standing grant")
    if defect is not None:
        with pytest.raises(SystemExit): Z.main(command)
        assert all(method == "GET" for method, _ in calls)
        if defect.startswith("stale-"): assert calls == []
    else:
        assert Z.main(command) == 0
        assert [method for method, _ in calls] == ["GET", "POST"]
        assert json.loads((tmp_path / "receipt.json.publish.json").read_text())["public_read_back"] is False
