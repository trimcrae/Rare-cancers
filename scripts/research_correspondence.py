"""Private, provider-neutral correspondence ledger. This program never sends mail.

Scope decisions and mailbox verification are reviewed by the agent, not inferred by
this ledger. Reserve BEFORE any future external send: reservation immediately means
send_uncertain, so interruption cannot make a request automatically retryable.
Private mailbox.json must record sender, provider, send_verified, receive_verified,
and verification_evidence. These are attestations, not a transport implementation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid

DEFAULT_STATE = Path.home() / '.codex' / 'research-correspondence' / 'EMC-Research'
DEFAULT_AUTHORITY = Path(__file__).resolve().parents[1] / 'research/autonomy/publication-authority.json'


def required(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be nonempty text')
    return value.strip()


class Ledger:
    def __init__(self, state_dir=DEFAULT_STATE, authority=DEFAULT_AUTHORITY):
        self.directory = Path(state_dir)
        self.authority = Path(authority)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.directory / 'ledger.sqlite3', timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY, digest TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL, status TEXT NOT NULL,
                token TEXT, message_id TEXT, receipt TEXT);
            CREATE TABLE IF NOT EXISTS suppressed (recipient TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY, request_id TEXT, event TEXT,
                evidence TEXT, utc TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
        ''')

    def close(self):
        self.db.close()

    def event(self, request_id, event, evidence):
        self.db.execute('INSERT INTO events(request_id,event,evidence) VALUES(?,?,?)',
                        (request_id, event, evidence))

    def import_queue(self, queue):
        if queue.get('_schema', queue.get('schema')) != 'emc-research-correspondence-queue/1':
            raise ValueError('unsupported queue schema')
        requests = queue.get('requests')
        if not isinstance(requests, list):
            raise ValueError('requests must be a list')
        count = 0
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            for incoming in requests:
                row = dict(incoming)
                for key in ('request_id', 'subject', 'body', 'scientific_dependency', 'source_doi'):
                    row[key] = required(row.get(key), key)
                recipients = row.get('recipients')
                if not isinstance(recipients, list) or not recipients:
                    raise ValueError('recipients must be a nonempty list')
                row['recipients'] = sorted(set(required(r, 'recipient').lower() for r in recipients))
                if any(not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', r) for r in row['recipients']):
                    raise ValueError('invalid recipient')
                payload = json.dumps(row, sort_keys=True)
                # Equivalent messages with a renamed queue ID are duplicates too.
                identity = {k: row[k] for k in ('recipients', 'subject', 'body')}
                digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
                prior = self.db.execute('SELECT * FROM requests WHERE id=? OR digest=?',
                                        (row['request_id'], digest)).fetchone()
                if prior:
                    if prior['id'] == row['request_id'] and prior['payload'] != payload:
                        raise ValueError('request ID already exists with different content')
                    continue
                suppressed = self.is_suppressed(row)
                self.db.execute('INSERT INTO requests(id,digest,payload,status) VALUES(?,?,?,?)',
                                (row['request_id'], digest, payload, 'closed' if suppressed else 'prepared'))
                self.event(row['request_id'], 'imported', 'suppressed recipient' if suppressed else digest)
                count += 1
        return count

    def is_suppressed(self, payload):
        return any(self.db.execute('SELECT 1 FROM suppressed WHERE recipient=?', (r,)).fetchone()
                   for r in payload['recipients'])

    def readiness(self):
        reasons = []
        try:
            grant = json.loads(self.authority.read_text(encoding='utf-8'))['research_correspondence']
            if grant.get('standing_grant') is not True:
                reasons.append('no standing research correspondence authority')
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            reasons.append('no readable research correspondence authority')
        try:
            mailbox = json.loads((self.directory / 'mailbox.json').read_text(encoding='utf-8'))
            for key in ('provider', 'sender', 'verification_evidence'):
                required(mailbox.get(key), key)
            if mailbox.get('send_verified') is not True or mailbox.get('receive_verified') is not True:
                raise ValueError('unverified mailbox')
        except (OSError, ValueError, TypeError, AttributeError):
            reasons.append('no verified send-and-receive mailbox configuration')
        return {'ready_to_reserve': not reasons, 'reasons': reasons,
                'transport_implemented': False, 'verification': 'operator-attested'}

    def status(self):
        return {**self.readiness(), 'requests': [dict(r) for r in self.db.execute(
            'SELECT id,status,message_id FROM requests ORDER BY id')]}

    def show(self, request_id):
        row = self.db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
        if not row:
            raise ValueError('unknown request ID')
        result = dict(row)
        result['payload'] = json.loads(result['payload'])
        result['events'] = [dict(event) for event in self.db.execute(
            'SELECT sequence,event,evidence,utc FROM events WHERE request_id=? ORDER BY sequence',
            (request_id,))]
        return result

    def record_event(self, request_id, kind, evidence, next_action):
        """Record private incoming/followup context without changing send eligibility."""
        if kind not in ('reply', 'followup_context', 'note'):
            raise ValueError('event kind must be reply, followup_context, or note')
        evidence = required(evidence, 'provider evidence or private record path')
        next_action = required(next_action, 'next action')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if not self.db.execute('SELECT 1 FROM requests WHERE id=?', (request_id,)).fetchone():
                raise ValueError('unknown request ID')
            self.event(request_id, kind, json.dumps({'evidence': evidence, 'next_action': next_action}))

    def reserve(self, request_id):
        readiness = self.readiness()
        if not readiness['ready_to_reserve']:
            raise ValueError('; '.join(readiness['reasons']))
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
            if not row or row['status'] != 'prepared':
                raise ValueError('request is not prepared; reconcile uncertain sends before retrying')
            payload = json.loads(row['payload'])
            if self.is_suppressed(payload):
                raise ValueError('recipient is suppressed')
            if re.search(r'\{\{|\}\}|<[^>]+>|\[[^\]]+\]|\b(?:TODO|TBD|PLACEHOLDER)\b',
                         payload['subject'] + '\n' + payload['body'], re.I):
                raise ValueError('message contains possible placeholders; review before reserving')
            if self.db.execute("SELECT 1 FROM requests WHERE status='send_uncertain'").fetchone():
                raise ValueError('another unresolved reservation owns the send slot')
            token = str(uuid.uuid4())
            self.db.execute("UPDATE requests SET status='send_uncertain',token=? WHERE id=?", (token, request_id))
            self.event(request_id, 'reserved_send_uncertain', token)
        return token

    def reconcile(self, request_id, token, outcome, evidence, message_id=None):
        evidence = required(evidence, 'verified provider evidence')
        if outcome not in ('sent', 'absent'):
            raise ValueError('outcome must be sent or absent')
        if outcome == 'sent':
            message_id = required(message_id, 'provider message ID')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
            if not row or row['status'] != 'send_uncertain' or row['token'] != token:
                raise ValueError('no matching uncertain reservation')
            suppressed = self.is_suppressed(json.loads(row['payload']))
            status = 'sent' if outcome == 'sent' else ('closed' if suppressed else 'prepared')
            self.db.execute('UPDATE requests SET status=?,token=NULL,message_id=?,receipt=? WHERE id=?',
                            (status, message_id, evidence, request_id))
            self.event(request_id, 'verified_' + outcome, evidence)

    def refuse(self, recipient, evidence):
        recipient = required(recipient, 'recipient').lower()
        evidence = required(evidence, 'refusal evidence')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            self.db.execute('INSERT OR IGNORE INTO suppressed VALUES(?)', (recipient,))
            for row in self.db.execute('SELECT id,payload,status FROM requests').fetchall():
                if recipient in json.loads(row['payload'])['recipients']:
                    # Preserve uncertainty until provider reconciliation; suppression blocks future sends.
                    if row['status'] != 'send_uncertain':
                        self.db.execute("UPDATE requests SET status='closed' WHERE id=?", (row['id'],))
                    self.event(row['id'], 'recipient_refused', evidence)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, default=DEFAULT_STATE)
    parser.add_argument('--authority', type=Path, default=DEFAULT_AUTHORITY)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    commands.add_parser('status')
    imp = commands.add_parser('import')
    imp.add_argument('queue', type=Path)
    reserve = commands.add_parser('reserve')
    reserve.add_argument('request_id')
    show = commands.add_parser('show')
    show.add_argument('request_id')
    event = commands.add_parser('record-event')
    event.add_argument('request_id')
    event.add_argument('--kind', choices=('reply', 'followup_context', 'note'), required=True)
    event.add_argument('--evidence', required=True, help='provider thread/message evidence or private record path')
    event.add_argument('--next-action', required=True)
    for name in ('confirm-sent', 'reconcile'):
        command = commands.add_parser(name)
        command.add_argument('request_id')
        command.add_argument('--token', required=True)
        command.add_argument('--evidence', required=True, help='actual verified provider receipt/history evidence')
        command.add_argument('--message-id', required=name == 'confirm-sent')
        if name == 'reconcile':
            command.add_argument('--outcome', choices=('sent', 'absent'), required=True)
    refusal = commands.add_parser('refuse')
    refusal.add_argument('recipient')
    refusal.add_argument('--evidence', required=True)
    args = parser.parse_args(argv)
    ledger = Ledger(args.state_dir, args.authority)
    try:
        if args.command == 'import':
            result = {'imported': ledger.import_queue(json.loads(args.queue.read_text(encoding='utf-8')))}
        elif args.command == 'reserve':
            result = {'token': ledger.reserve(args.request_id), 'status': 'send_uncertain'}
        elif args.command == 'show':
            result = ledger.show(args.request_id)
        elif args.command == 'record-event':
            ledger.record_event(args.request_id, args.kind, args.evidence, args.next_action)
            result = ledger.show(args.request_id)
        elif args.command in ('confirm-sent', 'reconcile'):
            ledger.reconcile(args.request_id, args.token,
                             'sent' if args.command == 'confirm-sent' else args.outcome,
                             args.evidence, args.message_id)
            result = ledger.status()
        elif args.command == 'refuse':
            ledger.refuse(args.recipient, args.evidence)
            result = ledger.status()
        else:
            result = ledger.status()
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error) as error:
        print(json.dumps({'error': str(error)}))
        return 1
    finally:
        ledger.close()


if __name__ == '__main__':
    raise SystemExit(main())
