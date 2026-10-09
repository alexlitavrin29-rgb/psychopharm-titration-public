"""Apply explicit dependency ordering after the frozen review has finished."""
from pathlib import Path

O=Path(__file__).resolve().parent.parent
p=O/'build_graphs.py';t=p.read_text(encoding='utf-8')
assert 'def dependencies(i):' not in t, 'Dependency ordering already applied'
a="    if k=='field_true':return g.get(p['field']) is True"
assert a in t
t=t.replace(a,a+"\n    if k=='all_equals':return all(g.get(field)==value for field,value in p['values'].items())")
a='paths=[];graphs=[];ledger=[]'
b="""def dependencies(i):
    p=i['requirement_predicate'];k=p['kind']
    if k=='field_true':return [p['field']]
    if k=='all_equals':return list(p['values'])
    if k in {'increase','action_choice'}:return ['clinician_action']
    if k in {'maoi_record','stopped_maoi_record'}:return ['medicines']
    if k=='ecg_if_cad':return ['coronary_disease']
    if k=='correction_if_electrolytes':return ['electrolyte_disturbance']
    return []
paths=[];graphs=[];ledger=[]"""
assert a in t;t=t.replace(a,b)
a="    inputs=[i for i in r['inputs'] if i['data_type']!='structured_form']"
b=a+"""
    pending=inputs[:];inputs=[]
    while pending:
        names={i['input_id'] for i in pending}
        ready=next((i for i in pending if not names.intersection(dependencies(i))),None)
        assert ready is not None, 'Cyclic question dependencies: '+rid
        inputs.append(ready);pending.remove(ready)"""
assert a in t;t=t.replace(a,b)
a="nodes.append(dict(node_id='check_'+k,requirement_predicate=i['requirement_predicate'],edges="
b="nodes.append(dict(node_id='check_'+k,requirement_predicate=i['requirement_predicate'],requires_known_inputs=dependencies(i),edges="
assert a in t;t=t.replace(a,b)
a="or '--audit-recheck-' in c['case_id'])"
assert a in t;t=t.replace(a,"or '--audit-recheck-' in c['case_id'] or '--audit-final-' in c['case_id'])")
p.write_text(t,encoding='utf-8')
p=O/'verify_contracts.py';t=p.read_text(encoding='utf-8')
a="            if pred['kind']=='field_true' and g.get(pred['field']) is True: applicable.add(key)"
assert a in t;t=t.replace(a,a+"\n            if pred['kind']=='all_equals' and all(g.get(field)==value for field,value in pred['values'].items()): applicable.add(key)")
p.write_text(t,encoding='utf-8')
p=O/'verify_graphs.py';t=p.read_text(encoding='utf-8')
a="    if len(ns)!=len(graph['nodes']):errors.append('duplicate node: '+rid)"
b=a+"""
    order={n['node_id']:pos for pos,n in enumerate(graph['nodes'])}
    for node in graph['nodes']:
        for dep in node.get('requires_known_inputs',[]):
            controller='check_'+dep
            if controller not in order or order[controller]>=order[node['node_id']]:errors.append('question controller not visited before dependency: '+rid+'/'+dep+'/'+node['node_id'])"""
assert a in t;p.write_text(t.replace(a,b),encoding='utf-8')
print('Declared predicate controls precede dependent questions; all_equals bound to static contract validation')
