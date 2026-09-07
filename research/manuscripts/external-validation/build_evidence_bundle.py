"""Build the public evidence ZIP from byte-verified, committed source files."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUDIT = ROOT / 'research/autonomy/peerj-validation-audit-2026-09-07'
MAPPING = AUDIT / 'public-bundle-integration.json'
OUTPUT = HERE / 'emc-external-validation-comment-evidence.zip'
STAMP = HERE / 'emc-external-validation-comment-evidence.build-stamp.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    mapping = json.loads(MAPPING.read_text(encoding='utf-8'))
    entries = mapping['files']
    if len({r['archive_path'] for r in entries}) != len(entries):
        raise ValueError('Duplicate archive paths')
    verified = []
    for entry in entries:
        rel = entry['repository_path']
        source = ROOT / rel
        data = source.read_bytes()
        committed = subprocess.check_output(['git', 'show', commit + ':' + rel], cwd=ROOT)
        if data != committed or sha(data) != entry['sha256']:
            raise ValueError('Source is not the verified committed file: ' + rel)
        archive_path = Path(entry['archive_path'])
        if archive_path.is_absolute() or '..' in archive_path.parts:
            raise ValueError('Unsafe archive member')
        verified.append((entry, data))
    with zipfile.ZipFile(OUTPUT, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for entry, data in sorted(verified, key=lambda pair: pair[0]['archive_path']):
            info = zipfile.ZipInfo(entry['archive_path'], date_time=(2026, 9, 7, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(entries):
            raise ValueError('Invalid archive')
        for entry in entries:
            if sha(archive.read(entry['archive_path'])) != entry['sha256']:
                raise ValueError('Archive member changed')
    stamp = {
        'artifact': OUTPUT.name,
        'artifact_sha256': sha(OUTPUT.read_bytes()),
        'bytes': OUTPUT.stat().st_size,
        'source_commit': commit,
        'builder': Path(__file__).relative_to(ROOT).as_posix(),
        'builder_sha256': sha(Path(__file__).read_bytes()),
        'source_mapping_sha256': sha(MAPPING.read_bytes()),
        'members': entries,
        'scope': 'Packaging of original source bytes and reproduced metadata; no expression analysis.'
    }
    STAMP.write_text(json.dumps(stamp, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'artifact': OUTPUT.name, 'bytes': stamp['bytes'],
                      'sha256': stamp['artifact_sha256'], 'members': len(entries),
                      'source_commit': commit}))


if __name__ == '__main__':
    main()
