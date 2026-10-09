from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import sys, json, yaml, hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]; O=ROOT/'research/remediation_round3'
sys.path.insert(0,str(O))
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
m={'__file__':str(O/'verify_contracts.py'),'__name__':'independent_safe'}
exec(compile((O/'verify_contracts.py').read_text('utf8'),str(O/'verify_contracts.py'),'exec'),m)
d=m['collect'](); paths=read(O/'actual_question_paths.json'); graphs=yaml.safe_load((O/'question_graphs.yaml').read_text('utf8'))['graphs']
a={'__file__':str(O/'verify_final_repairs.py'),'__name__':'independent_safe','verify_contracts':SimpleNamespace(collect=m['collect'],validate=m['validate'])}
exec(compile((O/'verify_final_repairs.py').read_text('utf8').replace('import verify_contracts','').split("if __name__=='__main__':")[0],str(O/'verify_final_repairs.py'),'exec'),a)
baseline=a['check'](d,graphs,paths)
mutations=[]
for name in ['PAR_universal_history','PHEN_false_hold_protocol','PREG_borrowed_AD_protocol','unknown_age_as_adult','unknown_A_action','hidden_A_phase','controller_after_dependent','proposed_dose_as_current_use','inactive_dose_as_current_use','zero_dose_as_current_use','unknown_dose_as_current_use']:
    x=deepcopy(d);gg=deepcopy(graphs);pp=deepcopy(paths)
    if name=='PAR_universal_history':x['contracts']['parox-taper-example']['input_requirements']['duration']={'kind':'always'}
    elif name=='PHEN_false_hold_protocol':next(i for i in x['rules']['phen-taper-limit']['inputs'] if i['input_id']=='withdrawal_severity')['necessity_reason']='Тяжесть задаёт hold/resumption/slower по инструкции'
    elif name=='PREG_borrowed_AD_protocol':x['rules']['preg-taper-limit']['logic']['actions'].append('КР предусматривает более медленную индивидуальную отмену')
    elif name=='unknown_age_as_adult':next(c for c in x['cases'] if c['case_id']=='preg-taper-limit--audit-final-age-unknown')['expected']['population_applicability']='adult'
    elif name=='unknown_A_action':next(c for c in x['cases'] if '--audit-final-A-phase-unknown' in c['case_id'])['expected']['source_actions']=[dict(action='discontinue_selected_medication',medication_role='selected_or_A')]
    elif name=='hidden_A_phase':next(p for p in pp if 'selected_drug_treatment_phase' in p['initial_selections'])['initial_selections'].remove('selected_drug_treatment_phase')
    elif name=='controller_after_dependent':
        ns=next(g for g in gg if g['rule_id']=='ser-adult-adjust')['nodes'];node=next(n for n in ns if n['node_id']=='assess_clinician_action');ns.remove(node);ns.append(node)
    else:
        i=next(i for i in x['rules']['ser-adult-adjust']['inputs'] if i['input_id']=='current_dose')
        if name=='proposed_dose_as_current_use':i['fact_semantics']='proposed_daily_dose'
        elif name=='inactive_dose_as_current_use':i['requirement_predicate']={'kind':'reported_context'}
        else:next(c for c in x['cases'] if c['case_id']=='ser-adult-adjust--audit-recheck-symptomatic_hyponatremia-positive')['given']['current_dose']=0 if name=='zero_dose_as_current_use' else 'unknown'
    found=a['check'](x,gg,pp);mutations.append(dict(name=name,rejected=bool(found),evidence=found[:2]))
enum_mutations=[]
for name in ['unrecognized_A_phase','unknown_A_missing_from_domain']:
    x=deepcopy(d)
    if name=='unrecognized_A_phase':x['cases'][0]['external_context']['treatment_phase']='unrecognized_phase'
    else:x['schema']['external_context']['treatment_phase']['allowed_values'].remove('unknown')
    found=m['validate'](x);enum_mutations.append(dict(name=name,rejected=any('phase declaration/value not typed' in s for s in found)))

def active(i,g,ctx):
    p=i['requirement_predicate'];k=p['kind']
    if k=='always':return True
    if k in {'reported_source_information','reported_current_event'}:return i['input_id'] in g
    if k=='field_true':return g.get(p['field']) is True
    if k=='all_equals':return all(g.get(f)==v for f,v in p['values'].items())
    if k in {'increase','action_choice'}:return g.get('clinician_action') in p['actions']
    return False
def phase(r,g,ctx):
    explicit=ctx.get('treatment_phase','selected_mode')
    if explicit in {'ongoing','unknown','not_started'}:return explicit,'explicit_treatment_phase'
    if r['identity']['mode']=='start':return 'not_started','first_start_selection'
    i=next((i for i in r['inputs'] if i['input_id']=='current_dose'),None)
    v=g.get('current_dose')
    if i and i.get('fact_semantics')=='actually_taken_current_daily_dose' and active(i,g,ctx) and type(v) in (int,float) and v>0:
        return 'ongoing','consumed_actual_current_dose'
    return 'unknown','selected_mode_does_not_establish_current_use'
phase_errors=[]; actors=0
for c in d['cases']:
    r=d['rules'][c['rule_id']];e=c['expected'];ctx=c['external_context']
    owner=next((i['source_refs'][0] for i in r['inputs'] if i['input_id'] in {'form','from_form'}),None)
    is_A=owner is not None and e.get('stop_medication')==owner or any(x.get('medication_role')=='selected_or_A' for x in e.get('source_actions',[]))
    if is_A:
        actors+=1
        if phase(r,c['given'],ctx)[0]!='ongoing':phase_errors.append(c['case_id'])
projection_phase_errors=[]
for p in paths:
    actual=phase(d['rules'][p['rule_id']],p['full_projected_given'],p['full_external_context'])
    if actual!=(p['resolved_selected_phase'],p['selected_phase_provenance']):projection_phase_errors.append(p['full_example'])
# Own finite counterexamples, without requiring a running medical calculator.
r=deepcopy(d['rules']['ser-adult-adjust']); base=dict(treatment_phase='selected_mode');own=[]
for label,value,semantics,kind,explicit,wanted in [
    ('actual_positive',100,'actually_taken_current_daily_dose','always','selected_mode','ongoing'),
    ('zero',0,'actually_taken_current_daily_dose','always','selected_mode','unknown'),
    ('unknown','unknown','actually_taken_current_daily_dose','always','selected_mode','unknown'),
    ('proposed',100,'proposed_daily_dose','always','selected_mode','unknown'),
    ('inactive',100,'actually_taken_current_daily_dose','reported_context','selected_mode','unknown'),
    ('explicit_unknown',100,'actually_taken_current_daily_dose','always','unknown','unknown'),
    ('explicit_notstarted',100,'actually_taken_current_daily_dose','always','not_started','not_started')]:
    rr=deepcopy(r);i=next(i for i in rr['inputs'] if i['input_id']=='current_dose');i['fact_semantics']=semantics;i['requirement_predicate']={'kind':kind}
    resolved=phase(rr,{'current_dose':value},{'treatment_phase':explicit})[0]
    own.append(dict(case=label,expected_phase=wanted,actual_phase=resolved,pass_=resolved==wanted))
population=[];par=[]
for c in d['cases']:
    rid=c['rule_id'];e=c['expected'];g=c['given']
    if rid in {'preg-taper-limit','phen-taper-limit'}:
        if '--audit-final-age-' in c['case_id']:
            age=g.get('age');wanted='adult' if type(age) in (int,float) and age>=18 else 'nonadult_plan_not_established' if type(age) in (int,float) else 'not_assessed'
            ok=e.get('population_applicability')==wanted and e.get('individual_duration_weeks') is None and e.get('individual_taper_schedule') is None and not e['schedule'] and e['total_daily_dose_mg'] is None and e['clinical_clearance'] is False
            if rid=='preg-taper-limit':ok=ok and e['duration_constraint']['scope']=='adult_source_reference_only' and e['duration_constraint']['minimum_weeks']==1
            population.append(dict(case=c['case_id'],population=wanted,pass_=ok,source=rid,locator='RU-PREG §4.2 physical4–5/§4.3 physical6; RU-PHEN §4.2 physical2–3/§4.3 physical3'))
    if rid=='parox-taper-example' and '--audit-final-qualitative-' in c['case_id']:
        par.append(dict(case=c['case_id'],pass_=e['result_type']=='clinician_choice' and not e['schedule'] and e['total_daily_dose_mg'] is None and not e['missing_fields'],locator='RU-PAROX §4.2 physical3–4; context §4.4 physical9–10'))
dependency_errors=[]
for graph in graphs:
    nodes={n['node_id']:j for j,n in enumerate(graph['nodes'])}
    for i in d['rules'][graph['rule_id']]['inputs']:
        p=i['requirement_predicate'];k=p['kind'];deps=[]
        if k=='field_true':deps=[p['field']]
        if k=='all_equals':deps=list(p['values'])
        if k in {'increase','action_choice'}:deps=['clinician_action']
        if k in {'maoi_record','stopped_maoi_record'}:deps=['medicines']
        if k=='ecg_if_cad':deps=['coronary_disease']
        if k=='correction_if_electrolytes':deps=['electrolyte_disturbance']
        for f in deps:
            if nodes.get('assess_'+f,10**9)>=nodes.get('check_'+i['input_id'],-1):dependency_errors.append(graph['rule_id']+'/'+i['input_id']+'/'+f)
prev={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (O/'recheck2_snapshot/research/remediation_round3/rules').glob('*.yaml')}
numeric_changes=[rid for rid,r in d['rules'].items() if r['clinical_parameters']!=prev[rid]['clinical_parameters']]
save('recheck3_checks.json',dict(author_final_baseline_errors=baseline,author_final_mutations=mutations,author_enum_mutations=enum_mutations,own_phase_counterexamples=own,all_current_A_action_cases_checked=actors,current_A_action_phase_errors=phase_errors,projected_phase_errors=projection_phase_errors,population_primary_expected_checks=population,par_qualitative_primary_expected_checks=par,dependency_order_errors=dependency_errors,parameter_objects_changed=numeric_changes,cases=len(d['cases']),paths=len(paths),scope='Finite independent recheck of R2-01..04 and full static/projection set; not exhaustive clinical audit of all source clauses or necessity decisions'))
print(json.dumps(dict(cases=len(d['cases']),paths=len(paths),baseline=baseline,mutations_rejected=all(x['rejected'] for x in mutations+enum_mutations),A_phase_errors=phase_errors,projection_phase_errors=projection_phase_errors,population_failures=[x for x in population if not x['pass_']],par_failures=[x for x in par if not x['pass_']],dependency_errors=dependency_errors,numeric_changes=numeric_changes),ensure_ascii=False))
