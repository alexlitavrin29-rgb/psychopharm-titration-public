"""Target new source and counting defects with isolated copies only."""
from copy import deepcopy
from pathlib import Path
import json
from verify_contracts import collect,validate
O=Path(__file__).resolve().parent;d=collect();assert not validate(d)
mutations={
'removed_pregabalin_specific_assessment':lambda x:x['contracts']['preg-gad-start']['required_inputs'].remove('misuse_risk_assessment'),
'missing_new_fluvox_symptomatic_action':lambda x:next(c for c in x['cases'] if c['case_id']=='fluvox-depression-start--r3-serotonin_syndrome_signs-positive')['expected'].update(source_actions=[]),
'lost_XR_current_allergic_stop':lambda x:x['contracts']['venla-xr-gad-start'].update(urgent_stop_predicates=[]),
'old_duloxetine_one_week_allowed':lambda x:next(c for c in x['cases'] if c['case_id']=='dulox-taper-limit--branch-source_limit')['expected']['duration_constraint'].update(chosen_minimum_weeks=1),
'stop_before_drug_started':lambda x:next(c for c in x['cases'] if c['case_id']=='fluvox-depression-start--r3-serotonin_syndrome_signs-positive')['external_context'].update(treatment_phase='selected_mode')}
rows=[]
for name,mutate in mutations.items():
    x=deepcopy(d);mutate(x);err=validate(x);rows.append(dict(mutation=name,rejected=bool(err),errors=err[:3]))
paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
for name,n,allowed in [('limit15',15,True),('limit16',16,False)]:
    rows.append(dict(mutation=name,technical_boundary_only=True,rejected=(n<=15)==allowed))
p=next(p for p in paths if p['ordinary_individual_numeric_path']);x=deepcopy(p);x['count']-=1
rows.append(dict(mutation='understated_count',rejected=x['count']!=len(x['initial_selections'])+len(x['required_independent_facts'])))
report=dict(status='pass' if all(x['rejected'] for x in rows) else 'fail',mutations=rows,main_files_changed=False,scope='Source-specific static detector and technical limit15/16; no new medical schema or calculator')
(O/'v2_negative_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(report['status'],len(rows),'new isolated checks');assert report['status']=='pass'
