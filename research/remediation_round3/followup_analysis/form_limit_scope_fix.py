"""Selected whole-unit form impossibility is not individual treatment admission."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'form_limit_scope_repairs.json').exists(),'One-use correction'
rid='venla-xr-panic-form-limit';p=O/'rules'/(rid+'.yaml');r=yaml.safe_load(p.read_text(encoding='utf-8'))
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));con=C['rules'][rid];F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'));rows=[];changed=set()
for i in r['inputs']:
 k=i['input_id'];kind=i['requirement_predicate']['kind']
 if k=='form' or kind in {'reported_context','reported_current_event','reported_source_information','maoi_record','stopped_maoi_record'}:continue
 pred=dict(kind='reported_current_event' if kind=='ongoing_selected_drug' else 'reported_source_information')
 reason='Выбранные целые XR-капсулы 75/150 мг не обеспечивают опубликованный исходный компонент 37,5 мг. Для этого источникового вывода нужна идентичность формы, а не полный клинический допуск. Пациентские сведения при сообщении сохраняются и считаются; unknown/отсутствие остаются not_assessed. Справочные числа не становятся дозой/календарём пациента; известные источниковые действия требуют своего подтверждённого текущего приёма.'
 old=deepcopy(i['requirement_predicate']);i.update(requirement_predicate=pred,required_for_individual_result=False,input_role=pred['kind'],necessity_reason=reason,why_needed=reason,required_when='Only when explicitly supplied',show_when='Only when explicitly supplied')
 con['input_requirements'][k]=pred
 if k not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(k)
 rec=dict(rule_id=rid,input_id=k,old=old,new=pred,source_refs=i['source_refs'],locator=i['source_locator'],reason=reason);rows.append(rec);D['decisions'].append(deepcopy(rec));changed.add(k)
con['required_inputs']=['form'];con['qualitative_result_scope']='Selected whole-unit source-form impossibility only; published start components are source references, no patient dose/calendar/clinical admission or IR substitution.'
con['branches'][0]['expected_output'].update(clinical_clearance=False,individual_start_allowed=False,published_components_scope='Adult source reference only; not an individual patient start')
for c in F['cases']:
 if c['rule_id']!=rid:continue
 e=c['expected'];g=c['given'];missing=e.get('missing_fields',[]);removed=[k for k in missing if k.split('.')[0] in changed]
 if removed:
  left=[k for k in missing if k not in removed]
  if left:e['missing_fields']=left
  else:c['expected']=e=deepcopy(con['branches'][0]['expected_output'])
 e['clinical_clearance']=False
 e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in changed if g.get(k) in (None,'unknown','not_assessed')})
 if e['result_type']=='form_not_feasible':e.update(individual_start_allowed=False,published_components_scope='Adult source reference only; not an individual patient start')
base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='form_limit');n=deepcopy(base);n['case_id']=rid+'--audit-final-source-form-without-patient-screen';n['given']={'form':n['given']['form']};n['expected']=deepcopy(con['branches'][0]['expected_output']);n['expected'].update(confirmed_negatives=[],unassessed_context=sorted(i['input_id'] for i in r['inputs'] if i['input_id']!='form'),population_applicability='not_assessed');n['fixture_scope']=con['qualitative_result_scope'];F['cases'].append(n)
r['output']['branches']=con['branches'];p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for name,data in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D)]:
 (O/name).write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=110) if name.endswith('.yaml') else json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'form_limit_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_case=n['case_id'],scope=con['qualitative_result_scope'],independent_acceptance='pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Source form-limit requirements aligned',len(rows))
