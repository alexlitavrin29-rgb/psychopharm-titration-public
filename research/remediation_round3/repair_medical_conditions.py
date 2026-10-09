"""Source-reviewed condition/action corrections; prepared fixtures, no dose evaluator."""
from pathlib import Path
from copy import deepcopy
import json, yaml

O = Path(__file__).resolve().parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8')) if p.suffix == '.json' else yaml.safe_load(p.read_text(encoding='utf-8'))
def save(p, data):
    text = json.dumps(data, ensure_ascii=False, indent=2) if p.suffix == '.json' else yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110)
    p.write_text(text, encoding='utf-8')
rs = {p.stem: read(p) for p in (O / 'rules').glob('*.yaml')}
C, F, D = [read(O / name) for name in ['result_contracts.yaml', 'full_scenarios.json', 'necessity_decisions.json']]
repairs, specs, defaults = [], [], {}

def condition(rid, key, sid, loc, question, positive=True, default=False, datatype='boolean', values=None, operator='equals', action='source_stop_action', extras=None, target=False):
    r, con = rs[rid], C['rules'][rid]
    pred = dict(kind='ongoing_selected_drug') if r['identity']['mode'] == 'start' else dict(kind='always')
    if key == 'bipolar_risk_screening':
        pred = dict(kind='always')
    if target:
        pred = dict(kind='target_ongoing')
    i = next((x for x in r['inputs'] if x['input_id'] == key), None)
    reason = ('§4.4 требует отдельного предлечебного скрининга рискаБАР. Принимается узкое заключение врача по этому условию; оно не подтверждает другие ограничения и не заменяет диагноз.' if key == 'bipolar_risk_screening' else 'Текущее источниковое условие меняет действие при приёме препарата; отмена/переключение не отменяют его. При положительном ответе обычный календарь не исполняется; экстренный числовой темп не придуман.')
    if i is None:
        i = dict(input_id=key, question_ru=question, data_type=datatype, unit='mmHg' if key == 'diastolic_BP' else None, allowed_values=values or [], source_refs=[sid], source_locator=loc, unknown_allowed=True, changes=['source_action_or_applicability'], fact_origin='explicit physician fact for this calculation')
        r['inputs'].append(i)
        defaults.setdefault(rid, {})[key] = default
        D['decisions'].append(dict(rule_id=rid, input_id=key, old=None, new=pred, reason=reason, source_refs=[sid], locator=loc))
    i.update(question_ru=question, source_locator=loc, requirement_predicate=pred, required_for_individual_result=pred['kind']=='always', input_role='required_selected_result_operand_or_source_gate' if pred['kind']=='always' else pred['kind'], required_when=reason, show_when=reason, why_needed=reason, necessity_reason=reason, action_if_unknown='insufficient_data when the exact phase/result predicate applies; otherwise explicit not_assessed, no clinical clearance')
    p = dict(input=key, operator=operator, value=positive, action=action, source_ref=sid, source_locator=loc, requirement_predicate=pred)
    if pred['kind'] == 'ongoing_selected_drug':
        p['treatment_phase'] = 'ongoing'
    if target:
        p.update(target_treatment_phase='ongoing', medication_role='B', scope='Only stop explicitly ongoing target B; never infer B phase from A')
    dest = 'urgent_stop_predicates' if action == 'source_stop_action' else 'typed_source_conditions'
    old = next((x for x in con.get(dest, []) if x.get('input')==key and x.get('source_ref')==sid), None)
    if old is None:
        con.setdefault(dest, []).append(p)
    else:
        old.update(p)
    specs.append(dict(rule_id=rid, input_id=key, source_ref=sid, locator=loc, positive=positive, default=default, datatype=datatype, operator=operator, action=action, extras=extras or [], target=target))
    repairs.append(dict(rule_id=rid, input_id=key, source_ref=sid, locator=loc, repaired='typed source predicate and full positive/negative/unknown prepared fixtures'))

serotonin = 'Во время текущей терапии подтверждены признаки серотонинового синдрома или состояния, подобного ЗНС?'
for rid in ['parox-panic-kr', 'parox-taper-example', 'switch-parox-ago', 'switch-parox-ago-selected-example']:
    condition(rid, 'serotonin_syndrome_signs', 'RU-PAROX', '§4.4 с.7', serotonin, extras=['start_supportive_symptomatic_treatment_by_clinician'])
condition('parox-panic-kr', 'bipolar_risk_screening', 'RU-PAROX', '§4.4 с.7–8', 'Выполнен тщательный скрининг рискаБАР по §4.4, и врач допускает выбранный режим пароксетина?', positive='требуется отдельное решение врача', default='врач допускает выбранный режим', datatype='enum', values=['врач допускает выбранный режим', 'требуется отдельное решение врача'], action='clinician_choice')

condition('parox-taper-example', 'new_seizures', 'RU-PAROX', '§4.4 с.9', 'При терапии пароксетином возникли судорожные припадки?')
for rid in ['fluvox-taper-limit']:
    condition(rid, 'serotonin_syndrome_signs', 'RU-FLUVOX', '§4.4 с.5', serotonin, extras=['start_symptomatic_treatment_by_clinician'])
    condition(rid, 'new_or_increased_seizures', 'RU-FLUVOX', '§4.4 с.5', 'На терапии Феварином возникли эпилептические приступы или увеличилась их частота?')
    condition(rid, 'liver_injury_signs', 'RU-FLUVOX', '§4.4 с.5', 'На терапии Феварином повысилась активность печёночных ферментов с соответствующими клиническими симптомами?')
    condition(rid, 'mania_symptoms', 'RU-FLUVOX', '§4.4 с.7', 'На терапии Феварином развилась маниакальная фаза?')
for rid in ['venla-xr-gad-start', 'venla-xr-social-start', 'venla-xr-panic-form-limit', 'venla-xr-taper-limit']:
    condition(rid, 'diastolic_BP', 'RU-VENLA-XR', '§4.4 с.9', 'Текущее диастолическое АД при приёме ВелаксинаXR, мм рт.ст.?', positive=100, default=80, datatype='number', operator='greater_than')
    if rid.endswith('taper-limit'):
        condition(rid, 'current_allergic_reaction', 'RU-VENLA-XR', '§4.4 с.13', 'На терапии ВелаксиномXR появилась сыпь, крапивница или другая аллергическая реакция?')
for key, loc, extras in [('arrhythmia_signs', '§4.4 с.6', ['obtain_ECG']), ('serotonin_syndrome_signs', '§4.4 с.5–6', ['start_symptomatic_treatment_by_clinician'])]:
    question = 'При текущем приёме эсциталопрама появились признаки аритмии?' if key=='arrhythmia_signs' else serotonin
    condition('switch-esc-ago', key, 'RU-ESC', loc, question, extras=extras)
condition('switch-esc-ago', 'seizure_state', 'RU-ESC', '§4.4 с.4', 'Подтверждённое состояние судорог при текущем приёме эсциталопрама?', positive='первичные/участившиеся приступы', default='нет', datatype='enum', values=['нет', 'контролируемые', 'неконтролируемые', 'первичные/участившиеся приступы'])
for rid,target in [('switch-esc-ser',False),('switch-ser-esc',True)]:
    prefix='target_' if target else ''
    condition(rid,prefix+'arrhythmia_signs','RU-ESC','§4.4 с.6','Во время приёма эсциталопрама появились признаки аритмии?',extras=['obtain_ECG'],target=target)
    condition(rid,prefix+'serotonin_syndrome_signs','RU-ESC','§4.4 с.5–6',serotonin,extras=['start_symptomatic_treatment_by_clinician'],target=target)
    condition(rid,prefix+'seizure_state','RU-ESC','§4.4 с.4','Подтверждённое состояние судорог во время приёма эсциталопрама?',positive='первичные/участившиеся приступы',default='нет',datatype='enum',values=['нет','контролируемые','неконтролируемые','первичные/участившиеся приступы'],target=target)
condition('fluvox-depression-start','new_or_increased_seizures','RU-FLUVOX','§4.4 с.5','На текущей терапии Феварином возникли эпилептические приступы или увеличилась их частота?')
condition('switch-ser-esc','new_seizures','RU-SER','§4.4 с.4','При текущем приёме сертралина возникли судорожные приступы?')
condition('switch-esc-ser','target_new_seizures','RU-SER','§4.4 с.4','При уже начатом приёме целевого сертралина возникли судорожные приступы?',target=True)
schema=read(O/'input_contracts.yaml')
schema['requirement_predicates']['target_ongoing']='Required for explicit target_treatment_phase=ongoing only; never infer B phase from A. Unknown B phase is retained; a target cessation request needs explicit phase data and cannot stop a drug before its first administration.'
save(O/'input_contracts.yaml',schema)

# Explicit interaction classes use the already declared medicines input, not new patient fields.
for rid, con in C['rules'].items():
    for gate in con.get('source_gates', []):
        sid = gate['source_ref']
        if sid == 'RU-SER':
            gate['current_medicines_avoid_standard_combination'] = ['strong_CYP3A4']
            gate.setdefault('interaction_class_locators', {})['strong_CYP3A4'] = '§4.5 с.10'
            repairs.append(dict(rule_id=rid, source_ref=sid, locator='§4.5 с.10', repaired='strong CYP3A4 inhibitors: avoid, distinguished from formal contraindication'))
        if sid == 'RU-DULOX':
            for name, loc in [('CNS_depressant', '§4.5 с.8'), ('CYP1A2_inhibitor', '§4.5 с.7–8'), ('CYP2D6_substrate', '§4.5 с.8'), ('hepatotoxic', '§4.4 с.7')]:
                if name not in gate['current_medicines_caution']:
                    gate['current_medicines_caution'].append(name)
                gate.setdefault('interaction_class_locators', {})[name] = loc
            repairs.append(dict(rule_id=rid, source_ref=sid, locator='§4.4 с.7; §4.5 с.7–8', repaired='CNS, CYP1A2 inhibitor, CYP2D6 substrate and hepatotoxic caution classes; no invented reduction coefficient'))
        if not any(i['input_id']=='medicines' for i in rs[rid]['inputs']):
            gate['interaction_scope']='Source interaction information only for this limited qualitative result; no patient-specific interaction clearance or dose is granted without a separate medicines contract.'

# Narrow current-page repairs, with the owner fixed separately by repair_source_bindings.py.
def locators(x):
    if isinstance(x, list):
        for n,v in enumerate(x):
            if isinstance(v,str):
                x[n]=v.replace('RU-PAROX §4.2 с.16–17','RU-PAROX §4.2 с.3–4').replace('RU-PAROX §4.2 с. 16–17','RU-PAROX §4.2 с.3–4')
            else:
                locators(v)
    elif isinstance(x, dict):
        if x.get('source_ref')=='RU-PAROX' and x.get('input')=='seizure_state' and x.get('value')=='новые приступы':
            x['source_locator']='§4.4 с.9'
        if x.get('source_ref')=='RU-PANIC' and x.get('input')=='hepatic' and x.get('value')=='hepatic_impairment':
            x.update(source_ref='RU-PAROX',source_locator='§4.2 с.4')
        for k, v in list(x.items()):
            if isinstance(v, str):
                x[k]=v.replace('RU-PAROX §4.2 с.16–17', 'RU-PAROX §4.2 с.3–4').replace('RU-PAROX §4.2 с. 16–17', 'RU-PAROX §4.2 с.3–4')
            else:
                locators(v)
for r in rs.values():
    locators(r)
locators(C)
locators(F)
for c in F['cases']:
    for k, value in defaults.get(c['rule_id'], {}).items():
        c['given'][k]=deepcopy(value)

newcases=[]
for spec in specs:
    rid, key = spec['rule_id'], spec['input_id']
    base = next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id'])
    for state in ['positive', 'negative', 'omitted', 'unknown']:
        c=deepcopy(base)
        c.update(case_id=rid+'--audit-v2-'+key+'-'+state, branch_id=None)
        if rs[rid]['identity']['mode']=='start' and key!='bipolar_risk_screening':
            c['external_context']['treatment_phase']='ongoing'
        if spec['target']:
            c['external_context']['target_treatment_phase']='ongoing'
        if state=='omitted':
            c['given'].pop(key, None)
        elif state=='unknown':
            c['given'][key]='unknown'
        elif state=='negative':
            c['given'][key]=deepcopy(spec['default'])
        else:
            c['given'][key]=100.01 if spec['operator']=='greater_than' else spec['positive']
        e=c['expected']
        if state in {'omitted', 'unknown', 'positive'}:
            e.update(result_type='insufficient_data' if state in {'omitted','unknown'} else spec['action'], total_daily_dose_mg=None, dose_per_administration_mg=None, administrations_per_day=None, schedule=[], missing_fields=[key] if state in {'omitted','unknown'} else [], clinical_clearance=False)
            if state=='positive':
                e['source_condition']=dict(input=key, source_ref=spec['source_ref'], source_locator=spec['locator'])
                if spec['action']=='source_stop_action':
                    e['stop_medication']=spec['source_ref']
                    actions=['discontinue_selected_medication']+spec['extras']
                    if spec['source_ref']=='RU-ESC' and key.endswith('serotonin_syndrome_signs'):
                        actions=['immediately_discontinue_SSRI_and_current_serotonergic_drugs']+spec['extras']
                    e['source_actions']=[dict(action=a, source_ref=spec['source_ref'], source_locator=spec['locator']) for a in actions]
                    if rs[rid]['identity']['mode']=='switch':
                        e['no_automatic_target_start']=True
        if spec['operator']=='greater_than' and state=='negative':
            c['given'][key]=100
        newcases.append(c)
    if spec['target']:
        for phase in ['not_started','unknown']:
            c=deepcopy(base)
            c.update(case_id=rid+'--audit-v2-'+key+'-target-phase-'+phase,branch_id=None)
            c['external_context']['target_treatment_phase']=phase
            c['given'][key]=spec['positive']
            c['expected'].update(result_type='clinician_choice' if phase=='not_started' else 'insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[] if phase=='not_started' else ['external_context.target_treatment_phase'],clinical_clearance=False,no_automatic_target_start=True)
            c['expected'].pop('stop_medication',None)
            c['expected'].pop('source_actions',None)
            newcases.append(c)

# Directly specified representatives, plus unmapped class fixtures, expose generic class gaps.
for rid, con in C['rules'].items():
    if not any(i['input_id']=='medicines' for i in rs[rid]['inputs']):
        continue
    for gate in con.get('source_gates', []):
        classes = gate.get('current_medicines_avoid_standard_combination', [])
        if gate['source_ref']=='RU-DULOX':
            classes+=['CNS_depressant','CYP1A2_inhibitor','CYP2D6_substrate','hepatotoxic']
        for cls in classes:
            base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id'])
            c=deepcopy(base)
            c.update(case_id=rid+'--audit-v2-interaction-'+cls, branch_id=None)
            representative={'strong_CYP3A4':'кетоконазол','CNS_depressant':'фенобарбитал','CYP2D6_substrate':'флекаинид'}.get(cls)
            c['fixture_scope']='Source-class predicate specification; a generic class fixture is not an executed INN classifier or a patient medication record'
            c['given']['medicines']=[dict(record_id='audit_class', inn=representative or 'synthetic_class_fixture:'+cls, status='current', interaction_class=cls, classification_basis=dict(source_ref=gate['source_ref'], source_locator=gate['interaction_class_locators'][cls]))]
            c['expected'].update(result_type='clinician_choice', total_daily_dose_mg=None, dose_per_administration_mg=None, administrations_per_day=None, schedule=[], missing_fields=[], clinical_clearance=False)
            c['expected']['source_condition']=dict(input='medicines', interaction_class=cls, source_ref=gate['source_ref'], source_locator=gate['interaction_class_locators'][cls], action='avoid_standard_combination' if cls=='strong_CYP3A4' else 'source_caution_without_invented_coefficient')
            newcases.append(c)
F['cases']=[c for c in F['cases'] if '--audit-v2-' not in c['case_id']] + newcases
for c in F['cases']:
    g, e = c['given'], c['expected']
    e['confirmed_negatives']=[k for k,v in g.items() if v is False]
    if c['rule_id'].startswith('venla-xr-') and isinstance(g.get('diastolic_BP'), (int,float)) and g['diastolic_BP']>100 and e['result_type']=='source_stop_action':
        e.update(stop_medication='RU-VENLA-XR', source_condition=dict(input='diastolic_BP', source_ref='RU-VENLA-XR', source_locator='§4.4 с.9'))
        e['source_actions']=[dict(action='discontinue_selected_medication', source_ref='RU-VENLA-XR', source_locator='§4.4 с.9')]
for rid, r in rs.items():
    con=C['rules'][rid]
    con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['required_for_individual_result']]
    con['input_requirements']={i['input_id']:i['requirement_predicate'] for i in r['inputs']}
    r['output']['branches']=deepcopy(con['branches'])
    save(O/'rules'/(rid+'.yaml'),r)
save(O/'result_contracts.yaml',C)
save(O/'full_scenarios.json',F)
save(O/'necessity_decisions.json',D)
save(O/'medical_condition_repairs.json',repairs)
print('Source corrections:', len(repairs), '; new prepared fixtures:',len(newcases), '; total:',len(F['cases']), '; no calculator executed.')
