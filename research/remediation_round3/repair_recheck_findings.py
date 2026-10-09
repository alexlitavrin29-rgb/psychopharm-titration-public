"""Apply the independently identified source-event and locator recheck corrections."""
from pathlib import Path
from copy import deepcopy
import json, yaml

O=Path(__file__).resolve().parent
assert not (O/'recheck_repairs.json').exists(), 'One-use correction; do not replay over a reviewed snapshot'
def read(p):
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.suffix=='.yaml' else json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
    p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110) if p.suffix=='.yaml' else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
S=read(O/'sources.json');C=read(O/'result_contracts.yaml');F=read(O/'full_scenarios.json');D=read(O/'necessity_decisions.json')
rs={p.stem:read(p) for p in (O/'rules').glob('*.yaml')};changes=[];specs=[]

# Physical pages in the exact 26-page current PAROX SmPC, not the old PIL+SmPC bundle.
locs={
 'age':'§4.1 с.1–2; §4.2 с.4; §4.3 с.5', 'form':'§3 с.1; §4.2 с.4', 'from_form':'§3 с.1; §4.2 с.4',
 'hepatic':'§4.2 с.4', 'from_hepatic':'§4.2 с.4', 'renal':'§4.2 с.4', 'from_renal':'§4.2 с.4',
 'pregnancy':'§4.6 с.14–15', 'lactation':'§4.6 с.15', 'medicines':'§4.3 с.4–5; §4.5 с.11–14', 'allergy':'§4.3 с.4',
 'response':'§4.2 с.3', 'tolerability':'§4.2 с.3', 'current_dose':'§4.2 с.3–4', 'time_at_dose':'§4.2 с.3',
 'from_taper_plan':'§4.2 с.3–4; §4.4 с.9–10', 'maoi_type':'§4.3 с.4–5; §4.5 с.11', 'maoi_stopped_at':'§4.3 с.4–5; §4.5 с.11',
 'elderly_population':'§4.2 с.4', 'mania':'§4.4 с.7–8', 'suicide_risk':'§4.4 с.5–7', 'akathisia':'§4.4 с.7',
 'diabetes':'§4.4 с.8', 'glaucoma':'§4.4 с.9', 'bleeding_risk':'§4.4 с.9', 'qt_risk':'§4.4 с.9', 'ect':'§4.4 с.9',
 'seizure_state':'§4.4 с.8–9', 'serotonin_syndrome_signs':'§4.4 с.7', 'bipolar_risk_screening':'§4.4 с.7–8',
 'duration':'§4.4 с.9–10', 'past_withdrawal':'§4.4 с.9–10', 'withdrawal_severity':'§4.2 с.3–4; §4.4 с.9–10',
 'example_selected':'§4.2 с.3–4'}
questions={'mania':'Есть мания в анамнезе?', 'suicide_risk':'Врач выявил суицидальный риск или клиническое ухудшение?', 'akathisia':'Есть акатизия?', 'diabetes':'Есть сахарный диабет?', 'glaucoma':'Есть закрытоугольная глаукома?', 'bleeding_risk':'Есть известная склонность к кровотечениям?', 'qt_risk':'Есть известный риск удлинения QT?', 'ect':'Проводится ЭСТ?', 'seizure_state':'Каково подтверждённое состояние эпилепсии/приступов, включая возникшие при приёме пароксетина?', 'from_hepatic':'Какова подтверждённая функция печени для исходного пароксетина?'}
old_pages={'§4.3 с.17–18':'§4.3 с.4–5','§4.3 с.17':'§4.3 с.4','§4.2 с.16':'§4.2 с.3','§4.2 с.17':'§4.2 с.4','§4.4 с.18–20':'§4.4 с.5–7','§4.4 с.20':'§4.4 с.7–8','§4.4 с.21':'§4.4 с.8–9','§4.4 с.22':'§4.4 с.9'}
for rid,r in rs.items():
    for i in r['inputs']:
        if 'RU-PAROX' not in i['source_refs'] or i['input_id'] not in locs:
            continue
        k=i['input_id'];old=i['source_locator'];i['source_locator']='RU-PAROX '+locs[k]
        i['source_refs']=[s for s in i['source_refs'] if s not in {'RU-PANIC','RU-DEP'}]
        if 'RU-AGO' in i['source_refs']:
            i['source_locator']+='; RU-AGO '+dict(age='§4.2 с.2',medicines='§4.3 с.3; §4.5 с.5–6',allergy='§4.3 с.3',pregnancy='§4.6 с.6',lactation='§4.6 с.6').get(k,S['RU-AGO']['exact_locator'])
        if k in {'duration','past_withdrawal'}:
            if 'RU-DEP' not in i['source_refs']:
                i['source_refs'].append('RU-DEP')
            i['source_locator']+='; RU-DEP Б5 с.105–106, риск синдрома отмены'
        for field in ['question_ru','why_needed','necessity_reason','required_when','show_when']:
            for a,b in old_pages.items():
                i[field]=i[field].replace(a,b)
        if k in questions:
            i['question_ru']=questions[k]
        changes.append(dict(rule_id=rid,input_id=k,old_locator=old,new_locator=i['source_locator'],repair='input/question/necessity current physical locator'))
        for x in D['decisions']:
            if x.get('rule_id')==rid and x.get('input_id')==k:
                x['locator']=i['source_locator']
                x['source_refs']=i['source_refs'][:]
                if 'reason' in x:
                    for a,b in old_pages.items():x['reason']=x['reason'].replace(a,b)

# Current DULOX questions must follow the current physical source, including the
# diabetes context (adverse reactions, not an invented dose modifier in §4.4).
dulox_questions={'mania':'Есть маниакальные эпизоды или биполярное расстройство в анамнезе?', 'suicide_risk':'Врач выявил суицидальный риск или клиническое ухудшение?', 'bleeding_risk':'Есть известная склонность к кровотечениям?', 'hyponatremia_risk':'Есть известные факторы риска гипонатриемии?', 'diabetes':'Есть сахарный диабет, если врач сообщает этот контекст?', 'seizure_state':'Есть судороги в анамнезе?'}
for rid,r in rs.items():
    for i in r['inputs']:
        if 'RU-DULOX' not in i['source_refs'] or i['input_id'] not in dulox_questions:continue
        k=i['input_id'];i['question_ru']=dulox_questions[k]
        if k=='diabetes':
            i['source_locator']='§4.8 с.11, гипергликемия; с.14, данные исследований диабетической нейропатии'
            i['why_needed']=i['necessity_reason']='Сообщённый контекст нежелательных реакций: гипергликемия отмечалась особенно у пациентов с диабетом (§4.8 с.11); данные с.14 относятся к диабетической нейропатии. Источник не задаёт коэффициент или обязательное изменение психиатрической дозы.'
            i['changes']=['source_adverse_reaction_context']
        else:i['why_needed']='Источниковое предупреждение по RU-DULOX '+i['source_locator']+'; контекст не является автоматическим коэффициентом дозы.'
        changes.append(dict(rule_id=rid,input_id=k,repair='DULOX plain question/current physical locator',new_locator=i['source_locator']))
        for x in D['decisions']:
            if x.get('rule_id')==rid and x.get('input_id')==k:
                x.update(locator=i['source_locator'],source_refs=i['source_refs'][:],reason=i['necessity_reason'])
    if rid.startswith('dulox-'):
        for gate in C['rules'][rid]['source_gates']:
            if gate['source_ref']=='RU-DULOX':gate.setdefault('context_field_locators',{})['diabetes']='§4.8 с.11,14; adverse reaction context, no psychiatric dose coefficient'

for rid in ['preg-taper-limit','phen-taper-limit']:
    for b in C['rules'][rid]['branches']:
        e=b['expected_output']
        if 'prior_dose_resumption' in e:
            e['prior_dose_resumption']=None
            e['prior_dose_resumption_source_gap']='Selected product source does not provide a universal prior-dose resumption rule; separate physician decision, no automatic resumption dose.'
    for c in F['cases']:
        if c['rule_id']==rid and 'prior_dose_resumption' in c['expected']:
            c['expected']['prior_dose_resumption']=None
            c['expected']['prior_dose_resumption_source_gap']='Selected product source does not provide a universal prior-dose resumption rule; separate physician decision, no automatic resumption dose.'
for rid,r in rs.items():
    if rid.startswith('venla-xr-'):
        for i in r['inputs']:
            if i['input_id']=='pregnancy':i['question_ru']='Беременность подтверждена?'
            if i['input_id']=='pregnancy_suspected':i['question_ru']='Есть подозрение на беременность без её подтверждения?'
    for c in F['cases']:
        if c['rule_id']==rid and c['given'].get('severe_skin_reaction') is True and c['expected'].get('stop_medication')=='RU-PREG':
            c['expected']['source_actions']=[dict(action='immediately_discontinue_pregabalin',source_ref='RU-PREG',source_locator='§4.4 с.6'),dict(action='consider_alternative_treatment_if_needed',source_ref='RU-PREG',source_locator='§4.4 с.6',condition='if needed; physician selects alternative; no automatic drug or dose')]

definitions=[
 ('RU-SER','symptomatic_hyponatremia','§4.4 с.6','Врач подтвердил симптоматическую гипонатриемию при текущем приёме сертралина?', ['consider_discontinuation_of_sertraline','provide_appropriate_medical_care']),
 ('RU-PREG','current_suicidal_thoughts_or_behavior','§4.4 с.8','На текущей терапии прегабалином возникли суицидальные мысли или поведение?', ['consider_discontinuation_of_pregabalin','consider_appropriate_treatment_and_seek_medical_care']),
 ('RU-DULOX','persistent_BP_increase','§4.4 с.4','Врач установил стойкое повышение АД на фоне текущего приёма дулоксетина?', ['consider_dose_adjustment_or_gradual_discontinuation']),
 ('RU-VENLA-XR','suspected_serotonin_syndrome','§4.4 с.8','При текущем приёме Велаксина XR врач подозревает серотониновый синдром?', ['consider_dose_reduction_or_discontinuation_according_to_symptom_severity'])]
for sid,key,loc,question,actions in definitions:
    for rid,r in rs.items():
        if sid not in {s['source_id'] for s in r['sources']}:
            continue
        if sid=='RU-SER' and rid=='switch-esc-ser':target=True
        else:target=False
        if sid=='RU-SER' and rid not in {'ser-panic-start','ser-social-start','ser-adult-adjust','ser-taper-limit','switch-ser-ago','switch-ser-esc','switch-esc-ser'}:continue
        k=('target_' if target else '')+key;con=C['rules'][rid];pred=dict(kind='reported_current_event')
        reason='Обрабатывает отдельно сообщённое текущее источниковое событие при явном приёме соответствующего препарата. Не универсальный обязательный скрининг и не отрицание события при отсутствии/unknown. Положительный известный факт останавливает автоматический календарь и сохраняет опубликованный выбор врача; числовое снижение/немедленная отмена не придуманы.'
        i=dict(input_id=k,question_ru=question,data_type='boolean',unit=None,allowed_values=[],source_refs=[sid],source_locator=loc,unknown_allowed=True,changes=['source_clinician_action'],requirement_predicate=pred,required_for_individual_result=False,input_role='reported_current_event',required_when='Not an unconditional required absence check; source event handling when explicitly reported',show_when='Если врач отдельно сообщает это текущее событие; фаза принимаемого A/B известна отдельно',why_needed=reason,necessity_reason=reason,action_if_unknown='Explicit not_assessed; no clinical clearance. A reported unknown current event needs clinician assessment, not a confirmed negative or automatic calendar.',fact_origin='explicitly supplied current physician event, not hidden pre-screening')
        r['inputs']=[x for x in r['inputs'] if x['input_id']!=k]+[i]
        con.setdefault('typed_source_conditions',[]).append(dict(input=k,operator='equals',value=True,action='clinician_choice',source_ref=sid,source_locator=loc,requirement_predicate=pred,source_phase='target_ongoing' if target else 'ongoing',medication_role='B' if target else 'selected_or_A',source_actions=actions))
        D['decisions'].append(dict(rule_id=rid,input_id=k,old=None,new=pred,reason=reason,source_refs=[sid],locator=loc))
        specs.append(dict(rule_id=rid,input_id=k,source_ref=sid,locator=loc,actions=actions,target=target))
        changes.append(dict(rule_id=rid,input_id=k,repair='known ongoing event, source physician choice, no universal new questionnaire'))

for rid in ['switch-ser-esc','switch-esc-ser']:
    con=C['rules'][rid]
    gate=deepcopy(C['rules']['ser-panic-start']['source_gates'][0])
    gate.update(exclusions=[],cautions=[],stop=[],medication_role='A' if rid=='switch-ser-esc' else 'B',scope='SER-specific medicine applicability/avoidance. A cessation and B not_started/ongoing are distinct; no complete pair calendar is supplied.')
    con['source_gates'].append(gate)
for rid,con in C['rules'].items():
    for gate in con['source_gates']:
        if gate['source_ref']=='RU-VENLA-XR':
            gate['current_medicines_caution']=sorted(set(gate.get('current_medicines_caution',[]))|{'CYP2D6_inhibitor','CYP3A4_inhibitor','CNS_active','metoprolol'})
            gate['current_medicines_avoid_standard_combination']=['QT_prolonging','serotonin_precursor','weight_loss_agent']
            gate.setdefault('interaction_class_locators',{}).update(CYP2D6_inhibitor='§4.5 с.16',CYP3A4_inhibitor='§4.5 с.16',QT_prolonging='§4.5 с.15–16',CNS_active='§4.5 с.15',metoprolol='§4.5 с.17',serotonin_precursor='§4.4 с.8; §4.5 с.15',weight_loss_agent='§4.4 с.10')
            changes.append(dict(rule_id=rid,repair='XR CYP inhibitors caution and explicit QT avoidance, no invented dose coefficient'))
        if gate['source_ref']=='RU-DULOX':
            gate['current_medicines_avoid_standard_combination']=['duplicate_duloxetine_product']
            gate.setdefault('interaction_class_locators',{})['duplicate_duloxetine_product']='§4.4 с.7'
            gate['duplicate_product_requirement']='An additional current duloxetine product is explicitly confirmed; do not infer duplication from one current record of the selected product itself.'
for rid in ['ser-taper-limit','esc-taper-limit','preg-taper-limit','dulox-taper-limit','fluvox-taper-limit','venla-xr-taper-limit','phen-taper-limit']:
    r=rs[rid];i=next((i for i in r['inputs'] if i['input_id']=='medicines'),None)
    if i is None:
        sid=next(g['source_ref'] for g in C['rules'][rid]['source_gates'])
        i=dict(input_id='medicines',question_ru='Сопутствующие препараты, если врач сообщает их для отдельного источникового предупреждения?',data_type='medication_list',unit=None,allowed_values=[],source_refs=[sid],source_locator=S[sid]['exact_locator'],unknown_allowed=True,changes=['source_interaction_warning'],fact_origin='explicitly supplied current medicines; no hidden questionnaire')
        r['inputs'].append(i)
    i.update(requirement_predicate=dict(kind='reported_source_information'),input_role='reported_source_information',required_for_individual_result=False,required_when='Optional explicitly supplied medicines; not a routine prerequisite to the qualitative cessation limit',show_when='Если врач сообщает сопутствующие лекарства для источникового предупреждения',necessity_reason='Известное избегаемое сочетание сохраняется с источником; unknown/непредоставленный список не нормализуется. Это предупреждение при выбранной отмене, не клинический допуск и не запрет прекращения.',why_needed='Source warning for explicitly supplied current medicines; no new initiation clearance',action_if_unknown='Explicit unassessed interaction context; qualitative cessation limit remains source-bound, no numerical plan')
    D['decisions']=[x for x in D['decisions'] if not (x.get('rule_id')==rid and x.get('input_id')=='medicines' and 'new' in x)]
    D['decisions'].append(dict(rule_id=rid,input_id='medicines',old='outside_cessation_scope or no input',new=i['requirement_predicate'],reason=i['necessity_reason'],source_refs=i['source_refs'],locator=i['source_locator']))

newcases=[]
for spec in specs:
    rid,k=spec['rule_id'],spec['input_id'];base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id'])
    for state in ['positive','negative','unknown','omitted']:
        c=deepcopy(base);c.update(case_id=rid+'--audit-recheck-'+k+'-'+state,branch_id=None)
        if rs[rid]['identity']['mode']=='start':c['external_context']['treatment_phase']='ongoing'
        if spec['target']:c['external_context']['target_treatment_phase']='ongoing'
        if state!='omitted':c['given'][k]=True if state=='positive' else False if state=='negative' else 'unknown'
        e=c['expected'];e['clinical_clearance']=False
        if state in {'positive','unknown'}:
            e.update(result_type='clinician_choice',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],no_automatic_medication_change=True)
            e['source_condition']=dict(input=k,source_ref=spec['source_ref'],source_locator=spec['locator'],state=state)
            e['source_actions']=[dict(action=a,source_ref=spec['source_ref'],source_locator=spec['locator'],medication_role='B' if spec['target'] else 'selected_or_A') for a in spec['actions']] if state=='positive' else []
            if rs[rid]['identity']['mode']=='switch':e['no_automatic_target_start']=True
        newcases.append(c)
    if spec['target'] or rs[rid]['identity']['mode']=='start':
        for phase in ['not_started','unknown']:
            c=deepcopy(base);c.update(case_id=rid+'--audit-recheck-'+k+'-phase-'+phase,branch_id=None);c['given'][k]=True
            phasekey='target_treatment_phase' if spec['target'] else 'treatment_phase';c['external_context'][phasekey]=phase
            c['expected'].update(result_type='clinician_choice' if phase=='not_started' else 'insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[] if phase=='not_started' else ['external_context.'+phasekey],clinical_clearance=False,source_actions=[],no_automatic_medication_change=True,no_automatic_target_start=True)
            c['expected'].pop('stop_medication',None);newcases.append(c)

for rid in ['venla-xr-gad-start','venla-xr-social-start','venla-xr-panic-form-limit','venla-xr-taper-limit','switch-ser-esc','switch-esc-ser']:
    sid='RU-VENLA-XR' if rid.startswith('venla') else 'RU-SER'
    for cls,name in ([('CYP2D6_inhibitor','хинидин'),('CYP3A4_inhibitor','кетоконазол'),('QT_prolonging','моксифлоксацин'),('CNS_active','synthetic_class_fixture:CNS_active'),('metoprolol','метопролол'),('serotonin_precursor','L-триптофан'),('weight_loss_agent','фентермин')] if sid=='RU-VENLA-XR' else [('strong_CYP3A4','кетоконазол')]):
        base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']);c=deepcopy(base);c.update(case_id=rid+'--audit-recheck-interaction-'+cls,branch_id=None)
        gate=next(g for g in C['rules'][rid]['source_gates'] if g['source_ref']==sid);loc=gate['interaction_class_locators'][cls]
        c['fixture_scope']='Prepared source-class representative; not execution of an INN classifier'
        c['given']['medicines']=[dict(record_id='recheck_class',inn=name,status='current',interaction_class=cls,classification_basis=dict(source_ref=sid,source_locator=loc))]
        c['expected'].update(result_type='clinician_choice',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],clinical_clearance=False)
        c['expected']['source_condition']=dict(input='medicines',interaction_class=cls,source_ref=sid,source_locator=loc,action='not_recommended_combination' if cls in {'serotonin_precursor','weight_loss_agent'} else 'avoid_standard_combination' if cls in {'strong_CYP3A4','QT_prolonging'} else 'source_caution_without_invented_coefficient')
        if rs[rid]['identity']['mode']=='switch':c['expected']['no_automatic_target_start']=True
        newcases.append(c)
for rid in ['dulox-depression-start','dulox-gad-start','dulox-gad-adjust','dulox-taper-limit']:
    base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id'])
    for state in ['positive','selected_product_only','unknown_additional_product']:
        c=deepcopy(base);c.update(case_id=rid+'--audit-recheck-duplicate-duloxetine-'+state,branch_id=None)
        c['fixture_scope']='Explicit synthetic additional-product reconciliation fact, not a duplicate inferred from INN alone or execution of an INN classifier'
        c['given']['medicines']=[dict(record_id='duloxetine_product',inn='дулоксетин',status='current',interaction_class='duplicate_duloxetine_product' if state!='selected_product_only' else 'selected_medication',additional_product=True if state=='positive' else False if state=='selected_product_only' else 'unknown',classification_basis=dict(source_ref='RU-DULOX',source_locator='§4.4 с.7'))]
        if state=='selected_product_only' and rs[rid]['identity']['mode']=='start':
            c['external_context']['treatment_phase']='ongoing'
        if state!='selected_product_only':
            c['expected'].update(result_type='clinician_choice' if state=='positive' else 'insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[] if state=='positive' else ['medicines.duloxetine_product.additional_product'],clinical_clearance=False)
            c['expected']['source_condition']=dict(input='medicines',interaction_class='duplicate_duloxetine_product',source_ref='RU-DULOX',source_locator='§4.4 с.7',action='avoid_multiple_duloxetine_products' if state=='positive' else 'do_not_infer_duplicate_from_unconfirmed_identity')
        newcases.append(c)
F['cases']=[c for c in F['cases'] if '--audit-recheck-' not in c['case_id']]+newcases
for rid,r in rs.items():
    con=C['rules'][rid];con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['required_for_individual_result']];con['input_requirements']={i['input_id']:i['requirement_predicate'] for i in r['inputs']}
    con['monitoring_context_fields']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_current_event','reported_source_information'}]
    r['output']['branches']=deepcopy(con['branches']);save(O/'rules'/(rid+'.yaml'),r)
for c in F['cases']:
    g,e=c['given'],c['expected'];con=C['rules'][c['rule_id']]
    e['confirmed_negatives']=[k for k,v in g.items() if v is False]
    e['unassessed_context']=sorted({k for k in con.get('monitoring_context_fields',[]) if k not in g or g[k] in (None,'unknown','not_assessed','неизвестно','не исследовано')})
schema=read(O/'input_contracts.yaml')
schema['requirement_predicates'].update(reported_current_event='Optional explicitly supplied current source-defined event: consumed and counted if present; positive action requires explicit ongoing source/target phase; missing/unknown never confirms absence or clinical clearance.',reported_source_information='Optional explicitly supplied information for a source warning; count every consumed fact/record. It is not an unconditional cessation/start prerequisite.')
schema['structures']['medication_list']['entry_fields']['additional_product']='Optional boolean | unknown. Required for an asserted duplicate_duloxetine_product class: an independently supplied confirmation of an additional concurrent product, counted separately. A single selected current product is not a duplicate.'
save(O/'input_contracts.yaml',schema);save(O/'result_contracts.yaml',C);save(O/'full_scenarios.json',F);save(O/'necessity_decisions.json',D);save(O/'recheck_repairs.json',changes)
R=O.parent
replacements={
 '01_scope_and_sources.md':{
  'текущий числовой модуль эсциталопрама блокирован F01':'источниковые стартовые ветки текущей Селектры подтверждены',
  'Для F40.1 здесь извлечены сертралин и источник венлафаксинаXR; эсциталопрам блокирован F01':'Для F40.1 здесь извлечены стартовые ветки сертралина, эсциталопрама и венлафаксина XR',
  'полный текущий оригинал не получен. Январская копия архивная и не заменяет его.':'полный текущий официальный оригинал получен во втором проходе и сохранён со SHA. Январская копия архивная и не заменяет активную редакцию.',
  '| Беременность | RU-SER §4.6; RU-PREG §4.6: решение по пользе/риску; текущий RU-ESC не подтверждён |':'| Беременность | RU-SER §4.6; RU-PREG §4.6: решение по пользе/риску; RU-ESC §4.6 с.10: отдельная оценка необходимости и пользы/риска |',
  'текущий RU-ESC не подтверждён':'текущая RU-ESC доступна; взрослый режим не переносится на детей автоматически',
  'Пожилая ветка текущей Селектры не подтверждена.':'Текущая Селектра: источниковая ветка для возраста старше 65 лет подтверждена (§4.2 с.3).',
  'текущая RU-ESC-классификация не подтверждена':'RU-ESC §4.2 с.3: категории Child–Pugh A/B подтверждены; при C осторожность и тщательная титрация, без придуманного коэффициента',
  'текущий RU-ESC-предикат не подтверждён':'RU-ESC §4.2 с.3: CLcr >30 без изменения, <30 осторожность; ровно30 источник не присваивает категории'},
 '09_download_links.md':{
  '- Полный текущий оригинал Селектры недоступен: token403, загрузка в реестре требует CAPTCHA. Публичная январская копия архивная; числовой модуль блокирован F01.':'- Полный текущий оригинал Селектры получен после CAPTCHA: [официальная копия](remediation_round2/Selectra_current_registry.pdf); SHA и подтверждение редакции — sources.json. Прежний token403 и январская архивная копия сохранены как история доступа.'}}
for name,subs in replacements.items():
    p=R/name;t=p.read_text(encoding='utf-8')
    for a,b in subs.items():t=t.replace(a,b)
    p.write_text(t,encoding='utf-8')
print('Recheck fixes:',len(changes),'; prepared cases:',len(F['cases']),'; current event fixtures:',len(newcases))
