"""Make the absence of pair permission explicit on every bounded reference."""
from pathlib import Path
import json
O=Path(__file__).resolve().parent.parent
assert not (O/'reference_guard_repairs.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[]
guard=dict(no_automatic_target_start=True,automatic_direct_switch=False,next_drug_start_day=None,full_pair_calendar=None,clinical_clearance=False)
for c in F['cases']:
 e=c['expected']
 if c['rule_id'] not in {'switch-esc-ago','switch-parox-ago','switch-ser-ago'} or e['result_type']!='clinician_choice':continue
 if any(e.get(k)!=v or k not in e for k,v in guard.items()):rows.append(c['case_id'])
 e.update(guard)
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'reference_guard_repairs.json').write_text(json.dumps(dict(cases=rows,published_values_changed=False,scope='Explicit no patient pair calendar/start on all bounded references, including caution/physician-choice variants'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Explicit reference guards aligned',len(rows))
