from pathlib import Path
import datetime, hashlib, json, sys
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
R3 = ROOT / 'research/remediation_round3'
PREV = OUT.parent / 'recheck2'
def read(p): return json.loads(p.read_text('utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
m=read(R3/'final_manifest.json')
assert m['snapshot_sha256']=='ac33f61373c22b1c160de40057815b16c27bc67e4beb870a56057992f0b06148'
assert len(m['files'])==177
assert all(sha(ROOT/x['path'])==x['sha256'] for x in m['files'])
prior=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p)) for p in OUT.parent.rglob('*') if p.is_file() and OUT not in p.parents]
tracked={x['path'].replace('\\','/'):x for x in m['files']}
for x in read(PREV/'initial_manifest.json')['files']:
    p=ROOT/x['path']
    tracked.setdefault(x['path'].replace('\\','/'),dict(path=x['path'],sha256=sha(p)))
save('initial_manifest.json',dict(snapshot=m['snapshot_sha256'],core_files=177,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_own_audit_files=prior,files=list(tracked.values())))
old={x['path'].replace('\\','/'):x for x in read(R3/'final_manifest_recheck2.json')['files']}
new={x['path'].replace('\\','/'):x for x in m['files']}
save('snapshot_changes.json',dict(old_snapshot=read(R3/'final_manifest_recheck2.json')['snapshot_sha256'],new_snapshot=m['snapshot_sha256'],added=sorted(set(new)-set(old)),removed=sorted(set(old)-set(new)),changed=[k for k in old.keys() & new.keys() if old[k]['sha256']!=new[k]['sha256']]))
s=(PREV/'verify_independent.py').read_text('utf8')
s=s.replace('import json, yaml, hashlib','import json, yaml, hashlib, sys\nsys.dont_write_bytecode=True\nsys.path.insert(0,str(Path(__file__).resolve().parents[3]/\'research/remediation_round3\'))')
s=s.replace("    if kind == 'field_true': return given.get(p['field']) is True", "    if kind == 'field_true': return given.get(p['field']) is True\n    if kind == 'all_equals': return all(given.get(k)==v for k,v in p['values'].items())")
s=s.replace("if rule['identity']['mode']=='start' and c['external_context'].get('treatment_phase') in ('ongoing','unknown'): initial += ['selected_drug_treatment_phase']", "if c['external_context'].get('treatment_phase') in ('ongoing','unknown','not_started') and not (rule['identity']['mode']=='start' and c['external_context'].get('treatment_phase')=='not_started'): initial += ['selected_drug_treatment_phase']")
s=s.replace('All 531 supplied traces','All 737 supplied traces').replace('all 5224 expected','all 5430 expected')
(OUT/'verify_independent.py').write_text(s,encoding='utf8')
s=(PREV/'additional_checks.py').read_text('utf8').replace('import json,yaml,hashlib,re,fitz','import json,yaml,hashlib,re,fitz,sys\nsys.dont_write_bytecode=True\nsys.path.insert(0,str(Path(__file__).resolve().parents[3]/\'research/remediation_round3\'))')
(OUT/'additional_checks.py').write_text(s,encoding='utf8')
notes=read(PREV/'source_verification.json')
changes=[]
for x in notes['sources']:
    p=Path(x['path'])
    if not p.is_absolute():p=ROOT/p
    if not p.is_file():p=ROOT/'research'/x['path']
    if not p.is_file() or sha(p)!=x['sha256']:changes.append(x['source_id'])
assert not changes
notes.update(snapshot=m['snapshot_sha256'],source_original_hash_changes=changes,recheck3_basis='Earlier actual reading and visual page checks reused only after exact source SHA equality; additional recheck3 pages recorded separately. No repeated human registry download claimed.')
save('source_verification.json',notes)
print('setup',len(prior),'prior own files; changed',len(read(OUT/'snapshot_changes.json')['changed']))
