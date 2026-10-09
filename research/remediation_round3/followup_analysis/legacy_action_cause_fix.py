"""Name already sourced causes of legacy current-treatment cessation fixtures."""
from pathlib import Path
from copy import deepcopy
import json,yaml,sys
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from bounded_source_actions import source_action_scope
assert not (O/'legacy_action_cause_repairs.json').exists(),'One-use correction'
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules'];F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[];new=[]
for c in F['cases']:
 e=c['expected'];rid=c['rule_id'];r=R[rid]
 if e['result_type']!='source_stop_action' or rid=='ago-stop' or source_action_scope(r,C[rid],c) is not None:continue
 ins={i['input_id']:i for i in r['inputs']};sid=e['stop_medication'];key=None;predicate={}
 marker='--stop-'+sid+'-'
 if marker in c['case_id']:key=c['case_id'].split(marker,1)[1]
 elif '--current-alt_ratio_uln-ongoing-above3' in c['case_id']:key='alt_ratio_uln';predicate=dict(operator='greater_than',value=3)
 elif '--current-ast_ratio_uln-ongoing-above3' in c['case_id']:key='ast_ratio_uln';predicate=dict(operator='greater_than',value=3)
 elif '--round2-seizure-' in c['case_id']:key='seizure_state';predicate=dict(operator='equals',value=c['given']['seizure_state'])
 assert key in ins and sid in ins[key]['source_refs'],c['case_id']
 if not predicate:assert c['given'][key] is True,c['case_id'];predicate=dict(operator='equals',value=True)
 sc=dict(source_ref=sid,source_locator=ins[key]['source_locator'],input=key,**predicate)
 e['source_condition']=sc;scope=source_action_scope(r,C[rid],c);assert scope is not None,c['case_id']
 rows.append(dict(case_id=c['case_id'],source_condition=sc,source_basis=c['source_basis']))
 n=deepcopy(c);n['case_id']+='--audit-final-bounded-action-legacy';n['branch_id']=None
 keep=set(scope['required_cause_fields'])|{i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
 n['given']={k:v for k,v in c['given'].items() if k in keep};n['expected']['confirmed_negatives']=[k for k,v in n['given'].items() if v is False];n['expected']['unassessed_context']=sorted(set(ins)-set(n['given']))
 n['fixture_scope']='Legacy primary cessation with explicit named cause/source/ongoing actor and no individual numerical admission form. Sparse data do not imply clinical clearance.'
 assert source_action_scope(r,C[rid],n) is not None,n['case_id'];new.append(n)
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'legacy_action_cause_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],medical_values_changed=False,scope='Existing independently read source causes named explicitly; finite sparse witnesses, not a clinical engine'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Legacy primary action causes named',len(rows),'new sparse witnesses',len(new))
