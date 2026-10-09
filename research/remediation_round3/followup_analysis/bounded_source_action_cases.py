"""Prepare explicit sparse same-action witnesses for finite terminal scopes."""
from pathlib import Path
from copy import deepcopy
import sys,json,yaml
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from bounded_source_actions import source_action_scope
assert not (O/'bounded_source_action_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};rows=[];new=[];seen=set()
for c in F['cases']:
    r=R[c['rule_id']];scope=source_action_scope(r,C['rules'][c['rule_id']],c)
    if scope is None:continue
    rows.append(dict(case_id=c['case_id'],rule_id=c['rule_id'],**scope))
    marker=json.dumps([c['rule_id'],scope['primary_cause'],c['external_context'],[(k,c['given'].get(k)) for k in scope['required_cause_fields']]],sort_keys=True,ensure_ascii=False)
    if marker in seen:continue
    seen.add(marker);n=deepcopy(c);n['case_id']=c['case_id']+'--audit-final-bounded-action';n['branch_id']=None
    keep=set(scope['required_cause_fields'])|{i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
    n['given']={k:v for k,v in c['given'].items() if k in keep}
    n['expected']['confirmed_negatives']=[k for k,v in n['given'].items() if v is False]
    n['expected']['unassessed_context']=sorted({i['input_id'] for i in r['inputs'] if i['input_id'] not in n['given']})
    n['expected']['clinical_clearance']=False
    n['fixture_scope']='Same known primary current-treatment action with source identity/cause/actor-phase only. No numerical admission form, patient dose, future taper or target permission. All absent fields unassessed.'
    assert source_action_scope(r,C['rules'][c['rule_id']],n) is not None,n['case_id'];new.append(n)
F['cases']+=new
for rid,con in C['rules'].items():
    con['bounded_source_action_input_policy']='Individual numeric required_inputs do not delay a known source-specific current-treatment cessation. Only declared source cause, actual source identity and ongoing actor phase are prerequisites; supplied context remains counted. Prepared source-action specifications do not execute a medical engine.'
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8');(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'bounded_source_action_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],scope='Finite source cause/identity/phase certificates, not a claim of clinical exhaustive routing; independent acceptance pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Bounded same-action input contracts',len(rows),'new sparse witnesses',len(new))
