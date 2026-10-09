"""Read-only acceptance checks; all output stays in this independent audit directory.

Medical assertions reflect facts independently read in the named primary PDFs.
They are not an implementation of the proposed clinical calculator.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter, defaultdict
import json, yaml, hashlib

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
R3 = ROOT / 'research/remediation_round3'
initial_manifest=json.loads((OUT/'initial_manifest.json').read_text(encoding='utf-8'))
current_manifest=json.loads((R3/'final_manifest.json').read_text(encoding='utf-8'))
if current_manifest['snapshot_sha256']!=initial_manifest['executor_snapshot_id'] or any(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()!=x['sha256'] for x in current_manifest['files']):
    raise RuntimeError('Audit snapshot changed; do not overwrite original checks with a different revision.')

def read(name):
    p = R3 / name
    return json.loads(p.read_text(encoding='utf-8')) if p.suffix == '.json' else yaml.safe_load(p.read_text(encoding='utf-8'))

def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

rules = {p.stem: yaml.safe_load(p.read_text(encoding='utf-8')) for p in (R3/'rules').glob('*.yaml')}
sources = read('sources.json')
contracts = read('result_contracts.yaml')['rules']
cases = read('full_scenarios.json')['cases']
paths = read('actual_question_paths.json')
graphs = {g['rule_id']: g for g in read('question_graphs.yaml')['graphs']}

# Safe reuse of the read author's validator, without entering its writing __main__.
module = {'__file__': str(R3/'verify_contracts.py'), '__name__': 'independent_read_only_validator'}
exec(compile((R3/'verify_contracts.py').read_text(encoding='utf-8'), str(R3/'verify_contracts.py'), 'exec'), module)
data = module['collect']()
errors = module['validate'](data)
author_negatives = []
for filename, marker in [('verify_new_negative_checks.py', 'rows=[]'), ('verify_v2_negatives.py', 'rows=[]')]:
    code = (R3/filename).read_text(encoding='utf-8').replace('from verify_contracts import collect,validate', '')
    ns = {'__file__': str(R3/filename), '__name__': 'independent_isolated_negative', 'collect': module['collect'], 'validate': module['validate']}
    exec(compile(code.split(marker)[0], filename, 'exec'), ns)
    if 'checks' in ns:
        for key, expected_error in ns['checks'].items():
            obj = deepcopy(data); ns['apply'](obj, key)
            found = module['validate'](obj)
            author_negatives.append({'origin': filename, 'name': key, 'rejected': any(expected_error in e for e in found)})
    else:
        for key, mutate in ns['mutations'].items():
            obj = deepcopy(data); mutate(obj)
            author_negatives.append({'origin': filename, 'name': key, 'rejected': bool(module['validate'](obj))})

# Recompute predicate selection from the full scenario, independently of supplied trace/count.
def enabled(i, given, context):
    p = i['requirement_predicate']; kind = p['kind']
    if kind == 'always': return True
    if kind in ('increase', 'action_choice'): return given.get('clinician_action') in p['actions']
    if kind == 'ongoing_selected_drug': return context.get('treatment_phase') == 'ongoing'
    if kind == 'field_true': return given.get(p['field']) is True
    if kind == 'ecg_if_cad': return given.get('coronary_disease') is True
    if kind == 'correction_if_electrolytes': return given.get('electrolyte_disturbance') is True
    if kind in ('maoi_record', 'stopped_maoi_record'):
        return any(m.get('interaction_class') in ('maoi','unknown') and (kind == 'maoi_record' or m.get('status') == 'stopped') for m in given.get('medicines', []) if isinstance(m,dict))
    return False

def independent_facts(i, given):
    key, dtype = i['input_id'], i['data_type']
    if dtype == 'structured_renal': return [key+'.clinician_confirmed_source_value']
    if dtype == 'paired_allergy': return [key+'.A', key+'.B']
    if dtype == 'record_map':
        return [key+'.'+m['record_id'] for m in given.get('medicines', []) if m.get('interaction_class') == 'maoi' and (key == 'maoi_type' or m.get('status') == 'stopped')]
    if dtype == 'medication_list':
        ms = given.get(key)
        return [key+'.'+m['record_id']+'.'+k for m in ms for k in ('inn','status')] if isinstance(ms,list) and ms else [key+'.confirmed_empty_or_unknown_list']
    if dtype == 'dose_schedule':
        plan = given.get(key); stages = plan.get('stages',[]) if isinstance(plan,dict) else []
        return [key+f'.stage{n}.'+k for n,_ in enumerate(stages,1) for k in ('start_day','total_daily_mg','administrations_per_day')] or [key+'.unknown_plan_cardinality']
    return [key]

by_case = {c['case_id']:c for c in cases}
path_rows, projection_conflicts, graph_errors = [], [], []
for path in paths:
    rid = path['rule_id']; rule = rules[rid]; c = by_case[path['full_example']]
    ins = [i for i in rule['inputs'] if i['data_type'] != 'structured_form']
    initial = ['diagnosis','mode','identified_product_form_strength'] if rule['identity']['mode'] != 'switch' else ['diagnosis','mode','identified_A_product_form_strength','identified_B_product_form_strength']
    if rule['identity']['mode']=='start' and c['external_context'].get('treatment_phase')=='ongoing': initial += ['ongoing_selected_drug_phase']
    if rule['identity']['mode']=='switch' and 'target_treatment_phase' in c['external_context']: initial += ['target_treatment_phase']
    facts = [fact for i in ins if enabled(i,c['given'],c['external_context']) for fact in independent_facts(i,c['given'])]
    n = len(initial) + len(facts)
    asked = {'ask_'+i['input_id'] for i in ins if enabled(i,c['given'],c['external_context'])}
    trace_asked = {x for x in path['traversed_node_ids'] if x.startswith('ask_')}
    nd = {x['node_id']:x for x in graphs[rid]['nodes']}
    trace = path['traversed_node_ids']
    edges_ok = all(b in {x['target'] for x in nd[a]['edges']} for a,b in zip(trace,trace[1:]))
    row = {'rule_id':rid,'case_id':c['case_id'],'branch_id':c['branch_id'],'recomputed_count':n,'author_count':path['count'],'same_facts':facts==path['required_independent_facts'],'predicate_trace_matches':asked==trace_asked,'edges_exist':edges_ok,'ordinary':path['ordinary_individual_numeric_path'],'complexity':path['complexity_source_trigger'],'count_is_lower_bound':any('unknown_plan_cardinality' in f for f in facts),'within_15_by_count':n<=15,'independent_facts':facts,'initial_selections':initial}
    path_rows.append(row)
    if n != path['count'] or not row['same_facts'] or not row['predicate_trace_matches'] or not edges_ok: graph_errors.append(row)
    given = path['full_projected_given']; exp = path['full_projected_expected']
    absent = [k for k in exp.get('confirmed_negatives',[]) if k not in given]
    overlap = sorted(set(exp.get('confirmed_negatives',[])) & set(exp.get('unassessed_context',[])))
    if absent or overlap: projection_conflicts.append({'rule_id':rid,'case_id':c['case_id'],'absent_confirmed_negatives':absent,'negative_and_unassessed':overlap})
ordinary = []
for rid in rules:
    pp=[p for p in path_rows if p['rule_id']==rid and p['ordinary']]
    ordinary.append({'rule_id':rid,'counts':sorted(set(x['recomputed_count'] for x in pp)),'maximum':max((x['recomputed_count'] for x in pp),default=None),'path_count':len(pp)})
save('independent_paths.json', {'scope':'All 255 supplied traces recomputed from full givens and rule predicates. Completeness of all possible medical alternatives is not established by this traversal.', 'paths':path_rows,'ordinary_summary':ordinary,'graph_errors':graph_errors,'projection_conflicts':projection_conflicts})

# Every complete given/context with conflicting expected is a material consistency candidate.
groups=defaultdict(list)
for c in cases:
    groups[(c['rule_id'],json.dumps(c['given'],sort_keys=True,ensure_ascii=False),json.dumps(c['external_context'],sort_keys=True,ensure_ascii=False))].append(c)
duplicates=[]
for group in groups.values():
    signatures={json.dumps(c['expected'],sort_keys=True,ensure_ascii=False) for c in group}
    if len(signatures)>1: duplicates.append({'rule_id':group[0]['rule_id'],'cases':[c['case_id'] for c in group],'different_complete_expected':len(signatures)})
save('complete_given_consistency.json', {'groups_with_different_expected':duplicates,'scope':'Raw whole-object difference, may include provenance/presentation rather than dose; each candidate requires review.'})

primary=[]
def check(name, condition, source, locator, cases_checked):
    primary.append({'name':name,'pass':bool(condition),'source':source,'locator':locator,'cases_checked':cases_checked})
def selected(rid, pattern): return [c for c in cases if c['rule_id']==rid and pattern in c['case_id']]
def cp(rid,p): return next(x for x in rules[rid]['clinical_parameters'] if x['parameter_id']==p)
check('AGO depression25 / GAD25 and distinct higher2/4 weeks',cp('ago-depression-start','start')['value']==25 and cp('ago-gad-start','start')['value']==25 and cp('ago-depression-start','earliest_higher_stage')['value']==2 and cp('ago-gad-start','earliest_higher_stage')['value']==4,'RU-AGO','§4.2 pp1–2',[])
check('AGO repeat48 and monitoring3/6/12/24',cp('ago-gad-start','repeat_liver_tests_hours')['value']==48 and cp('ago-gad-start','liver_monitoring_weeks')['value']==[3,6,12,24],'RU-AGO','§4.4 pp3–4',[])
check('DULOX30/60 and elderly2weeks',cp('dulox-gad-start','usual_start')['value']==30 and cp('dulox-gad-start','with_depression_start')['value']==60 and cp('dulox-gad-start','elderly_initial_period')['value']==2,'RU-DULOX','§4.2 pp2–3',[])
cs=selected('dulox-taper-limit','branch-source_limit')
check('DULOX no ordinary oneweek taper',all(c['expected']['duration_constraint']['chosen_minimum_weeks']>=2 for c in cs),'RU-DULOX','§4.2 p3 and §4.4 p6',[c['case_id'] for c in cs])
check('FLUV50or100 and >150 division threshold',cp('fluvox-depression-start','start_options')['value']==[50,100] and cp('fluvox-depression-start','divided_dose_threshold')['value']==150,'RU-FLUVOX','§4.2 p2',[])
check('PREG GAD150/300/450/600 and weekly',all(cp('preg-gad-start','d'+str(n))['value']==n for n in [150,300,450,600]) and cp('preg-gad-start','interval')['value']==1,'RU-PREG','§4.2 p3',[])
check('PREG renal cutoffs15/30/60 and variable25–50',cp('preg-renal-start','clcr_cutoffs')['value']==[15,30,60] and cp('preg-renal-start','start_15_30')['lower']==25 and cp('preg-renal-start','start_15_30')['upper']==50,'RU-PREG','Table1 p5; visually checked formula/table/footnotes',[])
check('PAROX10 weekly10 with40recommended60max',cp('parox-panic-kr','start')['value']==10 and cp('parox-panic-kr','step')['value']==10 and cp('parox-panic-kr','recommended_dose')['value']==40 and cp('parox-panic-kr','maximum')['value']==60,'RU-PAROX / RU-PANIC','§4.2 p3 / KR p26',[])
check('PAROX taper example10/wk until20 hold1',cp('parox-taper-example','weekly_decrement')['value']==10 and cp('parox-taper-example','last_source_dose')['value']==20 and cp('parox-taper-example','last_hold')['value']==1,'RU-PAROX','§4.2 pp3–4',[])
check('SER25→50, selected increase50 / week max200',cp('ser-panic-start','start')['value']==25 and cp('ser-panic-start','after_week')['value']==50 and cp('ser-adult-adjust','step')['value']==50 and cp('ser-adult-adjust','maximum')['value']==200,'RU-SER','§4.2 pp2–3',[])
cs=[c for c in cases if c['rule_id'].startswith('esc-') and c['case_id'].endswith('--current-clcr-30')]
check('ESC exactly30 sourcegap gives no dose',bool(cs) and all(c['expected']['result_type'] not in ('exact','selected_source_example') for c in cs),'RU-ESC','§4.2 p3 >30 and <30; visually checked',[c['case_id'] for c in cs])
cs=selected('esc-elderly-start','current-age-65')
check('ESC65 no automatic >65 special dose',bool(cs) and all(c['expected'].get('total_daily_dose_mg')!=5 for c in cs),'RU-ESC','§4.2 p3 strictly older65',[c['case_id'] for c in cs])
check('XR75,225,>=2week / panic37.5,7day then75',cp('venla-xr-gad-start','start')['value']==75 and cp('venla-xr-gad-start','maximum')['value']==225 and cp('venla-xr-gad-start','increase_min_interval')['value']==2 and cp('venla-xr-panic-form-limit','initial_dose')['value']==37.5 and cp('venla-xr-panic-form-limit','initial_duration')['value']==7,'RU-VENLA-XR','§4.2 pp2–5',[])
cs=[c for c in cases if c['rule_id'].startswith('venla-xr-') and 'diastolic-BP-100.01' in c['case_id']]
check('XR known ongoing BP>100 stops',bool(cs) and all(c['expected']['result_type']=='source_stop_action' for c in cs),'RU-VENLA-XR','§4.4 p9',[c['case_id'] for c in cs])
save('primary_expected_checks.json',{'scope':'Independent selected source assertions; not proof of all 4953 expected or all unique medical conditions','checks':primary})

# Additional own mutation detectors: checks rooted in independently observed evidence.
def provenance_ok(obj):
    errors=[]
    def walk(v,path):
        if isinstance(v,dict):
            sid=v.get('source_id')
            if sid in sources and 'version' in v and v['version']!=sources[sid]['version_or_update_date']: errors.append(path)
            for k,x in v.items():walk(x,path+'/'+str(k))
        elif isinstance(v,list):
            for k,x in enumerate(v):walk(x,path+'/'+str(k))
    walk(obj,'');return not errors
def projection_ok(p):
    e=p['full_projected_expected'];g=p['full_projected_given']
    return all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])) and not set(e.get('confirmed_negatives',[]))&set(e.get('unassessed_context',[]))
own=[]
normal=next(p for p in paths if p['ordinary_individual_numeric_path'])
clean=deepcopy(normal);clean['full_projected_expected']['confirmed_negatives']=[k for k,v in clean['full_projected_given'].items() if v is False];clean['full_projected_expected']['unassessed_context']=[k for k in clean['full_projected_expected'].get('unassessed_context',[]) if k not in clean['full_projected_expected']['confirmed_negatives']]
for name, mutate in [('unknown_to_negative',lambda p:p['full_projected_expected']['confirmed_negatives'].append('absent_patient_fact')),('hidden_input',lambda p:p['full_projected_given'].pop('age')),('understated_count',lambda p:p.update(count=p['count']-1)),('other_mode_required',lambda p:p['required_independent_facts'].append('future_increase_dose'))]:
    x=deepcopy(clean);mutate(x)
    accepted=projection_ok(x) and x['count']==len(x['initial_selections'])+len(x['required_independent_facts']) and 'age' in x['full_projected_given']
    own.append({'name':name,'rejected':not accepted})
for n, expected in [(15,True),(16,False)]:own.append({'name':'inclusive_count_boundary_'+str(n),'rejected':(n<=15)==expected,'technical_boundary_only':True})
base={'source_id':'RU-VENLA-IR','version':sources['RU-VENLA-IR']['version_or_update_date']}
wrong=deepcopy(base);wrong['version']=sources['RU-VENLA-XR']['version_or_update_date']
own.append({'name':'IR_version_replaced_by_XR','rejected':provenance_ok(base) and not provenance_ok(wrong)})
mutdata=deepcopy(data);mutdata['contracts']['preg-gad-start']['required_inputs'].remove('misuse_risk_assessment')
own.append({'name':'missing_explicit_PREG_preuse_assessment','rejected':bool(module['validate'](mutdata))})
def product_binding(form):
    sid=form.get('source_id')
    if sid not in sources: return False
    registration=sources[sid].get('registration',{})
    expected_ru=registration.get('registration_number') if isinstance(registration,dict) else None
    if not expected_ru:
        observation=sources[sid].get('registry_observation',{})
        expected_ru=observation.get('registration_number')
    return form.get('source_version')==sources[sid]['version_or_update_date'] and (not expected_ru or form.get('registration_number')==expected_ru)
form=deepcopy(next(c for c in cases if c['rule_id']=='preg-gad-start' and c['case_id'].endswith('--branch-normal'))['given']['form']) if any(c['case_id']=='preg-gad-start--branch-normal' for c in cases) else deepcopy(next(c for c in cases if c['rule_id']=='preg-gad-start')['given']['form'])
wrong_form=deepcopy(form);wrong_form['source_version']='historical unverified edition'
own.append({'name':'form_version_substitution','rejected':product_binding(form) and not product_binding(wrong_form)})
structured_renal=deepcopy(next(c for c in cases if c['rule_id']=='esc-gad-start')['given']['renal'])
wrong_renal=deepcopy(structured_renal);wrong_renal['unit']='mL/min/1.73m2'
own.append({'name':'renal_absolute_vs_indexed_unit_substitution','rejected':structured_renal['metric']=='CLcr' and structured_renal['unit']=='mL/min' and wrong_renal['unit']!='mL/min'})
own.append({'name':'explicit_prerequisite_wrongly_reported_only','rejected':enabled({'requirement_predicate':{'kind':'always'}},{},{}) and not enabled({'requirement_predicate':{'kind':'reported_context'}},{},{})})
own.append({'name':'hidden_conditional_trigger_as_normal','rejected':not enabled({'requirement_predicate':{'kind':'field_true','field':'reproductive_population'}},{},{}) and enabled({'requirement_predicate':{'kind':'field_true','field':'reproductive_population'}},{'reproductive_population':True},{})})
save('independent_checks.json', {'author_validator_independently_run':True,'baseline_errors':errors,'author_negative_mutations_reexecuted_isolated':author_negatives,'own_mutations':own,'graph_errors':len(graph_errors),'projection_inconsistencies':len(projection_conflicts),'clinical_calculator_executed':False,'limits':['Static checks do not evaluate full medical truth of each predicate/branch.','Reused authored detectors test exactly the read detector properties, not independent medical validation.','Own count follows declared predicate applicability; primary necessity remains separately reviewed.']})
print(json.dumps({'static_errors':len(errors),'author_negatives':len(author_negatives),'author_missed':[x['name'] for x in author_negatives if not x['rejected']],'own_mutations':len(own),'primary_assertions':len(primary),'primary_failures':[x['name'] for x in primary if not x['pass']],'paths':len(paths),'graph_errors':len(graph_errors),'projection_conflicts':len(projection_conflicts),'duplicate_candidates':len(duplicates),'ordinary':ordinary},ensure_ascii=False))
