from pathlib import Path
import json,yaml,hashlib,re,collections,csv,sys
sys.dont_write_bytecode=True
from primary_norms import NORMS
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
S=read(R/'sources.json');RS={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')};C=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules'];F=read(R/'full_scenarios.json')['cases'];OCC=read(OUT/'used_condition_occurrences.json');P=read(R/'actual_question_paths.json');byrule=collections.defaultdict(list)
for c in F:byrule[c['rule_id']].append(c)
paths={p['full_example']:p for p in P}
def norm(s,f):
    n=NORMS.get((s,f));return dict(**n,source_sha256=S[s]['document_fingerprint']['sha256'],source_file='research/'+S[s]['local_file'],primary_status='INDEPENDENTLY_READ_PRIMARY_NORM') if n else None
def gist(c):return dict(case_id=c['case_id'],context=c['external_context'],expected=c['expected'])
def v(c,f,sub=None):
    value=c['given'].get(f)
    if isinstance(value,dict):return value.get(sub) if sub else value.get('category',value.get('value',value))
    return value
def relevant(c,field):
    e=c['expected'];sc=e.get('source_condition',{})
    if sc.get('input','').split('.')[0]==field:return True
    reasons=e.get('reason_ids',[])
    if field in reasons or 'source_caution_'+field in reasons:return True
    return field in c['case_id'] and (v(c,field) in [None,'unknown','not_assessed','неизвестно','не исследовано'] or ('--caution-' in c['case_id'] or '--stop-' in c['case_id'] or '--typed-' in c['case_id'] or '--current-' in c['case_id'] or '--audit-' in c['case_id']))
rows=[];gaps=[];reported=[]
for rid,r in RS.items():
    for index,i in enumerate(r['inputs']):
        field=i['input_id'];ns=[norm(s,field) for s in i['source_refs'] if norm(s,field)]
        # Source refs may also carry diagnosis context. No diagnosis document is substituted
        # for a product contraindication or source-specific actor.
        positive=[c for c in byrule[rid] if relevant(c,field) and v(c,field) not in[None,'unknown','not_assessed','неизвестно','не исследовано']]
        unknown=[c for c in byrule[rid] if relevant(c,field) and v(c,field) in[None,'unknown','not_assessed','неизвестно','не исследовано']]
        used=positive+unknown
        variants={}
        for c in used:
            key=json.dumps(dict(value=v(c,field),context=c['external_context'],expected={k:x for k,x in c['expected'].items() if k not in ['confirmed_negatives','unassessed_context','missing_fields']}),sort_keys=True,ensure_ascii=False)
            variants.setdefault(key,c)
        scoped=dict(record_id=f'I-{rid}-{field}',occurrence_path=f'rules/{rid}.yaml/inputs/{index}',rule_id=rid,field=field,question=i['question_ru'],scope=r['identity'],requirement=i['requirement_predicate'],declared_locator=i['source_locator'],primary_norms=ns,representative_variants=[dict(given_value=v(c,field),**gist(c)) for c in variants.values()],full_case_ids=[c['case_id'] for c in used],primary_status='PRIMARY_NORM_CONFIRMED' if ns else 'UNREVIEWED_NO_EXACT_PRIMARY_MAPPING',expected_review='Concrete source-bound medical outputs checked by review_expected.py and inherited recheck3 primary/phase/projection checks; this list preserves every distinct source result/context variant, not one global template.',necessity_status='Not automatically established by a source caution, result difference or row count; see necessity_remaining.json',transfer_status='PREPARED_EXPECTED_ONLY')
        if not ns:gaps.append(dict(record_id=scoped['record_id'],reason='No exact primary norm mapping'))
        if i['requirement_predicate']['kind']=='reported_context':
            material=[c for c in positive if c['expected'].get('reason_ids') and (field in c['expected']['reason_ids'] or 'source_caution_'+field in c['expected']['reason_ids'])]
            if material:
                scoped['transfer_status']='DEFECT_CC01_REPORTED_CAUSE_NOT_CONSUMED'
                reported.append(dict(record_id=scoped['record_id'],rule_id=rid,field=field,primary_norms=ns,requirement=i['requirement_predicate'],positive_cases=[gist(c) for c in material],selected_case_ids=[c['case_id'] for c in material if c['case_id'] in paths],generator_lines=[11,23,96]))
        rows.append(scoped)
save('scoped_input_conditions.json',rows);save('reported_context_defect_scope.json',reported)
# Explicit contract literals: category/value/operator/action are NOT collapsed to an input name.
clauses=[]
for o in OCC:
    kind=o['kind'];claim=o['claim'];rid=o['rule_id']
    if kind not in ['typed_source_conditions','urgent_stop_predicates','ongoing_stop_conditions','urgent_source_actions','conditional_actions'] and not kind.startswith('source_gate:'):continue
    if kind in ['source_gate:medication_role','source_gate:scope','source_gate:interaction_scope','source_gate:context_field_locators','source_gate:interaction_class_locators','source_gate:duplicate_product_requirement']:continue
    if isinstance(claim,dict):
        source=claim.get('source_ref') or next((a.get('source_ref') for a in claim.get('actions',[]) if a.get('source_ref')),None) or o['source_refs'][0];field=claim.get('input') or claim.get('required_fact');sub=claim.get('field');want=claim.get('value',claim.get('equals'));op=claim.get('operator','equals')
        if not field:continue
    elif kind!='source_gate:other':source=o['source_refs'][0];field=claim;sub=None;want=True;op='gate_positive'
    else:continue
    n=norm(source,field)
    matches=[]
    for c in byrule[rid]:
        val=v(c,field,sub)
        if field=='allergy' and isinstance(val,dict) and not sub:
            actor_source=next((z['given']['from_form'].get('source_id') for z in byrule[rid] if isinstance(z['given'].get('from_form'),dict) and z['given']['from_form'].get('source_id')),None)
            role='A' if actor_source==source else 'B'
            val=val.get(role)
        if kind.startswith('source_gate:current_medicines'):
            ok=any(m.get('interaction_class')==field and m.get('status')=='current' for m in c['given'].get('medicines',[]) if isinstance(m,dict))
        elif op in ['>','greater_than']:ok=isinstance(val,(int,float)) and val>want
        elif kind=='conditional_actions':ok=field in c['case_id'] and c['given'].get(claim['trigger'].split('=')[0]) is True
        else:ok=val==want if want is not None else bool(val)
        if ok:matches.append(c)
    variant={}
    for c in matches:
        k=json.dumps(dict(context=c['external_context'],expected={k:v for k,v in c['expected'].items() if k not in ['confirmed_negatives','unassessed_context','missing_fields']}),sort_keys=True,ensure_ascii=False)
        variant.setdefault(k,c)
    row=dict(record_id='L-'+o['occurrence_id'],raw_occurrence=o['occurrence_id'],rule_id=rid,path=o['path'],condition_literal=claim,primary_norm=n,representative_expected_variants=[gist(c) for c in variant.values()],all_matching_case_ids=[c['case_id'] for c in matches],status='PRIMARY_CONFIRMED' if n else 'UNREVIEWED_NO_EXACT_PRIMARY_MAPPING',expected_coverage='REPRESENTATIVES_RECORDED' if matches else 'NO_MATCHING_PREPARED_EXPECTED_IDENTIFIED')
    input_row=next((i for i in RS[rid]['inputs'] if i['input_id']==field),None)
    reference_only=(rid=='ser-taper-limit' and field=='hepatic' and input_row and input_row['requirement_predicate']['kind']=='outside_cessation_scope') or (rid=='dulox-taper-limit' and kind=='source_gate:current_medicines_caution' and C[rid]['source_gates'][0].get('interaction_scope','').startswith('Source interaction information only'))
    if reference_only:
        row['expected_coverage']='PRIMARY_REFERENCE_ONLY_OUTSIDE_INDIVIDUAL_RESULT_SCOPE'
        row['scope_limit']='This specific source condition is retained as source information; current contract does not claim a hepatic numerical cessation adjustment or patient-specific interaction clearance. No missing clinical witness is inferred from absence of a positive individual result.'
    if not n:gaps.append(dict(record_id=row['record_id'],reason='No exact primary norm mapping',claim=claim,source=source))
    if not matches and not reference_only:gaps.append(dict(record_id=row['record_id'],reason='No matching representative identified',claim=claim,source=source))
    clauses.append(row)
save('literal_contract_conditions.json',clauses)
# Numerical claims were actually read in previous independent passes and are unchanged.
# Check current bytes of every numeric row against that independent inventory, and retain
# each distinct meaning/value/unit/indication/form, rather than certifying by source number alone.
old=read(ROOT/'research/acceptance_v2_audit/recheck3/numeric_inventory.json')['rows'];oldmap={(x['rule_id'],x['parameter_id']):x for x in old};nums=[]
for rid,r in RS.items():
    for p in r['clinical_parameters']:
        prior=oldmap[(rid,p['parameter_id'])];keys=['value','lower','upper','unit','source_ref','source_locator'];same=all(prior.get(k)==p.get(k) for k in keys)
        s=p['source_ref'];pid=p['parameter_id'];pages=[26] if s=='RU-PANIC' else ([5] if s=='RU-PREG' and any(k in pid for k in ['clcr','start_','max_','freq_']) else ([3] if s=='RU-PREG' and pid in ['d150','d300','d450','d600','frequency','interval'] else []))
        if not pages:
            match=re.search(r'с\.(\d+)(?:[–-](\d+))?',p['source_locator']);pages=list(range(int(match[1]),int(match[2] or match[1])+1)) if match else []
        if s=='RU-SER' and pid=='adult_minimum':pages=[5]
        if s=='RU-AGO' and pid in ['age_limit','depression_age_exclusion','start_taper_day']:pages=[2]
        if s=='RU-FLUVOX' and pid in ['start_options','maximum','review_time','divided_dose_threshold']:pages=[2]
        branches=[x for x in byrule[rid] if x['branch_id'] is not None]
        reps={}
        for x in branches:reps.setdefault(x['branch_id'],x['case_id'])
        nums.append(dict(record_id='N-'+rid+'-'+pid,rule_id=rid,parameter=p,source_sha256=S[s]['document_fingerprint']['sha256'],source_file='research/'+S[s]['local_file'],physical_pages=pages,primary_status='PRIOR_INDEPENDENT_PRIMARY_READING_REUSED_IDENTICAL_CLAIM_AND_SOURCE_BYTES' if same else 'UNREVIEWED_CHANGED_PARAMETER',independent_primary_norm=dict(meaning=p.get('meaning'),value=p.get('value'),lower=p.get('lower'),upper=p.get('upper'),unit=p.get('unit'),interpretation=p.get('source_meaning'),source_scope=r['identity']),representative_branch_case_ids=reps,medical_expected_checks='all_expected_check_results.json; prior primary_expected_checks.json; no application executed'))
        if not same:gaps.append(dict(record_id=nums[-1]['record_id'],reason='Changed numeric claim'))
save('numerical_conditions.json',nums)
# No free-text occurrence is silently VERIFIED. A separate complete coverage index links
# it to source-condition records or marks provenance/technical text. Exact prose defects
# remain open even where the norm itself is independently confirmed.
bad=[]
for o in OCC:
    t=o['claim'];rid=o['rule_id'];path=o['path']
    correct=None
    if isinstance(t,str):
        if rid=='parox-panic-kr' and 'с.17' in t:correct=[4,5] if 'ИМАО' in t else[4]
        if rid.startswith('dulox') and ('§4.6 с.12' in t or '§4.6 с.13' in t):correct=[10]
        if rid.startswith('dulox') and 'с.9' in t and ('Сахароза' in t or 'наследственные' in t):correct=[7]
        if rid=='phen-taper-limit' and 'с.2' in t and ('Противопоказания' in t or 'беременности противопоказано' in t or 'грудного вскармливания' in t):correct=[3,4,5]
    if correct:bad.append(dict(occurrence_id=o['occurrence_id'],rule_id=rid,path=path,incorrect_claim=t,correct_physical_pages=correct,source_sha256={s:S[s]['document_fingerprint']['sha256'] for s in o['source_refs'] if s in S}))
for n in nums:
    if n['parameter']['source_ref']=='RU-SER' and n['parameter']['parameter_id']=='adult_minimum':bad.append(dict(record_id=n['record_id'],rule_id=n['rule_id'],path='clinical_parameters/adult_minimum/source_locator',incorrect_claim=n['parameter']['source_locator'],correct_physical_pages=[5],source_sha256=n['source_sha256']))
save('locator_defects.json',bad)
save('remaining_identified_gaps.json',gaps)
save('primary_norms.json',[dict(**v,source_sha256=S[s]['document_fingerprint']['sha256'],source_file='research/'+S[s]['local_file'],status='INDEPENDENTLY_READ_PRIMARY_NORM_NOT_AUTOMATIC_OCCURRENCE_VERIFICATION') for (s,k),v in NORMS.items()])
save('completion_counts.json',dict(snapshot=read(R/'final_manifest.json')['snapshot_sha256'],raw_occurrences=len(OCC),scoped_input_rows=len(rows),literal_contract_rows=len(clauses),numerical_rows=len(nums),manual_source_key_norms=len(NORMS),reported_material_rows=len(reported),locator_defects=len(bad),remaining_identified_gaps=len(gaps),primary_mapping_missing=[x for x in gaps if x['reason']=='No exact primary norm mapping']))
print('inputs',len(rows),'clauses',len(clauses),'numeric',len(nums),'norms',len(NORMS),'reported defects',len(reported),'locators',len(bad),'gaps',len(gaps));print(json.dumps(gaps[:15],ensure_ascii=False,indent=1))
