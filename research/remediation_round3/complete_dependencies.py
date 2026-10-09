"""Complete primary constraints omitted by metadata-only migration."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent;R=O.parent
def ry(p):return yaml.safe_load(p.read_text(encoding='utf-8'))
def rj(p):return json.loads(p.read_text(encoding='utf-8'))
def sy(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def sj(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
rs={p.stem:ry(p) for p in (O/'rules').glob('*.yaml')};C=ry(O/'result_contracts.yaml');F=rj(O/'full_scenarios.json');D=rj(O/'necessity_decisions.json')
for rid,r in rs.items():
    con=C['rules'][rid]
    for i in r['inputs']:
        k=i['input_id'];kind=i['requirement_predicate']['kind'];sid=i['source_refs'][0]
        if kind=='ongoing_selected_drug':
            for p in con.get('typed_source_conditions',[])+con.get('urgent_stop_predicates',[]):
                if p.get('input')==k:p['treatment_phase']='ongoing'
        if k in {'serotonin_syndrome_signs','current_allergic_reaction','unusual_reactions'} and ((rid=='fluvox-depression-start' and k=='serotonin_syndrome_signs') or k in {'current_allergic_reaction','unusual_reactions'}):
            action=dict(input=k,operator='equals',value=True,action='source_stop_action',source_ref=sid,source_locator=i['source_locator'],stop_medication=sid,treatment_phase='ongoing' if kind=='ongoing_selected_drug' else 'current_cessation')
            if not any(p.get('input')==k for p in con.get('urgent_stop_predicates',[])):con.setdefault('urgent_stop_predicates',[]).append(action)
            if k=='serotonin_syndrome_signs':action['additional_action']='start_symptomatic_treatment_by_clinician'
        if k in {'misuse_risk_assessment','effective_contraception'}:
            value='требуется отдельное решение врача' if k=='misuse_risk_assessment' else False
            con.setdefault('typed_source_conditions',[]).append(dict(input=k,operator='equals',value=value,action='clinician_choice_no_standard_dose',source_ref=sid,source_locator=i['source_locator'],requirement_predicate=i['requirement_predicate']))
    if rid=='dulox-taper-limit':
        r['clinical_parameters'].append(dict(parameter_id='source_minimum_weeks_4_4',meaning='minimum gradual reduction recommendation in §4.4; not a complete taper',value=2,lower=None,upper=None,lower_inclusive=None,upper_inclusive=None,unit='week',source_ref='RU-DULOX',source_locator='§4.4 с.6, Отмена лечения',source_meaning='предписание',derivation=None))
        r['logic']['current_taper_texts']=dict(section_4_2='§4.2 с.3: 1–2 недели; более постепенно при выраженных симптомах',section_4_4='§4.4 с.6: не менее 2 недель в соответствии с потребностями пациента',resolution='Обычная ветка не разрешает план менее 2 недель; точный темп и календарь не заданы, верхней границы нет.')
        def fix(x):
            if isinstance(x,list):
                for z in x:fix(z)
            elif isinstance(x,dict):
                if x.get('source_ref')=='RU-DULOX' and 'hard_upper_limit_weeks' in x:
                    x.update(operator='minimum',chosen_minimum_weeks=2,hard_upper_limit_weeks=None,source_locator='§4.2 с.3; §4.4 с.6',note='§4.2 указывает 1–2 недели, §4.4 отдельно рекомендует не менее 2 недель. Обычный план менее 2 недель не подтверждён. Точный срок/ступени не задаются.')
                for z in x.values():fix(z)
        fix(r);fix(con)
        for c in F['cases']:
            if c['rule_id']==rid:fix(c['expected'])
    r['output']['branches']=deepcopy(con['branches'])
    sy(O/'rules'/ (rid+'.yaml'),r)
est=ry(R/'renal_estimator.yaml')
est['source_locator']='§4.2 с.3 текущей ОХЛП; формула, таблица1 и сноска'
for p in est['parameters']:p['source_locator']='§4.2 с.3'
est['source_version']=rj(O/'sources.json')['RU-PREG-RICHTER']['version_or_update_date'];sy(O/'renal_estimator.yaml',est)
sy(O/'result_contracts.yaml',C);sj(O/'full_scenarios.json',F)
print('New acute conditions and narrow pregabalin pretreatment gates bound to contracts; current duloxetine taper minimum and Richter locator synchronized.')
