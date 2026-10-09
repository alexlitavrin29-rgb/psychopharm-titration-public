from pathlib import Path
from copy import deepcopy
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
actions={
 'arrhythmia_signs':[dict(action='discontinue_ESC',source_ref='RU-ESC',source_locator='§4.4 с.6'),dict(action='obtain_ECG',source_ref='RU-ESC',source_locator='§4.4 с.6')],
 'serotonin_syndrome_signs':[dict(action='immediately_discontinue_SSRI_and_current_serotonergic_drugs',source_ref='RU-ESC',source_locator='§4.4 с.6'),dict(action='start_symptomatic_treatment_by_clinician',source_ref='RU-ESC',source_locator='§4.4 с.6',automatic_medication_or_dose=None)]}
for p in (R/'rules').glob('*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));rid=r['rule_id'];con=C['rules'][rid]
    if any(s['source_id']=='RU-ESC' for s in r['sources']):
        for i in r['inputs']:
            for key in ['source_locators','source_locators_by_ref']:
                if isinstance(i.get(key),dict) and 'RU-ESC' in i[key]:
                    i[key]['RU-ESC']={'allergy':'§4.3 с.4','age':'§4.1 с.2; §4.2 с.3','medicines':'§4.3 с.4; §4.5 с.7–9','pregnancy':'§4.6 с.10','lactation':'§4.6 с.10'}.get(i['input_id'],'§4.2–4.6 с.2–10, current original')
    if rid.startswith('esc'):
        con['urgent_source_actions']=[dict(input=k,equals=True,actions=v) for k,v in actions.items()]
        r['logic']['urgent_source_actions']=deepcopy(con['urgent_source_actions'])
    if rid in ['switch-ser-esc','switch-esc-ser']:
        a='RU-SER' if rid=='switch-ser-esc' else 'RU-ESC';b='RU-ESC' if a=='RU-SER' else 'RU-SER'
        a_loc='§4.2 с.2–3; §4.4 с.4–6';b_loc='§4.1–4.6 с.2–10' if b=='RU-ESC' else '§4.1–4.6 с.1–11'
        for i in r['inputs']:
            k=i['input_id']
            if k in ['from_form','to_form']:
                owner=a if k=='from_form' else b;i.update(source_refs=[owner],source_locator='§3 с.1–2' if owner=='RU-ESC' else '§3 с.1')
            elif k in ['current_dose','duration','last_dose_time','withdrawal_symptoms']:i.update(source_refs=[a],source_locator=a_loc)
            elif k=='target_applicability':i.update(source_refs=[b],source_locator=b_loc,why_needed='Именованная оценка применимости B; source-gap результат не подтверждает все ограничения B и не разрешает его старт.')
            elif k in ['medicines','maoi_type','maoi_stopped_at']:i.update(source_refs=[a,b],source_locator=a+' §4.3/4.5; '+b+' §4.3/4.5')
        r['logic']['maoi_history_contract']['scope']='Shared patient MAOI history; RU-SER is '+('A' if a=='RU-SER' else 'B')+' and its own §4.3/4.5 interval applies only to SER. RU-ESC is '+('A' if a=='RU-ESC' else 'B')+' and has separate §4.5 intervals. No history interval licenses an SSRI→SSRI calendar or overlap.'
        r['logic']['maoi_history_contract']['source_product_role']='A' if a=='RU-SER' else 'B'
        r['logic']['additional_maoi_history_basis']=dict(source_ref='RU-ESC',source_product_role='A' if a=='RU-ESC' else 'B',source_locator='§4.5 с.7–8',scope='ESC-specific history; not a pair switch washout',irreversible_after_days=14,to_maoi_days=7,moclobemide_after_minimum_days=1)
    p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for c in D['cases']:
    if c['rule_id'].startswith('esc') and c['expected']['result_type']=='source_stop_action':
        for k,v in actions.items():
            if c['given'].get(k) is True:
                c['expected']['source_actions']=deepcopy(v)
                if k=='serotonin_syndrome_signs':c['expected']['other_current_serotonergic_drugs_action']='discontinue immediately if present; not an invented regimen'
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
print('Current A/B locators and MAOI owner scope repaired; ESC arrhythmia ECG/serotonin symptomatic actions complete.')
