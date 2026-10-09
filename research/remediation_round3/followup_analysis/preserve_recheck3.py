"""Preserve the exact 177-file independently reviewed snapshot before correcting it."""
from pathlib import Path
import json,hashlib,shutil
O=Path(__file__).resolve().parent.parent;W=O.parents[1]
M=json.loads((O/'final_manifest.json').read_text(encoding='utf-8'))
assert M['snapshot_sha256']=='ac33f61373c22b1c160de40057815b16c27bc67e4beb870a56057992f0b06148'
assert not (O/'final_manifest_recheck3.json').exists(),'Snapshot already preserved'
for row in M['files']:
    p=W/row['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['path']
for row in M['files']:
    p=W/row['path'];q=O/'recheck3_snapshot'/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    assert hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],row['path']
shutil.copyfile(O/'final_manifest.json',O/'final_manifest_recheck3.json')
for p in O.glob('*verification*.json'):
    shutil.copyfile(p,O/('recheck3_executor_'+p.name))
print('Preserved',len(M['files']),'exact files and current executor verification reports')
