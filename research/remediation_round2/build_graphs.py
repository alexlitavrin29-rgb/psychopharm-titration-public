"""Document real question paths and independent subfields; no dose calculation."""
from pathlib import Path
from copy import deepcopy
import json,csv
import yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (R/'rules').glob('*.yaml')}
contracts=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
cases=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']

def cost(i,r):
    # An assessed source renal category has three independently supplied facts.
    if i['data_type']=='structured_renal':return ['metric','value_and_unit','method']
    if i['input_id']=='allergy' and r['identity']['mode']=='switch':return ['hypersensitivity_A','hypersensitivity_B']
    if i['input_id']=='from_taper_plan':return ['each independent clinician-supplied stage/dose/frequency; variable cardinality']
    return [i['input_id']]

def applicable(i,g):
    p=i['requirement_predicate'];k=p['kind']
    if k=='always':return True
    if k in {'increase','action_choice'}:return g.get('clinician_action','not_chosen') in p['actions']
    if k=='maoi_record':return any(m.get('interaction_class') in ['maoi','unknown'] for m in g.get('medicines',[]))
    if k=='stopped_maoi_record':return any(m.get('interaction_class')=='maoi' and m.get('status')=='stopped' for m in g.get('medicines',[]))
    if k=='ecg_if_cad':return g.get('coronary_disease') is True
    if k=='correction_if_electrolytes':return g.get('electrolyte_disturbance') is True
    return False

graphs=[];paths=[]
for rid,r in sorted(rules.items()):
    blocked=any(s['source_id']=='RU-ESC' and s.get('access_status')!='full' for s in r['sources'])
    initial=['diagnosis','mode','identified_product_form_strength'] if r['identity']['mode']!='switch' else ['diagnosis','mode','identified_A_product_form_strength','identified_B_product_form_strength']
    facts_inputs=[i for i in r['inputs'] if i['data_type']!='structured_form']
    first='check_'+facts_inputs[0]['input_id'] if facts_inputs else 'source_result'
    nodes=[dict(node_id='select',ask=initial,cost=len(initial),edges=[dict(when='selections_supplied',target='source_gate')])]
    nodes.append(dict(node_id='source_gate',ask=[],cost=0,condition='identified exact source available',edges=[dict(when='source_available',target=first),dict(when='source_unavailable',target='terminal_source_unavailable')]))
    terminal_types=['source_unavailable','insufficient_data','not_applicable','source_stop_action','clinician_choice','exact','range','selected_source_example','form_not_feasible']
    for typ in terminal_types:nodes.append(dict(node_id='terminal_'+typ,ask=[],cost=0,result_type=typ,clinical_clearance=False))
    nodes.append(dict(node_id='source_result',ask=[],cost=0,result_contract='result_contracts.yaml#rules/'+rid,
        edges=[dict(when='source_contract_result_type='+typ,target='terminal_'+typ) for typ in terminal_types],
        scope='Prepared source-contract result; source medical branch predicates stay in that contract, no implemented dose evaluator'))
    for index,i in enumerate(facts_inputs):
        k=i['input_id'];nxt='check_'+facts_inputs[index+1]['input_id'] if index+1<len(facts_inputs) else 'source_result'
        monitor=i['requirement_predicate']['kind']=='reported_context'
        nodes.append(dict(node_id='check_'+k,ask=[],cost=0,predicate=i['requirement_predicate'],edges=[dict(when='requirement_predicate_active',target='ask_'+k),dict(when='requirement_predicate_inactive',target=nxt)],inactive_state='not_assessed with source warning' if monitor else 'not required for selected result'))
        nodes.append(dict(node_id='ask_'+k,ask=cost(i,r),cost=len(cost(i,r)),source_refs=i['source_refs'],locator=i['source_locator'],cost_policy='MAOI maps cost per relevant record; physician stage count variable; declared assessed categories include evidence metadata',edges=[dict(when='fact_submitted',target='assess_'+k)]))
        nodes.append(dict(node_id='assess_'+k,ask=[],cost=0,source_refs=i['source_refs'],locator=i['source_locator'],edges=[dict(when='applicable_fact_missing_or_unassessed',target='terminal_insufficient_data'),dict(when='confirmed_source_urgent_stop',target='terminal_source_stop_action'),dict(when='confirmed_source_exclusion',target='terminal_not_applicable'),dict(when='confirmed_source_caution_without_selected_source_branch',target='terminal_clinician_choice'),dict(when='confirmed_applicable_fact',target=nxt)],source_predicates_contract='result_contracts.yaml#rules/'+rid))
    node_map={x['node_id']:x for x in nodes}
    assert all(e['target'] in node_map for n in nodes for e in n.get('edges',[]))
    def walk_questions(g,result_type):
        # Traverses explicit question edges. Medical action predicates are not calculated here;
        # the separately source-reviewed prepared result selects the final clinical terminal.
        trace=['select','source_gate'];asked=[]
        if blocked:return trace+['terminal_source_unavailable'],initial,[]
        for i in facts_inputs:
            k=i['input_id'];trace.append('check_'+k)
            if not applicable(i,g):continue
            trace+=['ask_'+k,'assess_'+k]
            if i['data_type']=='record_map':
                refs=[m['record_id'] for m in g.get('medicines',[]) if m.get('interaction_class')=='maoi' and (k=='maoi_type' or m.get('status')=='stopped')]
                asked += [k+'.'+ref for ref in refs]
            else:asked += cost(i,r)
        trace+=['source_result','terminal_'+result_type]
        assert all(t in node_map for t in trace)
        assert all(b in [e['target'] for e in node_map[a].get('edges',[])] for a,b in zip(trace,trace[1:]))
        return trace,initial,asked
    example_cases=[c for c in cases if c['rule_id']==rid and c['branch_id']]
    selected=[]
    for c in example_cases:
        path_label=c['branch_id']+(' / conditional ECG and electrolytes' if 'conditional-checks-completed' in c['case_id'] else '')
        if 'maoi-14' in c['case_id'] or 'moclobemide-24h' in c['case_id']:path_label+=' / '+c['case_id'].split('--')[-1]
        if any(p['path_label']==path_label for p in selected):continue
        g=c['given'];required=[i for i in r['inputs'] if i['data_type']!='structured_form' and applicable(i,g)]
        projected={i['input_id']:deepcopy(g[i['input_id']]) for i in r['inputs'] if i['input_id'] in g and (i['data_type']=='structured_form' or applicable(i,g))}
        expected=deepcopy(c['expected'])
        if rid.startswith('ser') and rid!='ser-taper-limit':
            expected['unassessed_context']=contracts[rid].get('monitoring_context_fields',[])
            expected['clinical_clearance']=False
        if rid.startswith('esc'):
            expected['unassessed_context']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='reported_context']
            expected['clinical_clearance']=False
        facts=[f for i in required for f in cost(i,r)]
        variable=any('variable cardinality' in f for f in facts)
        n=len(initial)+len(facts)
        history=[]
        for m in g.get('medicines',[]) if isinstance(g.get('medicines'),list) else []:
            if m.get('interaction_class')=='maoi':
                history.append('maoi_type.'+m['record_id'])
                if m['status']=='stopped':history.append('maoi_stopped_at.'+m['record_id'])
        # Maps counted per record, not once more as generic fields.
        facts=[f for f in facts if f not in {'maoi_type','maoi_stopped_at'}]+history
        n=len(initial)+len(facts)
        trace,initial,facts=walk_questions(g,c['expected']['result_type'])
        n=len(initial)+len(facts)
        p=dict(rule_id=rid,branch_id=c['branch_id'],path_label=path_label,initial_selections=initial,required_independent_facts=facts,
               count=n,count_is_lower_bound=variable,result_type=c['expected']['result_type'],
               full_example=c['case_id'],known_facts_reused='none assumed; supplied provenance can remove repeat questions within this calculation',
               traversed_node_ids=trace,count_method='Explicit active question-node traversal, with per-record MAOI costs; medical expected independently reviewed separately',
               full_projected_given=projected,full_projected_expected=expected,
               full_external_context=deepcopy(c['external_context']),
               product_metadata_questions=0,scope='source-bound selected result; not full clinical clearance',
               within_5_10=5<=n<=10 and not variable and c['expected']['result_type'] in {'exact','selected_source_example','source_stop_action'})
        selected.append(p);paths.append(p)
    graphs.append(dict(rule_id=rid,nodes=nodes,paths=selected,blocked_current_original=blocked,edge_targets_checked=True,prepared_paths_traversed=True))

data=dict(schema_version='1.0',nature='Research question graphs; no implemented dialogue',
          count_policy='INN derived from one identified product/form/strength selection; patient facts independent; ALT and AST separate; each relevant MAOI type and stopped timestamp separate',
          graphs=graphs)
(O/'question_graphs.yaml').write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'actual_question_paths.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2),encoding='utf-8')
# Source-proven lower bound, excluding every monitoring risk and reproductive/renal caution.
lower=dict(rule_id='ago-depression-start',result='adult individualized start dose from RU-AGO',
           initial_selections=['diagnosis','mode','identified_product_form_strength'],
           independent_facts=[
               {'field':'age','locator':'§4.2 с.2, adult/elderly applicability'},
               {'field':'hepatic','locator':'§4.3 с.3, active disease/cirrhosis'},
               {'field':'ALT_ratio','locator':'§4.4 с.3, each baseline liver test'},
               {'field':'AST_ratio','locator':'§4.4 с.3, each baseline liver test'},
               {'field':'medicines','locator':'§4.3 с.3; §4.5 с.5–6, CYP1A2'},
               {'field':'allergy','locator':'§4.3 с.3'},
               {'field':'galactose_intolerance','locator':'§4.3 с.3'},
               {'field':'complete_lactase_deficiency','locator':'§4.3 с.3'},
               {'field':'glucose_galactose_malabsorption','locator':'§4.3 с.3'}],
           count=12,lower_bound_not_full_clearance=True,source_ref='RU-AGO',
           reason='Even after excluding all observation-only, renal and pregnancy/lactation inputs, the unchanged source-specific individual applicability contract requires 12 independent selections/facts. No universal clearance checkbox; AST cannot be inferred from ALT; liver insufficiency cannot be inferred from enzymes.',
           remaining_requirement='Criterion 18 remains partial; 12 is a sufficient lower bound for the conflict, not proof of a universal optimal questionnaire',
           proposed_requirement_change='Allow 5–10 dose questions after a separately enumerated, source-specific applicability check; count and show its independent facts openly. Requires a separate user decision and reacceptance; not applied here.')
(O/'question_limit_conflict.json').write_text(json.dumps(lower,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(graphs),'graphs;',len(paths),'branch paths; agomelatine source-specific lower bound 12 independent facts/selections.')
