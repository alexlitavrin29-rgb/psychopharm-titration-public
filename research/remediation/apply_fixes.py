"""Apply reviewed research corrections. This is a data migration, not a calculator."""
from pathlib import Path
import csv, json, hashlib, copy
import yaml

R=Path(__file__).resolve().parents[1]
O=R/'remediation'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (R/'rules').glob('*.yaml')}
def dump(p,d): p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def param(r,pid,value,unit,sid,loc,meaning='предписание'):
    p=dict(parameter_id=pid,meaning=pid,value=value,lower=None,upper=None,lower_inclusive=None,
           upper_inclusive=None,unit=unit,source_ref=sid,source_locator=loc,source_meaning=meaning,derivation=None)
    r['clinical_parameters'].append(p)
    return p
def inp(r,key,question,kind,sid,loc,values=None,unit=None,required='individual_result'):
    if any(i['input_id']==key for i in r['inputs']): return
    r['inputs'].append(dict(input_id=key,question_ru=question,data_type=kind,unit=unit,
        allowed_values=values or [],required_when=required,show_when=required,
        why_needed=f'Изменяет применимость/действие: {loc}.',changes=['applicability','action'],
        unknown_allowed=True,action_if_unknown=f'insufficient_data; запросить {key}; числовой выход отсутствует.',
        source_refs=[sid],source_locator=loc,input_role='applicability_gate'))

# Explicitly bind copies to their actual source, without substituting an archive for RU-ESC.
copies=[]
by_hash={s.get('document_fingerprint',{}).get('sha256'):sid for sid,s in S.items()
         if s.get('document_fingerprint',{}).get('sha256')}
for folder in ('source_downloads','source_snapshots','audit/retrieved','remediation/retrieved','../tmp_acceptance'):
    for p in sorted((R/folder).glob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.pdf','.docx','.html'}: continue
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        sid=by_hash.get(sha)
        if not sid and p.stem in S: sid=p.stem
        if not sid: continue  # Miscellaneous discovery HTML is not a medical original.
        rel=p.relative_to(R) if R in p.parents else Path('..')/p.relative_to(R.parent)
        row=dict(source_id=sid,local_file=rel.as_posix(),sha256=sha,version=S[sid]['version_or_update_date'] if sha==S[sid].get('document_fingerprint',{}).get('sha256') else 'byte-different snapshot; medical revision not independently established',
                 url=S[sid]['url'],download_date='2026-10-08',
                 byte_identity_to_primary_snapshot=sha==S[sid].get('document_fingerprint',{}).get('sha256'),
                 latest_registration_revision_confirmed=False)
        copies.append(row)
for sid,s in S.items():
    found=[c for c in copies if c['source_id']==sid]
    matched=[c for c in found if c['byte_identity_to_primary_snapshot']]
    if matched and not s.get('local_file'):
        s['local_file']=matched[0]['local_file']
    s['document_copies']=found
    s['dates']={'registration':s.get('registry_observation',{}).get('registration_date'),
                'revision': '2024-07-18' if sid=='RU-DULOX' else None,
                'publication':s.get('publication_date'),'download':'2026-10-08'}
    s['latest_registration_revision_confirmed']=False
    if s['source_type']=='guideline' and sid.startswith('RU-'):
        s['current_guideline_status_evidence']='audit/current_minzdrav_catalog.json; 2026-10-08; CodeVersion/ApplyStatusCalculated'
S['RU-ESC']['access_status']='unavailable_current_original'
S['RU-ESC']['evidence_limitations']='ОХЛП нужного РУ не сохранена и не воспроизведена. 08.10.2026 официальный поиск подтвердил РУ и формы, скачивание потребовало CAPTCHA. Token-ссылка не дала оригинала. Архив RU-ESC-2025-JAN не заменяет эту версию; F01/F02/F13 открыты.'
S['RU-ESC']['registry_observation']['remediation_observation']='08.10.2026: Селектра, ЛП-№(012351)-(РГ-RU), 05.11.2025, 5/10/15/20 мг; при нажатии Скачать показана CAPTCHA; не решалась.'
S['RU-ESC-2025-JAN']['evidence_limitations']='Архивная инструкция 14.01.2025. Не подтверждает дозовые числа, деление или органные условия новой RU-ESC.'
dump(O/'source_copy_inventory.yaml',{'nature':'Copy provenance, not medical currency','copies':copies})

unknown=['unknown','not_assessed']
boolean_fields={'pregnancy','lactation','allergy','mania','qt_risk','bleeding_risk','hyponatremia_risk',
    'suicide_risk','akathisia','diabetes','glaucoma','dialysis','substance_use','respiratory','example_selected',
    'past_withdrawal','prior_withdrawal','comorbid_depression','elderly_population','uncontrolled_hypertension',
    'closed_angle_glaucoma','dementia','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption',
    'fructose_intolerance','sucrase_isomaltase_deficiency','liver_injury_signs','transaminases_rising',
    'overweight_obesity','fatty_liver','alcohol_abuse','alcohol_use','ect','angioedema','severe_skin_reaction','mania_symptoms'}
schema={
 'schema_version':'2.0','nature':'Research input contract; not executed calculator',
 'missing_states':{'omitted':'missing','null':'missing','unknown':'known to be unknown','not_assessed':'not assessed; never normal'},
 'boolean_aliases':{'да':True,'нет':False,'неизвестно':'unknown','не исследовано':'not_assessed'},
 'action_aliases':{'сохранить':'keep','повысить':'increase','снизить':'decrease','прекратить':'stop','действие не выбрано':'not_chosen'},
 'units':{'week_to_day':{'factor':7,'basis':'calendar unit conversion, not a treatment interval'},
          'CLcr':'mL/min','absolute_GFR':'mL/min','indexed_eGFR':'mL/min/1.73m2','automatic_renal_conversion':False},
 'structures':{
   'structured_form':{'fields':{'product':'string','registration_number':'string','source_id':'string',
       'dosage_form':'enum: tablet | capsule | orodispersible_tablet','strengths_mg':'list[number]',
       'release':'enum: immediate | enteric | prolonged','route':'oral'},
       'splitting':'derived only from the identified source/form; never an unchecked physician checkbox'},
   'medication_list':{'type':'list','entry_fields':{'inn':'string','status':'current | stopped',
       'interaction_class':'source-mapped class | unknown'},'empty_list':'confirmed none; unknown is not []',
       'timestamps':'Separate fields maoi_type/maoi_stopped_at per relevant record; counted separately'},
   'structured_renal':{'fields':{'metric':'CLcr | absolute_GFR | indexed_eGFR','value':'number',
       'unit':'string','method':'string | unknown','assessment':'known | unknown | not_assessed'},
       'not_interchangeable':True,'implicit_normal_category_for_missing_value':False},
   'source_hepatic_category':{'fields':{'category':'source-specific string','assessment':'known | unknown | not_assessed',
       'classification':'source-specific classification | not_specified','evidence':'clinician supplied assessment'},
       'no_inference_from_single_enzyme':True},
   'dose_schedule':{'fields':{'stages':'list of day, total_daily_mg, frequency, proceed, hold, stop',
       'basis':'source and locator | clinician choice'},'unpublished_values':'clinician choice, never engine defaults'},
   'clinical_assessment':{'type':'explicit clinician decision with source-specific category; not blanket safety clearance'}
 },
 'external_context':{
   'diagnosis':{'data_type':'string','unit':None,'origin':'physician-selected diagnosis, no rediagnosis'},
   'drug':{'data_type':'string','unit':None,'origin':'physician-selected INN'},
   'mode':{'data_type':'enum','unit':None,'allowed_values':['start','adjust','taper','switch','candidates'],'origin':'physician action'},
   'from_drug':{'data_type':'string','unit':None,'origin':'physician switch selection'},
   'to_drug':{'data_type':'string','unit':None,'origin':'physician switch selection'},
   'requested_mg':{'data_type':'number','unit':'mg','origin':'form feasibility fixture; not prescribed dose'},
   'foreign_requested_strategy':{'data_type':'string','unit':None,'origin':'negative routing fixture'},
   'withdrawal_plan_duration_days':{'data_type':'number','unit':'day','origin':'physician-supplied plan; not washout evidence'},
   'usual_dose_mg_per_day':{'data_type':'number','unit':'mg/day','origin':'arithmetic fixture base; bound to source start parameter'},
   'unit':{'data_type':'string','unit':None,'origin':'unit-validation fragment for renal operand'},
   'eGFR':{'data_type':'number','unit':'mL/min/1.73m2','origin':'negative fixture, cannot populate CLcr'}
 }}

for rid,r in rules.items():
    for i in r['inputs']:
        key=i['input_id']
        i['source_locator']=i.get('source_locator') or S[i['source_refs'][0]]['exact_locator']
        i['missing_states']=unknown
        if key in boolean_fields:
            i['data_type']='boolean';i['allowed_values']=[True,False]+unknown
            i['value_aliases']=schema['boolean_aliases']
        elif key=='clinician_action':
            i['allowed_values']=['keep','increase','decrease','stop','not_chosen']+unknown
            i['value_aliases']=schema['action_aliases']
        elif key in {'form','from_form','to_form'}:
            i['data_type']='structured_form';i['allowed_values']=[];i['structure_ref']='input_contracts.yaml#structures/structured_form'
        elif key=='medicines':
            i['allowed_values']=[];i['structure_ref']='input_contracts.yaml#structures/medication_list'
        elif key in {'renal','renal_metric'} and not rid.startswith('fluvox'):
            i['data_type']='structured_renal';i['allowed_values']=[]
            i['structure_ref']='input_contracts.yaml#structures/structured_renal'
            i['required_metric']='absolute_GFR' if rid.startswith('venla') else 'CLcr'
            i['required_unit']='mL/min'
        elif key=='hepatic':
            i['data_type']='source_hepatic_category';i['allowed_values']=[]
            i['structure_ref']='input_contracts.yaml#structures/source_hepatic_category'
            if 'RU-ESC' in [s['source_id'] for s in r['sources']]:
                i['category_mapping_status']='unverified_current_original; no automatic A/B/C mapping'
            elif rid.startswith('ser'):
                i['source_categories']=['no_impairment_after_assessment','hepatic_impairment','severe_hepatic_impairment']
            elif rid.startswith('dulox'):
                i['source_categories']=['no_impairment_after_assessment','liver_disease_with_insufficiency']
            elif rid.startswith('venla'):
                i['source_categories']=['no_impairment_after_assessment','mild','moderate','severe']
            elif rid.startswith('ago') or '-ago' in rid:
                i['source_categories']=['no_impairment_after_assessment','hepatic_insufficiency','cirrhosis','active_liver_disease']
            else: i['source_categories']=['no_impairment_after_assessment','hepatic_impairment']
        elif key=='response': i['allowed_values']=['достаточный','недостаточный']+unknown
        elif key=='tolerability': i['allowed_values']=['достаточная','неприемлемая']+unknown;i['value_aliases']={'приемлемая':'достаточная'}
        elif key in {'withdrawal_severity','current_withdrawal','withdrawal_symptoms'}:
            i['data_type']='enum';i['allowed_values']=['нет','лёгкие','умеренные','тяжёлые','непереносимые','выраженные']+unknown
            i['value_aliases']={'нет требующих замедления симптомов':'нет'}
        elif key=='duration_of_use':
            i['data_type']='number';i['unit']='week';i['allowed_values']=[]
        i['required_for_individual_result']=True
        if key in {'response','tolerability','adherence'} and rid=='ser-adult-adjust':
            i['required_for_individual_result']='clinician_action in [not_chosen, unknown, not_assessed]'
        i['condition_effect']='missing -> insufficient_data; confirmed source exclusion -> not_applicable; source caution -> clinician_choice unless an explicit source-specific decision is present'

# F03: semantic operator, not a two-week ceiling.
for rid,operator in [('ser-taper-limit','minimum_choice'),('fluvox-taper-limit','minimum_choice'),
                     ('venla-xr-taper-limit','minimum_choice'),('dulox-taper-limit','recommended_period')]:
    r=rules[rid];p=r['clinical_parameters'][0]
    p.update(value=[1,2],lower=None,upper=None,lower_inclusive=None,upper_inclusive=None)
    p['duration_semantics']={'operator':operator,'source_options_weeks':[1,2],'chosen_minimum_weeks':None,
        'hard_upper_limit_weeks':None,'exact_taper_duration_weeks':None,'slower_if_symptoms':True}
    p['meaning']='Опубликованная формулировка срока; 2 недели не максимальная общая длительность'
    r['output']['duration_constraint']=copy.deepcopy(p['duration_semantics'])
    r['output']['duration_constraint']['source_ref']=p['source_ref']
    r['output']['duration_constraint']['source_locator']=p['source_locator']
    if rid=='dulox-taper-limit':
        r['output']['duration_constraint']['note']='§4.2 с.4: «в течение», без «минимум»; при симптомах более постепенно. Не переносить оператор minimum других препаратов.'
    for c in r['test_cases']:
        c['expected']['duration_upper_limit_weeks']=None
        c['expected']['duration_operator']=operator
    r['logic']['actions'].append('Ни source_options_weeks, ни номинальный срок не ограничивают максимальную длительность; конкретный темп/пауза и возврат к прежней дозе остаются решениями врача по симптомам.')

# F10: preserve the full Russian strategy, including syntax uncertainty.
panic={'source_ref':'RU-PANIC','source_locator':'456_3 §3.1 PDF с.31–32, приложение Б4',
 'course':{'minimum_months':6,'comment_alternative_months':12,'meaning':'профилактика рецидива; сохранять достигнутую эффективную дозу'},
 'discontinuation':{'gradual':True,'careful_observation':True,'source_minimum_phrase_months':[2,3],
 'taper_only_duration_months':None,'observation_only_duration_months':None,
 'interpretation':'Фраза относится к постепенному снижению с тщательным контролем; источник не разделяет их длительности. Не строить собственный точный календарь.'},
 'guideline_algorithm':'Б4: профилактика/ведение СОПА; не график универсальных доз'}
dump(O/'panic_discontinuation_context.yaml',panic)
for rid in ('ser-taper-limit','esc-taper-limit','parox-taper-example'):
    r=rules[rid];r['logic']['panic_discontinuation_context']=panic
    if not any(s['source_id']=='RU-PANIC' for s in r['sources']):r['sources'].append(S['RU-PANIC'])
    for sec in ('applicability','logic','output'):
        if 'RU-PANIC' not in r[sec]['source_refs']:r[sec]['source_refs'].append('RU-PANIC')

# F07: explicit direction and independent, counted timestamp fields.
maoi_specs={
 'RU-SER':{'locator':'§4.3 с.3; §4.5 с.7–8','irreversible_days':14,'to_maoi_days':7,
     'reversible':'Источник допускает короче 14 дней, но не задаёт точный срок: clinician_choice без разрешения старта по числу.',
     'concurrent':['irreversible_maoi','reversible_selective_maoi','reversible_nonselective_maoi','pimozide']},
 'RU-DULOX':{'locator':'§4.3 с.4; §4.5 с.9–10','all_maoi_days':14,'to_maoi_days':5,
     'concurrent':['maoi','strong_CYP1A2']},
 'RU-PAROX':{'locator':'§4.3 с.17–18','irreversible_days':14,'reversible_hours':24,'to_maoi_days':7,
     'concurrent':['maoi','pimozide','thioridazine'],
     'exception':'Линезолид только исключительная клиническая ветка при отсутствии альтернатив, доступном наблюдении и оценке пользы/риска; обычный старт не разрешается.'},
 'RU-FLUVOX':{'locator':'§4.3 с.3','irreversible_days':14,'reversible_calendar':'next_calendar_day',
     'to_maoi_days':7,'concurrent':['maoi','tizanidine','pimozide','ramelteon']},
 'RU-VENLA-XR':{'locator':'HTML §4.3; §4.5 ИМАО','irreversible_days':14,'to_maoi_days':7,
     'reversible':'Период может быть короче 14 дней, точный не извлечён: clinician_choice.',
     'concurrent':['maoi']}
}
for rid,r in rules.items():
    if r['identity']['mode'] not in {'start','adjust','switch'}:continue
    sid=next((x for x in maoi_specs if any(s['source_id']==x for s in r['sources'])),None)
    if not sid:continue
    spec=maoi_specs[sid]
    inp(r,'maoi_type','Тип каждого текущего/отменённого ИМАО?', 'enum',sid,spec['locator'],
        ['none_after_medication_history','irreversible','reversible_selective','reversible_nonselective']+unknown,
        required='если список medicines содержит ИМАО или его класс неясен; separate per relevant record')
    inp(r,'maoi_stopped_at','Дата и время последнего приёма каждого отменённого ИМАО?', 'datetime',sid,spec['locator'],
        required='если ИМАО отменён; separate per relevant record')
    for i in r['inputs']:
        if i['input_id']=='maoi_type': i['required_for_individual_result']='medicines contains current/stopped MAOI or unidentified interaction class'
        if i['input_id']=='maoi_stopped_at': i['required_for_individual_result']='medicines contains stopped MAOI; per relevant record'
    r['logic']['maoi_history_contract']={'source_ref':sid,'source_locator':spec['locator'],**spec,
        'fields':['medicines','maoi_type','maoi_stopped_at'],'reference_time':'external_context.calculation_at',
        'required_timestamp_unknown':'insufficient_data; missing maoi_stopped_at; start_allowed=false',
        'current_maoi':'not_applicable for standard branch; no numeric start',
        'multiple_records':'all applicable direction gates must be satisfied; no single last record shortcut',
        'calendar_day':'next calendar date; not elapsed 24 hours unless that specific source says 24 hours'}
schema['external_context']['calculation_at']={'data_type':'datetime','unit':None,'origin':'calculation context, ISO8601 with UTC offset; not clinician question'}

# F08 and newly found DULOX sucrose exclusions: concrete independent fields.
ago_fields={
 'elderly_population':('Врач относит пациента к пожилым?', '§4.4 с.4; числовая граница категории не задана'),
 'dementia':('Есть деменция?', '§4.4 с.4'),
 'galactose_intolerance':('Редкая наследственная непереносимость галактозы?', '§4.3 с.3; §4.4 с.5'),
 'complete_lactase_deficiency':('Полная лактазная недостаточность?', '§4.3 с.3; §4.4 с.5'),
 'glucose_galactose_malabsorption':('Глюкозо-галактозная мальабсорбция?', '§4.3 с.3; §4.4 с.5'),
 'liver_injury_signs':('Есть признаки возможного поражения печени?', '§4.4 с.4: темная моча, обесцвеченный стул, желтуха, боль справа вверху живота, новая необъяснимая постоянная утомляемость'),
 'transaminases_rising':('Установлено повышение активности трансаминаз в ходе лечения?', '§4.4 с.4'),
 'overweight_obesity':('Есть избыточная масса тела/ожирение?', '§4.4 с.3'),
 'fatty_liver':('Есть неалкогольная жировая болезнь печени?', '§4.4 с.3'),
 'diabetes':('Есть диабет?', '§4.4 с.3'),
 'alcohol_abuse':('Есть алкоголизм или злоупотребление алкоголем?', '§4.4 с.3'),
 'alcohol_use':('Предполагается совместное употребление алкоголя?', '§4.5 с.6'),
 'mania':('Есть мания/гипомания или БАР в анамнезе?', '§4.4 с.4'),
 'mania_symptoms':('Появились текущие симптомы мании?', '§4.4 с.4'),
 'suicide_risk':('Врач выявил суицидальный риск?', '§4.4 с.4–5'),
 'ect':('Применяется ЭСТ?', '§4.5 с.6')
}
ago_actions=[
 {'id':'hereditary_exclusion','fields':['galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'],
  'if':'any true','then':'not_applicable; no start','source_ref':'RU-AGO','source_locator':'§4.3 с.3'},
 {'id':'elderly_dementia','fields':['elderly_population','dementia'],'if':'both true',
  'then':'not_applicable; no start','source_ref':'RU-AGO','source_locator':'§4.4 с.4'},
 {'id':'liver_stop','fields':['liver_injury_signs','ALT_ratio','AST_ratio'],'if':'liver_injury_signs true OR ALT > 3 OR AST > 3 during treatment',
  'then':'stop agomelatine immediately; regular liver tests until normalization; no further numeric stage',
  'source_ref':'RU-AGO','source_locator':'§4.4 с.4'},
 {'id':'repeat_liver_tests','fields':['transaminases_rising'],'if':'true',
  'then':'repeat liver tests within repeat_liver_tests_hours; independently assess stop conditions',
  'source_ref':'RU-AGO','source_locator':'§4.4 с.4'},
 {'id':'liver_risk_review','fields':['overweight_obesity','fatty_liver','diabetes','alcohol_abuse','medicines'],
  'if':'risk factor present or hepatotoxic comedication','then':'clinician benefit/risk assessment before start; no dose coefficient',
  'source_ref':'RU-AGO','source_locator':'§4.4 с.3'},
 {'id':'renal_caution','fields':['renal_state'],'if':'средняя or тяжёлая','then':'clinician_choice; no new renal factor',
  'source_ref':'RU-AGO','source_locator':'§4.2 с.2; §4.4 с.4'},
 {'id':'pregnancy_lactation','fields':['pregnancy','lactation'],'if':'true','then':'pregnancy avoid; lactation choose stopping breastfeeding or therapy; no standard automatic start',
  'source_ref':'RU-AGO','source_locator':'§4.6 с.6'},
 {'id':'cyp1a2','fields':['medicines'],'if':'strong CYP1A2 current','then':'not_applicable; moderate inhibitor -> clinician_choice; no PK-to-dose coefficient',
  'source_ref':'RU-AGO','source_locator':'§4.3 с.3; §4.5 с.5–6'},
 {'id':'mania_stop','fields':['mania_symptoms'],'if':'true during treatment','then':'stop agomelatine; source caution for history of mania/BAR is a separate mania field',
  'source_ref':'RU-AGO','source_locator':'§4.4 с.4'}
]
for rid,r in rules.items():
    target=rid in {'ago-gad-start','ago-depression-start'} or '-ago' in rid
    if not target:continue
    for key,(q,loc) in ago_fields.items():
        inp(r,key,q,'boolean','RU-AGO',loc,[True,False]+unknown)
    inp(r,'renal_state','Категория почечной недостаточности по оценке врача?', 'enum','RU-AGO','§4.2 с.2; §4.4 с.4',
        ['недостаточность не выявлена после оценки','лёгкая','средняя','тяжёлая']+unknown)
    for i in r['inputs']:
        if i['input_id'] in ago_fields or i['input_id']=='renal_state':i['required_for_individual_result']=True;i['missing_states']=unknown
    r['applicability']['exclusions'] += ['Редкие наследственные непереносимость галактозы, полная лактазная недостаточность, глюкозо-галактозная мальабсорбция (§4.3 с.3).',
        'Пожилые с деменцией: не назначать (§4.4 с.4); не выводить категорию пожилых из самостоятельно выбранного возраста.']
    r['logic']['agomelatine_conditions']=copy.deepcopy(ago_actions)
    r['logic']['agomelatine_conditions'][2]['fields']=['liver_injury_signs',
        'alt_ratio_uln' if '-ago' in rid else 'ALT_ratio','ast_ratio_uln' if '-ago' in rid else 'AST_ratio']
    param(r,'repeat_liver_tests_hours',48,'hour','RU-AGO','§4.4 PDF с.4')
    param(r,'liver_monitoring_weeks',[3,6,12,24],'week','RU-AGO','§4.2 с.1; §4.4 с.3')
    r['output']['liver_monitoring']={'before_start':True,'approximate_weeks_parameter':'liver_monitoring_weeks',
        'restart_same_frequency_after_dose_increase':True,'rising_repeat_hours_parameter':'repeat_liver_tests_hours',
        'stop_signs_action':'immediate cessation; tests until normal','source_ref':'RU-AGO','source_locator':'§4.2 с.1; §4.4 с.3–4'}
    r['output']['mandatory_checks']=['Каждый применимый agomelatine_conditions; АЛТ/АСТ независимо; форма B; неизвестный обязательный ответ не норма.']
for rid in ('dulox-gad-start','dulox-depression-start','dulox-gad-adjust'):
    r=rules[rid]
    for key,q in [('fructose_intolerance','Наследственная непереносимость фруктозы?'),
                  ('glucose_galactose_malabsorption','Глюкозо-галактозная мальабсорбция?'),
                  ('sucrase_isomaltase_deficiency','Дефицит сахаразы-изомальтазы?'),
                  ('akathisia','Развилась акатизия?')]:
        loc='§4.4 с.9'
        inp(r,key,q,'boolean','RU-DULOX',loc,[True,False]+unknown)
        r['inputs'][-1]['required_for_individual_result']=True
    r['applicability']['exclusions'].append('Сахароза: редкие наследственные непереносимость фруктозы, глюкозо-галактозная мальабсорбция, дефицит сахаразы-изомальтазы; §4.4 с.9.')
    r['logic']['actions'].append('Указанные наследственные состояния исключают приём Дулоксенты. При акатизии повышение может нанести вред: не выдавать автоматическое повышение (§4.4 с.9).')

# F05: source-specific elderly category; never a guessed numeric cutoff.
inp(rules['parox-panic-kr'],'elderly_population','Пациент относится к пожилой популяции по решению врача?',
    'boolean','RU-PAROX','§4.2 с.17; возрастная граница не задана',[True,False]+unknown)
rules['parox-panic-kr']['inputs'][-1]['required_for_individual_result']=True

# F09: supported class composition + the exact selected A example, with inherited constraints.
selected=rules['switch-parox-ago-selected-example']
selected['logic']['combination_justification']='RU-AGO §4.2 с.2 прямо разрешает начало в первый день постепенного снижения СИОЗС/СИОЗСН и отсылает к инструкции A. RU-PAROX §4.2 с.16–17 даёт выбранный пример отмены. Это источниковая композиция, не испытанный парный протокол; opt-in только выбирает пример.'
selected['logic']['component_constraints']={'A':'parox-taper-example and RU-PAROX §4.2–4.6',
    'B':'ago-depression-start; all agomelatine_conditions mandatory',
    'baseline_scope':'current_dose=40 mg/day; Reksetin 20 mg; normal assessed hepatic/renal categories; no current interacting contraindicated medicine'}
inp(selected,'from_renal','Функция почек для исходного пароксетина?', 'structured_renal','RU-PAROX','§4.2 с.17')
inp(selected,'from_hepatic','Функция печени для исходного пароксетина?', 'source_hepatic_category','RU-PAROX','§4.2 с.17')
selected['verification'].update(russian_applicability_checked=True,combined_rules_justified=True,
    ready_for_technical_implementation=True)
selected['verification']['unresolved_items']=['Последняя реестровая редакция A/B не подтверждена; выбранная композиция переносима только по данным опубликованным копиям, не полный парный протокол.']
rules['parox-taper-example']['verification']['ready_for_technical_implementation']=True
rules['parox-taper-example']['verification']['transfer_scope']='only clinician-selected source example at 40 mg/day; no generalized taper tail'
for st in selected['output']['schedule']:
    st['condition_to_hold']='Симптомы отмены A -> врач оценивает возврат прежней дозы и более медленное снижение; неподтвержденные входы -> не выполнять следующий этап.'
    st['condition_to_stop']='Признаки поражения печени B, АЛТ/АСТ >3 ВГН или новая мания -> немедленно прекратить B по RU-AGO §4.4 с.4; календарь A пересматривает врач.'
    st['source_locators']=['RU-PAROX §4.2 с.16–17','RU-AGO §4.2 с.1–2; §4.4 с.4']

# RU-ESC remains an open medical blocker, not a successful flag correction.
for rid,r in rules.items():
    if not any(s['source_id']=='RU-ESC' for s in r['sources']):continue
    r['verification'].update(primary_source_checked=False,all_clinical_parameters_have_sources=False,
                            population_and_indication_checked=False,ready_for_technical_implementation=False)
    r['verification']['unresolved_items'] += ['F01/F02/F13: полный актуальный RU-ESC недоступен; все числа, знаки, формы, деление и органные категории требуют повторной проверки.']
    r['profile']['selection_status']='blocked_unverified_current_original'
    r['logic']['source_blocker']={'source_ref':'RU-ESC','medical_predicates_confirmed':False,
        'renal_boundary_operator':None,'hepatic_class_mapping':None,
        'action':'source_unavailable; no individualized numeric or combined result'}
    r['output']['source_blocker']='F01/F02/F13; no executable numeric result'
    for p in r['clinical_parameters']:
        if p['source_ref']=='RU-ESC':
            p['confirmation_status']='unverified_current_original'
            if p['parameter_id']=='renal_caution_threshold':
                p['meaning']='Заявленный порог; знак < или <= не установлен по доступному актуальному оригиналу'
                p['boundary_operator']=None
                p['lower_inclusive']=p['upper_inclusive']=None
    for c in r['test_cases']:
        if 'clcr-exact-30-current-label' in c['case_id']:
            c['expected']={'result_type':'source_unavailable','renal_caution':None,
                'renal_boundary_operator':None,'unconditional_dose':None}
        c['case_kind']='unverified_source_fragment'
        c['transfer_allowed']=False
        c['source_confirmation']='current RU-ESC original unavailable'
    r['applicability']['renal_constraints']=['Знак источниковой границы не подтверждён; опубликованную копию другой редакции не подставлять. F02 открыт.']
    if rid=='esc-hepatic-start':
        r['applicability']['hepatic_constraints']=['Сопоставление категорий источника, включая Child–Pugh, не подтверждено; общая метка «нарушена» не выбирает числовую ветку. F13 открыт.']
        next(i for i in r['inputs'] if i['input_id']=='hepatic')['category_mapping_status']='unverified; no automatic branch selection'

# Correct a copied multi-product locator in the pregabalin-only numeric catalogue.
for rid,r in rules.items():
    if not rid.startswith('preg'):continue
    for p in r['clinical_parameters']:
        if p['parameter_id']=='adult_minimum':p['source_locator']='RU-PREG §4.1 с.3; §4.2–4.3 с.5–6'

schema['fragment_bindings']={}
for rid,r in rules.items():
    keys={i['input_id'] for i in r['inputs']}
    bindings={}
    for c in r['test_cases']:
        c.setdefault('case_kind','parameter_or_constraint_fragment')
        for key in c['given']:
            if key in keys:
                bindings[key]={'target':f'inputs.{key}','data_type':next(i['data_type'] for i in r['inputs'] if i['input_id']==key),
                    'unit':next(i['unit'] for i in r['inputs'] if i['input_id']==key)}
            elif key in {'indication','diagnosis'}:bindings[key]={'target':'external_context.diagnosis','data_type':'string','unit':None}
            elif key=='cyp2c19':bindings[key]={'target':'inputs.known_cyp2c19','data_type':'enum','unit':None}
            elif key=='elderly':bindings[key]={'target':'inputs.age','data_type':'integer','unit':'year','note':'legacy value is age, not elderly boolean'}
            elif key=='population':bindings[key]={'target':'inputs.elderly_population','data_type':'boolean','unit':None,'value_map':{'пожилой':True},'numeric_age_threshold':None}
            elif key in {'CLcr_mL_min','clcr_mL_min','GFR_mL_min'}:
                dest='renal' if 'renal' in keys else 'renal_metric'
                bindings[key]={'target':f'inputs.{dest}.value','data_type':'number','unit':'mL/min',
                    'metric':'absolute_GFR' if key=='GFR_mL_min' else 'CLcr'}
            elif key in schema['external_context']:
                bindings[key]={'target':f'external_context.{key}',**schema['external_context'][key]}
            else:raise ValueError(f'Unmapped {rid}: {key}')
    schema['fragment_bindings'][rid]=bindings
    r['input_contract_ref']=f'remediation/input_contracts.yaml#fragment_bindings/{rid}'
    r['logic']['parameter_refs']=[p['parameter_id'] for p in r['clinical_parameters']]
    r['sources']=[S[s['source_id']] for s in r['sources']]
    for i in r['inputs']:
        i.setdefault('required_for_individual_result',True);i.setdefault('missing_states',unknown)
        if i['data_type'] in schema['structures']:i['structure_ref']='input_contracts.yaml#structures/'+i['data_type']
        if i['input_id'] in boolean_fields:
            i['data_type']='boolean';i['allowed_values']=[True,False]+unknown;i['value_aliases']=schema['boolean_aliases']
        if i['input_id']=='from_renal':i.update(required_metric='CLcr',required_unit='mL/min')
        if i['input_id']=='from_hepatic':i['source_categories']=['нет недостаточности после оценки','печёночная недостаточность']
    dump(R/'rules'/f'{rid}.yaml',r)
dump(O/'input_contracts.yaml',schema)
(R/'sources.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
print('Corrected sources, input types, minimum semantics, MAOI history, agomelatine constraints, selected composition; ESC blockers remain open.')
