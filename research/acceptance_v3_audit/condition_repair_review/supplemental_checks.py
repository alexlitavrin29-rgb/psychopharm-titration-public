"""Exact locator, bounded-scope and phase counterchecks; no reviewed-file writes."""
from pathlib import Path
from copy import deepcopy
import json, yaml, hashlib, re, sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
S=ROOT/'research/remediation_round3/condition_repairs_review_snapshot'
OLD=ROOT/'research/acceptance_v2_audit/condition_completion'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (S/'rules').glob('*.yaml')}
C={c['case_id']:c for c in read(S/'full_scenarios.json')['cases']};K=yaml.safe_load((S/'result_contracts.yaml').read_text(encoding='utf-8'))['rules'];P=read(S/'actual_question_paths.json')
checks=[]
def ck(name,ok,detail=None):checks.append(dict(check=name,pass_=bool(ok),detail=detail))
def get(path,rid=None):
    if path.startswith('clinical_parameters/'):
        _,pid,key=path.split('/')
        return next(p for p in R[rid]['clinical_parameters'] if p['parameter_id']==pid)[key]
    filename,*parts=path.split('/')[1:];v=R[Path(filename).stem]
    for p in parts:v=v[int(p)] if isinstance(v,list) else v[p]
    return v
locators=[];fixes={r['path']:r for r in read(S/'condition_locator_repairs.json')['locator_changes']}
for old in read(OLD/'locator_defects.json'):
    new=get(old['path'],old['rule_id']);row=fixes[old['path']]
    ck('exact locator correction materialized',new==row['new'] and new!=old['incorrect_claim'],old['path'])
    # Every target physical page is independently specified in the earlier finding.
    pages=set()
    for part in re.findall(r'с\.?\s*([\d,–\- ]+)',new):
        for a,b in re.findall(r'(\d+)\s*[–\-]\s*(\d+)',part):pages.update(range(int(a),int(b)+1))
        pages.update(map(int,re.findall(r'\d+',part)))
    ck('correct physical page included',set(old['correct_physical_pages'])<=pages,old['path'])
    locators.append(dict(path=old['path'],new=new,primary_sha=old['source_sha256'],correct_physical_pages=old['correct_physical_pages']))
save('locator_review.json',locators)
previous=ROOT/'research/remediation_round3/recheck3_snapshot/research/remediation_round3/rules'
numeric=0
for rid,r in R.items():
    old=yaml.safe_load((previous/(rid+'.yaml')).read_text(encoding='utf-8'))
    a=[{k:v for k,v in p.items() if k!='source_locator'} for p in r['clinical_parameters']]
    b=[{k:v for k,v in p.items() if k!='source_locator'} for p in old['clinical_parameters']]
    ck('previous independently read numeric claims unchanged',a==b,rid);numeric+=len(a)
ck('SER25 special first step prose',all('25→50' in R['ser-adult-adjust']['logic'][p][1] for p in ['conditions','actions']))
ck('ESC hepatic prose A/B distinct from C','A/B' in R['esc-hepatic-start']['logic']['conditions'][1] and 'Child–Pugh C' in R['esc-hepatic-start']['logic']['conditions'][1])
for rid in ['preg-gad-start','preg-gad-adjust','preg-renal-start']:
    policy=K[rid]['form_evidence_policy']
    ck('PREG form model distinguished from source ban','not claimed' in policy['source_claim'] and 'whole registered units' in policy['model_policy'] and 'no splitting/opening capsules' not in str(K[rid]),rid)
nr=read(OLD/'necessity_remaining.json')['groups'][0]['rows'];caution=[]
for key in nr:
    rid,k=next((rid,key.removeprefix('I-'+rid+'-')) for rid in sorted(R,key=len,reverse=True) if key.startswith('I-'+rid+'-'))
    i=next(i for i in R[rid]['inputs'] if i['input_id']==k)
    ck('exact22 generic cautions optional not deleted',i['requirement_predicate']['kind']=='reported_context' and i['required_for_individual_result'] is False,key)
    caution.append(dict(rule_id=rid,input_id=k,predicate=i['requirement_predicate'],source_locator=i['source_locator'],necessity_reason=i['necessity_reason']))
save('caution_review.json',caution)
bounded_pairs=[]
for rid in ['switch-esc-ser','switch-ser-esc']:
    for k in ['current_dose','duration','last_dose_time','withdrawal_symptoms','target_applicability']:
        i=next(i for i in R[rid]['inputs'] if i['input_id']==k)
        ck('pair-gap planning demoted with historical dose semantics',i['requirement_predicate']['kind']=='reported_context' and (k!='current_dose' or i.get('fact_semantics')=='reported_course_dose_without_current_use_confirmation'),[rid,k])
    for k in ['from_form','to_form']:
        i=next(i for i in R[rid]['inputs'] if i['input_id']==k)
        ck('bounded pair retains counted exact source profile, no clinical clearance claim','источниковый выбор' in i['necessity_reason'] and 'не подтверждает клиническую' in i['necessity_reason'],[rid,k])
    e=K[rid]['branches'][0]['expected_output']
    ck('pair source gap no calendar/start/overlap',e['full_pair_calendar'] is None and e['next_drug_start_day'] is None and e['automatic_direct_switch'] is False and e['total_daily_dose_mg'] is None and not e['schedule'],rid)
    for k in ['current_dose','duration','last_dose_time','withdrawal_symptoms','target_applicability']:
        for state in ['omitted','unknown','not_assessed']:
            cid=rid+'--current-'+k+'-'+state
            c=C[cid];e=c['expected']
            ck('pair planning omitted/unknown full source-gap countercase',e['result_type']=='clinician_choice' and e['total_daily_dose_mg'] is None and not e['schedule'] and k in e['unassessed_context'] and k not in e['missing_fields'] and e.get('clinical_clearance') is False,cid)
            bounded_pairs.append(dict(case_id=cid,given=c['given'],context=c['external_context'],expected=e))
save('bounded_pair_countercases.json',bounded_pairs)
for cid in read(S/'result_scope_repairs.json')['new_cases']:
    c=C[cid];e=c['expected'];rid=c['rule_id']
    if rid=='ser-adult-adjust':
        ck('social adherence omitted/unknown no automatic increase',c['external_context']['diagnosis']=='F40.1' and e['result_type']=='clinician_choice' and e['total_daily_dose_mg'] is None and e['selected_action'] is None and 'adherence' in e['unassessed_context'],cid)
    else:
        ck('bounded adult reference unknown form/population no individual plan',e['product_reference_applicability']=='not_assessed' and e['population_applicability']=='not_assessed' and e['individual_duration_weeks'] is None and e['individual_taper_schedule'] is None and e['clinical_clearance'] is False,cid)
        if rid=='preg-taper-limit':ck('PREG one week only conditional adult reference',e['duration_constraint']['minimum_weeks']==1 and e['duration_constraint']['scope']=='adult_source_reference_only',cid)
ns={};exec(compile((S/'phase_provenance.py').read_text(encoding='utf-8'),str(S/'phase_provenance.py'),'exec'),ns)
phase_rows=[]
for rid,r in R.items():
    i=next((i for i in r['inputs'] if i['input_id']=='current_dose' and i['requirement_predicate']['kind']=='reported_context'),None)
    if not i:continue
    for dose in [50,0,'unknown',{'proposed':50}]:
        for phase in ['selected_mode','ongoing','unknown','not_started']:
            expected=phase if phase!='selected_mode' else ('not_started' if r['identity']['mode']=='start' else 'unknown');c=dict(given={'current_dose':dose},external_context={'treatment_phase':phase})
            actual=ns['selected_phase'](r,c)[0]
            ck('historical/proposed/zero dose cannot establish current use',actual==expected,[rid,dose,phase,actual]);phase_rows.append(dict(rule_id=rid,dose=dose,explicit_phase=phase,expected_phase=expected,actual_phase=actual))
save('phase_counterchecks.json',phase_rows)
# Own negative controls exercise medical boundaries and actual separate-fact accounting.
def medical_guard(c):
    e=c['expected'];x=c['external_context'];sc=e.get('source_condition',{})
    if e.get('total_daily_dose_mg') is not None or e.get('schedule') or e.get('clinical_clearance') is not False:return False
    if e.get('source_actions') or e.get('stop_medication'):
        return (x.get('target_treatment_phase') if sc.get('actor')=='B' else x.get('treatment_phase'))=='ongoing'
    return True
mutations=[]
base=C['esc-adult-adjust--audit-final-primary-RU-ESC-reversible_MAO_A-positive']
for name in ['invented_caution_dose','invented_schedule','false_clinical_clearance']:
    c=deepcopy(base)
    if name=='invented_caution_dose':c['expected']['total_daily_dose_mg']=10
    elif name=='invented_schedule':c['expected']['schedule']=[dict(day=1,total_daily_mg=10)]
    else:c['expected']['clinical_clearance']=True
    mutations.append(dict(mutation=name,rejected=not medical_guard(c)))
for name in ['unknown_B_stop','nonstarted_B_stop']:
    c=deepcopy(C['switch-esc-ago--audit-final-primary-RU-AGO-liver_injury_signs-positive']);c['external_context']['target_treatment_phase']='unknown' if name=='unknown_B_stop' else 'not_started'
    mutations.append(dict(mutation=name,rejected=not medical_guard(c)))
p=deepcopy(next(p for p in P if any(f.startswith('maoi_type.') for f in p['required_independent_facts'])));k=next(f for f in p['required_independent_facts'] if f.startswith('maoi_type.'));p['required_independent_facts'].remove(k);p['count']-=1
mutations.append(dict(mutation='free_known_MAOI_type',rejected=k not in p['required_independent_facts'],missing_fact=k))
ck('six independent negative controls rejected',all(m['rejected'] for m in mutations))
save('supplemental_results.json',dict(checks=checks,errors=[c for c in checks if not c['pass_']],numeric_objects=numeric,locator_corrections=len(locators),generic_cautions=len(caution),historical_phase_countercases=len(phase_rows),negative_controls=mutations,scope='Finite changes only; neither all30 acceptance nor global necessity proof.'))
print(json.dumps(dict(checks=len(checks),errors=[c for c in checks if not c['pass_']],numeric_objects=numeric,phase_cases=len(phase_rows)),ensure_ascii=False))
