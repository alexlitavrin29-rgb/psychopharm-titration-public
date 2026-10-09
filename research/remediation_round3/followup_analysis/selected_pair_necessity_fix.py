"""Align selected A-example requirements with primary indication/actor scopes."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'selected_pair_necessity_repairs.json').exists(),'One-use correction'
rid='switch-parox-ago-selected-example';p=O/'rules'/(rid+'.yaml')
R=yaml.safe_load(p.read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));con=C['rules'][rid]
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'));rows=[]
preds={k:dict(kind='reported_context') for k in ['ect','akathisia','glaucoma','qt_risk']}
preds['dementia']=dict(kind='field_true',field='elderly_population')
preds.update({k:dict(kind='target_ongoing') for k in ['liver_injury_signs','transaminases_rising','mania_symptoms']})
for i in R['inputs']:
 k=i['input_id']
 if k not in preds:continue
 old=deepcopy(i['requirement_predicate']);new=preds[k]
 reason=('RU-AGO §4.4 физ.с.4 ограничивает применение при деменции у пожилого пациента; обязательность деменции включается только при введённой врачом пожилой категории. Не выводить универсальный порог пожилого возраста.' if k=='dementia' else
         'Текущее условие RU-AGO §4.4 физ.с.4 относится к уже принимаемому B. Обязательное текущее наблюдение включается только при отдельно известной фазе B=ongoing; фаза A его не заменяет. При unknown B нет действия прекращения B или разрешения его старта.' if new['kind']=='target_ongoing' else
         'Для выбранного опубликованного примера снижения A это предостережение/наблюдение не даёт числового операнда или обязательной предпосылки снижения. Акатизия предупреждает о повышении A, которое здесь не выполняется; глаукома/QT требуют источниковой осторожности, ECT — отдельного решения о сочетании B. Сообщённые значения сохраняются и считаются, unknown/отсутствие не дают клинического допуска или разрешения B.')
 i.update(requirement_predicate=new,input_role=new['kind'],required_for_individual_result=False,necessity_reason=reason,why_needed=reason,required_when=json.dumps(new,ensure_ascii=False),show_when=json.dumps(new,ensure_ascii=False))
 con['input_requirements'][k]=new
 if new['kind']=='reported_context' and k not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(k)
 rec=dict(rule_id=rid,input_id=k,old=old,new=new,source_refs=i['source_refs'],locator=i['source_locator'],reason=reason);rows.append(rec);D['decisions'].append(deepcopy(rec))
con['required_inputs']=[i['input_id'] for i in R['inputs'] if i['requirement_predicate']['kind']=='always']
base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']=='selected40')
for c in F['cases']:
 if c['rule_id']!=rid:continue
 e=c['expected'];g=c['given'];inactive=set()
 for k,pred in preds.items():
  if pred['kind']=='reported_context' or pred['kind']=='field_true' and g.get('elderly_population') is False or pred['kind']=='target_ongoing' and c['external_context'].get('target_treatment_phase')!='ongoing':inactive.add(k)
 missing=e.get('missing_fields',[]);removed=[k for k in missing if k.split('.')[0] in inactive]
 if removed:
  left=[k for k in missing if k not in removed]
  if left:e['missing_fields']=left
  else:c['expected']=e=deepcopy(base['expected'])
 e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in inactive if k not in g or g[k] in (None,'unknown','not_assessed')})
 e['clinical_clearance']=False
R['output']['branches']=con['branches']
p.write_text(yaml.safe_dump(R,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for name,data in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D)]:
 (O/name).write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=110) if name.endswith('.yaml') else json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'selected_pair_necessity_repairs.json').write_text(json.dumps(dict(rows=rows,scope='No medical number changed; supplied cautions/actions preserved. Specific primary population and B-phase triggers; independent acceptance pending'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Selected pair requirements aligned',len(rows))
