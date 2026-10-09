"""Make five non-numerical adult taper references explicitly conditional."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'taper_reference_scope_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'));rows=[];new=[]
rids=['dulox-taper-limit','esc-taper-limit','fluvox-taper-limit','ser-taper-limit','venla-xr-taper-limit']
for rid in rids:
 p=O/'rules'/(rid+'.yaml');r=yaml.safe_load(p.read_text(encoding='utf-8'));con=C['rules'][rid];changed=set()
 for i in r['inputs']:
  k=i['input_id']
  if i['requirement_predicate']['kind']!='always' or k=='form':continue
  pred=dict(kind='reported_source_information' if k=='age' else 'reported_current_event')
  reason='Ограниченная взрослая источниковая справка не задаёт индивидуальную схему/срок и не устанавливает отсутствие текущего события. Возраст/событие — контекст при сообщении, counted; отсутствие/unknown явно unassessed. Известный симптом выбирает только своё опубликованное условие. Срочное источниковое действие требует фактического препарата и собственной подтверждённой фазы; справка не клинический допуск.'
  old=deepcopy(i['requirement_predicate']);i.update(requirement_predicate=pred,required_for_individual_result=False,input_role=pred['kind'],necessity_reason=reason,why_needed=reason,required_when='Only when explicitly supplied',show_when='Only when explicitly supplied');con['input_requirements'][k]=pred
  if k not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(k)
  rec=dict(rule_id=rid,input_id=k,old=old,new=pred,source_refs=i['source_refs'],locator=i['source_locator'],reason=reason);rows.append(rec);D['decisions'].append(deepcopy(rec));changed.add(k)
 con['required_inputs']=['form'];con['qualitative_result_scope']='Conditional adult source reference only; no individual taper duration/schedule, child extrapolation, clinical admission or assertion that unreported urgent/withdrawal events are absent.'
 for b in con['branches']:
  b['expected_output'].update(adult_source_reference_only=True,individual_duration_weeks=None,individual_taper_schedule=None,clinical_clearance=False)
  if b['branch_id']=='source_limit':b['when']='Selected versioned adult-source reference; current events unassessed unless supplied; no individualized taper or absence-of-urgent-event assertion'
 for c in F['cases']:
  if c['rule_id']!=rid:continue
  e=c['expected'];g=c['given'];missing=e.get('missing_fields',[]);removed=[k for k in missing if k.split('.')[0] in changed]
  if removed:
   left=[k for k in missing if k not in removed]
   if left:e['missing_fields']=left
   else:c['expected']=e=deepcopy(con['branches'][0]['expected_output'])
  e.update(adult_source_reference_only=True,individual_duration_weeks=None,individual_taper_schedule=None,clinical_clearance=False)
  age=g.get('age');e['population_applicability']='adult_source_population' if type(age) in (int,float) and age>=18 else 'nonadult_plan_not_established' if type(age) in (int,float) else 'not_assessed'
  e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in changed if g.get(k) in (None,'unknown','not_assessed')})
 base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='source_limit');n=deepcopy(base);n['case_id']=rid+'--audit-final-conditional-adult-reference';n['given']={'form':n['given']['form']};n['expected']=deepcopy(con['branches'][0]['expected_output']);n['expected'].update(population_applicability='not_assessed',unassessed_context=sorted(i['input_id'] for i in r['inputs'] if i['input_id']!='form'),confirmed_negatives=[]);n['external_context']['treatment_phase']='selected_mode';n['fixture_scope']=con['qualitative_result_scope'];new.append(n)
 r['output']['branches']=con['branches'];p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
F['cases']+=new
stale=[]
for c in F['cases']:
 e=c['expected'];g=c['given'];invalid=[k for k in e.get('confirmed_negatives',[]) if k not in g or g[k] is not False]
 if invalid:
  stale.append(dict(case_id=c['case_id'],removed_invalid_negatives=invalid));e['confirmed_negatives']=[k for k in e['confirmed_negatives'] if k not in invalid];e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in invalid if k not in g or g[k] in (None,'unknown','not_assessed')})
for name,data in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D)]:
 (O/name).write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=110) if name.endswith('.yaml') else json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'taper_reference_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],stale_negative_repairs=stale,medical_values_changed=False,independent_acceptance='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Conditional taper scope changes',len(rows),'new references',len(new),'stale negative cases',len(stale))
