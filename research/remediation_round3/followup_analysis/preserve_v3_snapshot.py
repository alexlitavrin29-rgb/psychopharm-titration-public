"""Preserve the exact first full V3 review checkpoint before review changes."""
from pathlib import Path
import json,hashlib,shutil
O=Path(__file__).resolve().parent.parent;root=O.parents[1]
target=O/'v3_review1_snapshot';manifest=O/'final_manifest_v3_review1.json'
assert not target.exists() and not manifest.exists(),'One-use preservation'
m=json.loads((O/'final_manifest.json').read_text(encoding='utf-8'));errors=[]
for row in m['files']:
 p=root/row['path'];q=target/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['path']
 q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 assert hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],row['path']
shutil.copyfile(O/'final_manifest.json',manifest)
(O/'v3_review1_preservation.json').write_text(json.dumps(dict(status='pass',snapshot_sha256=m['snapshot_sha256'],copied_files=len(m['files']),scope='Exact review checkpoint preservation; no acceptance or medical validation'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Exact V3 review checkpoint preserved',m['snapshot_sha256'],len(m['files']))
