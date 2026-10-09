"""Keep partial optional information explicit and refresh own minimal fixtures."""
from pathlib import Path
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'scope_metadata_repairs.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[]
for c in F['cases']:
 if c['rule_id']=='venla-xr-panic-form-limit' and '--nested-renal_metric-' in c['case_id'] and c['expected']['result_type']=='form_not_feasible':
  c['expected'].setdefault('reported_input_issues',{})['renal_metric']='Supplied object lacks '+c['case_id'].split('--nested-renal_metric-',1)[1].removesuffix('-omitted')+'; not an assessed renal operand for this source-form reference.'
  c['expected']['unassessed_context']=sorted(set(c['expected'].get('unassessed_context',[]))|{'renal_metric'});rows.append(dict(case_id=c['case_id'],repair='Named incomplete optional renal information'))
 if c['rule_id']=='switch-parox-ago-selected-example' and '--audit-final-minimal-routine' in c['case_id']:
  removed={k:c['given'].pop(k) for k in ['ect','akathisia','glaucoma','qt_risk'] if k in c['given']}
  if removed:
   assert all(v is False for v in removed.values()),c['case_id']
   c['expected']['confirmed_negatives']=[k for k in c['expected'].get('confirmed_negatives',[]) if k not in removed];c['expected']['unassessed_context']=sorted(set(c['expected'].get('unassessed_context',[]))|set(removed));rows.append(dict(case_id=c['case_id'],repair='Own omitted-context witness updated for new predicates; original supplied-context fixture kept separately',omitted=removed))
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
for rid in ['dulox-taper-limit','fluvox-taper-limit','venla-xr-taper-limit','esc-taper-limit','ser-taper-limit']:
 p=O/'rules'/(rid+'.yaml');r=yaml.safe_load(p.read_text(encoding='utf-8'))
 for i in r['inputs']:
  if i['input_id']=='form':i['necessity_reason']=i['why_needed']='Идентичность выбранной российской формы и версии связывает опубликованное условие отмены с источником. Это начальный выбор, считаемый один раз; числовое деление/индивидуальный календарь здесь не рассчитываются.'
  if rid=='dulox-taper-limit' and i['input_id']=='withdrawal_severity':i['necessity_reason']=i['why_needed']='При непереносимых симптомах источник допускает врачебное рассмотрение прежней дозы и более медленного снижения: §4.2 физ.с.3; §4.4 физ.с.6. Числовой шаг и индивидуальный срок не опубликованы.'
 p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'scope_metadata_repairs.json').write_text(json.dumps(dict(rows=rows,taper_form_explanation='Source identity selection, no dose feasibility calculation claimed',medical_values_changed=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Scope metadata aligned',len(rows))
