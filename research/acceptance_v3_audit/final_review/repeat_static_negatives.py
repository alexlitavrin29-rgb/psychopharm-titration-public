"""Repeat frozen author's detectors without their report-writing entry points."""
from pathlib import Path
from copy import deepcopy
import sys,ast,json,yaml,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
R=ROOT/'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
sys.path.insert(0,str(R))
ns={'__file__':str(R/'verify_contracts.py'),'__name__':'read_only_import'}
s=(R/'verify_contracts.py').read_text('utf8').replace("d['root']/'remediation_round3/necessity_policy.yaml'","O/'necessity_policy.yaml'")
exec(compile(s,str(R/'verify_contracts.py'),'exec'),ns)
base=dict(root=ROOT/'research',sources=json.loads((R/'sources.json').read_text('utf8')),rules={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')},contracts=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules'],schema=yaml.safe_load((R/'input_contracts.yaml').read_text('utf8')),cases=json.loads((R/'full_scenarios.json').read_text('utf8'))['cases'])
validate=ns['validate'];baseline=validate(base)
tree=ast.parse((R/'verify_new_negative_checks.py').read_text('utf8'))
parts=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['scenario','apply'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='checks' for t in n.targets)]
neg={};exec(compile(ast.Module(body=parts,type_ignores=[]),'frozen_mutations_without_runner','exec'),neg)
rows=[]
for kind,msg in neg['checks'].items():
    d=deepcopy(base);neg['apply'](d,kind);errors=validate(d);match=[e for e in errors if msg in e]
    rows.append(dict(mutation=kind,rejected=bool(match),matching_errors=match[:4]))
graphs=yaml.safe_load((R/'question_graphs.yaml').read_text('utf8'))['graphs'];graph_errors=[];paths=0
for graph in graphs:
    n={x['node_id']:x for x in graph['nodes']}
    if len(n)!=len(graph['nodes']):graph_errors.append([graph['rule_id'],'duplicate'])
    for p in graph['paths']:
        paths+=1;trace=p['traversed_node_ids']
        for a,b in zip(trace,trace[1:]):
            if b not in [e['target'] for e in n[a].get('edges',[])]:graph_errors.append([graph['rule_id'],a,b])
        if p['count']!=len(p['initial_selections'])+len(p['required_independent_facts']) or len(set(p['required_independent_facts']))!=len(p['required_independent_facts']):graph_errors.append([graph['rule_id'],'count'])
        if n[trace[-1]].get('result_type')!=p['result_type']:graph_errors.append([graph['rule_id'],'terminal'])
flows=yaml.safe_load((ROOT/'research/remediation_round3/v3_review1_snapshot/research/question_flows.yaml').read_text('utf8'))
try:flows['flows'][0]['count']-=1;old_mutation_error=None
except KeyError as e:old_mutation_error=repr(e)
report=dict(baseline_errors=baseline,mutations=rows,mutations_rejected=sum(r['rejected'] for r in rows),mutation_total=len(rows),missed=[r['mutation'] for r in rows if not r['rejected']],graphs=len(graphs),paths=paths,graph_errors=graph_errors,old_root_mutation_error=old_mutation_error,scope='Actually repeated author validate/mutator functions on isolated in-memory frozen data and own graph-edge checks; root stale mutation failure reproduced on in-memory flows. Author report entry points were not called; not medical/app validation.')
(OUT/'static_detectors_repeat.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='mutations'},ensure_ascii=False))
