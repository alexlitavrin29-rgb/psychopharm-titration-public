"""Bounded source references do not require an individual-treatment admission form."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'qualitative_result_scope_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'));rows=[];new=[]
rids=['switch-esc-ago','switch-parox-ago','switch-ser-ago','switch-esc-ser','switch-ser-esc','preg-taper-limit','phen-taper-limit']
for rid in rids:
    p=O/'rules'/(rid+'.yaml');r=yaml.safe_load(p.read_text(encoding='utf-8'));con=C['rules'][rid]
    assert all(not b['expected_output']['schedule'] and b['expected_output']['total_daily_dose_mg'] is None for b in con['branches']),rid
    forms={i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form' and i['requirement_predicate']['kind']=='always'}
    urgent={p['input'] for p in con.get('urgent_stop_predicates',[])}|{k for gate in con['source_gates'] for k in gate.get('stop',[])}|{p['input'] for p in con.get('typed_source_conditions',[]) if p.get('action','').startswith('stop')}
    changed=set()
    for i in r['inputs']:
        key=i['input_id'];kind=i['requirement_predicate']['kind']
        if key in forms or kind in {'maoi_record','stopped_maoi_record','outside_cessation_scope','reported_context','reported_current_event','reported_source_information'}:continue
        pred=dict(kind='reported_current_event' if key in urgent or kind in {'ongoing_selected_drug','target_ongoing'} else 'reported_source_information')
        reason='Для этого ограниченного источникового результата индивидуальная доза/календарь/разрешение старта не выдаются. Пациентское сведение не является обязательной предпосылкой чтения выбранной российской инструкции. Явно сообщённые значения и источниковые ограничения сохраняются и считаются; отсутствие/unknown остаётся not_assessed. Сообщённое текущее условие источникового прекращения получает приоритет только при подтверждённых идентичности фактического препарата и фазе соответствующего A/B. Для отдельного индивидуального дозового/клинического действия нужен его собственный контракт входов.'
        old=deepcopy(i['requirement_predicate']);i.update(requirement_predicate=pred,required_for_individual_result=False,input_role=pred['kind'],required_when='Only when explicitly supplied for this bounded source result',show_when='Only when explicitly supplied',why_needed=reason,necessity_reason=reason,action_if_unknown='Named unassessed context; no clinical clearance or automatic action')
        if key=='current_dose':
            i.update(fact_semantics='reported_course_dose_without_current_use_confirmation',question_ru='Сообщённая исходная/последняя суточная доза курса для контекста (мг/сут)? Она не подтверждает текущую фазу приёма.',fact_origin='Reported course-dose context only; ongoing current source action requires a separately supplied counted phase.')
        con['input_requirements'][key]=pred
        if key not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(key)
        record=dict(rule_id=rid,input_id=key,old=old,new=pred,reason=reason,source_refs=i['source_refs'],locator=i['source_locator']);rows.append(record);D['decisions'].append(deepcopy(record));changed.add(key)
    con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='always']
    con['qualitative_result_scope']='Versioned product-source reference/gap only; no patient dose, individual duration, target permission, overlap permission or clinical admission. Supplied source conditions remain visible and source-specific current actions need their own known actor/phase.'
    for c in F['cases']:
        if c['rule_id']!=rid:continue
        e=c['expected'];g=c['given'];oldmissing=e.get('missing_fields',[])
        removed=[k for k in oldmissing if k.split('.')[0] in changed]
        if removed:
            remain=[k for k in oldmissing if k not in removed]
            if remain:e['missing_fields']=remain
            else:
                e=deepcopy(con['branches'][0]['expected_output']);c['expected']=e
                e['unassessed_context']=sorted({k.split('.')[0] for k in removed})
        e['clinical_clearance']=False
        optional={i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_current_event','reported_source_information'}}
        e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in optional if g.get(k) in (None,'unknown','not_assessed','неизвестно','не исследовано')})
        e['confirmed_negatives']=[k for k in e.get('confirmed_negatives',[]) if k in g and g[k] is False]
        owner=next((i['source_refs'][0] for i in r['inputs'] if i['input_id']=='from_form'),None)
        if owner and (e.get('stop_medication')==owner or any(a.get('medication_role')=='selected_or_A' for a in e.get('source_actions',[]))) and c['external_context'].get('treatment_phase')=='selected_mode':
            dose=g.get('current_dose');assert type(dose) in (int,float) and dose>0,c['case_id'];c['external_context']['treatment_phase']='ongoing'
        if rid in {'preg-taper-limit','phen-taper-limit'}:e.update(individual_duration_weeks=None,individual_taper_schedule=None)
    base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']==con['branches'][0]['branch_id'])
    n=deepcopy(base);n['case_id']=rid+'--audit-final-reference-without-patient-screen';n['given']={k:v for k,v in n['given'].items() if k in forms};n['external_context'].pop('target_treatment_phase',None)
    n['expected'].update(unassessed_context=sorted(i['input_id'] for i in r['inputs'] if i['input_id'] not in forms),confirmed_negatives=[],clinical_clearance=False,source_actions=[])
    n['expected'].pop('stop_medication',None)
    if rid in {'preg-taper-limit','phen-taper-limit'}:n['expected'].update(population_applicability='not_assessed',product_reference_applicability='not_assessed',individual_duration_weeks=None,individual_taper_schedule=None)
    n['fixture_scope']='Bounded selected source-profile reference with no patient preflight or implicit negatives. Not an individual treatment action; reported urgent conditions have separate source-bound actor/phase outcomes.';new.append(n)
    r['output']['branches']=con['branches'];p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
F['cases']+=new
for n,x in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D)]:
    (O/n).write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110) if n.endswith('.yaml') else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'qualitative_result_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],scope='No numeric/action contract demoted. Seven source-reference/gap cards have result-specific requirements; known source events are not ignored.',independent_acceptance='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Bounded reference requirements aligned',len(rows),'new sparse references',len(new))
