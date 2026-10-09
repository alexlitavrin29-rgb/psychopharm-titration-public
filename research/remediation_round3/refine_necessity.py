"""Apply explicit source/result decisions to the isolated candidate, not a dose evaluator."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent
def ry(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def rj(p): return json.loads(p.read_text(encoding='utf-8'))
def sy(p,x): p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def sj(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
rs={p.stem:ry(p) for p in (O/'rules').glob('*.yaml')}; C=ry(O/'result_contracts.yaml'); S=rj(O/'sources.json'); F=rj(O/'full_scenarios.json'); schema=ry(O/'input_contracts.yaml')
changes=[]; changed={}; additions={}
MON='reported_context'
def setpred(r,i,p,reason):
    old=deepcopy(i['requirement_predicate']); rid=r['rule_id']; k=i['input_id']
    if old==p:return
    i.update(requirement_predicate=p,required_for_individual_result=p['kind']=='always',input_role='required_selected_result_operand_or_source_gate' if p['kind']=='always' else p['kind'],necessity_reason=reason,required_when=reason,show_when=reason,action_if_unknown='insufficient_data only when exact predicate active; otherwise explicit not_assessed warning, no clinical clearance')
    changes.append(dict(rule_id=rid,input_id=k,old=old,new=p,reason=reason,source_refs=i['source_refs'],locator=i['source_locator'])); changed.setdefault(rid,{})[k]=p
def add(r,k,q,t,values,p,sid,loc,reason,default):
    i=dict(input_id=k,question_ru=q,data_type=t,unit=None,allowed_values=values,required_when=reason,show_when=reason,why_needed=reason,changes=['source_action_or_applicability'],unknown_allowed=True,action_if_unknown='insufficient_data when active; explicit not_assessed when inactive',source_refs=[sid],input_role='required_selected_result_operand_or_source_gate' if p['kind']=='always' else p['kind'],source_locator=loc,required_for_individual_result=p['kind']=='always',requirement_predicate=p,necessity_reason=reason,fact_origin='explicit physician fact for this calculation; no inference from other negative answers')
    r['inputs'].append(i); additions.setdefault(r['rule_id'],{})[k]=default
    changes.append(dict(rule_id=r['rule_id'],input_id=k,old=None,new=p,reason=reason,source_refs=[sid],locator=loc))
for rid,r in rs.items():
    mode=r['identity']['mode']; ins={i['input_id']:i for i in r['inputs']}
    # Context fields may change a warning or an explicitly reported caution; unknown does not assert their absence.
    monitor=set()
    if rid.startswith('ago-') and rid!='ago-stop':monitor={'mania','suicide_risk','ect','alcohol_use'}
    if rid.startswith('dulox-') and mode in {'start','adjust'}:
        monitor={'mania','suicide_risk','bleeding_risk','hyponatremia_risk','diabetes','seizure_state'}
        if mode=='start':monitor.add('akathisia')
    if rid=='fluvox-depression-start':monitor={'mania','akathisia','bleeding_risk','suicide_risk','diabetes','glaucoma','ect'}
    if rid=='parox-panic-kr':
        monitor={'mania','suicide_risk','akathisia','diabetes','glaucoma','bleeding_risk','qt_risk','ect','response','tolerability','current_dose','time_at_dose'}
    if rid.startswith('venla-xr-') and mode=='start':
        monitor={'recent_infarction','unstable_angina','heart_failure','coronary_disease','ecg_change','electrolyte_imbalance','hypertension','tachycardia','seizure_history','glaucoma','mania','bleeding_risk','low_body_mass','urinary_impairment','low_blood_pressure','diabetes','recent_stroke','hyponatremia_risk','ect','hypercholesterolemia','alcohol_use','suicide_risk'}
    if rid.startswith('preg-') and mode in {'start','adjust'}:monitor={'substance_use','suicide_risk','heart_failure','diabetes_weight_gain'}
    for k in monitor & set(ins):
        reason='Сообщённый контекст/наблюдение или данные будущего этапа: не операнд выбранной начальной дозы. Сохранить источниковое предупреждение и результат при известном положительном ответе; неизвестность не даёт полного клинического допуска.'
        setpred(r,ins[k],dict(kind=MON),reason)
    ongoing=[]
    if mode=='start':
        if rid.startswith(('ago-','esc-','fluvox-','preg-','ser-')):ongoing=['mania_symptoms','arrhythmia_signs','serotonin_syndrome_signs','liver_injury_signs','transaminases_rising','angioedema','severe_skin_reaction']
        if rid.startswith('venla-xr'):ongoing=['diastolic_BP']
    for k in set(ongoing)&set(ins):
        setpred(r,ins[k],dict(kind='ongoing_selected_drug'), 'Обязательно при уже начатой терапии данным препаратом (treatment_phase=ongoing). Выбор start/selected_mode означает первую дозу; положительный сообщённый признак до первой дозы требует решения врача, а не прекращения ещё не начатого препарата.')
    if rid.startswith('ago-') and rid!='ago-stop' and 'dementia' in ins:
        setpred(r,ins['dementia'],dict(kind='field_true',field='elderly_population'), 'Обязательно если врач отнёс пациента к пожилой популяции; источник запрещает применение у пожилых с деменцией. Возрастная граница пожилой популяции не выдумана.')
    for i in r['inputs']:
        if i['data_type']=='structured_renal':
            i.update(question_ru=f"Подтверждённое врачом значение {i['required_metric']} в мл/мин? Индексированная СКФ не подходит; при отсутствии применимой оценки выберите «неизвестно».",metric_origin='fixed_source_metadata',unit_origin='fixed_source_metadata',method_required_for_selected_result=False,counted_independent_facts=['clinician_confirmed_source_renal_value'])
            changes.append(dict(rule_id=rid,input_id=i['input_id'],change='source-bound numeric entry, metric/unit fixed by question; method optional provenance',old_count=3,new_count=1,source_refs=i['source_refs'],locator=i['source_locator']))
    if rid.startswith('preg-') and mode in {'start','adjust'}:
        add(r,'misuse_risk_assessment','Оценка риска неправильного применения, злоупотребления и зависимости по §4.4 завершена для выбранного режима?', 'enum',['врач допускает выбранный режим','требуется отдельное решение врача'],dict(kind='always'),'RU-PREG','§4.4 с.8–9','Источниковая оценка конкретного риска до назначения. Не подтверждает остальные противопоказания; исходные сведения не являются скрытыми операндами дозы. Неизвестная/незавершённая оценка блокирует индивидуальный результат.','врач допускает выбранный режим')
        add(r,'reproductive_population','Пациентка относится к женщинам репродуктивного возраста?', 'boolean',[],dict(kind='always'),'RU-PREG','§4.4 с.9; §4.6 с.12','Отдельный триггер требования контрацепции; не выводить из pregnancy=false или возраста без данных.',False)
        add(r,'effective_contraception','Используется эффективная контрацепция?', 'boolean',[],dict(kind='field_true',field='reproductive_population'),'RU-PREG','§4.6 с.12','Обязательно при reproductive_population=true; отрицательный/неизвестный ответ не разрешает обычный индивидуальный старт.',False)
    if rid=='fluvox-depression-start':
        add(r,'serotonin_syndrome_signs','Во время терапии появились признаки серотонинового синдрома/ЗНС?', 'boolean',[],dict(kind='ongoing_selected_drug'),'RU-FLUVOX','§4.4 с.5','При подтверждённых признаках прекратить флувоксамин и начать симптоматическое лечение; обязателен на текущей терапии.',False)
    if rid.startswith('venla-xr-') and mode=='start':
        add(r,'current_allergic_reaction','Во время терапии появилась сыпь, крапивница или другая аллергическая реакция?', 'boolean',[],dict(kind='ongoing_selected_drug'),'RU-VENLA-XR','§4.4 с.13','Подтверждённая реакция во время терапии требует прекращения венлафаксина; не делить с аллергией в анамнезе.',False)
    if rid=='phen-taper-limit':
        add(r,'unusual_reactions','Возникли необычные реакции, перечисленные в §4.4 (агрессивность, возбуждение, страх, суицидальные мысли, галлюцинации, усиление судорог, нарушения сна)?', 'boolean',[],dict(kind='always'),'RU-PHEN','§4.4 с.4','Один источниковый синдром с одним действием: лечение прекратить; способ прекращения определяет врач, числовую экстренную схему не придумывать.',False)

schema['structures']['structured_renal']['optional_provenance_fields']=['method']
schema['structures']['structured_renal']['fixed_metadata_fields']=['metric','unit']
schema['structures']['structured_renal']['entry_policy']='Numeric physician-confirmed value for named source metric and fixed mL/min unit; method is optional provenance, not a second/third patient question. Wrong/indexed metric or wrong unit must still be rejected.'
schema['external_context']['treatment_phase']['origin']='start + selected_mode explicitly means first administration of this product; ongoing is a separately selected significant branch, counted once; no inference of B phase from A'
for rid,r in rs.items():
    con=C['rules'][rid]
    con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='always']
    con['input_requirements']={i['input_id']:i['requirement_predicate'] for i in r['inputs']}
    con['monitoring_context_fields']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']==MON]
    con['round3_necessity_scope']='Selected source dose/action; not full clinical admission. Explicit phase predicates and unassessed context retained.'
    for b in con['branches']:
        if b['expected_output']['result_type'] in {'exact','selected_source_example'}:b['expected_output']['clinical_clearance']=False
    r['output']['branches']=deepcopy(con['branches'])
    r['logic']['input_necessity_policy_ref']='remediation_round3/necessity_decisions.json#'+rid
baselines={rid:[c for c in F['cases'] if c['rule_id']==rid and c['branch_id'] and c['expected']['result_type'] in {'exact','selected_source_example','clinician_choice','form_not_feasible'}] for rid in rs}
def active(i,c):
    p=i['requirement_predicate']; k=p['kind'];g=c['given'];ctx=c['external_context']
    if k=='always':return True
    if k in {'increase','action_choice'}:return g.get('clinician_action','not_chosen') in p['actions']
    if k=='field_true':return g.get(p['field']) is True
    if k=='ongoing_selected_drug':return ctx.get('treatment_phase')=='ongoing'
    if k=='ecg_if_cad':return g.get('coronary_disease') is True
    if k=='correction_if_electrolytes':return g.get('electrolyte_disturbance') is True
    return False
revised=[]
for c in F['cases']:
    rid=c['rule_id'];r=rs[rid]; ins={i['input_id']:i for i in r['inputs']};g=c['given'];e=c['expected'];ctx=c['external_context']
    for k,v in additions.get(rid,{}).items():g[k]=deepcopy(v)
    if e['result_type']=='source_stop_action' and r['identity']['mode']=='start':ctx['treatment_phase']='ongoing'
    if c['branch_id']=='repeat_tests' and 'RU-AGO' in [s['source_id'] for s in r['sources']]:ctx['treatment_phase']='ongoing'
    if e['result_type']=='insufficient_data':
        inactive={k for k,p in changed.get(rid,{}).items() if not active(ins[k],c)}
        oldmissing=e['missing_fields'][:]
        remaining=[k for k in oldmissing if k.split('.')[0] not in inactive and not(k.endswith('.method') and ins[k.split('.')[0]]['data_type']=='structured_renal')]
        if remaining!=oldmissing:
            if not remaining:
                pool=baselines[rid]
                # Recover prepared parent branch by unchanged source operands; never calculate a new medical dose here.
                nearest=max(pool,key=lambda x:sum(x['given'].get(k)==v for k,v in g.items() if k not in inactive and k not in additions.get(rid,{})))
                c['expected']=e=deepcopy(nearest['expected'])
                e['missing_fields']=[]
            else:e['missing_fields']=remaining
            revised.append(dict(case_id=c['case_id'],old_missing=oldmissing,new_missing=remaining,reason='inactive result-specific input or optional renal method; existing prepared parent expected reused, primary anchor review separate'))
    if e['result_type'] in {'exact','selected_source_example'}:
        e['clinical_clearance']=False
        e['unassessed_context']=sorted({i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {MON,'ongoing_selected_drug'} and (i['input_id'] not in g or g[i['input_id']] in (None,'unknown','not_assessed','не исследовано','неизвестно') or not active(i,c))})
    if c['branch_id']:
        b=next(b for b in C['rules'][rid]['branches'] if b['branch_id']==c['branch_id'])
        if b['expected_output']['result_type'] in {'exact','selected_source_example'}:e['clinical_clearance']=False
for rid,newfields in additions.items():
    base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id'])
    for k in newfields:
        i=next(i for i in rs[rid]['inputs'] if i['input_id']==k)
        for state in ['positive','omitted','unknown','negative']:
            c=deepcopy(base);c['case_id']=rid+'--r3-'+k+'-'+state;c['branch_id']=None
            if i['requirement_predicate']['kind']=='ongoing_selected_drug':c['external_context']['treatment_phase']='ongoing'
            if k=='effective_contraception':c['given']['reproductive_population']=True
            if state=='omitted':c['given'].pop(k)
            elif state=='unknown':c['given'][k]='unknown'
            else:c['given'][k]=(True if state=='positive' else False) if i['data_type']=='boolean' else ('требуется отдельное решение врача' if state=='positive' else 'врач допускает выбранный режим')
            e=c['expected']
            if state in {'omitted','unknown'}:
                e.update(result_type='insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[k])
            elif (state=='positive' and k not in {'reproductive_population','effective_contraception'}) or (state=='negative' and k=='effective_contraception'):
                stop=k in {'serotonin_syndrome_signs','current_allergic_reaction','unusual_reactions'}
                e.update(result_type='source_stop_action' if stop else 'clinician_choice',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],clinical_clearance=False)
                e['source_condition']=dict(input=k,source_ref=i['source_refs'][0],source_locator=i['source_locator'])
                if stop:
                    e['stop_medication']=i['source_refs'][0]
                    e['source_actions']=[dict(action='discontinue_selected_medication',source_ref=i['source_refs'][0],source_locator=i['source_locator'])]
                    if k=='serotonin_syndrome_signs':e['source_actions'].append(dict(action='start_symptomatic_treatment_by_clinician',source_ref='RU-FLUVOX',source_locator=i['source_locator']))
            elif k=='reproductive_population' and state=='positive':
                e.update(result_type='clinician_choice',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],clinical_clearance=False)
            F['cases'].append(c)
    # Cases above are source-reviewed expected specifications, not executed treatment decisions.
for rid,r in rs.items():sy(O/'rules'/ (rid+'.yaml'),r)
sy(O/'result_contracts.yaml',C);sj(O/'full_scenarios.json',F);sy(O/'input_contracts.yaml',schema)
sj(O/'necessity_decisions.json',dict(scope='Explicit reviewed source/result changes; unchanged rows are not automatically certified minimal',decisions=changes))
sj(O/'scenario_revisions.json',revised)
print(len(changes),'necessity/schema decisions;',len(revised),'prepared expectations revised;',len(F['cases']),'prepared full scenarios; no calculator executed.')
