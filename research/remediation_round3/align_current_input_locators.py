"""Align current input metadata with clauses actually read; no dose logic changes."""
from pathlib import Path
import json,yaml

O=Path(__file__).resolve().parent
D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'))
maps={
 'RU-AGO':{'age':'§4.1 с.1; §4.2 с.2','form':'§1–3 с.1; §4.2 с.2','hepatic':'§4.2 с.2; §4.3 с.3','pregnancy':'§4.6 с.6','lactation':'§4.6 с.6','medicines':'§4.3 с.3; §4.4–4.5 с.3,5–6','allergy':'§4.3 с.3','ALT_ratio':'§4.3–4.4 с.3–4','AST_ratio':'§4.3–4.4 с.3–4','renal_state':'§4.2 с.2; §4.4 с.4'},
 'RU-PREG':{'age':'§4.1 с.3; §4.2 с.5; §4.3 с.6','form':'§1–3 с.1–2; §4.2 с.3,5','pregnancy':'§4.4 с.9; §4.6 с.12','lactation':'§4.6 с.12–13','medicines':'§4.4 с.7–8,10; §4.5 с.11–12','allergy':'§4.3 с.6','clcr':'§4.2 с.4–5, таблица 1 с.5; формула с.4 не исполняется','dialysis':'§4.2 с.4–5, таблица 1','respiratory':'§4.4 с.7–8','frequency':'§4.2 с.3,5','current_dose':'§4.2 с.3–5; §4.4 с.9','time_at_dose':'§4.2 с.3, ГТР','response':'§4.2 с.3, ГТР','tolerability':'§4.2 с.3, ГТР','duration_of_use':'§4.4 с.9','prior_withdrawal':'§4.4 с.9','current_withdrawal':'§4.2 с.4; §4.4 с.9'}}
changes=[]
for p in (O/'rules').glob('*.yaml'):
 r=yaml.safe_load(p.read_text(encoding='utf-8'))
 for i in r['inputs']:
  k=i['input_id'];refs=i['source_refs'];old=i['source_locator']
  for sid,locs in maps.items():
   if refs==[sid] and k in locs:i['source_locator']=locs[k]
  if refs==['RU-PREG'] and k=='age':i['why_needed']=i['necessity_reason']='§4.1 с.3 и §4.3 с.6: взрослое показание и возрастное противопоказание; возраст не заменяет подтверждённый CLcr для дозовой таблицы.'
  if refs==['RU-PREG'] and k=='medicines':i['why_needed']='§4.4 с.7–8,10 и §4.5 с.11–12: взаимодействия с угнетающими ЦНС средствами/опиоидами; не ИМАО-интервал от другого препарата. Пустой и непроверенный список различаются.'
  if refs==['RU-DULOX']:
   replacements={'elderly_population':('§4.2 с.4','§4.2 с.3'),'closed_angle_glaucoma':('§4.3 с.4','§4.3 с.3'),'maoi_type':('§4.5 с.9–10','§4.5 с.7–9'),'maoi_stopped_at':('§4.5 с.9–10','§4.5 с.7–9'),'fructose_intolerance':('§4.4 с.9','§4.4 с.7'),'glucose_galactose_malabsorption':('§4.4 с.9','§4.4 с.7'),'sucrase_isomaltase_deficiency':('§4.4 с.9','§4.4 с.7'),'akathisia':('§4.4 с.9','§4.4 с.7')}
   if k in replacements:
    a,b=replacements[k]
    for field in ['question_ru','why_needed','necessity_reason','required_when','show_when']:i[field]=i[field].replace(a,b)
  if old!=i['source_locator'] or (refs==['RU-DULOX'] and k in replacements) or (refs==['RU-PREG'] and k in {'age','medicines'}):
   changes.append(dict(rule_id=r['rule_id'],input_id=k,old_locator=old,new_locator=i['source_locator'],scope='Current input/necessity metadata only; medical expected and mandatory predicates unchanged'))
   for x in D['decisions']:
    if x.get('rule_id')==r['rule_id'] and x.get('input_id')==k:x.update(locator=i['source_locator'],source_refs=refs,reason=i['necessity_reason'])
 p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'necessity_decisions.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'current_input_locator_repairs.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('Current input locator/wording metadata corrected:',len(changes))
