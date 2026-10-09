"""Preserve the exact227-file delta for independent final acceptance."""
from pathlib import Path
import json,hashlib,shutil
O=Path(__file__).resolve().parent.parent;root=O.parents[1];target=O/'v3_recheck1_snapshot';manifest=O/'final_manifest_v3_recheck1.json'
assert not target.exists() and not manifest.exists(),'One-use preservation'
m=json.loads((O/'final_manifest.json').read_text(encoding='utf-8'))
assert m['snapshot_sha256']=='27ef14e77185b7b104d43199664a5b1ca42b73dd8b09f921ee539e97fae971f8' and len(m['files'])==227
for row in m['files']:
 p=root/row['path'];q=target/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['path']
 q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);assert hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],row['path']
shutil.copyfile(O/'final_manifest.json',manifest)
(O/'v3_recheck1_preservation.json').write_text(json.dumps(dict(status='pass',snapshot_sha256=m['snapshot_sha256'],copied_files=len(m['files']),nature='Exact snapshot preservation; independent acceptance separate'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Final delta snapshot preserved',m['snapshot_sha256'],len(m['files']))
