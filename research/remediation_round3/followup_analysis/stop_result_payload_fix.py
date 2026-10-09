"""Remove inherited routine treatment payload from every cessation terminal."""
from pathlib import Path
import json
O=Path(__file__).resolve().parent.parent
assert not (O/'stop_result_payload_repairs.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
keys={'duration_constraint','maximum_mg','minimum_increase_interval_weeks','review_period_weeks','source_initial_mg','initial_days','source_next_mg','hold_if','recommended_mg','optional_increment_mg','minimum_interval_weeks','beyond_recommended_requires','target_source_start_mg','overlap_allowed_on_first_day_of_A_reduction','monitoring','published_option_mg','conditional_next_total_mg','initial_period_weeks'}
rows=[]
for c in F['cases']:
    e=c['expected']
    if e['result_type']!='source_stop_action':continue
    removed={k:e.pop(k) for k in list(e) if k in keys}
    if removed:rows.append(dict(case_id=c['case_id'],removed=removed,source_condition=e.get('source_condition'),source_actions=e.get('source_actions',[]),source_basis=c['source_basis']))
    e.update(total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],clinical_clearance=False,automatic_next_stage=False)
    if c['external_context']['mode']=='switch':e.update(no_automatic_target_start=True,next_drug_start_day=None,full_pair_calendar=None,automatic_direct_switch=False,target_start_allowed=False)
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'stop_result_payload_repairs.json').write_text(json.dumps(dict(rows=rows,cases_with_removed_routine_payload=len(rows),all_stop_cases=sum(c['expected']['result_type']=='source_stop_action' for c in F['cases']),scope='Current source cessation/urgent help retains its own primary actions and post-cessation followup. No inherited future dose, routine taper, target-start/overlap or pretreatment monitoring schedule. Independent acceptance pending.'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Cessation terminals aligned',len(rows),'of',sum(c['expected']['result_type']=='source_stop_action' for c in F['cases']))
