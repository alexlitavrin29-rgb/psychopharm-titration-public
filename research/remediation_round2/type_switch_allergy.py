from pathlib import Path
from copy import deepcopy
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
schema['structures']['paired_allergy']=dict(fields={'A':'boolean | unknown | not_assessed','B':'boolean | unknown | not_assessed'},owner='A/B refer to identified from_form/to_form; two independently supplied facts, counted2; source refs per product',derived_any='May derive any confirmed positive for exclusion; unknown member never becomes false')
schema['external_context']['target_treatment_phase'].update(data_type='enum',unit=None,allowed_values=['not_started','ongoing','unknown','not_assessed'])
schema['external_context']['target_treatment_phase'].pop('type',None)
new=[]
for p in (R/'rules').glob('switch-*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));rid=r['rule_id'];i=next((x for x in r['inputs'] if x['input_id']=='allergy'),None)
    if not i:continue
    a=next(x for x in r['inputs'] if x['input_id']=='from_form')['source_refs'][0];b=next(x for x in r['inputs'] if x['input_id']=='to_form')['source_refs'][0]
    i.update(data_type='paired_allergy',allowed_values=[],structure_ref='remediation_round2/input_contracts.yaml#structures/paired_allergy',question_ru='Отдельно: гиперчувствительность к A и его компонентам? К B и его компонентам?',source_owner_by_member={'A':a,'B':b})
    con=C['rules'][rid]
    for member,sid in [('A',a),('B',b)]:
        con['typed_source_conditions'].append(dict(input='allergy',field=member,operator='field_equals',value=True,action='not_applicable standard branch',source_ref=sid,source_locator='§4.3 с.4' if sid=='RU-ESC' else '§4.3 с.17' if sid=='RU-PAROX' else '§4.3 с.3'))
    for c in D['cases']:
        if c['rule_id']==rid and type(c['given'].get('allergy')) is bool:c['given']['allergy']={'A':c['given']['allergy'],'B':c['given']['allergy']}
    base=next(c for c in D['cases'] if c['rule_id']==rid and c['branch_id'])
    for member,sid in [('A',a),('B',b)]:
        for state in [True,'omitted','unknown','not_assessed']:
            c=deepcopy(base);c.update(case_id=rid+'--round2-allergy-'+member+'-'+str(state),branch_id=None)
            c['given']['allergy']={'A':False,'B':False}
            if state=='omitted':c['given']['allergy'].pop(member)
            else:c['given']['allergy'][member]=state
            c['expected']=dict(result_type='not_applicable' if state is True else 'insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[] if state is True else ['allergy.'+member],clinical_clearance=False,unconditional_future_stages=False)
            if state is True:c['expected']['source_condition']=next(x for x in con['typed_source_conditions'] if x['input']=='allergy' and x.get('field')==member)
            new.append(c)
    p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
D['cases']+=new
(O/'input_contracts.yaml').write_text(yaml.safe_dump(schema,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
print('A/B allergy facts explicitly typed;32 independent member expectations added.')
