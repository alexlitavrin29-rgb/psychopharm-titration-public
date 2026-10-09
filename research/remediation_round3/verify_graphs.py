from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round3'
graphs=yaml.safe_load((O/'question_graphs.yaml').read_text(encoding='utf-8'))['graphs'];errors=[];count=0
for graph in graphs:
    ns={n['node_id']:n for n in graph['nodes']};rid=graph['rule_id']
    if len(ns)!=len(graph['nodes']):errors.append('duplicate node: '+rid)
    order={n['node_id']:pos for pos,n in enumerate(graph['nodes'])}
    for node in graph['nodes']:
        for dep in node.get('requires_known_inputs',[]):
            controller='check_'+dep
            if controller not in order or order[controller]>=order[node['node_id']]:errors.append('question controller not visited before dependency: '+rid+'/'+dep+'/'+node['node_id'])
    for node in ns.values():
        for edge in node.get('edges',[]):
            if edge['target'] not in ns:errors.append('unresolved edge: '+rid+'/'+edge['target'])
    for p in graph['paths']:
        count+=1;trace=p['traversed_node_ids']
        for a,b in zip(trace,trace[1:]):
            if b not in [e['target'] for e in ns[a].get('edges',[])]:errors.append('path edge absent: '+rid+'/'+a+'/'+b)
        if p['count']!=len(p['initial_selections'])+len(p['required_independent_facts']):errors.append('path count drift: '+rid)
        if not ns[trace[-1]].get('result_type'):errors.append('nonterminal path: '+rid)
        if len(p['required_independent_facts'])!=len(set(p['required_independent_facts'])):errors.append('double-counted fact: '+rid)
report=dict(status='pass' if not errors else 'fail',graphs=len(graphs),prepared_paths=count,explicit_edges=True,counts_from_question_traversal=True,clinical_result_scope='Prepared separately source-bound expected; graph verification does not execute medical branch evaluation or a calculator',errors=errors)
(O/'graph_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))
