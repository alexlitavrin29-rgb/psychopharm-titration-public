from pathlib import Path
import hashlib,json
W=Path(__file__).resolve().parents[2];O=W/'research/remediation_round2'
B=json.loads((O/'baseline_manifest.json').read_text(encoding='utf-8'))['files']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[];changed=[]
for b in B:
    p=W/b['path'];same=p.is_file() and sha(p)==b['sha256']
    if b['protected']:protected.append(dict(path=b['path'],sha256_before=b['sha256'],sha256_after=sha(p) if p.is_file() else None,unchanged=same))
    elif not same:changed.append(dict(path=b['path'],change='modified' if p.is_file() else 'deleted',sha256_before=b['sha256'],sha256_after=sha(p) if p.is_file() else None))
report=dict(status='pass' if all(x['unchanged'] for x in protected) else 'fail',baseline='baseline_manifest.json',protected_files=len(protected),protected_changed=[x['path'] for x in protected if not x['unchanged']],protected=protected,working_files_changed=len(changed),working_changes=changed,application_written=False)
(O/'preservation_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
known={b['path'] for b in B};new=[];snapshot_paths=[]
for p in sorted(W.rglob('*')):
    if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:continue
    rel=p.relative_to(W).as_posix()
    if rel.startswith('research/remediation_round2/baseline/') or rel=='research/remediation_round2/final_manifest.json':continue
    snapshot_paths.append((p,rel))
    if rel not in known:new.append(rel)
(O/'changes_manifest.json').write_text(json.dumps(dict(working_changes=changed,new_files=new,protected_changes=report['protected_changed']),ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=[dict(path=rel,size=p.stat().st_size,sha256=sha(p)) for p,rel in snapshot_paths]
(O/'final_manifest.json').write_text(json.dumps(dict(date='2026-10-08',scope='Workspace files excluding baseline duplicate, caches,git and own self hash',files=snapshot),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'protected_files':len(protected),'protected_changed':report['protected_changed'],'working_files_changed':len(changed)},ensure_ascii=False))
raise SystemExit(report['status']!='pass')
