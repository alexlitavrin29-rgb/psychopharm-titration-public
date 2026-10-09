"""Last finite metadata delta; previous complete USED review is reused, not rerun."""
from pathlib import Path
from copy import deepcopy
import json,yaml,hashlib,sys,ast,collections
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
OLD=ROOT/'research/remediation_round3/v3_recheck1_snapshot/research/remediation_round3'
PRIOR=ROOT/'research/acceptance_v3_audit/final_recheck'
SHA='b66e9e0dadca7234ed1e66bc8c103047ff2f96e963313d07dd0075494695f0a4'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
errors=[];checks=[]
def ck(label,ok,detail=None):
 x=dict(check=label,pass_=bool(ok),detail=detail);checks.append(x)
 if not ok:errors.append(x)
old={c['case_id']:c for c in read(OLD/'full_scenarios.json')['cases']}
current={c['case_id']:c for c in read(R/'full_scenarios.json')['cases']}
oldpaths={p['full_example']:p for p in read(OLD/'actual_question_paths.json')}
paths=read(R/'actual_question_paths.json');pp={p['full_example']:p for p in paths}
ids=set(read(PRIOR/'findings.json')['findings'][0]['exact_cases'])
journal=read(R/'sparse_population_metadata_repairs.json')['rows'];ck('repair exact22 own finding IDs',len(journal)==22 and {x['case_id'] for x in journal}==ids)
ck('all6646 case IDs and2652 path IDs unchanged',set(old)==set(current) and set(pp)==set(oldpaths) and len(current)==6646 and len(pp)==2652)
def sanitized(c):
 c=deepcopy(c);e=c['expected'];e.pop('population_applicability',None);e['unassessed_context']=[k for k in e.get('unassessed_context',[]) if k!='age'];return c
case_deltas=[]
for cid,c in current.items():
 if old[cid]!=c:
  case_deltas.append(cid);ck('only exact population22 and unassessed age changed',cid in ids and sanitized(old[cid])==sanitized(c),cid)
for cid in ids:
 c=current[cid];e=c['expected'];p=pp[cid]
 ck('raw absent age is not assessed',c['given'].get('age') in [None,'unknown','not_assessed'] and e['population_applicability']=='not_assessed' and 'age' in e['unassessed_context'],cid)
 ck('projected absent age is not assessed',p['full_projected_given'].get('age') in [None,'unknown','not_assessed'] and p['full_projected_expected']['population_applicability']=='not_assessed' and 'age' in p['full_projected_expected']['unassessed_context'],cid)
ck('only exact22 raw cases changed',set(case_deltas)==ids)
def sanitized_path(p):
 p=deepcopy(p);e=p['full_projected_expected'];e.pop('population_applicability',None);e['unassessed_context']=[k for k in e.get('unassessed_context',[]) if k!='age'];return p
path_deltas=[]
for cid,p in pp.items():
 if p!=oldpaths[cid]:path_deltas.append(cid)
 ck('same path counts/questions/given/phase/actions except population metadata',sanitized_path(p)==sanitized_path(oldpaths[cid]),cid)
ck('only exact22 projected paths changed',set(path_deltas)==ids)
graphs=yaml.load((R/'question_graphs.yaml').read_text(encoding='utf8'),Loader=yaml.CSafeLoader)['graphs']
oldgraphs=yaml.load((OLD/'question_graphs.yaml').read_text(encoding='utf8'),Loader=yaml.CSafeLoader)['graphs']
for g,h in zip(graphs,oldgraphs):
 ck('graph nodes/edges/rule identification unchanged',{k:v for k,v in g.items() if k!='paths'}=={k:v for k,v in h.items() if k!='paths'},g['rule_id'])
 ck('graph copies agree with actual corrected path objects',all(p==pp[p['full_example']] for p in g['paths']),g['rule_id'])
# Repeat our prior independent population invariant for all actual reference records.
population_rows=[]
for location,objects in [('raw',current.values()),('projected',[dict(case_id=p['full_example'],given=p['full_projected_given'],expected=p['full_projected_expected']) for p in paths])]:
 for c in objects:
  e=c['expected'];g=c['given'];age=g.get('age');label=e.get('population_applicability')
  if label=='adult_source_population':ck('own adult population requires actually supplied known adult age',type(age) in [int,float] and age>=18,[location,c['case_id'],age])
  if e.get('adult_source_reference_only'):
   adult=type(age) in [int,float] and age>=18
   ck('prior own reference population invariant',label=='adult_source_population' if adult else label in ['not_assessed','pediatric_plan_not_established','pediatric_withdrawal_plan_not_established'],[location,c['case_id'],age,label])
   ck('reference no individual dose/period/schedule',e.get('total_daily_dose_mg') is None and not e.get('schedule') and e.get('individual_duration_weeks') is None and e.get('individual_taper_schedule') is None and e.get('clinical_clearance') is False,[location,c['case_id']])
   population_rows.append(dict(location=location,case_id=c['case_id'],age=age,population=label))

# Read-only repeat of new guard and its thirteenth mutation; do not call run() writers.
sys.path.insert(0,str(R))
ns={'__file__':str(R/'verify_result_scopes.py'),'__name__':'read_only_guard_import'}
exec(compile((R/'verify_result_scopes.py').read_text(encoding='utf8'),str(R/'verify_result_scopes.py'),'exec'),ns)
data=dict(rules={p.stem:yaml.safe_load(p.read_text(encoding='utf8')) for p in (R/'rules').glob('*.yaml')},contracts=yaml.safe_load((R/'result_contracts.yaml').read_text(encoding='utf8'))['rules'],cases=list(current.values()))
baseline=ns['check'](data,paths);ck('current result scope guard read-only baseline',not baseline,baseline)
target=next(c for c in data['cases'] if '--audit-final-conditional-adult-reference' in c['case_id'])
dd=deepcopy(data);next(c for c in dd['cases'] if c['case_id']==target['case_id'])['expected']['population_applicability']='adult_source_population'
mutation_errors=ns['check'](dd,paths);ck('actual13th mutation absent age normalized adult rejected',any('adult applicability lacks known age' in x for x in mutation_errors),mutation_errors)
controls=[]
for value in [None,'unknown','not_assessed',17,True,'18']:
 dd=deepcopy(data);t=next(c for c in dd['cases'] if c['case_id']==target['case_id']);t['given']['age']=value;t['expected']['population_applicability']='adult_source_population'
 ee=ns['check'](dd,paths);ok=any('adult applicability lacks known age' in x for x in ee);controls.append(dict(raw_age=value,rejected=ok));ck('finite nonadult/raw unknown guard countercheck',ok,value)
for value in [None,'unknown','not_assessed',17,True,'18']:
 q=deepcopy(paths);p=next(p for p in q if p['full_example']==target['case_id']);p['full_projected_given']['age']=value;p['full_projected_expected']['population_applicability']='adult_source_population'
 ee=ns['check'](data,q);ok=any('projected adult applicability uses unasked age' in x for x in ee);controls.append(dict(projected_age=value,rejected=ok));ck('finite nonadult/projected unknown guard countercheck',ok,value)

# Verify the exact old228/227 difference, rather than trusting the editor journal.
old_manifest=read(PRIOR/'initial_manifest.json');new_manifest=read(OUT/'initial_manifest.json')
changed={x['path'] for x in new_manifest['files'] if {v['path']:v['sha256'] for v in old_manifest['files']}.get(x['path'])!=x['sha256']}
expected_changed={'research/remediation_round3/'+p for p in ['full_scenarios.json','question_graphs.yaml','actual_question_paths.json','verify_result_scopes.py','v3_completion_response.md','sparse_population_metadata_repairs.json']}
ck('only six intended changed/new files',changed==expected_changed,sorted(changed))
ck('all228 actual core hashes match frozen manifest',all(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in new_manifest['files']))
save('metadata_delta_checks.json',dict(snapshot=SHA,assertions=len(checks),errors=errors,checks=checks,changed_raw_cases=case_deltas,changed_projected_paths=path_deltas,
 previous_primary_numerical_causal_checks_reused='final_recheck227 and prior sameSHA USED independent primary reading; unchanged source/numeric/actions/questions confirmed by exact diff',clinical_engine_executed=False))
save('population_registry.json',population_rows)
save('guard_mutation_checks.json',dict(author13th_mutation_rejected=bool(mutation_errors),actual_error=mutation_errors,own_twelve_controls=controls,all_rejected=all(c['rejected'] for c in controls),baseline_errors=baseline,scope='Actually called current read-only check; not author run/report or application execution.'))
print(json.dumps(dict(assertions=len(checks),errors=len(errors),changed_cases=len(case_deltas),changed_paths=len(path_deltas),mutation13_rejected=bool(mutation_errors),first_errors=errors[:5]),ensure_ascii=False))
