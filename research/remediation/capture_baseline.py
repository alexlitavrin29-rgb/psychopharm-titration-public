"""Record pre-remediation bytes; never overwrite an existing baseline."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/remediation'
manifest = OUT / 'baseline_manifest.json'
if manifest.exists():
    raise SystemExit('Baseline already exists; preserved')
files = sorted(p for directory in ('psychopharm_codex_pack', 'research', 'tmp_acceptance')
               for p in (ROOT / directory).rglob('*')
               if p.is_file() and OUT not in p.parents and '__pycache__' not in p.parts)
files += [ROOT / 'AGENTS.md', ROOT / 'PROJECT_BRIEF.md']
records = []
for p in files:
    rel = p.relative_to(ROOT).as_posix()
    data = p.read_bytes()
    records.append({'path': rel, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    if p.suffix.lower() in {'.yaml', '.json', '.csv', '.md', '.py'} and 'audit' not in p.parts:
        backup = OUT / 'baseline' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, backup)
manifest.write_text(json.dumps({'captured_on': '2026-10-08', 'files': records}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Captured {len(records)} files; audit and original ACCEPTANCE protected by hashes')
