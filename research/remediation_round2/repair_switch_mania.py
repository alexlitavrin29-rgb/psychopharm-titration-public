"""One source predicate with separate actions for drug A and drug B; no switch calendar."""
from pathlib import Path
from copy import deepcopy
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
for rid,a in [('switch-ser-ago','RU-SER'),('switch-esc-ago','RU-ESC'),('switch-ser-esc','RU-SER'),('switch-esc-ser','RU-ESC')]:
    p=R/'rules'/f'{rid}.yaml';r=yaml.safe_load(p.read_text(encoding='utf-8'));con=C['rules'][rid]
    b='RU-AGO' if rid.endswith('ago') else ('RU-ESC' if a=='RU-SER' else 'RU-SER')
    i=next((i for i in r['inputs'] if i['input_id']=='mania_symptoms'),None)
    if i is None:
        i=dict(input_id='mania_symptoms',question_ru='Подтверждена текущая маниакальная фаза? Анамнез проверяется отдельно.',data_type='boolean',unit=None,allowed_values=[True,False,'unknown','not_assessed'],unknown_allowed=True,missing_states=['unknown','not_assessed'],changes=['applicability','action'])
        r['inputs'].append(i)
        for c in D['cases']:
            if c['rule_id']==rid:c['given']['mania_symptoms']=False
    loc=a+' §4.4 с.4; '+b+(' §4.4 с.4' if b=='RU-SER' else ' §4.4 с.4' if b=='RU-ESC' else ' §4.4 с.5')
    i.update(source_refs=[a,b],source_locator=loc,required_for_individual_result=True,requirement_predicate={'kind':'always'},required_when='для выбранного результата, текущая фаза',show_when='выбранная ветка',input_role='required_selected_result_operand_or_source_gate',why_needed='Один текущий факт меняет отдельные действия A/B по их ОХЛП.',necessity_reason='Текущая фаза требует прекращения принимаемого A; B не начинать автоматически. Не выводить текущую фазу из анамнеза.',action_if_unknown='insufficient_data; request mania_symptoms; no individual dose',fact_origin='patient_fact')
    if 'mania_symptoms' not in con['required_inputs']:con['required_inputs'].append('mania_symptoms')
    con['input_requirements']['mania_symptoms']={'kind':'always'}
    con['conditional_inputs'].pop('mania_symptoms',None)
    con['urgent_stop_predicates']=[dict(input='mania_symptoms',equals=True,action='source_stop_action',source_ref=a,source_locator=a+' §4.4 с.4',scope='stop currently administered A; no automatic B start'),dict(input='mania_symptoms',equals=True,action='source_stop_action',source_ref=b,source_locator=b+(' §4.4 с.5' if b=='RU-AGO' else ' §4.4 с.4'),scope='B: stop if administered; no automatic start')]
    base=deepcopy(next(c for c in D['cases'] if c['rule_id']==rid and c['branch_id']))
    for state in [True,'unknown','not_assessed']:
        c=deepcopy(base);c['case_id']=rid+'--round2-A-active-mania-'+str(state);c['branch_id']=None;c['given']['mania_symptoms']=state
        c['expected']=dict(result_type='source_stop_action' if state is True else 'insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[] if state is True else ['mania_symptoms'],clinical_clearance=False,automatic_next_stage=False,target_start_allowed=False)
        if state is True:c['external_context']['treatment_phase']='ongoing';c['expected'].update(stop_medication=a,source_condition=con['urgent_stop_predicates'][0])
        D['cases'].append(c)
    r['logic']['urgent_switch_actions']=deepcopy(con['urgent_stop_predicates'])
    p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
print('Current manic phase now has separate A/B source actions in four affected switches.')
