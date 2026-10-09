"""Author research contracts and synthetic expectations; no dosing engine is executed."""
from pathlib import Path
from copy import deepcopy
import json, csv
import yaml

R=Path(__file__).resolve().parents[1]; O=R/'remediation'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((R/'rules').glob('*.yaml'))}
schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
def dump(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def add_input(r,key,sid,loc,kind='boolean',values=None,unit=None):
    if any(i['input_id']==key for i in r['inputs']):return
    r['inputs'].append(dict(input_id=key,question_ru=f'Подтверждённое значение {key} по {loc}?',data_type=kind,
        unit=unit,allowed_values=values or ([True,False,'unknown','not_assessed'] if kind=='boolean' else []),
        required_when='для индивидуального результата этой ветки',show_when='эта ветка',
        why_needed=f'Изменяет допуск/действие по {sid} {loc}; не общий допуск врача.',changes=['applicability','action'],
        unknown_allowed=True,action_if_unknown=f'insufficient_data; missing=[{key}]; no individual dose',
        source_refs=[sid],source_locator=loc,required_for_individual_result=True,missing_states=['unknown','not_assessed']))

# Complete the source-specific value vocabularies, not generic "confirmed" answers.
for rid,r in rules.items():
    if rid=='dulox-depression-start':
        r['inputs']=[i for i in r['inputs'] if i['input_id'] not in {'comorbid_depression','elderly_population'}]
    for i in r['inputs']:
        if i['input_id']=='age':i['data_type']='integer'
        if i['data_type']=='enum':
            i['allowed_values']=list(dict.fromkeys([v for v in i['allowed_values'] if v!='неизвестно']+['unknown','not_assessed']))
            i.setdefault('value_aliases',{}).update({'неизвестно':'unknown','не исследовано':'not_assessed','не помню':'unknown'})
        if i['input_id']=='frequency':i['unit']='administration/day'
        if i['input_id']=='source_start_choice':i.update(allowed_values=[50,100,'not_chosen','unknown','not_assessed'],unit='mg/day',value_aliases={'50 мг':50,'100 мг':100,'не выбран':'not_chosen'})
        if i['input_id']=='clcr':i.update(metric='CLcr',method_context='clinician-confirmed CLcr; never indexed eGFR',unit='mL/min')
        if i['input_id']=='hepatic' and not i.get('source_categories'):
            i['source_categories']=['нет недостаточности после оценки','недостаточность: степень по источнику']
    if rid=='fluvox-depression-start':
        # Keep former operands only as documented aliases, not duplicate questions with contradictory clocks.
        r['inputs']=[i for i in r['inputs'] if i['input_id'] not in {'last_maoi_type','time_since_last_maoi'}]
        schema['fragment_bindings'][rid].update(last_maoi_type={'target':'inputs.maoi_type','data_type':'enum','unit':None,
            'value_map':{'обратимый':'reversible_selective','необратимый':'irreversible'}},
            time_since_last_maoi={'target':'derived elapsed from maoi_stopped_at + calculation_at','data_type':'number','unit':'day',
            'not_user_question':True,'calendar_next_day_cannot_be_replaced_by_elapsed_days':True})
        renal=next(i for i in r['inputs'] if i['input_id']=='renal_metric')
        renal.update(data_type='enum',allowed_values=['недостаточность не выявлена после оценки','почечная недостаточность','unknown','not_assessed'],unit=None)
        for key,loc in [('mania','§4.4 с.7'),('mania_symptoms','§4.4 с.7'),('akathisia','§4.4 с.5'),('bleeding_risk','§4.4 с.6'),
                        ('suicide_risk','§4.4 с.4'),('diabetes','§4.4 с.6'),('glaucoma','§4.4 с.6'),('ect','§4.4 с.6'),
                        ('liver_injury_signs','§4.4 с.5')]:add_input(r,key,'RU-FLUVOX',loc)
        add_input(r,'seizure_state','RU-FLUVOX','§4.4 с.5','enum',['не отмечены','контролируемые','неконтролируемые','новые приступы','unknown','not_assessed'])
    if rid.startswith('preg'):
        for key in ('angioedema','severe_skin_reaction'):add_input(r,key,'RU-PREG','§4.4 с.6')
        for key in ('galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'):add_input(r,key,'RU-PREG','§4.4 с.10, вспомогательные вещества')
        for key,loc in [('suicide_risk','§4.4 с.8'),('heart_failure','§4.4 с.10'),('diabetes_weight_gain','§4.4 с.6')]:add_input(r,key,'RU-PREG',loc)
    if rid=='parox-panic-kr' or rid in {'switch-parox-ago','switch-parox-ago-selected-example'}:
        for key,loc in [('mania','§4.4 с.20'),('suicide_risk','§4.4 с.18–20'),('akathisia','§4.4 с.20'),('diabetes','§4.4 с.21'),
                        ('glaucoma','§4.4 с.22'),('bleeding_risk','§4.4 с.22'),('qt_risk','§4.4 с.22'),('ect','§4.4 с.22')]:add_input(r,key,'RU-PAROX',loc)
        add_input(r,'seizure_state','RU-PAROX','§4.4 с.21','enum',['не отмечены','контролируемые','неконтролируемые','новые приступы','unknown','not_assessed'])
    if rid in {'dulox-gad-start','dulox-gad-adjust','dulox-depression-start'}:
        for key,loc in [('mania','§4.4 с.5'),('suicide_risk','§4.4 с.7–8'),('bleeding_risk','§4.4 с.8'),('hyponatremia_risk','§4.4 с.8'),('diabetes','§4.4 с.5')]:add_input(r,key,'RU-DULOX',loc)
        add_input(r,'seizure_state','RU-DULOX','§4.4 с.5','enum',['не отмечены','контролируемые','неконтролируемые','unknown','not_assessed'])
    if rid in {'venla-xr-gad-start','venla-xr-social-start','venla-xr-panic-form-limit'}:
        for key in ('recent_infarction','unstable_angina','heart_failure','coronary_disease','ecg_change','qt_risk','electrolyte_imbalance',
                    'hypertension','tachycardia','seizure_history','glaucoma','mania','bleeding_risk','low_body_mass','urinary_impairment',
                    'low_blood_pressure','diabetes','recent_stroke','hyponatremia_risk','ect','hypercholesterolemia','alcohol_use','suicide_risk'):
            add_input(r,key,'RU-VENLA-XR','HTML §4.4 С осторожностью / Особые указания')
        add_input(r,'pregnancy_suspected','RU-VENLA-XR','HTML §4.3')
        add_input(r,'diastolic_BP','RU-VENLA-XR','HTML §4.4: контроль АД, прекращение при диастолическом АД выше 100 мм рт.ст.','number',unit='mmHg')
        if not any(p['parameter_id']=='diastolic_BP_stop_threshold' for p in r['clinical_parameters']):
            r['clinical_parameters'].append(dict(parameter_id='diastolic_BP_stop_threshold',meaning='Строго выше порога: прекращение приёма',value=100,lower=None,upper=None,
                lower_inclusive=None,upper_inclusive=None,unit='mmHg',source_ref='RU-VENLA-XR',source_locator='HTML §4.4 контроль АД',source_meaning='предписание',derivation=None))
    if rid in {'switch-ser-ago','switch-parox-ago'}:
        sid='RU-SER' if rid=='switch-ser-ago' else 'RU-PAROX'
        add_input(r,'from_hepatic',sid,'§4.2 с.3' if sid=='RU-SER' else '§4.2 с.17','source_hepatic_category')
        if sid=='RU-PAROX':add_input(r,'from_renal',sid,'§4.2 с.17','structured_renal')
    if rid in {'ser-panic-start','ser-social-start','switch-ser-ago'}:
        add_input(r,'akathisia','RU-SER','§4.4 с.6')
    if rid=='switch-ser-ago':
        for key,loc in [('qt_risk','§4.4 с.4'),('bleeding_risk','§4.4 с.5'),('hyponatremia_risk','§4.4 с.5–6')]:add_input(r,key,'RU-SER',loc)
        add_input(r,'seizure_state','RU-SER','§4.4 с.4','enum',['не отмечены','контролируемые','неконтролируемые','новые приступы','unknown','not_assessed'])
    for i in r['inputs']:
        if i['data_type'] in schema['structures']:i['structure_ref']='remediation/input_contracts.yaml#structures/'+i['data_type']
        if i['input_id']=='from_renal':i.update(required_metric='CLcr',required_unit='mL/min')
        if i['input_id']=='from_hepatic':
            i['source_categories']=['no_impairment_after_assessment','hepatic_impairment','severe_hepatic_impairment'] if rid=='switch-ser-ago' else ['no_impairment_after_assessment','hepatic_insufficiency']
            i['source_locator']='§4.2 с.2, нарушение функции печени' if rid=='switch-ser-ago' else '§4.2 с.17, нарушение функции печени'
        if i['data_type']=='record_map':i['allowed_values']=list(dict.fromkeys(i['allowed_values']))
        if i['input_id']=='seizure_state' and 'RU-SER' in i['source_refs']:
            i['allowed_values']=list(dict.fromkeys(i['allowed_values']+['новые приступы']))
            i['source_refs']=['RU-SER'];i['source_locator']='§4.4 с.4, судороги: прекращение при развитии приступов'
        if rid.startswith('switch') and rid.endswith(('ago','ago-selected-example')):
            # Target-organ and form operands belong to B, not the first source of a pair.
            loc={'hepatic':'§4.3 с.3, печёночная недостаточность (цирроз или активное заболевание печени)',
                 'alt_ratio_uln':'§4.3 с.3; §4.4 с.3–4, АЛТ отдельно',
                 'ast_ratio_uln':'§4.3 с.3; §4.4 с.3–4, АСТ отдельно',
                 'to_form':'§2–3 с.1, Вальдоксан 25 мг',
                 'renal_state':'§4.2 с.2, почечная недостаточность'}
            if i['input_id'] in loc:i['source_refs']=['RU-AGO'];i['source_locator']=loc[i['input_id']]
            a='RU-PAROX' if 'parox' in rid else 'RU-SER' if 'ser' in rid else 'RU-ESC'
            if i['input_id'] in {'from_form','current_dose','from_taper_plan','withdrawal_severity','duration','past_withdrawal','example_selected'}:
                i['source_refs']=[a];i['source_locator']=('§4.2 с.16–17, прекращение/симптомы отмены; §3 с.15, форма' if a=='RU-PAROX' else '§4.2 с.2–3, прекращение; §3 с.1, форма' if a=='RU-SER' else S[a]['exact_locator'])
            i['source_condition_ownership']='B=RU-AGO' if i['source_refs']==['RU-AGO'] else 'A='+a if i['source_refs']==[a] else 'Shared patient/history fact; each applicable source gate evaluated separately'
            if i['input_id'] in {'age','medicines','allergy','pregnancy','lactation'}:
                k=i['input_id']
                ago_locs={'age':'§4.2 с.2, возрастная применимость','medicines':'§4.3 с.3; §4.5 с.5–6','allergy':'§4.3 с.3','pregnancy':'§4.6 с.6','lactation':'§4.6 с.6'}
                a_locs=({'age':'§4.2 с.17; §4.4 с.18','medicines':'§4.3 с.17–18; §4.5 с.24–26','allergy':'§4.3 с.17','pregnancy':'§4.6 с.27–28','lactation':'§4.6 с.28'} if a=='RU-PAROX' else
                        {'age':'§4.1 с.1; §4.4 с.4','medicines':'§4.3 с.3; §4.5 с.7–11','allergy':'§4.3 с.3','pregnancy':'§4.6 с.10–11','lactation':'§4.6 с.11'} if a=='RU-SER' else {k:S[a]['exact_locator']})
                i['source_refs']=[a,'RU-AGO'];i['source_locators_by_ref']={a:a_locs[k],'RU-AGO':ago_locs[k]}
                i['source_locator']='; '.join(s+': '+loc for s,loc in i['source_locators_by_ref'].items())

gatebook={
 'RU-AGO':dict(locator='§4.1–4.4 с.1–5; §4.5–4.6 с.5–6',exclusions=['allergy','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'],
    cautions=['pregnancy','lactation','mania','suicide_risk','overweight_obesity','fatty_liver','diabetes','alcohol_abuse','alcohol_use','ect'],
    current_medicines_excluded=['strong_CYP1A2'],current_medicines_caution=['moderate_CYP1A2','hepatotoxic'],
    stop=['liver_injury_signs','mania_symptoms'],other='ALT and AST separately >3 exclude start; (1,3] caution; liver insufficiency/cirrhosis/active disease exclude; elderly+dementia exclude; GAD >65, BDR >=75 exclude; <18 exclude; moderate/severe renal caution; rising transaminases repeat within 48 hours'),
 'RU-SER':dict(locator='§4.1–4.4 с.1–7; §4.5–4.6 с.7–11',exclusions=['allergy'],
    cautions=['pregnancy','lactation','mania','qt_risk','bleeding_risk','hyponatremia_risk','suicide_risk','akathisia'],
    current_medicines_excluded=['maoi','pimozide'],current_medicines_caution=['serotonergic','QT_prolonging','bleeding'],
    other='<18 not adult anxiety/BDR; severe hepatic no; other hepatic lower dose/frequency unspecified; unstable epilepsy avoid; seizures/current mania stop; renal no adjustment; alcohol/grapefruit avoid; akathisia no automatic increase'),
 'RU-DULOX':dict(locator='§4.1–4.3 с.2–4; §4.4–4.6 с.4–14',
    exclusions=['allergy','uncontrolled_hypertension','closed_angle_glaucoma','fructose_intolerance','glucose_galactose_malabsorption','sucrase_isomaltase_deficiency'],
    cautions=['pregnancy','lactation','akathisia','mania','suicide_risk','bleeding_risk','hyponatremia_risk','diabetes'],current_medicines_excluded=['maoi','strong_CYP1A2'],
    current_medicines_caution=['serotonergic','bleeding','CYP2D6_inhibitor'],
    other='<18 exclude; CLcr <30 exclude; hepatic disease with insufficiency exclude; akathisia increase harmful; no joint elderly+depression dose'),
 'RU-PAROX':dict(locator='§4.2–4.3 с.16–18; §4.4–4.6 с.18–28',exclusions=['allergy'],cautions=['pregnancy','lactation','mania','suicide_risk','akathisia','diabetes','glaucoma','bleeding_risk','qt_risk','ect'],
    current_medicines_excluded=['maoi','pimozide','thioridazine'],current_medicines_caution=['serotonergic','bleeding','CYP2D6_substrate'],
    other='<18 no adult scheme; elderly maximum 40 without invented age threshold; severe CLcr <30 or hepatic insufficiency low therapeutic range unspecified; no general taper tail; standard MAOI branch excludes exceptional linezolid use'),
 'RU-FLUVOX':dict(locator='§4.1–4.3 с.1–3; §4.4–4.6 с.4–11',exclusions=['allergy','lactation'],
    cautions=['pregnancy','mania','akathisia','bleeding_risk','suicide_risk','diabetes','glaucoma','ect'],
    current_medicines_excluded=['maoi','tizanidine','pimozide','ramelteon','terfenadine','astemizole','cisapride'],
    current_medicines_caution=['serotonergic','bleeding','CYP_substrate'],stop=['mania_symptoms','liver_injury_signs'],
    other='<18 depression no; renal/hepatic insufficiency low dose not numerically specified; uncontrolled epilepsy avoid; new seizures stop; >150 divided into 2 or 3 administrations by choice; next calendar day after reversible MAOI'),
 'RU-PREG':dict(locator='§4.1–4.3 с.3–6; §4.4–4.6 с.6–12',exclusions=['allergy','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'],cautions=['pregnancy','lactation','substance_use','respiratory','suicide_risk','heart_failure','diabetes_weight_gain'],
    current_medicines_excluded=[],current_medicines_caution=['CNS_depressant','opioid'],stop=['angioedema','severe_skin_reaction'],
    other='<18 exclude; CLcr source table; haemodialysis separate no complete scheme; hepatic no adjustment; no splitting/opening capsules; diabetes weight gain requires separate hypoglycaemic review'),
 'RU-VENLA-XR':dict(locator='HTML §4.2–4.6',exclusions=['allergy','pregnancy','pregnancy_suspected','lactation'],
    cautions=['recent_infarction','unstable_angina','heart_failure','coronary_disease','ecg_change','qt_risk','electrolyte_imbalance',
             'hypertension','tachycardia','seizure_history','glaucoma','mania','bleeding_risk','low_body_mass','urinary_impairment',
             'low_blood_pressure','diabetes','recent_stroke','hyponatremia_risk','ect','hypercholesterolemia','alcohol_use','suicide_risk'],
    current_medicines_excluded=['maoi'],current_medicines_caution=['serotonergic','QT_prolonging','bleeding'],
    other='<18 exclude; absolute GFR <10 contraindicated; 10..30 reduced by 50%; >30 unchanged; hepatic mild/moderate consider 50%; severe contraindicated; simultaneous modifiers no product; haemodialysis separate; XR 75/150 cannot realize 37.5; whole capsule with food'),
 'RU-PHEN':dict(locator='PDF с.2–5',exclusions=[],cautions=[],current_medicines_excluded=[],current_medicines_caution=[],
    other='Only gradual discontinuation statement; no numeric taper. Course duration is not taper duration.')}
def basis(r):return [dict(source_id=s['source_id'],version=s['version_or_update_date'],locator=s['exact_locator'],sha256=s.get('document_fingerprint',{}).get('sha256')) for s in r['sources']]
contracts={}
def branch(rid,bid,when,typ='exact',total=None,freq=None,**extra):
    r=rules[rid];o=dict(result_type=typ,total_daily_dose_mg=total,dose_per_administration_mg=(total/freq if total is not None and freq else None),
        administrations_per_day=freq,schedule=[],missing_fields=[],unconditional_future_stages=False)
    o.update(extra)
    contracts[rid]['branches'].append(dict(branch_id=bid,when=when,expected_output=o,source_basis=basis(r)))
    return o
for rid,r in rules.items():
    sids=[s['source_id'] for s in r['sources']]
    contracts[rid]=dict(required_inputs=[i['input_id'] for i in r['inputs'] if i['required_for_individual_result'] is True],
        conditional_inputs={i['input_id']:i['required_for_individual_result'] for i in r['inputs'] if i['required_for_individual_result'] is not True},
        source_gates=[dict(source_ref=sid,version=S[sid]['version_or_update_date'],**gatebook[sid]) for sid in gatebook if sid in sids],
        gate_order=['unavailable_source','known immediate stop/exclusion','invalid/missing applicable field','unresolved source caution/modifier','dose branch'],
        reference_display='Source scheme only, without individualized dose; no omitted field treated as negative',branches=[])
    contracts[rid]['source_gate_scope']='start/adjust applicability; both identified products for switch'
    contracts[rid]['typed_source_conditions']=[]
    for i in r['inputs']:
        k=i['input_id'];sid=i['source_refs'][0]
        if i['data_type']=='source_hepatic_category':
            for category in i['source_categories'][1:]:
                action='clinician_choice'
                if sid in {'RU-AGO','RU-DULOX'} or category in {'severe_hepatic_impairment','severe'}:action='not_applicable_standard_numeric_branch'
                contracts[rid]['typed_source_conditions'].append(dict(input=k,operator='category_equals',value=category,action=action,source_ref=sid,source_locator=i['source_locator']))
        if k=='seizure_state':
            for value in [x for x in i['allowed_values'] if x not in {'не отмечены','unknown','not_assessed'}]:
                action='clinician_choice'
                if value=='неконтролируемые' and sid in {'RU-SER','RU-FLUVOX'}:action='not_applicable_standard_branch; avoid unstable epilepsy'
                if value=='новые приступы' and sid in {'RU-SER','RU-PAROX','RU-FLUVOX'}:action='stop ongoing source medication'
                contracts[rid]['typed_source_conditions'].append(dict(input=k,operator='equals',value=value,action=action,source_ref=sid,source_locator=i['source_locator']))
    if r['identity']['mode']=='taper':
        contracts[rid]['source_gate_scope']='discontinuation statement and symptom-dependent hold/stop only; start exclusions do not prevent discontinuation'
        contracts[rid]['source_gates']=[dict(source_ref=sid,version=S[sid]['version_or_update_date'],locator=gatebook[sid]['locator'],
            exclusions=[],cautions=[],current_medicines_excluded=[],current_medicines_caution=[],
            stop=[k for k in gatebook[sid].get('stop',[]) if any(i['input_id']==k for i in r['inputs'])],
            other='Source-specific withdrawal guidance; exact taper not inferred. Published immediate cessation conditions take precedence if treatment ongoing.') for sid in gatebook if sid in sids]
    if rid=='ago-stop':
        contracts[rid]['source_gate_scope']='physician-chosen cessation of agomelatine only; no starting or next-drug clearance'
        contracts[rid]['source_gates']=[dict(source_ref='RU-AGO',version=S['RU-AGO']['version_or_update_date'],locator='§4.2 с.2, Прекращение лечения',
            exclusions=[],cautions=[],current_medicines_excluded=[],current_medicines_caution=[],other='No mandatory taper of agomelatine; no next-drug start time derived')]
    if 'RU-AGO' in sids and rid!='ago-stop':
        contracts[rid]['ongoing_stop_conditions']=[dict(input=k,operator='>',value=3,unit='ULN ratio',
            treatment_phase='ongoing',action='source_stop_action',stop_medication='RU-AGO',followup='liver tests regularly until normalization',
            source_ref='RU-AGO',source_locator='§4.4 с.4, немедленное прекращение при АЛТ или АСТ >3 ВГН') for k in
            (('ALT_ratio','AST_ratio') if rid.startswith('ago') else ('alt_ratio_uln','ast_ratio_uln'))]
    r['logic']['result_contract_ref']=f'remediation/result_contracts.yaml#rules/{rid}'
    r['logic']['individual_output_gate']='All required typed inputs and applicable conditional inputs must be known; evaluate every source-specific gate in result_contract. A caution has clinician_choice, not an invented coefficient. No blanket clinical clearance.'
    if 'RU-ESC' in sids:
        contracts[rid]['unverified_source_sections']=deepcopy(contracts[rid]['source_gates'])
        contracts[rid]['source_gates']=[]
        contracts[rid]['source_gate_scope']='Blocked before clinical predicates; source sections retained for future original review, not evaluated as confirmed rules'
        branch(rid,'unavailable','Current RU-ESC full original unavailable','source_unavailable',reason_ids=['F01','F02','F13']);continue
    if rid in {'ago-depression-start','ago-gad-start'}:
        branch(rid,'usual','all gates clear; assessed liver normal; ALT<=1 AND AST<=1; adult within indication-specific age',total=25,freq=1,
            monitoring=deepcopy(r['output']['liver_monitoring']),conditional_higher_dose_mg=50,earliest_higher_weeks=2 if rid=='ago-depression-start' else 4,
            higher_requires='no positive dynamics + clinician benefit/risk decision + liver monitoring')
        branch(rid,'liver_caution','ALT or AST >1 and <=3; no exclusion','clinician_choice',monitoring=deepcopy(r['output']['liver_monitoring']))
        branch(rid,'renal_caution','moderate/severe renal impairment','clinician_choice',dose_coefficient=None)
        branch(rid,'repeat_tests','rising transaminases; ALT and AST still <=3; no injury signs','clinician_choice',repeat_tests_within_hours=48)
    elif rid=='ago-stop':branch(rid,'chosen_stop','clinician_action=stop; current dose known','source_stop_action',mandatory_taper=False,next_drug_start_day=None)
    elif rid=='dulox-gad-start':
        branch(rid,'usual','elderly_population=false AND comorbid_depression=false',total=30,freq=1,automatic_day_for_60=None)
        branch(rid,'comorbid','elderly_population=false AND comorbid_depression=true',total=60,freq=1)
        branch(rid,'elderly','elderly_population=true AND comorbid_depression=false',total=30,freq=1,initial_period_weeks=2,conditional_next_total_mg=60)
        branch(rid,'overlap','elderly_population=true AND comorbid_depression=true','clinician_choice',automatic_combined_start=None)
    elif rid=='dulox-depression-start':branch(rid,'usual','all source gates clear; BDR',total=60,freq=1,automatic_escalation_to_120=False)
    elif rid=='dulox-gad-adjust':
        branch(rid,'at30','current=30; inadequate response; acceptable tolerance; no overlap','clinician_choice',published_options_mg=[60],automatic_interval_days=None)
        branch(rid,'at60','current=60; inadequate response; acceptable tolerance; no overlap','clinician_choice',published_options_mg=[90,120],automatic_interval_days=None)
        branch(rid,'other','other dose, adequate response, intolerance or combined modifiers','clinician_choice',automatic_next_dose=None)
    elif rid in {'ser-panic-start','ser-social-start'}:
        branch(rid,'usual','all source gates clear',total=25,freq=1,schedule=[dict(day=1,total_daily_mg=25,frequency=1),dict(day=8,total_daily_mg=50,frequency=1,conditional=True)],
            maximum_mg=200,future_increment_mg=50,minimum_interval_weeks=1)
    elif rid=='ser-adult-adjust':
        contracts[rid]['general_result_templates']=[
            dict(action='increase',conditions=['all applicable source gates known and clear','source-compatible current_dose>=50','time_at_dose>=interval','current_dose+step<=maximum','candidate realizable with identified source form'],
                 total_daily_dose_expression='current_dose + clinical_parameters.step',frequency_expression='clinical_parameters.frequency',dose_per_administration_expression='total_daily_dose / frequency',
                 source_ref='RU-SER',source_locator='§4.2 с.2–3',special_initial_25='panic/social first week only: published transition to50, not +50'),
            dict(action='keep',conditions=['current dose and form source-compatible','all applicable source gates known and clear'],total_daily_dose_expression='current_dose',source_ref='RU-SER',source_locator='§4.2 с.2–3, минимальная эффективная доза'),
            dict(action='increase',conditions=['candidate exceeds maximum OR minimum interval not yet reached'],result_type='clinician_choice',individual_dose=None,round_to_maximum=False,source_ref='RU-SER',source_locator='§4.2 с.2–3')]
        branch(rid,'increase','clinician_action=increase; current=100; time_at_dose>=1 week; no source cautions',total=150,freq=1,minimum_interval_weeks=1)
        branch(rid,'keep','clinician_action=keep; current=100; dose/form applicable',total=100,freq=1)
        for a,b in ((50,100),(150,200)):
            branch(rid,'increase-from'+str(a),f'clinician_action=increase; current={a}; time>=1week; all source gates clear',total=b,freq=1,minimum_interval_weeks=1)
        for a in (50,150,200):branch(rid,'keep'+str(a),f'clinician_action=keep; current={a}; dose/form applicable',total=a,freq=1)
        branch(rid,'initial25','clinician_action=increase; panic/social initial25 completed at least1week; all gates clear',total=50,freq=1,minimum_interval_weeks=1)
        branch(rid,'other-source-dose','clinician_action=increase; source-compatible current75; time>=1week; next125 achievable from 50mg tablets with equal halves; no caution',total=125,freq=1,
            expression='current_dose + clinical_parameters.step; only if candidate <=maximum, interval>=interval, source/form compatible; no rounding to maximum',expression_source_ref='RU-SER',expression_source_locator='§4.2 с.2–3')
        branch(rid,'ceiling','action=increase AND current_dose + step >maximum','clinician_choice',next_increase_mg=None)
        branch(rid,'early','time_at_dose<1 week AND action=increase','clinician_choice',increase_allowed=False)
        branch(rid,'decrease','clinician_action=decrease or stop','clinician_choice',automatic_smaller_dose=None)
        branch(rid,'clinical_option','action=not_chosen; response inadequate; tolerance adequate; adherence confirmed; current=100; time>=1week','clinician_choice',published_option_mg=150)
    elif rid=='parox-panic-kr':
        branch(rid,'usual','all gates clear; elderly_population=false; start',total=10,freq=1,recommended_mg=40,maximum_mg=60,optional_increment_mg=10,minimum_interval_weeks=1,
            beyond_recommended_requires='inadequate response after several weeks, no fabricated exact interval')
        branch(rid,'elderly','elderly_population=true; organs clear',total=10,freq=1,maximum_mg=40,elderly_age_cutoff=None)
        branch(rid,'organ_caution','CLcr<30 or hepatic insufficiency','clinician_choice',published_lower_therapeutic_range_no_exact_start=True)
    elif rid=='parox-taper-example':
        branch(rid,'selected40','current=40; example_selected=true; symptoms absent; form valid','selected_source_example',freq=1,
            schedule=[dict(day=1,total_daily_mg=30,frequency=1,conditional=True),dict(day=8,total_daily_mg=20,frequency=1,conditional=True),dict(day=15,total_daily_mg=0,frequency=1,conditional=True)],
            mandatory_for_all=False,hold_if='withdrawal symptoms; clinician reassessment/prior-dose resumption then slower, unspecified steps')
        branch(rid,'other','example not selected, current<20 or withdrawal symptoms','clinician_choice',invented_last_step=False)
    elif rid=='switch-parox-ago-selected-example':
        branch(rid,'selected40','current=40; example_selected=true; no withdrawal; all A/B gates clear; identified products','selected_source_example',
            schedule=deepcopy(r['output']['schedule']),monitoring=deepcopy(r['output']['liver_monitoring']),trial_validated_pair=False)
        branch(rid,'withdrawal_hold','withdrawal symptoms or previous difficult withdrawal','clinician_choice',automatic_next_stage=False,slower_step=None)
        branch(rid,'not_selected','example_selected=false or current dose !=40','clinician_choice',complete_calendar=None)
    elif rid in {'switch-ser-ago','switch-parox-ago'}:
        branch(rid,'source_class_overlap','A plan supplied by clinician; B all conditions evaluated; no exact A calendar inferred','clinician_choice',
            overlap_allowed_on_first_day_of_A_reduction=True,target_source_start_mg=25,full_pair_calendar=None,monitoring=deepcopy(r['output']['liver_monitoring']))
    elif rid=='fluvox-depression-start':
        for n in (50,100):branch(rid,f'selected{n}',f'source_start_choice={n}; organs assessed without insufficiency; all gates clear',total=n,freq=1,
            review_period_weeks=[3,4],automatic_next_increment=None)
        branch(rid,'choice','start choice not selected or renal/hepatic insufficiency','clinician_choice',published_start_options_mg=[50,100],numeric_organ_factor=None)
    elif rid in {'preg-gad-start','preg-gad-adjust'}:
        for f in (2,3):
            if rid=='preg-gad-start':branch(rid,f'frequency{f}',f'CLcr>=60; no dialysis; selected frequency={f}',total=150,freq=f,
                optional_stages_mg=[300,450,600],minimum_interval_weeks=1)
            else:
                for a,b in ((150,300),(300,450),(450,600)):
                    branch(rid,f'from{a}-frequency{f}',f'current={a}; time>=1week; inadequate response; adequate tolerance; adherence confirmed; CLcr>=60; frequency={f}',
                        'clinician_choice',published_option_mg=b,per_administration_option_mg=b/f,frequency_option=f,minimum_interval_weeks=1)
        if rid=='preg-gad-adjust':branch(rid,'other','other dose, interval short, sufficient response, ceiling, intolerance or renal impairment','clinician_choice',automatic_next_dose=None)
    elif rid=='preg-renal-start':
        for bid,when,start,maxi,f in [('ge60','CLcr>=60',150,600,[2,3]),('30_60','30<=CLcr<60',75,300,[2,3]),('15_30','15<=CLcr<30',[25,50],150,[1,2]),('lt15','0<=CLcr<15',25,75,[1])]:
            branch(rid,bid,when+'; no dialysis','clinician_choice',source_start_mg=start,maximum_mg=maxi,frequency_options=f,
                auto_selected_range_endpoint=None,source_interval_for_renal_titration=None,form_feasibility='each physician selected dose/frequency must be realizable with whole identified capsules')
    elif rid in {'venla-xr-gad-start','venla-xr-social-start'}:
        branch(rid,'usual','absolute_GFR>30; no hepatic insufficiency; all gates clear',total=75,freq=1,maximum_mg=225,minimum_increase_interval_weeks=2,
            automatic_increment=None,higher_social_benefit_proven=False if 'social' in rid else None)
        branch(rid,'renal_reduction','10<=absolute_GFR<=30; liver clear','form_not_feasible',published_reduction_percent=50,arithmetic_total_mg=37.5,
            executable_dose=None,IR_substitution_allowed=False)
        branch(rid,'hepatic_reduction','mild/moderate hepatic insufficiency; renal clear','clinician_choice',published_reduction_percent=50,arithmetic_total_mg=37.5,executable_dose=None)
        branch(rid,'joint_modifiers','renal and hepatic modifier overlap','clinician_choice',product_of_reductions=None)
    elif rid=='venla-xr-panic-form-limit':branch(rid,'form_limit','identified Velaxin XR 75/150','form_not_feasible',source_initial_mg=37.5,initial_days=7,source_next_mg=75,IR_substitution_allowed=False)
    elif 'taper' in rid:
        dc=deepcopy(r['output'].get('duration_constraint',{}))
        if rid=='preg-taper-limit':dc=dict(operator='minimum',minimum_weeks=1,hard_upper_limit_weeks=None,source_ref='RU-PREG',source_locator='§4.2 с.4')
        branch(rid,'source_limit','known current dose/form/duration; no urgent stop condition','clinician_choice',duration_constraint=dc,full_taper_calendar=None,universal_percentage=None)
        branch(rid,'withdrawal','withdrawal symptoms present','clinician_choice',automatic_next_reduction=False,slower_step=None,prior_dose_resumption='clinician consideration where source permits')
    else:raise ValueError(rid)
    # A branch dispatcher must not expose an unconditional default next to branch-dependent outputs.
    r['output'].update(result_type='branch_selected',dose_per_administration=None,administrations_per_day=None,total_daily_dose=None,
        branches=deepcopy(contracts[rid]['branches']),selection_contract=contracts[rid]['gate_order'])

schema['structures']['medication_list']['entry_fields']['record_id']='string; matches separate MAOI fields'
schema['structures']['medication_list']['entry_fields']['classification_basis']='optional object {source_ref:string, source_locator:string}; provenance, unit=null, not an additional clinical question'
schema['structures']['structured_form']['fields']['source_version']='exact sources.json version string'
schema['structures']['structured_form']['fields']['registration_number']='string | null only if source prints no number; null does not confirm registration/currency or individualized form clearance'
schema['external_context']['treatment_phase']={'data_type':'enum','unit':None,'allowed_values':['ongoing','selected_mode'],'origin':'synthetic scenario context; distinguishes cessation from start clearance'}
schema['external_context']['drug']['nullable_when']='mode=switch only; from_drug and to_drug are required instead'
schema['conditional_history_fields']={'maoi_type':'object keyed by relevant record_id; value in source-specific MAOI type enum',
    'maoi_stopped_at':'object keyed by stopped MAOI record_id; ISO8601 with UTC offset; each timestamp counted separately',
    'empty_history':'[] confirms none; omit conditional fields; omission is not unknown because predicate is false',
    'source_interval':'evaluate every record; do not infer interval after A from B-to-A interval'}
for r in rules.values():
    if 'maoi_history_contract' in r['logic'] and r['identity']['mode']=='switch':
        r['logic']['maoi_history_contract']['scope']='Medication-history applicability of the identified A source; not an A→AGO washout. B overlap is independently bound to RU-AGO §4.2.'
    for i in r['inputs']:
        if i['input_id'] in {'maoi_type','maoi_stopped_at'}:
            i['collection']='per medication record_id'
            i['value_data_type']='enum' if i['input_id']=='maoi_type' else 'datetime'
            i['data_type']='record_map'

forms={
 'RU-AGO':('Вальдоксан','ЛП-№(000528)-(РГ-RU)',[25],'tablet','immediate'),
 'RU-SER':('Золофт','ЛП-№(002851)-(РГ-RU)',[50,100],'tablet','immediate'),
 'RU-PAROX':('Рексетин','ЛП-№(008861)-(РГ-RU)',[20],'tablet','immediate'),
 'RU-DULOX':('Дулоксента','ЛП-№(000186)-(РГ-RU)',[30,60],'capsule','enteric'),
 'RU-FLUVOX':('Феварин','ЛП-№(008757)-(РГ-RU)',[50,100],'tablet','immediate'),
 'RU-PREG':('Лирика','ЛП-№(004450)-(РГ-RU)',[25,50,75,100,150,200,300],'capsule','immediate'),
 'RU-VENLA-XR':('Велаксин','ЛП-№(002093)-(РГ-RU)',[75,150],'capsule','prolonged'),
 'RU-PHEN':('Феназепам',None,[0.25,0.5,1],'orodispersible_tablet','immediate'),
 'RU-ESC':('Селектра','ЛП-№(012351)-(РГ-RU)',[5,10,15,20],'tablet','immediate')}
def form(sid):
    name,reg,strengths,kind,release=forms[sid]
    return dict(product=name,registration_number=reg,source_id=sid,source_version=S[sid]['version_or_update_date'],dosage_form=kind,strengths_mg=strengths,release=release,route='oral')
def source_for_form(rid,key):
    if rid.startswith('switch'):
        part=rid.split('-')[1 if key=='from_form' else 2]
        return {'parox':'RU-PAROX','ser':'RU-SER','esc':'RU-ESC','ago':'RU-AGO'}[part]
    return next(sid for sid in forms if rid.startswith({'RU-AGO':'ago','RU-SER':'ser','RU-PAROX':'parox','RU-DULOX':'dulox','RU-FLUVOX':'fluvox','RU-PREG':'preg','RU-VENLA-XR':'venla','RU-PHEN':'phen','RU-ESC':'esc'}[sid]))
def fixture(rid,r):
    d={}
    for i in r['inputs']:
        k=i['input_id'];t=i.get('value_data_type',i['data_type'])
        if i.get('collection')=='per medication record_id':continue
        if t=='record_map':continue
        if t=='boolean':v=False
        elif t=='structured_form':v=form(source_for_form(rid,k))
        elif t=='source_hepatic_category':v={'category':i['source_categories'][0],'assessment':'known','classification':'source-specific','evidence':'synthetic assessed category'}
        elif t=='structured_renal':v=dict(metric=i.get('required_metric','CLcr'),value=90,unit='mL/min',method='clinician-confirmed source-compatible assessment',assessment='known')
        elif t=='medication_list':v=[]
        elif t=='dose_schedule':v=dict(stages=[dict(day=1,total_daily_mg=30 if 'parox' in rid else 50,frequency=1,proceed='clinician chosen initial reduction',hold='withdrawal symptoms; reassess',stop='not predetermined')],
            basis='synthetic physician-supplied initial reduction; not an automatic published A calendar; subsequent A stages remain physician decisions')
        elif t=='clinical_assessment':v=dict(status='not_supported_for_full_pair',basis='no verified source interval')
        elif t=='datetime':v='2026-10-01T09:00:00+03:00'
        elif t in {'integer','number'}:
            v={'age':40,'current_dose':40 if 'parox' in rid else 100 if 'ser' in rid else 150 if 'preg' in rid else 30 if rid=='dulox-gad-adjust' else 75 if 'venla' in rid else 1.5 if 'phen' in rid else 60,
               'time_at_dose':1,'duration':2 if 'phen' in rid else 24,'duration_of_use':24,'ALT_ratio':1,'AST_ratio':1,'alt_ratio_uln':1,'ast_ratio_uln':1,'clcr':90,'diastolic_BP':80}.get(k,1)
        elif t=='enum':
            v={'renal_state':'недостаточность не выявлена после оценки','renal_metric':'недостаточность не выявлена после оценки',
               'clinician_action':'stop' if rid=='ago-stop' else 'increase','response':'недостаточный','tolerability':'достаточная','adherence':'подтверждён',
               'frequency':2,'source_start_choice':50,'seizure_state':'не отмечены','withdrawal_severity':'нет','current_withdrawal':'нет',
               'withdrawal_symptoms':'нет','known_cyp2c19':'не исследовано'}.get(k,i['allowed_values'][0])
        else:raise ValueError((rid,k,t))
        d[k]=v
    if 'example_selected' in d:d['example_selected']=True
    return d

scenarios=[]
def case(rid,cid,given,bid=None,typ=None,**expected):
    r=rules[rid]
    if bid:o=deepcopy(next(b['expected_output'] for b in contracts[rid]['branches'] if b['branch_id']==bid))
    else:o=dict(result_type=typ,total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,
        schedule=[],missing_fields=[],unconditional_future_stages=False)
    o.update(expected)
    stop_source=o.get('stop_medication',o.get('source_condition',{}).get('source_ref'))
    if stop_source=='RU-AGO' and o['result_type']=='source_stop_action':
        o['followup']='Discontinue agomelatine; if liver injury or ALT/AST >3 ULN, liver tests regularly until normalization; no automatic next-drug start'
    context=dict(diagnosis=r['identity']['diagnosis_code'].split('/')[0],drug=r['identity']['drug_inn'],mode=r['identity']['mode'],
        calculation_at='2026-10-08T09:00:00+03:00',treatment_phase='ongoing' if o['result_type']=='source_stop_action' else 'selected_mode')
    if r['identity']['mode']=='switch':context.update(from_drug=r['identity']['from_drug_inn'],to_drug=r['identity']['to_drug_inn'])
    scenarios.append(dict(case_id=rid+'--'+cid,rule_id=rid,case_kind='full_synthetic_input_scenario',
        not_executed_against_calculator=True,source_basis=basis(r),branch_id=bid,
        external_context=context,given=deepcopy(given),expected=o))
for rid,r in rules.items():
    base=fixture(rid,r)
    if 'RU-ESC' in [s['source_id'] for s in r['sources']]:case(rid,'blocked-original',base,'unavailable');continue
    for b in contracts[rid]['branches']:
        g=deepcopy(base);bid=b['branch_id']
        if bid=='comorbid':g['comorbid_depression']=True
        if bid=='elderly':g['elderly_population']=True;g['age']=70
        if bid=='overlap':g.update(elderly_population=True,comorbid_depression=True,age=70)
        if bid=='at30':g['current_dose']=30
        if bid=='at60':g['current_dose']=60
        if bid=='other':
            if 'response' in g:g['response']='достаточный'
            elif 'current_dose' in g:g['current_dose']=10
        if bid=='keep':g['clinician_action']='keep'
        if bid.startswith('keep') and bid!='keep':g['clinician_action']='keep';g['current_dose']=int(bid[4:])
        if bid.startswith('increase-from'):g['current_dose']=int(bid[13:])
        if bid=='initial25':g['current_dose']=25
        if bid=='other-source-dose':g['current_dose']=75
        if bid=='ceiling':g['current_dose']=200
        if bid=='early':g['time_at_dose']=0.5
        if bid=='decrease':g['clinician_action']='decrease'
        if bid=='clinical_option':g['clinician_action']='not_chosen'
        if bid.startswith('selected') and rid=='fluvox-depression-start':g['source_start_choice']=int(bid[8:])
        if bid=='choice':g['source_start_choice']='not_chosen'
        if bid=='not_selected':g['example_selected']=False
        if bid in {'withdrawal','withdrawal_hold'}:g['current_withdrawal' if 'current_withdrawal' in g else 'withdrawal_severity']='непереносимые'
        if bid=='liver_caution':g['ALT_ratio']=3
        if bid=='repeat_tests':g['transaminases_rising']=True;g['ALT_ratio']=2
        if bid=='renal_caution':g['renal_state']='средняя'
        if bid=='organ_caution':g['renal']['value']=29
        if bid=='renal_reduction':g['renal_metric']['value']=30
        if bid in {'hepatic_reduction','joint_modifiers'}:g['hepatic']['category']='mild'
        if bid=='joint_modifiers':g['renal_metric']['value']=20
        if bid in {'ge60','30_60','15_30','lt15'}:g['clcr']={'ge60':60,'30_60':30,'15_30':15,'lt15':14.9}[bid]
        if 'frequency' in bid:g['frequency']=int(bid[-1])
        if bid.startswith('from'):g['current_dose']=int(bid.split('-')[0][4:])
        case(rid,'branch-'+bid,g,bid)
    # Every compulsory field has omission, explicit unknown and not_assessed expectations.
    for k in contracts[rid]['required_inputs']:
        for state in ('omitted','unknown','not_assessed'):
            g=deepcopy(base)
            if state=='omitted':g.pop(k,None)
            else:g[k]=state
            case(rid,k+'-'+state,g,typ='insufficient_data',missing_fields=[k],start_allowed=False)
    # Confirmed negative answers are preserved as false in the full positive base.
    case(rid,'confirmed-negative-fields',base,contracts[rid]['branches'][0]['branch_id'],confirmed_negatives=[k for k,v in base.items() if v is False])
    if 'medicines' in base:
        g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic medication requiring classification',status='current',interaction_class='unknown')]
        case(rid,'medicine-class-unknown',g,typ='insufficient_data',missing_fields=['medicines.M1.interaction_class'],start_allowed=False)
    for gate in contracts[rid]['source_gates']:
        for k in gate.get('exclusions',[]):
            if k in base:
                g=deepcopy(base);g[k]=True;case(rid,'exclude-'+gate['source_ref']+'-'+k,g,typ='not_applicable',reason_ids=[k])
        for k in gate.get('cautions',[]):
            if k in base:
                g=deepcopy(base);g[k]=True;case(rid,'caution-'+gate['source_ref']+'-'+k,g,typ='clinician_choice',reason_ids=[k],automatic_numeric_modifier=None)
        for k in gate.get('stop',[]):
            if k in base:
                g=deepcopy(base);g[k]=True;case(rid,'stop-'+gate['source_ref']+'-'+k,g,typ='source_stop_action',stop_medication=gate['source_ref'],automatic_next_stage=False)
        if 'medicines' in base:
            for interaction_class in gate.get('current_medicines_excluded',[])+gate.get('current_medicines_caution',[]):
                names={'strong_CYP1A2':'флувоксамин','moderate_CYP1A2':'пропранолол','maoi':'synthetic irreversible MAOI',
                    'pimozide':'пимозид','thioridazine':'тиоридазин','tizanidine':'тизанидин','ramelteon':'рамелтеон','terfenadine':'терфенадин','astemizole':'астемизол','cisapride':'цизаприд',
                    'opioid':'synthetic assessed opioid','CNS_depressant':'synthetic assessed CNS depressant'}
                g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn=names.get(interaction_class,'synthetic clinically identified '+interaction_class+' medication'),
                    status='current',interaction_class=interaction_class,classification_basis=dict(source_ref=gate['source_ref'],source_locator=gate['locator']))]
                if interaction_class=='maoi' and any(i['input_id']=='maoi_type' for i in r['inputs']):g['maoi_type']={'M1':'irreversible'}
                typ='not_applicable' if interaction_class in gate.get('current_medicines_excluded',[]) else 'clinician_choice'
                case(rid,'medicine-'+gate['source_ref']+'-'+interaction_class,g,typ=typ,reason_ids=[interaction_class],automatic_numeric_modifier=None)
    if r['identity']['mode'] in {'start','adjust','switch'}:
        for pred in contracts[rid]['typed_source_conditions']:
            g=deepcopy(base);k=pred['input'];value=pred['value']
            if pred['operator']=='category_equals':g[k]['category']=value
            else:g[k]=value
            action=pred['action'];typ='source_stop_action' if action.startswith('stop') else 'not_applicable' if action.startswith('not_applicable') else 'clinician_choice'
            case(rid,'condition-'+k+'-'+value,g,typ=typ,reason_ids=[k,value],automatic_numeric_modifier=None,source_condition=pred)
        if 'dialysis' in base:
            g=deepcopy(base);g['dialysis']=True;case(rid,'dialysis-separate',g,typ='clinician_choice',automatic_dialysis_calendar=None)
        if 'age' in base:
            g=deepcopy(base);g['age']=17;case(rid,'under18-no-adult-transfer',g,typ='not_applicable',reason_ids=['adult_indication_required'])
    if any(s['source_id']=='RU-AGO' for s in r['sources']) and rid!='ago-stop':
        for k in ('dementia','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'):
            g=deepcopy(base);g[k]=True
            if k=='dementia':g['elderly_population']=True
            case(rid,'ago-exclusion-'+k,g,typ='not_applicable',reason_ids=[k])
        for k in ('ALT_ratio','AST_ratio') if rid.startswith('ago') else ('alt_ratio_uln','ast_ratio_uln'):
            for value in (3,3.01):
                g=deepcopy(base);g[k]=value;case(rid,k+'-'+str(value),g,typ='clinician_choice' if value==3 else 'not_applicable',reason_ids=['transaminases'],automatic_numeric_modifier=None)
            g=deepcopy(base);g[k]=3.01
            case(rid,k+'-ongoing-above3',g,typ='source_stop_action',stop_medication='RU-AGO',automatic_next_stage=False,
                source_condition=dict(input=k,operator='>',value=3,source_ref='RU-AGO',source_locator='§4.4 с.4, прекращение лечения при АЛТ или АСТ >3 ВГН; регулярные пробы до нормы'))
        for age in ((65,66) if rid=='ago-gad-start' else (74,75)):
            allowed=age in (65,74); individual=allowed and not rid.startswith('switch')
            g=deepcopy(base);g['age']=age;case(rid,'age-'+str(age),g,typ=('exact' if individual else 'clinician_choice') if allowed else 'not_applicable',
                total_daily_dose_mg=25 if individual else None,dose_per_administration_mg=25 if individual else None,administrations_per_day=1 if individual else None,
                reason_ids=['indication_specific_age'],note='For generic switches this confirms B age predicate only; does not license an A/B calendar',reference_only=rid.startswith('switch'))
    if rid=='dulox-gad-start':
        for val in (29.99,30,30.01):
            g=deepcopy(base);g['renal_metric']['value']=val
            case(rid,'clcr-'+str(val),g,'usual' if val>=30 else None,typ='not_applicable' if val<30 else None,reason_ids=['renal_boundary'])
    if rid=='preg-renal-start':
        for val,bid in [(14.99,'lt15'),(15,'15_30'),(15.01,'15_30'),(29.99,'15_30'),(30,'30_60'),(30.01,'30_60'),(59.99,'30_60'),(60,'ge60'),(60.01,'ge60')]:
            g=deepcopy(base);g['clcr']=val;case(rid,'clcr-'+str(val),g,bid)
    if rid in {'venla-xr-gad-start','venla-xr-social-start'}:
        for val,bid in ((9.99,None),(10,'renal_reduction'),(30,'renal_reduction'),(30.01,'usual')):
            g=deepcopy(base);g['renal_metric']['value']=val;case(rid,'absolute-GFR-'+str(val),g,bid,typ='not_applicable' if bid is None else None)
        for val in (100,100.01):
            g=deepcopy(base);g['diastolic_BP']=val;g['hypertension']=True;case(rid,'diastolic-BP-'+str(val),g,typ='clinician_choice' if val==100 else 'source_stop_action',
                reason_ids=['blood_pressure_review' if val==100 else 'source_diastolic_BP_above100_stop'],automatic_next_stage=False)
    if any(i['input_id']=='maoi_type' for i in r['inputs']):
        m=r['logic']['maoi_history_contract'];sid=m['source_ref']
        for days in (13,14):
            g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic irreversible MAOI',status='stopped',interaction_class='maoi')]
            g['maoi_type']={'M1':'irreversible'};g['maoi_stopped_at']={'M1':f'2026-09-{25 if days==13 else 24}T09:00:00+03:00'}
            case(rid,'maoi-'+str(days)+'days',g,contracts[rid]['branches'][0]['branch_id'] if days==14 else None,typ='not_applicable' if days==13 else None,start_allowed=False if days==13 else True,
                interval_gate_satisfied=days==14,individual_dose_after_other_gates_only=True)
        for k in ('maoi_type','maoi_stopped_at'):
            for state in ('omitted','unknown','not_assessed'):
                g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic MAOI',status='stopped',interaction_class='maoi')]
                g['maoi_type']={'M1':'irreversible'};g['maoi_stopped_at']={'M1':'2026-09-24T09:00:00+03:00'}
                if state=='omitted':g.pop(k)
                else:g[k]={'M1':state}
                case(rid,k+'-M1-'+state,g,typ='insufficient_data',missing_fields=[k+'.M1'],start_allowed=False)
        g=deepcopy(base);g['medicines']=[dict(record_id='M1',inn='synthetic MAOI',status='current',interaction_class='maoi')];g['maoi_type']={'M1':'irreversible'}
        case(rid,'maoi-current',g,typ='not_applicable',start_allowed=False,reason_ids=['current_maoi_standard_branch'])
    for k,i in ((i['input_id'],i) for i in r['inputs'] if i['data_type']=='structured_renal'):
        g=deepcopy(base);g[k]=dict(metric='indexed_eGFR',value=45,unit='mL/min/1.73m2',method='laboratory',assessment='known')
        case(rid,'wrong-renal-metric-'+k,g,typ='insufficient_data',missing_fields=[k+'.'+i.get('required_metric','CLcr')],automatic_unit_equivalence=False)
        g=deepcopy(base);g[k]['unit']='mL/min/1.73m2'
        case(rid,'wrong-renal-unit-'+k,g,typ='insufficient_data',missing_fields=[k+'.unit'],automatic_unit_equivalence=False)
    for i in r['inputs']:
        k=i['input_id'];t=i['data_type']
        if t not in {'structured_renal','source_hepatic_category','structured_form'}:continue
        for field in schema['structures'][t]['fields']:
            for state in ('omitted','unknown','not_assessed'):
                g=deepcopy(base)
                if state=='omitted':g[k].pop(field,None)
                else:g[k][field]=state
                case(rid,'nested-'+k+'-'+field+'-'+state,g,typ='insufficient_data',missing_fields=[k+'.'+field],start_allowed=False)
        if t=='structured_form':
            g=deepcopy(base);g[k]['release']='prolonged' if g[k]['release']!='prolonged' else 'immediate'
            case(rid,'wrong-release-'+k,g,typ='form_not_feasible',reason_ids=[k+'.release'],automatic_form_substitution=False)

# Explicit timing cases for source-specific reversible clocks (complete inputs otherwise).
for rid in ('fluvox-depression-start','parox-panic-kr'):
    base=fixture(rid,rules[rid]);base['medicines']=[dict(record_id='M1',inn='synthetic reversible MAOI',status='stopped',interaction_class='maoi')];base['maoi_type']={'M1':'reversible_selective'}
    for timestamp,ok,label in [('2026-10-07T23:59:00+03:00',rid.startswith('fluvox'),'previous-calendar-day'),('2026-10-08T00:01:00+03:00',False,'same-day'),('2026-10-07T09:00:00+03:00',True,'exact24hours')]:
        g=deepcopy(base);g['maoi_stopped_at']={'M1':timestamp};case(rid,'reversible-'+label,g,contracts[rid]['branches'][0]['branch_id'] if ok else None,typ=None if ok else 'not_applicable',interval_gate_satisfied=ok,start_allowed=ok)

# Legacy cases remain partial fragments. Their representation never supplies missing full inputs.
for rid,bindings in schema['fragment_bindings'].items():
    declared={i['input_id']:i for i in rules[rid]['inputs']}
    for old,binding in bindings.items():
        target=binding['target']
        values=[c['given'][old] for c in rules[rid]['test_cases'] if old in c['given']]
        names={bool:'boolean',int:'integer',float:'number',str:'string',dict:'object',list:'list',type(None):'null'}
        binding['original_fragment_representation']=dict(data_types=sorted({names[type(v)] for v in values}),unit=binding.get('unit'),
            nature='Actual legacy given representation; not the complete target input type')
        if target.startswith('inputs.') and target[7:] in declared:
            i=declared[target[7:]];binding.update(data_type=i['data_type'],unit=i['unit'])
            binding['full_input_conversion']='Explicit source-compatible structure required; fragment alone is not a complete input, clinical category or medication-history clearance'

dump(O/'result_contracts.yaml',dict(schema_version='2.0',nature='Source-bound research expectations; no calculator implementation',rules=contracts))
dump(O/'input_contracts.yaml',schema)
(O/'full_scenarios.json').write_text(json.dumps(dict(nature='Prepared expected outputs, not executed calculator tests',clinical_validation='not_performed',cases=scenarios),ensure_ascii=False,indent=2),encoding='utf-8')
for rid,r in rules.items():
    r['logic']['parameter_refs']=[p['parameter_id'] for p in r['clinical_parameters']]
    r['sources']=[S[s['source_id']] for s in r['sources']]
    dump(R/'rules'/f'{rid}.yaml',r)
print(f'Authored {len(contracts)} result contracts, {len(scenarios)} full synthetic scenarios.')
