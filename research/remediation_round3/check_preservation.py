"""Verify historical documents and original source snapshots against round3 baseline."""
from pathlib import Path
import hashlib, json

O = Path(__file__).resolve().parent
R = O.parents[1]
baseline = json.loads((O / 'baseline_manifest.json').read_text(encoding='utf-8'))
changed, errors = [], []
protected_count = original_count = 0
for row in baseline['files']:
    p = R / row['path']
    immutable_original = row['path'].startswith(('research/source_downloads/', 'research/source_snapshots/'))
    protected_count += bool(row['protected'])
    original_count += immutable_original
    same = p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
    if not same:
        changed.append(row['path'])
        if row['protected'] or immutable_original: errors.append(row['path'])
report = dict(status='pass' if not errors else 'fail', protected_files=protected_count,
              original_source_files=original_count, changed_baseline_files=changed,
              changed_protected_or_original_files=errors,
              scope='Preservation only; no medical, necessity or question-limit acceptance')
(O / 'preservation_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(errors))
