"""Publish explicit no-example/no-calendar witnesses without a dose admission form."""
from pathlib import Path
from copy import deepcopy
import json,yaml,sys
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from bounded_unselected_example import unselected_example_scope
assert not (O/'unselected_example_scope_repairs.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rid='switch-parox-ago-selected-example';r=yaml.safe_load((O/'rules'/(rid+'.yaml')).read_text(encoding='utf-8'));new=[];rows=[]
for c in F['cases']:
 if c['rule_id']!=rid or unselected_example_scope(r,c) is None:continue
 c['expected'].update(no_automatic_target_start=True,no_automatic_medication_change=True,clinical_clearance=False);rows.append(c['case_id'])
base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='not_selected')
for chosen in [False,True]:
 n=deepcopy(base);n['case_id']=rid+'--audit-final-unselected-example-'+str(chosen).lower();n['branch_id']=None;n['given']={k:n['given'][k] for k in ['from_form','to_form']};n['given']['example_selected']=chosen
 if chosen:n['given']['current_dose']=30
 n['external_context']['treatment_phase']='selected_mode';n['external_context'].pop('target_treatment_phase',None)
 n['expected'].update(confirmed_negatives=['example_selected'] if not chosen else [],unassessed_context=sorted(i['input_id'] for i in r['inputs'] if i['input_id'] not in n['given']),no_automatic_target_start=True,no_automatic_medication_change=True)
 n['fixture_scope']='Only absence of the selected published 40 mg example, no patient calendar/B start. Non40 30 mg is a synthetic input, not a published taper recommendation.'
 assert unselected_example_scope(r,n) is not None;new.append(n)
F['cases']+=new;(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'unselected_example_scope_repairs.json').write_text(json.dumps(dict(cases=rows,new_cases=[c['case_id'] for c in new],scope='False choice or known non40 dose; unknown selection never treated as false',medical_parameters_changed=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Not-selected scopes',len(rows),'new sparse witnesses',len(new))
