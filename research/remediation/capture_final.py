"""Capture final check reports and SHA preservation. No medical inference or audit writes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R.parent;O=R/'remediation'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=read(O/'baseline_manifest.json')['files'];changed=[];removed=[];protected=[]
for row in base:
    p=W/row['path'];current=sha(p) if p.is_file() else None
    locked=row['path']=='psychopharm_codex_pack/ACCEPTANCE.md' or row['path'].startswith('research/audit/')
    if locked:protected.append(dict(path=row['path'],baseline_sha256=row['sha256'],current_sha256=current,unchanged=current==row['sha256']))
    if current is None:removed.append(row['path'])
    elif current!=row['sha256']:changed.append(dict(path=row['path'],baseline_sha256=row['sha256'],current_sha256=current))
pres=dict(status='pass' if all(x['unchanged'] for x in protected) else 'fail',protected_files=len(protected),files=protected)
write(O/'preservation_check.json',pres)
baseline_paths={x['path'] for x in base}
new=[p.relative_to(W).as_posix() for p in R.rglob('*') if p.is_file() and p.relative_to(W).as_posix() not in baseline_paths and '/baseline/' not in p.as_posix() and '__pycache__' not in p.as_posix()]
write(O/'changes_manifest.json',dict(baseline_file_count=len(base),changed_existing_files=changed,removed_existing_files=removed,new_research_files=sorted(new)))
checks=[]
score=read(O/'scoring.json');acceptance=read(O/'acceptance_recheck.json')
weights=[x['weight_percent'] for x in score['dimensions']]
arithmetic=sum(x['score']*x['weight_percent']/100 for x in score['dimensions'])
score_ok=weights==[25,30,20,15,10] and abs(arithmetic-score['weighted_score'])<1e-10 and score['final_score']==min(arithmetic,score['original_audit_cap'])
counts_ok=len(acceptance['criteria'])==30 and sum(c['status']=='satisfied_for_research_stage' for c in acceptance['criteria'])==acceptance['satisfied_count'] and sum(c['status']=='partial' for c in acceptance['criteria'])==acceptance['partial_count']
checks.append(dict(check='score_and_acceptance_arithmetic',status='pass' if score_ok and counts_ok else 'fail',meaning='Weights, arithmetic and declared status counts only; not truth of the assessment'))
for name,src,target in [('structure',R/'verification_report.json',O/'verification_report.json'),('original_negative',R/'verification_negative_checks.json',O/'original_negative_checks.json'),('contracts',O/'contract_verification.json',None),('new_negative',O/'new_negative_checks.json',None)]:
    data=read(src)
    if target:target.write_bytes(src.read_bytes())
    checks.append(dict(check=name,status=data['status'],report=(target or src).relative_to(R).as_posix(),report_sha256=sha(target or src),
        meaning=data.get('nature'),rejected_mutations=sum(c.get('rejected',False) for c in data.get('cases',[]))))
checks.append(dict(check='protected_originals',status=pres['status'],report='remediation/preservation_check.json',meaning='Byte identity, not medical validation'))
status='pass' if all(c['status']=='pass' for c in checks) else 'fail'
write(O/'verification_results.json',dict(status=status,checks=checks,source_currency_proven=False,calculator_execution=False,clinical_validation='not_performed',
    full_synthetic_expected_cases=len(read(O/'full_scenarios.json')['cases']),unchanged_acceptance_criteria=30,
    limitation='PASS covers listed static invariants and rejection mutations. It is not independent evidence of every medical statement, latest source revision, or calculator execution.'))
print(json.dumps(dict(status=status,protected_unchanged=len(protected),changed_existing=len(changed),removed_existing=removed,checks=[(c['check'],c['status']) for c in checks])))
raise SystemExit(status!='pass')
