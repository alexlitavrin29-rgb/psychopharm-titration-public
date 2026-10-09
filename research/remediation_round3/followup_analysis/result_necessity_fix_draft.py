"""Prepared source/result corrections; apply after the frozen recheck2 completes."""
from pathlib import Path
from copy import deepcopy
import json,yaml

O=Path(__file__).resolve().parent.parent
assert not (O/'final_necessity_repairs.json').exists(), 'One-use correction; reviewed versions are preserved'
def read(n):
 p=O/n;return yaml.safe_load(p.read_text(encoding='utf-8')) if p.suffix=='.yaml' else json.loads(p.read_text(encoding='utf-8'))
def save(n,x):
 p=O/n;p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110) if p.suffix=='.yaml' else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
C=read('result_contracts.yaml');F=read('full_scenarios.json');D=read('necessity_decisions.json');schema=read('input_contracts.yaml')
rs={rid:read('rules/'+rid+'.yaml') for rid in ['parox-taper-example','preg-taper-limit','phen-taper-limit']};changes=[]
def pred(rid,k,p,reason):
 i=next(i for i in rs[rid]['inputs'] if i['input_id']==k);old=deepcopy(i['requirement_predicate'])
 i.update(requirement_predicate=p,required_for_individual_result=p['kind']=='always',input_role=p['kind'],required_when=reason,show_when=reason,why_needed=reason,necessity_reason=reason,action_if_unknown='Only an active required operand blocks its individual result; optional source-only context stays explicitly not_assessed and never becomes a negative or clinical clearance')
 changes.append(dict(rule_id=rid,input_id=k,old=old,new=p,reason=reason,source_refs=i['source_refs'],locator=i['source_locator']))
 D['decisions']=[x for x in D['decisions'] if not(x.get('rule_id')==rid and x.get('input_id')==k and 'new' in x)];D['decisions'].append(deepcopy(changes[-1]))
pred('parox-taper-example','current_dose',dict(kind='field_true',field='example_selected'),'Нужна при example_selected=true для проверки начальной дозы опубликованного примера. Если пример явно не выбран, качественный результат не рассчитывает дозы/календаря. Unknown выбор не равен false и запрашивается отдельно.')
for k in ['duration','past_withdrawal']:
 pred('parox-taper-example',k,dict(kind='all_equals',values=dict(example_selected=True,current_dose=40)),'Контекст риска отмены по КР Б5 для проверяемого выбранного примера40мг. При явно невыбранном примере либо иной известной начальной дозе результат только qualitative clinician_choice без календаря; сведения не становятся универсальным обязательным вводом.40мг — существующая начальная точка выбранного примера, а не новый коэффициент.')
schema['requirement_predicates']['all_equals']='Active only when every listed explicitly known field equals the supplied value. An unknown prerequisite is never a confirmed mismatch: its own required input requests clarification; no calendar can be issued from it.'
for rid,sid,loc in [('preg-taper-limit','RU-PREG','§4.2 с.4–5; §4.3 с.6'),('phen-taper-limit','RU-PHEN','§4.2 с.2–3; §4.3 с.3')]:
 pred(rid,'age',dict(kind='reported_source_information'),'Для этого качественного источникового результата возраст — отдельно сообщённый контекст. Применимость взрослой инструкции остаётся условной; unknown не подтверждает возраст. Индивидуальный срок/календарь и детский режим не рассчитываются. Для будущего индивидуального плана возраст станет отдельным обязательным входом.')
 i=next(i for i in rs[rid]['inputs'] if i['input_id']=='age');i['source_locator']=loc
 C['rules'][rid]['qualitative_population_scope']=dict(source_ref=sid,source_locator=loc,result_scope='Adult product source reference only; no patient-specific taper duration or schedule',missing_or_unknown_age='not_assessed; adult applicability not confirmed',known_nonadult='pediatric taper plan not established; never apply adult reference interval as an individual child duration')
 C['rules'][rid]['reference_display']='Published adult-source limitation, conditional on its source population. No individual duration, pediatric plan, dose or calendar is granted from absent/unknown age.'
 for b in C['rules'][rid]['branches']:
  e=b['expected_output'];e.update(individual_duration_weeks=None,individual_taper_schedule=None,clinical_clearance=False)
  if e.get('duration_constraint'):e['duration_constraint'].update(scope='adult_source_reference_only',application_condition='Adult source applicability established; physician plans cessation; not an individual duration for child/unknown population')
pred('phen-taper-limit','withdrawal_severity',dict(kind='reported_source_information'),'§4.4 с.4 описывает синдром отмены; сообщённые текущие симптомы требуют отдельной оценки врача. PHEN-источник не устанавливает удержание/возврат/замедление по тяжести и не вычисляет индивидуальный темп. Необычные реакции сохраняют отдельное опубликованное условие прекращения.')
i=next(i for i in rs['phen-taper-limit']['inputs'] if i['input_id']=='withdrawal_severity');i['source_locator']='§4.4 с.4, синдром отмены; индивидуальное решение врача без опубликованного правила hold/resumption/slower'
rs['phen-taper-limit']['logic']['actions'][0]=rs['phen-taper-limit']['logic']['actions'][0].replace('PDF с.3','§4.2 PDF с.2')
rs['preg-taper-limit']['logic']['actions']=[action.replace('Для длительного приёма/высокого риска КР предусматривает более медленную индивидуальную отмену без единого темпа.','При длительном приёме/высоком риске требуется отдельный план врача. RU-PREG §4.4 с.9 описывает риск синдрома отмены; точные дополнительные ступени/сроки не опубликованы. Приложение Б2 КР ГТР с.77–78 относится к антидепрессантам и не задаёт более медленный протокол прегабалина.') for action in rs['preg-taper-limit']['logic']['actions']]
for rid,r in rs.items():
 con=C['rules'][rid];con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='always'];con['input_requirements']={i['input_id']:i['requirement_predicate'] for i in r['inputs']};con['monitoring_context_fields']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_source_information','reported_current_event'}]
 if rid in {'preg-taper-limit','phen-taper-limit'}:con['source_gate_scope']='Published gradual cessation restriction and current source stop events; reported withdrawal symptoms require physician assessment. No product-specific hold/resumption/slower protocol is established.'
 r['output']['branches']=deepcopy(con['branches'])
def active(rid,k,g):
 p=C['rules'][rid]['input_requirements'][k]
 return p['kind']=='always' or p['kind']=='field_true' and g.get(p['field']) is True or p['kind']=='all_equals' and all(g.get(a)==b for a,b in p['values'].items())
def scope(rid,g,e):
 if rid not in {'preg-taper-limit','phen-taper-limit'}:return
 age=g.get('age');state='adult' if type(age) in (int,float) and age>=18 else 'nonadult_plan_not_established' if type(age) in (int,float) else 'not_assessed'
 e.update(population_applicability=state,individual_duration_weeks=None,individual_taper_schedule=None,clinical_clearance=False)
 if e.get('duration_constraint'):e['duration_constraint'].update(scope='adult_source_reference_only',application_condition='Adult source applicability established; physician plans cessation; not an individual duration for child/unknown population')
 if state!='adult':e['no_automatic_pediatric_or_unknown_population_taper']=True
for c in F['cases']:
 rid=c['rule_id']
 if rid not in rs:continue
 g,e=c['given'],c['expected'];fields={'current_dose','duration','past_withdrawal'} if rid=='parox-taper-example' else {'age','withdrawal_severity'} if rid=='phen-taper-limit' else {'age'}
 inactive={k for k in fields if not active(rid,k,g)}
 if e['result_type']=='insufficient_data':
  old=e['missing_fields'];remain=[k for k in old if k.split('.')[0] not in inactive]
  if old and not remain:
   b=next(b for b in C['rules'][rid]['branches'] if b['branch_id']==('other' if rid=='parox-taper-example' else 'source_limit'));c['expected']=e=deepcopy(b['expected_output'])
  else:e['missing_fields']=remain
 e['clinical_clearance']=False;scope(rid,g,e)
 if c['branch_id']:e.update(deepcopy(next(b['expected_output'] for b in C['rules'][rid]['branches'] if b['branch_id']==c['branch_id'])))
 e['confirmed_negatives']=[k for k,v in g.items() if v is False]
 e['unassessed_context']=[k for k in C['rules'][rid]['monitoring_context_fields'] if k not in g or g[k] in (None,'unknown','not_assessed','неизвестно','не исследовано')]
new=[]
base=next(c for c in F['cases'] if c['rule_id']=='parox-taper-example' and c['branch_id']=='other')
for chosen,dose,label in [(False,40,'not_selected'),(True,10,'nonexample_dose')]:
 for state in ['omitted','unknown']:
  c=deepcopy(base);c.update(case_id='parox-taper-example--audit-final-qualitative-'+label+'-'+state,branch_id=None);g=c['given'];g.update(example_selected=chosen,current_dose=dose)
  for k in ['duration','past_withdrawal']+(['current_dose'] if not chosen else []):
   if state=='omitted':g.pop(k,None)
   else:g[k]='unknown'
  c['expected']=deepcopy(C['rules']['parox-taper-example']['branches'][1]['expected_output']);c['expected']['clinical_clearance']=False;new.append(c)
for rid in ['preg-taper-limit','phen-taper-limit']:
 base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='source_limit')
 for state in ['omitted','unknown','child','adult']:
  c=deepcopy(base);c.update(case_id=rid+'--audit-final-age-'+state,branch_id=None)
  if state=='omitted':c['given'].pop('age',None)
  else:c['given']['age']='unknown' if state=='unknown' else 17 if state=='child' else 35
  scope(rid,c['given'],c['expected']);c['expected']['unassessed_context']=[k for k in C['rules'][rid]['monitoring_context_fields'] if k not in c['given'] or c['given'][k] in (None,'unknown','not_assessed')];new.append(c)
F['cases']+=new
for rid,r in rs.items():save('rules/'+rid+'.yaml',r)
for change in changes:
 i=next(i for i in rs[change['rule_id']]['inputs'] if i['input_id']==change['input_id']);change['locator']=i['source_locator']
 for x in D['decisions']:
  if x.get('rule_id')==change['rule_id'] and x.get('input_id')==change['input_id']:x['locator']=i['source_locator']
save('result_contracts.yaml',C);save('full_scenarios.json',F);save('necessity_decisions.json',D);save('input_contracts.yaml',schema);save('final_necessity_repairs.json',changes)
policy=read('necessity_policy.yaml');policy['taper_scope']['preg_required']=C['rules']['preg-taper-limit']['required_inputs']
policy['taper_scope']['qualitative_population_scope']='PREG/PHEN adult source reference only: age is reported context, unknown applicability stays unassessed, no individual or pediatric duration/schedule. See final_necessity_repairs.json.'
save('necessity_policy.yaml',policy)
print('Specific result/necessity fixes:',len(changes),'; new prepared cases:',len(new),'; numerical ordinary limit not declared fulfilled')
