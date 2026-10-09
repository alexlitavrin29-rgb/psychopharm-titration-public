"""Exact NR02–NR04 scope corrections; apply after the reviewed freeze is preserved."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'result_scope_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'))
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
changes=[];new=[];phase_changes=[]

def change(rid,key,pred,reason,role):
    r=R[rid];i=next(i for i in r['inputs'] if i['input_id']==key);old=deepcopy(i['requirement_predicate'])
    i.update(requirement_predicate=pred,required_for_individual_result=False,input_role=role,why_needed=reason,necessity_reason=reason,required_when='Exact predicate; otherwise only if explicitly supplied',show_when='Exact predicate; otherwise only if explicitly supplied',action_if_unknown='Named unassessed context; no normality or clinical clearance inferred')
    con=C['rules'][rid];con['input_requirements'][key]=pred
    con['required_inputs']=[x['input_id'] for x in r['inputs'] if x['requirement_predicate']['kind']=='always']
    if key not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(key)
    record=dict(rule_id=rid,input_id=key,old=old,new=pred,reason=reason,source_refs=i['source_refs'],locator=i['source_locator'])
    changes.append(record);D['decisions'].append(deepcopy(record))

change('ser-adult-adjust','adherence',dict(kind='indication_action_choice',diagnoses=['F41.0'],actions=['not_chosen','unknown','not_assessed']),
       'RU-PANIC физ.с.29–30: переоценка приверженности при недостаточном эффекте относится к паническому расстройству, когда выбирается клиническое действие. RU-PHOB физ.с.29 описывает инструмент оценки и не задаёт ту же обязательную предпосылку для F40.1. Для F40.1 сообщённые сведения сохраняются, отсутствие/unknown — not_assessed. Без выбранного действия повышение не выполняется; коэффициент приверженности отсутствует.',
       'indication_specific_clinical_reassessment')
base=next(c for c in F['cases'] if c['rule_id']=='ser-adult-adjust' and c['given'].get('clinician_action')=='not_chosen' and c['expected']['result_type']=='clinician_choice' and c['given'].get('current_dose')==100)
for val in ['omitted','unknown']:
    n=deepcopy(base);n['case_id']='ser-adult-adjust--audit-final-social-adherence-'+val;n['branch_id']=None;n['external_context']['diagnosis']='F40.1'
    if val=='omitted':n['given'].pop('adherence',None)
    else:n['given']['adherence']='unknown'
    n['expected']['unassessed_context']=sorted(set(n['expected'].get('unassessed_context',[]))|{'adherence'})
    n['expected']['clinical_clearance']=False
    n['expected']['selected_action']=None;n['expected']['total_daily_dose_mg']=None;n['expected']['schedule']=[]
    n['fixture_scope']='F40.1 clinical action not chosen; no automatic increase and no mandatory transfer of the F41.0 compliance prerequisite.'
    new.append(n)

planning=['current_dose','duration','last_dose_time','withdrawal_symptoms','target_applicability']
for rid in ['switch-esc-ser','switch-ser-esc']:
    for key in planning:
        change(rid,key,dict(kind='reported_context'),
               'Для ограниченного результата «в проверенных российских источниках не найден полный календарь этой пары» это не операнд. Данные нужны для отдельного индивидуального плана/оценки, который здесь не выдаётся. Сообщённое значение учитывается и считается; отсутствие/unknown остаётся not_assessed. Последняя доза сама по себе не создаёт опубликованный меж-СИОЗС интервал. Полный календарь, день старта B, перекрытие и клинический допуск не разрешаются.',
               'reported_context_for_separate_individual_plan')
    for key in ['from_form','to_form']:
        i=next(i for i in R[rid]['inputs'] if i['input_id']==key)
        i['why_needed']=i['necessity_reason']='Идентифицирует конкретный российский профиль продукта, формы и редакции A/B, для которого проверено отсутствие полного парного календаря. Это источниковый выбор, включённый в начальные сведения; он не подтверждает клиническую применимость B или исполнимость индивидуального плана. Иная/неизвестная редакция не получает утверждение о проверенном полном содержании этой пары.'
    C['rules'][rid]['source_gap_scope']=dict(full_pair_calendar=None,automatic_direct_switch=False,next_drug_start_day=None,patient_target_applicability='not_assessed unless separately reported; never clearance',planning_data='Reported only for this bounded source gap; current source actions retain their own known actor/phase requirements')
    for c in F['cases']:
        if c['rule_id']!=rid:continue
        e=c['expected'];missing=e.get('missing_fields',[])
        removed=set(missing)&set(planning)
        if removed:
            remain=[k for k in missing if k not in removed]
            if remain:e['missing_fields']=remain
            else:
                e=deepcopy(C['rules'][rid]['branches'][0]['expected_output']);e['source_gap_scope']=C['rules'][rid]['source_gap_scope'];c['expected']=e
        e['clinical_clearance']=False
        e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in planning if c['given'].get(k) in (None,'unknown','not_assessed','неизвестно')})
        e['confirmed_negatives']=[k for k in e.get('confirmed_negatives',[]) if k not in e['unassessed_context']]
        # Preserve the explicit synthetic witness for a formerly consumed ACTUAL
        # dose. This now becomes a separately counted actor-phase fact.
        if e.get('stop_medication')==next(i['source_refs'][0] for i in R[rid]['inputs'] if i['input_id']=='from_form') or any(a.get('medication_role')=='selected_or_A' for a in e.get('source_actions',[])):
            if c['external_context'].get('treatment_phase')=='selected_mode':
                v=c['given'].get('current_dose');assert type(v) in (int,float) and v>0,c['case_id']
                c['external_context']['treatment_phase']='ongoing';phase_changes.append(c['case_id'])

for rid,keys in [('preg-taper-limit',['form','current_withdrawal']),('phen-taper-limit',['form'])]:
    for key in keys:
        change(rid,key,dict(kind='reported_source_information'),
               'Только качественная справка по выбранному взрослому источниковому профилю: индивидуальная доза/ступени/срок не вычисляются. Фактическая форма и сообщённые симптомы сохраняются, но неизвестная форма/симптомы не препятствуют показу условной источниковой справки. Они остаются not_assessed; применимость продукта пациенту не подтверждается. Для исполнения индивидуального плана или источникового действия идентичность фактического препарата и текущая фаза проверяются отдельно.',
               'reported_source_information')
    con=C['rules'][rid];con['reference_product_scope']='The initial selection identifies the source product profile/version, not the actual patient product. Unknown actual form remains not_assessed; reference does not authorize an individual dose/duration/calendar or a current medication change.'
    for b in con['branches']:
        if b['branch_id']=='source_limit':b['when']='Selected source product profile; bounded adult-source reference, no individual dose/calendar; known urgent events have their own actor/phase contract'
    for c in F['cases']:
        if c['rule_id']!=rid:continue
        e=c['expected'];obsolete=set(e.get('missing_fields',[]))&set(keys)
        if obsolete:
            remain=[k for k in e['missing_fields'] if k not in obsolete]
            if remain:e['missing_fields']=remain
            else:
                e=deepcopy(con['branches'][0]['expected_output']);c['expected']=e
        e['clinical_clearance']=False;e['individual_duration_weeks']=None;e['individual_taper_schedule']=None
        e['product_reference_applicability']='not_assessed' if not isinstance(c['given'].get('form'),dict) else 'identified_source_profile_only; no clinical clearance'
        e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in keys if c['given'].get(k) in (None,'unknown','not_assessed')})
        e['confirmed_negatives']=[k for k in e.get('confirmed_negatives',[]) if k not in e['unassessed_context']]
    base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='source_limit')
    for state in ['omitted','unknown']:
        n=deepcopy(base);n['case_id']=rid+'--audit-final-bounded-source-reference-'+state
        fields={i['input_id'] for i in R[rid]['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_source_information','reported_current_event'}}
        for k in fields:
            if state=='omitted':n['given'].pop(k,None)
            else:n['given'][k]='unknown'
        n['expected']['product_reference_applicability']='not_assessed';n['expected']['population_applicability']='not_assessed'
        n['expected']['unassessed_context']=sorted(fields)
        n['expected']['confirmed_negatives']=[k for k,v in n['given'].items() if v is False]
        n['fixture_scope']='Selected versioned adult source profile only; actual product/population/symptoms explicitly unassessed. No individual duration/calendar, no current-medication action inferred.'
        new.append(n)

F['cases']+=new
graph=O/'build_graphs.py';t=graph.read_text(encoding='utf-8')
t=t.replace("if k in {'increase','action_choice'}:return g.get('clinician_action','not_chosen') in p['actions']", "if k=='indication_action_choice':return (ctx.get('diagnosis') in p['diagnoses'] and g.get('clinician_action','not_chosen') in p['actions']) or i['input_id'] in g\n    if k in {'increase','action_choice'}:return g.get('clinician_action','not_chosen') in p['actions']")
t=t.replace("if k in {'increase','action_choice'}:return ['clinician_action']", "if k in {'increase','action_choice','indication_action_choice'}:return ['clinician_action']")
t=t.replace("inputs=[i for i in r['inputs'] if i['data_type']!='structured_form']", "if rid in {'preg-taper-limit','phen-taper-limit'}:initial=['diagnosis','mode','selected_source_product_profile_version']\n    inputs=[i for i in r['inputs'] if i['data_type']!='structured_form' or i['requirement_predicate']['kind']!='always']")
t=t.replace("{'reported_context','ongoing_selected_drug','target_ongoing','reported_current_event','reported_source_information'}", "{'reported_context','ongoing_selected_drug','target_ongoing','reported_current_event','reported_source_information','indication_action_choice'}")
graph.write_text(t,encoding='utf-8')
p=O/'verify_contracts.py';t=p.read_text(encoding='utf-8')
needle="if pred['kind'] in {'increase','action_choice'} and g.get('clinician_action','not_chosen') in pred.get('actions',[]): applicable.add(key)"
assert needle in t
t=t.replace(needle,needle+"\n            if pred['kind']=='indication_action_choice' and context.get('diagnosis') in pred['diagnoses'] and g.get('clinician_action','not_chosen') in pred['actions']: applicable.add(key)")
p.write_text(t,encoding='utf-8')
schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
schema['requirement_predicates']['indication_action_choice']='Mandatory only for the listed physician-selected diagnoses and action-choice states. For other diagnoses, explicitly supplied information is consumed/counted; absence or unknown remains unassessed. No mandatory prerequisite is borrowed from another indication.'
(O/'input_contracts.yaml').write_text(yaml.safe_dump(schema,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
policy=yaml.safe_load((O/'necessity_policy.yaml').read_text(encoding='utf-8'))
policy['definitions']['indication_action_choice']=schema['requirement_predicates']['indication_action_choice']
(O/'necessity_policy.yaml').write_text(yaml.safe_dump(policy,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for rid,r in R.items():
    r['output']['branches']=C['rules'][rid]['branches']
    (O/'rules'/(rid+'.yaml')).write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for n,x in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D)]:
    (O/n).write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110) if n.endswith('.yaml') else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'result_scope_repairs.json').write_text(json.dumps(dict(changes=changes,new_cases=[c['case_id'] for c in new],separately_counted_actual_phase_witnesses=phase_changes,independent_acceptance='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Result-specific necessity corrections',len(changes),'new explicit scenarios',len(new))
