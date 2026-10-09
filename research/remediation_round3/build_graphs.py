"""Traverse adaptive fact predicates; prepared expected chooses terminal, no medical calculator."""
from pathlib import Path
from copy import deepcopy
import json,csv,yaml
from phase_provenance import selected_phase
from bounded_source_actions import source_action_scope
from bounded_source_exclusions import source_exclusion_scope,source_choice_scope,source_form_scope
from bounded_unselected_example import unselected_example_scope
O=Path(__file__).resolve().parent
S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
rs={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']

def resolve_terminal_scope(c):
    rid=c['rule_id']
    return source_action_scope(rs[rid],C[rid],c) or source_exclusion_scope(rs[rid],c) or source_choice_scope(rs[rid],c) or source_form_scope(rs[rid],c) or unselected_example_scope(rs[rid],c)
SCOPES={c['case_id']:resolve_terminal_scope(c) for c in F}
def terminal_scope(c):return SCOPES[c['case_id']]
def active(i,c):
    p=i['requirement_predicate'];k=p['kind'];g=c['given'];ctx=c['external_context']
    scope=terminal_scope(c)
    if scope is not None:return i['input_id'] in scope['used_fields']
    if k=='always':return True
    if k in {'reported_context','reported_current_event','reported_source_information'}:return i['input_id'] in g
    if k=='indication_action_choice':return (ctx.get('diagnosis') in p['diagnoses'] and g.get('clinician_action','not_chosen') in p['actions']) or i['input_id'] in g
    if k in {'increase','action_choice'}:return g.get('clinician_action','not_chosen') in p['actions']
    if k=='ongoing_selected_drug':return ctx.get('treatment_phase')=='ongoing'
    if k=='target_ongoing':return ctx.get('target_treatment_phase')=='ongoing'
    if k=='field_true':return g.get(p['field']) is True
    if k=='all_equals':return all(g.get(field)==value for field,value in p['values'].items())
    if k=='ecg_if_cad':return g.get('coronary_disease') is True
    if k=='correction_if_electrolytes':return g.get('electrolyte_disturbance') is True
    if k in {'maoi_record','stopped_maoi_record'}:return any(m.get('interaction_class')=='maoi' and (k=='maoi_record' or m.get('status')=='stopped') for m in g.get('medicines',[]) if isinstance(m,dict))
    return False
def facts(i,c,r):
    k=i['input_id'];g=c['given']
    if i['data_type']=='structured_renal':return [k+'.clinician_confirmed_source_value']
    if i['data_type']=='paired_allergy':
        scope=terminal_scope(c)
        return scope['fact_components'][k] if scope and k in scope.get('fact_components',{}) else [k+'.A',k+'.B']
    if i['data_type']=='record_map':return [k+'.'+m['record_id'] for m in g.get('medicines',[]) if m.get('interaction_class')=='maoi' and (k=='maoi_type' or m['status']=='stopped')]
    if i['data_type']=='medication_list':
        records=g.get(k,[])
        return [k+'.'+m['record_id']+'.'+field for m in records for field in ['inn','status']+(['additional_product'] if 'additional_product' in m else [])] if isinstance(records,list) and records else [k+'.confirmed_empty_or_unknown_list']
    if i['data_type']=='dose_schedule':
        plan=g.get(k);stages=plan.get('stages',[]) if isinstance(plan,dict) else []
        return [k+f'.stage{n}.'+f for n,_ in enumerate(stages,1) for f in ['start_day','total_daily_mg','administrations_per_day']] or [k+'.unknown_plan_cardinality']
    return [k]
def dependencies(i):
    p=i['requirement_predicate'];k=p['kind']
    if k=='field_true':return [p['field']]
    if k=='all_equals':return list(p['values'])
    if k in {'increase','action_choice','indication_action_choice'}:return ['clinician_action']
    if k in {'maoi_record','stopped_maoi_record'}:return ['medicines']
    if k=='ecg_if_cad':return ['coronary_disease']
    if k=='correction_if_electrolytes':return ['electrolyte_disturbance']
    return []
paths=[];graphs=[];ledger=[]
for rid,r in sorted(rs.items()):
    initial=['diagnosis','mode','identified_product_form_strength'] if r['identity']['mode']!='switch' else ['diagnosis','mode','identified_A_product_form_strength','identified_B_product_form_strength']
    if rid in {'preg-taper-limit','phen-taper-limit'}:initial=['diagnosis','mode','selected_source_product_profile_version']
    inputs=[i for i in r['inputs'] if i['data_type']!='structured_form' or i['requirement_predicate']['kind']!='always']
    pending=inputs[:];inputs=[]
    while pending:
        names={i['input_id'] for i in pending}
        ready=next((i for i in pending if not names.intersection(dependencies(i))),None)
        assert ready is not None, 'Cyclic question dependencies: '+rid
        inputs.append(ready);pending.remove(ready)
    first='check_'+inputs[0]['input_id'] if inputs else 'source_result'
    nodes=[dict(node_id='select',ask=initial,edges=[dict(target='phase')]),dict(node_id='phase',ask_policy='Every explicit selected/A status costs one fact except first-start not_started derived from start selection. Nonstart selected_mode alone has no current-use evidence; final source action may use consumed known positive actual current_dose; B remains separate',edges=[dict(target=first)])]
    for n,i in enumerate(inputs):
        k=i['input_id'];nxt='check_'+inputs[n+1]['input_id'] if n+1<len(inputs) else 'source_result'
        nodes.append(dict(node_id='check_'+k,requirement_predicate=i['requirement_predicate'],bounded_terminal_scope_override='A declared primary action/exclusion/caution or explicitly unselected example uses its named sufficient facts, source actor/required phase and all supplied context. Unused numerical/admission fields remain unassessed. This is a finite prepared result specification, not a medical branch evaluator.',requires_known_inputs=dependencies(i),edges=[dict(when='active',target='ask_'+k),dict(when='inactive',target=nxt)],inactive='not_assessed/context warning; not negative'))
        nodes.append(dict(node_id='ask_'+k,source_refs=i['source_refs'],source_locator=i['source_locator'],fact_cost_policy='facts(input, full scenario): fixed metadata zero; every actual stage/record separate',edges=[dict(target='assess_'+k)]))
        nodes.append(dict(node_id='assess_'+k,scope='typed value recorded; clinical terminal is prepared expected, no medical evaluator',edges=[dict(target=nxt)]))
    types=sorted({c['expected']['result_type'] for c in F if c['rule_id']==rid})
    nodes.append(dict(node_id='source_result',scope='prepared expected selects terminal; no calculator',edges=[dict(target='terminal_'+t) for t in types]))
    nodes.extend(dict(node_id='terminal_'+t,result_type=t,edges=[]) for t in types)
    for i in r['inputs']:
        for b in C[rid]['branches']:
            ledger.append(dict(rule_id=rid,branch_id=b['branch_id'],result_type=b['expected_output']['result_type'],input_id=i['input_id'],question=i['question_ru'],data_type=i['data_type'],unit=i['unit'],source_refs=' | '.join(i['source_refs']),versions=' | '.join(S[s]['version_or_update_date'] for s in i['source_refs']),locator=i['source_locator'],predicate=json.dumps(i['requirement_predicate'],ensure_ascii=False),role=i['input_role'],reason=i['necessity_reason'],fact_origin=i['fact_origin'],unknown_action=i['action_if_unknown'],contract='result_contracts.yaml#rules/'+rid,review_depth='explicit decision where listed in necessity_decisions; unchanged operands/source gates retained; independent primary audit required'))
    selected=[];seen=set()
    for c in [c for c in F if c['rule_id']==rid and (c['branch_id'] or c['expected']['result_type']=='source_stop_action' or '--r3-' in c['case_id'] or '--audit-v2-' in c['case_id'] or '--audit-recheck-' in c['case_id'] or '--audit-final-' in c['case_id'] or c['expected'].get('reason_ids') or c['expected'].get('terminal_source_certificate'))]:
        scenario_label=c['case_id'] if c['expected'].get('terminal_source_certificate') else c['branch_id'] or c['case_id'].split('--',1)[1]
        label=(scenario_label,c['external_context'].get('treatment_phase'),c['external_context'].get('target_treatment_phase'),tuple(i['input_id'] for i in inputs if active(i,c)))
        if label in seen:continue
        seen.add(label);init=initial[:];ctx=c['external_context']
        if ctx.get('treatment_phase') in {'ongoing','unknown','not_started'} and not (r['identity']['mode']=='start' and ctx.get('treatment_phase')=='not_started'):init.append('selected_drug_treatment_phase')
        if r['identity']['mode']=='switch' and 'target_treatment_phase' in ctx:init.append('target_treatment_phase')
        asked=[f for i in inputs if active(i,c) for f in facts(i,c,r)]
        trace=['select','phase']
        for i in inputs:
            k=i['input_id'];trace.append('check_'+k)
            if active(i,c):trace.extend(['ask_'+k,'assess_'+k])
        trace.extend(['source_result','terminal_'+c['expected']['result_type']])
        n=len(init)+len(asked);variable=any('unknown_plan_cardinality' in x for x in asked)
        complex_reason=[]
        if any(m.get('interaction_class')=='maoi' for m in c['given'].get('medicines',[]) if isinstance(m,dict)):complex_reason.append('source MAOI interaction/washout branch; type and stopped timestamp counted separately')
        if ctx.get('treatment_phase')=='ongoing' and r['identity']['mode']=='start':complex_reason.append('already taking identified drug; explicitly different from first administration')
        if r['identity']['mode']=='switch':complex_reason.append('two-product transition; both source conditions and separately supplied A stages')
        if c['branch_id'] in {'renal_caution','renal_reduction','hepatic_reduction','joint_modifiers','organ_caution','repeat_tests','liver_caution'}:complex_reason.append('documented organ/monitoring modifier selected by actual branch')
        if 'RU-ESC' in [s['source_id'] for s in r['sources']] and r['identity']['mode']=='start' and (c['given'].get('coronary_disease') is True or c['given'].get('electrolyte_disturbance') is True):
            complex_reason.append('RU-ESC §4.4 physical p6: actual coronary disease requires pretreatment ECG, actual electrolyte disturbance requires correction; classified by the source intervention trigger for every such path, independently of question count')
        numeric=c['expected']['result_type'] in {'exact','selected_source_example'}
        ordinary=numeric and not complex_reason
        projected={i['input_id']:deepcopy(c['given'][i['input_id']]) for i in r['inputs'] if i['input_id'] in c['given'] and (active(i,c) or i['data_type']=='structured_form')}
        expected=deepcopy(c['expected'])
        action_scope=source_action_scope(r,C[rid],c)
        exclusion_scope=source_exclusion_scope(r,c)
        choice_scope=source_choice_scope(r,c)
        form_scope=source_form_scope(r,c)
        unselected_scope=unselected_example_scope(r,c)
        # A projected complete path cannot confirm values it did not receive.
        expected['confirmed_negatives']=[k for k in expected.get('confirmed_negatives',[]) if k in projected and projected[k] is False]
        expected['unassessed_context']=sorted(set(expected.get('unassessed_context',[]))|{i['input_id'] for i in inputs if i['requirement_predicate']['kind'] in {'reported_context','ongoing_selected_drug','target_ongoing','reported_current_event','reported_source_information','indication_action_choice'} and (i['input_id'] not in projected or projected[i['input_id']] in (None,'unknown','not_assessed','не исследовано','неизвестно'))})
        scope=action_scope or exclusion_scope or choice_scope or form_scope or unselected_scope
        if scope is not None:
            expected['unassessed_context']=sorted(set(expected['unassessed_context'])|{i['input_id'] for i in r['inputs'] if i['input_id'] not in projected}|{k+'.'+field for k,components in scope.get('fact_components',{}).items() for field in ['A','B'] if k+'.'+field not in components})
        if numeric:expected.update(clinical_clearance=False)
        projected_case=dict(given=projected,external_context=ctx)
        p=dict(resolved_selected_phase=selected_phase(r,projected_case)[0],selected_phase_provenance=selected_phase(r,projected_case)[1],rule_id=rid,branch_id=c['branch_id'],full_example=c['case_id'],initial_selections=init,required_independent_facts=asked,count=n,count_is_lower_bound=variable,ordinary_individual_numeric_path=ordinary,complexity_source_trigger=complex_reason,result_type=c['expected']['result_type'],within_15=ordinary and n<=15 and not variable,bounded_source_action_scope=action_scope,bounded_source_exclusion_scope=exclusion_scope,bounded_source_choice_scope=choice_scope,bounded_unselected_example_scope=unselected_scope,traversed_node_ids=trace,full_projected_given=projected,full_projected_expected=expected,full_external_context=deepcopy(ctx),count_method='Every visited active fact; fixed form/renal metadata cost zero; actual taper stage day/dose/frequency separately; no prefilling assumed; prepared expected, no dose evaluator')
        p['bounded_source_form_scope']=form_scope
        selected.append(p);paths.append(p)
    graphs.append(dict(rule_id=rid,nodes=nodes,paths=selected,scope='Research predicate traversal; final prepared expected not execution of clinical logic'))
(O/'question_graphs.yaml').write_text(yaml.safe_dump(dict(graphs=graphs,nature='static research paths'),allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'actual_question_paths.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'input_necessity.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
summary=[dict(rule_id=rid,ordinary_counts=sorted(set(p['count'] for p in paths if p['rule_id']==rid and p['ordinary_individual_numeric_path'])),maximum_ordinary_count=max((p['count'] for p in paths if p['rule_id']==rid and p['ordinary_individual_numeric_path']),default=None)) for rid in rs]
(O/'path_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(graphs),'graphs;',len(paths),'selected complete paths;',len(ledger),'per-result input rows. Ordinary maxima:',[(x['rule_id'],x['maximum_ordinary_count']) for x in summary if x['maximum_ordinary_count'] is not None])
