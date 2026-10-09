from pathlib import Path
import yaml,json,sys
root=Path(__file__).resolve().parents[1]
for p in sorted((root/'rules').glob('*.yaml')):
 r=yaml.safe_load(p.read_text(encoding='utf-8'))
 if len(sys.argv)>1 and not any(p.stem.startswith(x) for x in sys.argv[1:]): continue
 print('\n###',p.stem, 'READY',r['verification']['ready_for_technical_implementation'])
 print('IDENTITY',json.dumps(r['identity'],ensure_ascii=False))
 print('APPLICABILITY',json.dumps(r['applicability'],ensure_ascii=False))
 print('PARAMETERS',json.dumps([{k:v for k,v in a.items() if v is not None} for a in r['clinical_parameters']],ensure_ascii=False))
 print('INPUTS',json.dumps([{k:a.get(k) for k in ['input_id','data_type','allowed_values','required_when','show_when','action_if_unknown']} for a in r['inputs']],ensure_ascii=False))
 print('LOGIC',json.dumps(r['logic'],ensure_ascii=False))
 print('OUTPUT',json.dumps(r['output'],ensure_ascii=False))
 print('CASES',json.dumps(r['test_cases'],ensure_ascii=False))
