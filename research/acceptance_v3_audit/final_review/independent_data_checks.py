"""Independent checks of frozen research data. Writes only this review directory."""
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import json, yaml, hashlib, collections, sys
sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
R=ROOT/'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
def read(p): return json.loads(p.read_text('utf8'))
def save(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
S=read(R/'sources.json'); RULES={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')}
C={c['case_id']:c for c in read(R/'full_scenarios.json')['cases']}; P=read(R/'actual_question_paths.json')
CON=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules']
checks=[]; errors=[]
def ck(label,ok,cid=None,detail=None):
    z=dict(check=label,pass_=bool(ok),case_id=cid,detail=detail);checks.append(z)
    if not ok:errors.append(z)
def phase(r,c,used=None):
    x=c['external_context']; g=c['given']; p=x.get('treatment_phase','selected_mode')
    if p in ['ongoing','unknown','not_started']: return p
    if r['identity']['mode']=='start':return 'not_started'
    i=next((i for i in r['inputs'] if i['input_id']=='current_dose'),None)
    if not i or i.get('fact_semantics')!='actually_taken_current_daily_dose':return 'unknown'
    pred=i['requirement_predicate'];active=pred['kind']=='always' or pred['kind']=='field_true' and g.get(pred['field']) is True
    d=g.get('current_dose')
    return 'ongoing' if active and (used is None or 'current_dose' in used) and type(d) in [int,float] and d>0 else 'unknown'
def active(i,c,bounded=None):
    k=i['input_id']; p=i['requirement_predicate'];kind=p['kind'];g=c['given'];x=c['external_context']
    if bounded is not None:return k in bounded['used_fields']
    if kind=='always':return True
    if kind in ['reported_context','reported_current_event','reported_source_information']:return k in g
    if kind=='indication_action_choice':return k in g or x.get('diagnosis') in p['diagnoses'] and g.get('clinician_action','not_chosen') in p['actions']
    if kind in ['action_choice','increase']:return g.get('clinician_action','not_chosen') in p['actions']
    if kind=='field_true':return g.get(p['field']) is True
    if kind=='all_equals':return all(g.get(f)==v for f,v in p['values'].items())
    if kind=='ecg_if_cad':return g.get('coronary_disease') is True
    if kind=='correction_if_electrolytes':return g.get('electrolyte_disturbance') is True
    if kind=='ongoing_selected_drug':return x.get('treatment_phase')=='ongoing'
    if kind=='target_ongoing':return x.get('target_treatment_phase')=='ongoing'
    if kind in ['maoi_record','stopped_maoi_record']:
        ms=g.get('medicines');return isinstance(ms,list) and any(isinstance(m,dict) and m.get('interaction_class')=='maoi' and (kind=='maoi_record' or m.get('status')=='stopped') for m in ms)
    return False
def facts(i,c):
    k=i['input_id'];g=c['given'];t=i['data_type'];v=g.get(k)
    if t=='structured_renal':return [k+'.clinician_confirmed_source_value']
    if t=='paired_allergy':return [k+'.A',k+'.B']
    if t=='record_map':return [k+'.'+m['record_id'] for m in g.get('medicines',[]) if isinstance(m,dict) and m.get('interaction_class')=='maoi' and (k=='maoi_type' or m.get('status')=='stopped')]
    if t=='medication_list':
        return [k+'.'+m['record_id']+'.'+f for m in v for f in ['inn','status']+(['additional_product'] if 'additional_product' in m else [])] if isinstance(v,list) and v else [k+'.confirmed_empty_or_unknown_list']
    if t=='dose_schedule':
        stages=v.get('stages',[]) if isinstance(v,dict) else []
        return [k+f'.stage{n}.'+f for n,_ in enumerate(stages,1) for f in ['start_day','total_daily_mg','administrations_per_day']] or [k+'.unknown_plan_cardinality']
    return [k]
def walk(v,path=''):
    if isinstance(v,dict):
        yield path,v
        for k,x in v.items():yield from walk(x,path+'/'+k)
    elif isinstance(v,list):
        for n,x in enumerate(v):yield from walk(x,path+'/'+str(n))
bindings=[]
for container,v in [('contracts',CON),('cases',list(C.values())),('rules',RULES)]:
    for loc,d in walk(v):
        sid=d.get('source_id');sha=d.get('sha256');version=d.get('version')
        if sid in S and sha is not None and version is not None:
            ok=(sha==S[sid].get('document_fingerprint',{}).get('sha256') and version==S[sid]['version_or_update_date']) if '/document_copies/' not in loc else any(sha==z.get('sha256') and version==z.get('version') for z in S[sid].get('document_copies',[]))
            ck('exact nested source owner/version/SHA',ok,detail=[container,loc,sid]);bindings.append(dict(container=container,path=loc,source=sid,pass_=ok))
save('source_binding_checks.json',bindings)
optional=collections.Counter(); stop_scopes=[]; count_rows=[]
future=['duration_constraint','withdrawal_rules','target_source_start_mg','overlap_allowed_on_first_day_of_A_reduction','overlap_allowed','published_option_mg','recommended_mg','hold_if','source_initial_mg','initial_days','minimum_interval_days','minimum_interval_weeks','optional_stages_mg','conditional_next_total_mg']
for c in C.values():
    cid=c['case_id'];rid=c['rule_id'];r=RULES[rid];e=c['expected'];g=c['given'];x=c['external_context'];sc=e.get('source_condition',{})
    ck('no calculator execution or clinical clearance claimed',c.get('not_executed_against_calculator') is True and e.get('clinical_clearance') is False,cid)
    ck('confirmed negatives have actual False given',all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])),cid)
    if e['result_type']=='source_stop_action':
        ck('urgent result no future dose/taper/overlap payload',e.get('total_daily_dose_mg') is None and not e.get('schedule') and not any(e.get(k) is not None for k in future),cid)
        if not sc:
            ck('AGO doctor-chosen source fact only',rid=='ago-stop' and e.get('mandatory_taper') is False and not e.get('stop_medication') and not e.get('source_actions') and g.get('clinician_action')=='stop',cid)
        else:
            sid=sc.get('source_ref');key=sc.get('input');v=g.get(key);own=next((i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form' and sid in i['source_refs']),None)
            op=sc.get('operator');wanted=sc.get('value');positive=type(v) in [int,float] and v>wanted if op in ['>','greater_than'] else v==wanted if 'value' in sc else v is True or isinstance(v,str) and v in ['новые приступы','первичные/участившиеся приступы','необычные реакции']
            if sid=='RU-VENLA-XR' and key=='diastolic_BP':positive=type(v) in [int,float] and v>100
            ck('named source stop actual known cause',positive and own in g and isinstance(g[own],dict) and g[own].get('source_id')==sid,cid,[sc,v])
            ph=x.get('target_treatment_phase') if own=='to_form' else phase(r,c)
            ck('source stop own actor currently treated',ph=='ongoing',cid,[sid,own,ph])
            stop_scopes.append(dict(case_id=cid,source=sid,cause=key,value=v,owner=own,phase=ph,locator=sc.get('source_locator')))
    if sc.get('input') and e['result_type'] not in ['insufficient_data']:
        ck('explicit source cause remains in full given',sc['input'] in g,cid,sc['input'])
for p in P:
    c=C[p['full_example']];r=RULES[p['rule_id']];cid=c['case_id'];b=p.get('bounded_source_action_scope');g=p['full_projected_given'];e=p['full_projected_expected']
    required=[f for i in r['inputs'] if (i['data_type']!='structured_form' or i['requirement_predicate']['kind']!='always') and active(i,c,b) for f in facts(i,c)]
    ck('independent stored fact enumeration',sorted(required)==sorted(p['required_independent_facts']),cid,[required,p['required_independent_facts']])
    ck('honest count including selections/phase',p['count']==len(p['initial_selections'])+len(required),cid)
    used={i['input_id'] for i in r['inputs'] if active(i,c,b)}
    ck('resolved A phase agrees with explicit/consumed current evidence',p['resolved_selected_phase']==phase(r,c,used),cid)
    if b:
        sc=b['primary_cause'];own=b['source_owner_input'];key=sc['input']
        ck('bounded action count excludes other numeric always',set(b['required_cause_fields'])<=used and b['required_cause_fields'] and g.get(own,{}).get('source_id')==sc['source_ref'] and key in g,cid)
        ck('bounded action no presumed clearance/dose',not e.get('schedule') and e.get('total_daily_dose_mg') is None and e.get('clinical_clearance') is False,cid)
    ck('projected source_condition has its named fact',not e.get('source_condition',{}).get('input') or e['source_condition']['input'] in g,cid)
    ck('projected negatives actual supplied False',all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])),cid)
    nodes=p['traversed_node_ids']
    for i in r['inputs']:
        k=i['input_id'];pred=i['requirement_predicate'];kind=pred['kind'];supplied=k in c['given']
        if kind in ['reported_context','reported_source_information','reported_current_event']:
            if supplied:
                v=c['given'][k];st='positive' if v is True else 'negative' if v is False else 'unknown' if v is None or v in ['unknown','not_assessed'] else 'other'
                optional[st]+=1;ck('provided optional any state consumed and counted',k in g and g[k]==v and all(f in required for f in facts(i,c)),cid,k)
            else:
                optional['absent']+=1;ck('absent optional is unassessed, never negative',k in e.get('unassessed_context',[]) and k not in e.get('confirmed_negatives',[]),cid,k)
        deps=[pred['field']] if kind=='field_true' else list(pred['values']) if kind=='all_equals' else ['clinician_action'] if kind in ['action_choice','increase','indication_action_choice'] else ['coronary_disease'] if kind=='ecg_if_cad' else ['electrolyte_disturbance'] if kind=='correction_if_electrolytes' else ['medicines'] if kind in ['maoi_record','stopped_maoi_record'] else []
        if 'ask_'+k in nodes:
            for d in deps:
                if 'ask_'+d in nodes:ck('causal question order',nodes.index('ask_'+d)<nodes.index('ask_'+k),cid,[d,k])
    count_rows.append(dict(case_id=cid,rule_id=p['rule_id'],count=p['count'],initial=p['initial_selections'],facts=required,bounded=bool(b),ordinary=p['ordinary_individual_numeric_path'],lower_bound=p['count_is_lower_bound']))
save('source_stop_scopes.json',stop_scopes);save('counts_independent.json',count_rows)
save('independent_data_results.json',dict(snapshot='b13033a0687a28b4da4299c171ac6b88a96667e2d6888ab8aecf5e9c85af0514',rules=len(RULES),cases=len(C),selected_paths=len(P),source_bindings=len(bindings),named_stop_scopes=len(stop_scopes),optional_states=dict(optional),assertions=len(checks),errors=errors,checks=checks,scope='Own invariant/typed phase/count/ownership assertions over frozen prepared research data, not application execution or clinical validation. Predicate correctness/necessity separately assessed against primary norms.'))
print(json.dumps(dict(assertions=len(checks),errors=len(errors),first_errors=errors[:12]),ensure_ascii=False))
