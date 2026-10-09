"""Isolated copy preflight; does not mutate the frozen candidate."""
from pathlib import Path
import importlib.util,json,shutil,subprocess,sys,yaml
O=Path(__file__).resolve().parent;T=O/'staging_recheck'
if not T.exists():
    T.mkdir()
    for name in ['sources.json','input_contracts.yaml','result_contracts.yaml','full_scenarios.json','necessity_decisions.json','necessity_policy.yaml','repair_recheck_findings.py','repair_qualitative_necessity.py','build_graphs.py','verify_contracts.py']:
        shutil.copyfile(O/name,T/name)
    shutil.copytree(O/'rules',T/'rules')
    p=T/'repair_qualitative_necessity.py';t=p.read_text(encoding='utf-8').replace("'phen-taper-limit','ser-taper-limit'","'phen-taper-limit','preg-taper-limit','ser-taper-limit'");p.write_text(t,encoding='utf-8')
    p=T/'build_graphs.py';t=p.read_text(encoding='utf-8')
    t=t.replace("if k=='always':return True","if k=='always':return True\n    if k in {'reported_current_event','reported_source_information'}:return i['input_id'] in g")
    t=t.replace("for field in ['inn','status']]","for field in (['inn','status']+(['additional_product'] if 'additional_product' in m else []))]")
    t=t.replace("or '--audit-v2-' in c['case_id']","or '--audit-v2-' in c['case_id'] or '--audit-recheck-' in c['case_id']")
    t=t.replace("{'reported_context','ongoing_selected_drug','target_ongoing'}","{'reported_context','reported_current_event','reported_source_information','ongoing_selected_drug','target_ongoing'}")
    p.write_text(t,encoding='utf-8')
    p=T/'repair_recheck_findings.py';t=p.read_text(encoding='utf-8');t=t[:t.index('R=O.parent')];p.write_text(t,encoding='utf-8')
    for name in ['repair_qualitative_necessity.py','repair_recheck_findings.py']:
        proc=subprocess.run([sys.executable,'-X','utf8',str(T/name)],capture_output=True,text=True,encoding='utf-8')
        print(name,proc.returncode,proc.stdout[-1800:]);assert proc.returncode==0,proc.stderr
else:
    assert (T/'recheck_repairs.json').exists(),'Incomplete stage requires explicit repair'
    print('Checking the already prepared isolated stage; no candidate recopy or patch replay.')
for name in ['build_graphs.py']:
    proc=subprocess.run([sys.executable,'-X','utf8',str(T/name)],capture_output=True,text=True,encoding='utf-8')
    print(name,proc.returncode,proc.stdout[-1800:]);assert proc.returncode==0,proc.stderr
# The staged rules/data are checked with the same real, read-only source archive.
spec=importlib.util.spec_from_file_location('staged_verify',T/'verify_contracts.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
d=v.collect(root=O.parent)
d.update(contracts=yaml.safe_load((T/'result_contracts.yaml').read_text(encoding='utf-8'))['rules'],schema=yaml.safe_load((T/'input_contracts.yaml').read_text(encoding='utf-8')),cases=json.loads((T/'full_scenarios.json').read_text(encoding='utf-8'))['cases'])
errors=v.validate(d)
import verify_recheck_repairs
paths=json.loads((T/'actual_question_paths.json').read_text(encoding='utf-8'));extra=verify_recheck_repairs.check(d,paths)
report=dict(status='pass' if not errors+extra else 'fail',scope='Isolated draft rules/contracts/cases/graph with read-only actual source archive; no frozen-core mutation or medical engine execution',contract_errors=errors,recheck_errors=extra)
(T/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors+extra))
