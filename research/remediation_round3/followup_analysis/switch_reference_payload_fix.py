"""Separate a published component reference from individual transition permission."""
from pathlib import Path
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'switch_reference_payload_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[]
def fix(e):
    if e.get('result_type')!='clinician_choice' or 'target_source_start_mg' not in e:return False
    ref=dict(scope='Published product component reference only; no individual pair calendar, target applicability, start permission or overlap permission',source_ref='RU-AGO',source_locator='§4.2 физ.с.2',published_target_start_mg=e.pop('target_source_start_mg'),published_overlap_on_first_day_of_A_reduction=e.pop('overlap_allowed_on_first_day_of_A_reduction',None))
    e.pop('target_source_start_scope',None)
    e.update(source_reference=ref,target_source_start_mg=None,overlap_allowed_on_first_day_of_A_reduction=None,no_automatic_target_start=True,automatic_direct_switch=False,next_drug_start_day=None,full_pair_calendar=None,clinical_clearance=False)
    return True
for rid,con in C['rules'].items():
    for b in con['branches']:fix(b['expected_output'])
for c in F['cases']:
    if fix(c['expected']):rows.append(c['case_id'])
for p in (O/'rules').glob('*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));r['output']['branches']=C['rules'][r['rule_id']]['branches'];p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'switch_reference_payload_repairs.json').write_text(json.dumps(dict(cases=rows,published_numbers_changed=False,scope='Source overlap/start component retained as a reference, individual top-level permission is null and target start remains nonautomatic'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Published switch components separated from permission',len(rows))
