from pathlib import Path
import sys, json, csv
import yaml
R = Path(__file__).resolve().parents[1]
mode = sys.argv[1]
if mode in ('cards','compact'):
    for p in sorted((R/'rules').glob('*.yaml')):
        if len(sys.argv)>2 and not any(p.stem.startswith(x) for x in sys.argv[2:]): continue
        d = yaml.safe_load(p.read_text(encoding='utf-8'))
        out = {'id':d['rule_id'],'app':d['applicability'],'logic':d['logic']['actions'],
               'params':[[p['parameter_id'],p['value'],p['lower'],p['upper'],p['unit'],p['source_locator']] for p in d['clinical_parameters']],
               'output':{k:d['output'][k] for k in ('result_type','dose_per_administration','administrations_per_day','total_daily_dose','schedule')},
               'cases':[[c['case_id'].split('__')[-1],c['given'],c['expected']] for c in d['test_cases']]}
        out['inputs'] = [[i['input_id'],i['data_type'],i['unit'],i['allowed_values']] for i in d['inputs']]
        if mode == 'compact': out.pop('app'); out['output'].pop('schedule')
        print(json.dumps(out,ensure_ascii=False))
elif mode == 'audit':
    for name in sys.argv[2:]:
        with (R/'audit'/name).open(encoding='utf-8-sig',newline='') as f:
            print(name)
            for row in csv.DictReader(f):
                for k in ('identity','value','given','expected','applicability_value'): row.pop(k,None)
                print(json.dumps(row,ensure_ascii=False))
elif mode == 'sources':
    d=json.loads((R/'sources.json').read_text(encoding='utf-8'))
    for k,v in d.items():
        if len(sys.argv)==2 or k in sys.argv[2:]: print(json.dumps(v,ensure_ascii=False))
elif mode == 'audit_summary':
    from collections import Counter
    for p in sorted((R/'audit').glob('*')):
        if p.suffix=='.csv':
            with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
            print(p.name,len(rows),list(rows[0]))
            for key in ('independent_review','transfer_decision','review','verdict','status','independent_conclusion','missing_declared_inputs','undeclared_keys'):
                if key in rows[0]: print(key,json.dumps(dict(Counter(r[key] for r in rows)),ensure_ascii=False))
