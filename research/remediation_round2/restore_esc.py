"""Source-reviewed ESC contracts from the human-downloaded current registry original."""
from pathlib import Path
from copy import deepcopy
import json,hashlib
import yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
def read(p):return yaml.safe_load(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
rules={p.stem:read(p) for p in (R/'rules').glob('*.yaml')}
C=read(O/'result_contracts.yaml');D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
ids=[rid for rid,r in rules.items() if any(s['source_id']=='RU-ESC' for s in r['sources'])]
oldbases={rid:deepcopy(next(c['given'] for c in D['cases'] if c['rule_id']==rid)) for rid in ids}
D['cases']=[c for c in D['cases'] if c['rule_id'] not in ids]
s=S['RU-ESC'];p=O/'Selectra_current_registry.pdf';sha=hashlib.sha256(p.read_bytes()).hexdigest()
version='РУ ЛП-№(012351)-(РГ-RU) 05.11.2025; экспертный отчёт 31.10.2025 №27320, последовательность 0002; текущая опубликованная ОХЛП реестра получена 08.10.2026'
s.update(url='https://lk.regmed.ru/Register/ViewPDFfromDAToken?Token=[REDACTED]',
         doi_or_registry_id='ЛП-№(012351)-(РГ-RU)',version_or_update_date=version,access_status='full',
         local_file='remediation_round2/Selectra_current_registry.pdf',exact_locator='§1–3 с.1–2; §4.1–4.2 с.2–3; §4.3–4.4 с.4–7; §4.5 с.7–9; §4.6 с.10; регистрационный и экспертный штампы с.1',
         evidence_limitations='Official currently listed edition verified; no implemented calculator or clinical validation. CLcr exactly 30 is not assigned by §4.2; no numeric step/interval for general escalation; no complete SSRI pair switch protocol.',
         latest_registration_revision_confirmed=True)
s['document_fingerprint']=dict(source_id='RU-ESC',url=s['url'],sha256=sha,pages=17,accessed_on='2026-10-08')
s['dates']=dict(registration='2025-11-05',expert_report='2025-10-31',approval=None,revision=None,publication=None,download='2026-10-08',filename_date_not_used='30092025')
s['latest_registry_document_comparison']=dict(registry_url='https://lk.regmed.ru/Register/EAEU_SmPC',observed_on='2026-10-08',
    currently_listed_document='1.3.1 Selectra_SmPC_30092025 _0002_clean (1747204851) [0002] штамп МЗ.pdf',
    currently_listed_documents_count=1,comparison='Human downloaded this listed file after CAPTCHA; local PDF registration/form/strengths and stamp visually match the opened registry PDF. This establishes the currently published official edition; unknown revision/publication dates are not fabricated.',
    sha256=sha,local_file=s['local_file'])
s['document_copies']=[dict(local_file=s['local_file'],sha256=sha,url=s['url'],download_date='2026-10-08',version=version,latest_registration_revision_confirmed=True,byte_identity_to_primary_snapshot=True),
    dict(local_file='remediation_round2/Selectra_current_registry_PIL.pdf',sha256=hashlib.sha256((O/'Selectra_current_registry_PIL.pdf').read_bytes()).hexdigest(),download_date='2026-10-08',document_type='PIL',role='Separate patient leaflet; not the SmPC dose basis',latest_registration_revision_confirmed=True)]
save(R/'sources.json',S)

def addinput(r,k,loc,t='boolean',values=None):
    if any(i['input_id']==k for i in r['inputs']):return
    r['inputs'].append(dict(input_id=k,question_ru='Подтверждённое врачом значение '+k+'?',data_type=t,unit=None,allowed_values=values or [True,False,'unknown','not_assessed'],required_when='для выбранного результата',show_when='выбранная ветка',why_needed='Источник RU-ESC '+loc,changes=['applicability','action'],unknown_allowed=True,action_if_unknown='insufficient_data; no individual dose',source_refs=['RU-ESC'],source_locator=loc,required_for_individual_result=True,missing_states=['unknown','not_assessed']))
def requirement(i,kind,loc,reason):
    i.update(requirement_predicate={'kind':kind},required_for_individual_result=kind=='always',
        required_when='для выбранного индивидуального результата' if kind=='always' else {'reported_context':'при сообщённом обстоятельстве; иначе not_assessed с предупреждением','outside_cessation_scope':'не условие выбранного прекращения','maoi_record':'каждый релевантный ИМАО','stopped_maoi_record':'каждый отменённый ИМАО отдельно','ecg_if_cad':'coronary_disease=true','correction_if_electrolytes':'electrolyte_disturbance=true'}.get(kind,kind),
        show_when='выбранная ветка или явно подтверждённый факт текущего расчёта',input_role='required_selected_result_operand_or_source_gate' if kind=='always' else kind,source_locator=loc,necessity_reason=reason,
        action_if_unknown='insufficient_data; request this applicable fact; no individual dose' if kind=='always' else 'retain unknown/not_assessed; evaluate only when predicate applies; never infer normality',fact_origin='product_metadata' if i['data_type']=='structured_form' else 'patient_fact')

def output(typ='clinician_choice',dose=None,**extra):
    e=dict(result_type=typ,total_daily_dose_mg=dose,dose_per_administration_mg=dose,administrations_per_day=1 if dose is not None else None,schedule=[],missing_fields=[],unconditional_future_stages=False,clinical_clearance=False)
    e.update(extra);return e
def basis(r):return [dict(source_id=x['source_id'],version=x['version_or_update_date'],locator=x['exact_locator'],sha256=x.get('document_fingerprint',{}).get('sha256')) for x in r['sources']]
def branch(rid,bid,when,e):
    C['rules'][rid]['branches'].append(dict(branch_id=bid,when=when,expected_output=e,source_basis=basis(rules[rid])))
def case(rid,name,g,e,bid=None):
    r=rules[rid];context=dict(diagnosis=r['identity']['diagnosis_code'].split('/')[0],drug=r['identity']['drug_inn'],mode=r['identity']['mode'],calculation_at='2026-10-08T09:00:00+03:00',treatment_phase='ongoing' if e['result_type']=='source_stop_action' else 'selected_mode')
    if r['identity']['mode']=='switch':context.update(from_drug=r['identity']['from_drug_inn'],to_drug=r['identity']['to_drug_inn'])
    D['cases'].append(dict(case_id=rid+'--current-'+name,rule_id=rid,case_kind='full_synthetic_input_scenario',not_executed_against_calculator=True,source_basis=basis(r),branch_id=bid,external_context=context,given=deepcopy(g),expected=deepcopy(e)))

for rid in ids:
    r=rules[rid];mode=r['identity']['mode'];con=C['rules'][rid]
    r['sources']=[S[x['source_id']] for x in r['sources']]
    r['logic'].pop('source_blocker',None);r['output'].pop('source_blocker',None)
    r['verification'].update(russian_applicability_checked=True,source_transfer_check='Current ESC original read and source predicates reconsidered; calculator_not_implemented; other product currency limitations remain',ready_for_technical_implementation=mode!='switch')
    r['applicability']['indication_status_in_russia']='confirmed_current_official_RU_ESC_SmPC'
    r['identity']['formulation_confirmation']='§3 с.1–2: equal halves for 10/15/20 mg; no half-dose claim for 5 mg'
    for cp in r['clinical_parameters']:
        if cp['source_ref']=='RU-ESC':
            cp['confirmation_status']='confirmed_current_registry_original'
            if cp['parameter_id']=='renal_caution_threshold':
                cp.update(boundary_operator='<',meaning='CLcr <30 caution; >30 no adjustment; exactly 30 not assigned',source_locator='§4.2 с.3, почечная недостаточность')
            if cp['parameter_id']=='elderly_threshold':cp.update(boundary_operator='>',meaning='Strictly older than 65; age 65 is not this special branch',source_locator='§4.2 с.3, лица пожилого возраста')
            if rid=='esc-taper-limit' and cp['parameter_id']=='reported_duration':
                cp.update(upper=None,meaning='Reported 1–2 week reduction period; §4.4 also allows several weeks/months',source_locator='§4.2 с.3; §4.4 с.6',duration_semantics={'source_reported_period_weeks':[1,2],'hard_upper_limit_weeks':None,'source_adjustment':'several weeks or months according to patient state'})
    if rid.startswith('esc'):
        for k,loc in [('mania_symptoms','§4.4 с.4'),('arrhythmia_signs','§4.4 с.6'),('serotonin_syndrome_signs','§4.4 с.5–6')]:addinput(r,k,loc)
        if mode=='start':
            for k,loc in [('coronary_disease','§4.4 с.6, stable CAD: ECG before start'),('electrolyte_disturbance','§4.4 с.6'),('ecg_done','§4.4 с.6'),('electrolytes_corrected','§4.4 с.6')]:addinput(r,k,loc)
        if mode in {'start','adjust'}:
            addinput(r,'maoi_type','§4.5 с.7–8','record_map',['irreversible','reversible_selective','reversible_nonselective','irreversible_selective_B','unknown','not_assessed'])
            addinput(r,'maoi_stopped_at','§4.5 с.7–8','record_map',[])
        for i in r['inputs']:
            k=i['input_id'];kind='always';loc='§4.2 с.2–3; §4.3–4.6 с.4–10';why=i['why_needed']
            if k=='hepatic':i.update(source_categories=['no_impairment_after_assessment','Child-Pugh_A','Child-Pugh_B','Child-Pugh_C']) ;loc='§4.2 с.3, точная классификация Чайлд-Пью'
            if k=='hepatic':i['question_ru']='Врач подтвердил отсутствие недостаточности или класс A/B/C по Чайлд–Пью? Не выводить класс из одного анализа.'
            if k=='renal':i.update(required_metric='CLcr',required_unit='mL/min');loc='§4.2 с.3, строго >30 и <30; =30 не определён'
            if k=='known_cyp2c19':kind='always' if rid=='esc-cyp2c19-start' else 'reported_context';loc='§4.2 с.3, известная слабая активность; обязательное тестирование не задано'
            if k in {'mania','qt_risk','bleeding_risk','hyponatremia_risk','suicide_risk','diabetes','glaucoma'}:kind='reported_context';loc={'mania':'§4.4 с.4, анамнез','qt_risk':'§4.4 с.6','bleeding_risk':'§4.4 с.5','hyponatremia_risk':'§4.4 с.5','suicide_risk':'§4.4 с.4–5','diabetes':'§4.4 с.4','glaucoma':'§4.4 с.7'}[k]
            if k=='mania':i['question_ru']='Мания/гипомания в анамнезе? Текущая фаза проверяется отдельно.'
            if k=='seizure_state':i['allowed_values']=list(dict.fromkeys(i['allowed_values']+['первичные/участившиеся приступы']));loc='§4.4 с.4'
            if k in {'maoi_type','maoi_stopped_at'}:kind='maoi_record' if k=='maoi_type' else 'stopped_maoi_record';i.update(collection='per medication record_id',value_data_type='enum' if k=='maoi_type' else 'datetime');loc='§4.5 с.7–8'
            if k=='ecg_done':kind='ecg_if_cad';loc='§4.4 с.6'
            if k=='electrolytes_corrected':kind='correction_if_electrolytes';loc='§4.4 с.6'
            if mode=='taper' and k not in {'age','form','current_dose','duration_of_use','prior_withdrawal','current_withdrawal','mania_symptoms','arrhythmia_signs','serotonin_syndrome_signs','seizure_state'}:kind='outside_cessation_scope'
            if mode=='adjust' and k in {'time_at_dose','adherence'}:kind='reported_context';why='No published fixed escalation interval/step; do not invent one.'
            requirement(i,kind,loc,why)
        r['applicability']['renal_constraints']=['CLcr >30: no adjustment; CLcr <30: caution; exactly 30: source gap, physician decision (§4.2 с.3)']
        r['applicability']['hepatic_constraints']=['Child–Pugh A/B: initial 5 mg/day for first two weeks, then possible 10 by response; C: close physician supervision, no automatic numeric correction (§4.2 с.3)']
        r['logic']['maoi_history_contract']=dict(source_ref='RU-ESC',source_locator='§4.5 с.7–8',irreversible_days=14,to_maoi_days=7,reversible='Moclobemide: at least one day; does not license all reversible MAOIs',fields=['medicines','maoi_type','maoi_stopped_at'],reference_time='external_context.calculation_at',current_maoi='not_applicable standard branch; exceptional combinations remain physician decisions',scope='ESC medication history, not a washout between the two SSRIs') if mode!='taper' else r['logic'].get('maoi_history_contract',{})
    else:
        for i in r['inputs']:
            requirement(i,'maoi_record' if i['input_id']=='maoi_type' else 'stopped_maoi_record' if i['input_id']=='maoi_stopped_at' else 'always',i['source_locator'],i['why_needed'])
        if rid=='switch-esc-ago':
            # The existing hepatic field belongs to target B; A has its own classification.
            addinput(r,'from_hepatic','§4.2 с.3','source_hepatic_category',[])
            i=r['inputs'][-1];i.update(source_categories=['no_impairment_after_assessment','Child-Pugh_A','Child-Pugh_B','Child-Pugh_C'],allowed_values=[],structure_ref='remediation_round2/input_contracts.yaml#structures/source_hepatic_category')
            requirement(i,'always','§4.2 с.3','Separate ESC A organ constraint; B hepatic insufficiency cannot be reused.')
            i=next(i for i in r['inputs'] if i['input_id']=='hepatic');i.update(source_refs=['RU-AGO'],source_categories=['no_impairment_after_assessment','hepatic_insufficiency','cirrhosis','active_liver_disease'],source_locator='RU-AGO §4.3 с.3')
    con.update(required_inputs=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='always'],conditional_inputs={i['input_id']:i['required_when'] for i in r['inputs'] if i['requirement_predicate']['kind']!='always'},input_requirements={i['input_id']:i['requirement_predicate'] for i in r['inputs']},branches=[],typed_source_conditions=[])
    con.pop('unverified_source_sections',None)
    con['source_gate_scope']='Source-specific selected result, with explicit monitoring context; no complete clinical clearance'
    con['monitoring_context_fields']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='reported_context']
    con['source_gates']=[dict(source_ref='RU-ESC',version=version,locator='§4.3–4.6 с.4–10',exclusions=['allergy'] if rid.startswith('esc') and mode!='taper' else [],cautions=[],stop=[k for k in ['mania_symptoms','arrhythmia_signs','serotonin_syndrome_signs'] if any(i['input_id']==k for i in r['inputs'])],current_medicines_excluded=['irreversible_maoi','pimozide','QT_prolonging'] if mode!='taper' else [],current_medicines_caution=['reversible_MAO_A','linezolid','selective_MAO_B','serotonergic','CYP2C19_inhibitor','cimetidine','bleeding'],other='CLcr=30 gap; Child–Pugh C supervision; no combined factors; QT electrolyte/ECG obligations; full pair switch calendar absent')]
    if rid.startswith('esc') and mode=='start':
        con['conditional_actions']=[
            dict(trigger='coronary_disease=true',required_fact='ecg_done',if_false='clinician_choice; obtain ECG before start; no dose',if_unknown='insufficient_data; missing ecg_done',source_ref='RU-ESC',source_locator='§4.4 с.6'),
            dict(trigger='electrolyte_disturbance=true',required_fact='electrolytes_corrected',if_false='clinician_choice; correct disturbances before start; no dose',if_unknown='insufficient_data; missing electrolytes_corrected',source_ref='RU-ESC',source_locator='§4.4 с.6')]
    if mode=='taper':con['source_gates'][0]['current_medicines_caution']=[]
    if rid=='switch-esc-ago':
        ago=deepcopy(next(g for g in C['rules']['switch-ser-ago']['source_gates'] if g['source_ref']=='RU-AGO'));con['source_gates'].append(ago)
        con['typed_source_conditions']=[dict(input='hepatic',operator='category_equals',value=cat,action='not_applicable',source_ref='RU-AGO',source_locator='§4.3 с.3') for cat in ['hepatic_insufficiency','cirrhosis','active_liver_disease']]
        con['ongoing_stop_conditions']=deepcopy(C['rules']['switch-ser-ago']['ongoing_stop_conditions'])
        r['output']['liver_monitoring']['rising_repeat_hours_parameter']='repeat_liver_tests_hours'
    if rid.startswith('esc'):
        con['typed_source_conditions'] += [dict(input='seizure_state',operator='equals',value=v,action='stop ESC' if v=='первичные/участившиеся приступы' else 'not_applicable standard branch',source_ref='RU-ESC',source_locator='§4.4 с.4') for v in ['неконтролируемые','первичные/участившиеся приступы']]
    if rid in ['esc-gad-start','esc-social-start']:
        branch(rid,'usual','adult <=65, liver assessed without impairment, CLcr>30, no known weak CYP/contraindication',output('exact',10,maximum_mg=20,automatic_increment_mg=None,automatic_interval_days=None))
    elif rid=='esc-panic-start':branch(rid,'usual','same ordinary adult conditions',output('exact',5,schedule=[dict(day=1,total_daily_mg=5,frequency=1),dict(day=8,total_daily_mg=10,frequency=1,conditional=True)],maximum_mg=20))
    elif rid=='esc-elderly-start':branch(rid,'elderly','age strictly >65; no overlapping modifier',output('exact',5,maximum_mg=10,automatic_day_for_increase=None))
    elif rid in ['esc-hepatic-start','esc-cyp2c19-start']:branch(rid,'special','Child-Pugh A/B OR known weak CYP respectively; no overlapping modifier',output('exact',5,initial_period_weeks=2,conditional_next_total_mg=10,next_requires='individual response and clinician decision; no automatic increase'))
    elif rid=='esc-adult-adjust':branch(rid,'response_decision','insufficient response; source permits up to20 but supplies no fixed increment or clock',output(published_maximum_mg=20,automatic_next_dose=None,automatic_interval_days=None))
    elif rid=='esc-taper-limit':branch(rid,'source_limit','no immediate-stop predicate; gradual withdrawal individualized',output(duration_constraint=dict(source_reported_period_weeks=[1,2],hard_upper_limit_weeks=None,source_adjustment='several weeks/months by patient state',source_ref='RU-ESC',source_locator='§4.2 с.3; §4.4 с.6'),full_taper_calendar=None,universal_percentage=None))
    elif rid=='switch-esc-ago':branch(rid,'class_overlap','A reduction physician-supplied; B independently applicable',output(overlap_allowed_on_first_day_of_A_reduction=True,target_source_start_mg=25,full_pair_calendar=None,monitoring=deepcopy(r['output']['liver_monitoring'])))
    else:branch(rid,'pair_gap','Russian sources do not supply exact pair strategy',output(automatic_direct_switch=False,full_pair_calendar=None,next_drug_start_day=None))
    r['output'].update(result_type='branch_selected',branches=deepcopy(con['branches']),schedule=[],total_daily_dose=None,dose_per_administration=None,administrations_per_day=None)
    for fragment in r['test_cases']:
        fragment.update(case_kind='isolated_source_fragment',source_confirmation='current official original reviewed; full inputs remain separate',transfer_allowed=True)
        if 'clcr-exact-30' in fragment['case_id']:
            fragment['expected']=dict(result_type='clinician_choice',renal_caution=None,renal_boundary_operator='source >30 / <30; =30 unassigned',unconditional_dose=None)
            fragment['note']='Current original §4.2 с.3: exact 30 is unassigned; isolated renal predicate, not a complete cessation/start result.'
        if rid=='esc-hepatic-start' and fragment['given'].get('hepatic')=='нарушена':
            fragment['given']['hepatic']='Child-Pugh_A';fragment['note']='Explicit source class A; unclassified hepatic impairment cannot be converted to this dose.'
    base=oldbases[rid]
    for i in r['inputs']:
        k=i['input_id']
        if k not in base:
            if i['data_type']=='record_map':continue
            base[k]=dict(category=i['source_categories'][0],assessment='known',classification='Child-Pugh' if k=='from_hepatic' else 'source-specific',evidence='synthetic assessed category') if i['data_type']=='source_hepatic_category' else False
        if i['data_type']=='structured_form':base[k]['source_version']=S[base[k]['source_id']]['version_or_update_date']
        if i['data_type']=='source_hepatic_category':base[k].update(category=i['source_categories'][0],classification='Child-Pugh' if 'RU-ESC' in i['source_refs'] else 'source-specific')
    if rid=='esc-elderly-start':base['age']=66
    if rid=='esc-hepatic-start':base['hepatic']['category']='Child-Pugh_A'
    if rid=='esc-cyp2c19-start':base['known_cyp2c19']='известная слабая активность'
    b=con['branches'][0];case(rid,'branch-'+b['branch_id'],base,b['expected_output'],b['branch_id'])
    if rid.startswith('esc'):
        g={k:v for k,v in base.items() if k not in con['monitoring_context_fields']}
        e=deepcopy(b['expected_output']);e['unassessed_context']=con['monitoring_context_fields']
        case(rid,'unassessed-monitoring-context',g,e,b['branch_id'])
    for k in con['required_inputs']:
        for state in ['omitted','unknown','not_assessed']:
            g=deepcopy(base)
            if state=='omitted':g.pop(k)
            else:g[k]=state
            case(rid,k+'-'+state,g,output('insufficient_data',missing_fields=[k]))
    if rid.startswith('esc') and mode in ['start','adjust']:
        if mode=='start':
            g=deepcopy(base);g.update(coronary_disease=True,ecg_done=True,electrolyte_disturbance=True,electrolytes_corrected=True)
            case(rid,'conditional-checks-completed',g,b['expected_output'],b['branch_id'])
            for trigger,key in [('coronary_disease','ecg_done'),('electrolyte_disturbance','electrolytes_corrected')]:
                for state in [False,'unknown','not_assessed']:
                    g=deepcopy(base);g[trigger]=True;g[key]=state
                    case(rid,key+'-'+str(state),g,output('clinician_choice' if state is False else 'insufficient_data',missing_fields=[] if state is False else [key],start_allowed=False,source_condition=dict(source_ref='RU-ESC',source_locator='§4.4 с.6')))
        for value,typ in [(29.99,'clinician_choice'),(30,'clinician_choice'),(30.01,b['expected_output']['result_type'])]:
            g=deepcopy(base);g['renal']['value']=value
            e=b['expected_output'] if value>30 else output(reason_ids=['CLcr_source_caution' if value<30 else 'CLcr_exact30_source_gap'])
            case(rid,'clcr-'+str(value),g,e,b['branch_id'] if value>30 else None)
        g=deepcopy(base);g['renal'].update(metric='indexed_eGFR',unit='mL/min/1.73m2');case(rid,'wrong-renal-metric',g,output('insufficient_data',missing_fields=['renal.CLcr']))
        for age in [17,65,66]:
            g=deepcopy(base);g['age']=age
            valid=(age>65 if rid=='esc-elderly-start' else age<=65 and age>=18)
            e=b['expected_output'] if valid else output('not_applicable' if age<18 else 'clinician_choice',reason_ids=['source_age_branch'])
            case(rid,'age-'+str(age),g,e,b['branch_id'] if valid else None)
        for cat in ['Child-Pugh_A','Child-Pugh_B','Child-Pugh_C']:
            g=deepcopy(base);g['hepatic']['category']=cat
            e=b['expected_output'] if rid=='esc-hepatic-start' and cat!='Child-Pugh_C' else output(reason_ids=['hepatic_special_or_supervision'],numeric_coefficient=None)
            case(rid,'hepatic-'+cat,g,e,b['branch_id'] if rid=='esc-hepatic-start' and cat!='Child-Pugh_C' else None)
        g=deepcopy(base);g.update(age=66,known_cyp2c19='известная слабая активность');g['hepatic']['category']='Child-Pugh_A'
        case(rid,'overlapping-modifiers',g,output(reason_ids=['combined_modifiers_not_published'],product_of_factors=None,automatic_selected_lower_dose=None))
        g=deepcopy(base);g['form']['release']='prolonged';case(rid,'wrong-release',g,output('form_not_feasible',automatic_form_substitution=False))
        g=deepcopy(base);g['form']['source_version']='historical_unverified';case(rid,'wrong-source-version',g,output('insufficient_data',missing_fields=['form.source_version']))
        for cls in ['pimozide','QT_prolonging','irreversible_maoi']:
            g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic source-classified '+cls,status='current',interaction_class=cls)]
            case(rid,'contra-'+cls,g,output('not_applicable',reason_ids=[cls]))
        for days in [13,14]:
            g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic nonselective irreversible MAOI',status='stopped',interaction_class='maoi')];g['maoi_type']={'M1':'irreversible'};g['maoi_stopped_at']={'M1':'2026-09-'+('25' if days==13 else '24')+'T09:00:00+03:00'}
            e=b['expected_output'] if days==14 else output('not_applicable',reason_ids=['MAOI_interval'])
            case(rid,'maoi-'+str(days),g,e,b['branch_id'] if days==14 else None)
        for hours in [23,24]:
            g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='моклобемид',status='stopped',interaction_class='maoi')];g['maoi_type']={'M1':'reversible_selective'};g['maoi_stopped_at']={'M1':'2026-10-07T'+('10' if hours==23 else '09')+':00:00+03:00'}
            case(rid,'moclobemide-'+str(hours)+'h',g,b['expected_output'] if hours==24 else output('not_applicable',reason_ids=['moclobemide_at_least_one_day']),b['branch_id'] if hours==24 else None)
        for k in ['maoi_type','maoi_stopped_at']:
            for state in ['omitted','unknown','not_assessed']:
                g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic stopped MAOI',status='stopped',interaction_class='maoi')];g['maoi_type']={'M1':'irreversible'};g['maoi_stopped_at']={'M1':'2026-09-24T09:00:00+03:00'}
                g[k]={} if state=='omitted' else {'M1':state}
                case(rid,k+'-'+state,g,output('insufficient_data',missing_fields=[k+'.M1']))
    for k in ['mania_symptoms','arrhythmia_signs','serotonin_syndrome_signs']:
        if k in base:
            g=deepcopy(base);g[k]=True;case(rid,k+'-stop',g,output('source_stop_action',stop_medication='RU-ESC',automatic_next_stage=False,source_condition=dict(source_ref='RU-ESC',source_locator='§4.4 с.4–6',input=k)))
    if rid=='switch-esc-ago':
        for k in ['alt_ratio_uln','ast_ratio_uln']:
            for val in [3,3.01]:
                g=deepcopy(base);g[k]=val;case(rid,k+'-'+str(val),g,output('clinician_choice' if val==3 else 'not_applicable',reason_ids=['target_liver_test'],source_condition=dict(source_ref='RU-AGO',source_locator='§4.3–4.4 с.3–4')))
            g=deepcopy(base);g[k]=3.01;case(rid,k+'-ongoing-above3',g,output('source_stop_action',stop_medication='RU-AGO',followup='liver tests regularly until normalization',automatic_next_stage=False,source_condition=dict(source_ref='RU-AGO',source_locator='§4.4 с.4')))
        for cls in ['strong_CYP1A2']:
            g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='флувоксамин',status='current',interaction_class=cls)];case(rid,'target-contra-'+cls,g,output('not_applicable',reason_ids=[cls],source_condition=dict(source_ref='RU-AGO',source_locator='§4.3 с.3; §4.5 с.5–6')))
    dump(R/'rules'/f'{rid}.yaml',r)

dump(O/'result_contracts.yaml',C);save(O/'full_scenarios.json',D)
for folder in ['findings','reference_rules']:
    for p in (R/folder).glob('*.yaml'):
        r=read(p);r['sources']=[S[x['source_id']] for x in r['sources']];dump(p,r)
print('Read current ESC original; restored 8 ESC and 3 dependent contracts with explicit CLcr=30 gap and directed-switch limits.')
