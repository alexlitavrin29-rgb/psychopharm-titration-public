import json,sys
from pathlib import Path
seen=set()
for p in sorted((Path(__file__).parent/'extracted').glob('*.json')):
 if len(sys.argv)>1 and not any(p.stem.startswith(x) for x in sys.argv[1:]): continue
 r=json.loads(p.read_text(encoding='utf-8'))
 print('\n###',p.stem,'READY',r['verification']['ready_for_technical_implementation'])
 print('IDENTITY',r['identity']['diagnosis_code'],r['identity']['formulation'])
 for k,v in r['applicability'].items():
  t=k+': '+str(v)
  if t not in seen: print('APP',t);seen.add(t)
 print('PAR', '; '.join(f"{v['parameter_id']}={v['value'] if v['value'] is not None else [v['lower'],v['upper']]} {v['unit']} @{v['source_ref']}:{v['source_locator']}" for v in r['clinical_parameters']))
 print('IN',','.join(v['input_id'] for v in r['inputs']))
 for k,v in r['logic'].items():
  if k in ['parameter_refs','source_refs']:continue
  t=k+': '+str(v)
  if t not in seen:print('LOG',t);seen.add(t)
 o=r['output'];print('OUT',o['result_type'],o['dose_per_administration'],o['administrations_per_day'],o['total_daily_dose'])
 if o['schedule']: print('SCHEDULE',json.dumps(o['schedule'],ensure_ascii=False))
 for k in ['warnings','mandatory_checks','clinician_decisions_remaining','rounding_or_formulation_rule']:
  t=k+': '+str(o[k])
  if t not in seen:print('OUT',t);seen.add(t)
 print('CASES',json.dumps(r['test_cases'],ensure_ascii=False))
