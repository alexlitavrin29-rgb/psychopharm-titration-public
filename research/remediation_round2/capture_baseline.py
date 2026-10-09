"""Capture once before round2 changes; do not overwrite earlier evidence."""
from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).resolve().parents[2];O=W/'research/remediation_round2'
manifest=O/'baseline_manifest.json'
if manifest.exists():raise SystemExit('Baseline already exists; refusing overwrite')
rows=[]
for p in sorted(W.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(W).as_posix()
    if any(x in p.parts for x in ('.git','__pycache__')) or rel.startswith('research/remediation_round2/'):continue
    protected=rel=='psychopharm_codex_pack/ACCEPTANCE.md' or rel.startswith(('research/audit/','research/remediation/'))
    rows.append(dict(path=rel,size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),protected=protected))
    if not protected and p.suffix.lower() in {'.yaml','.json','.csv','.md','.py','.txt'}:
        target=O/'baseline'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
manifest.write_text(json.dumps(dict(captured_on='2026-10-08',nature='Round2 baseline, before substantive edits',files=rows),ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Captured {len(rows)} files; protected {sum(r["protected"] for r in rows)}; no previous evidence changed.')
