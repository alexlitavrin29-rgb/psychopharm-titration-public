"""Extract used claims before review; no extracted row is automatically VERIFIED."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,yaml,datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
M=read(R/'final_manifest.json');assert M['snapshot_sha256']=='ac33f61373c22b1c160de40057815b16c27bc67e4beb870a56057992f0b06148'
assert all(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in M['files'])
S=read(R/'sources.json');RS={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')};CS=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules'];F=read(R/'full_scenarios.json')['cases']
records=[]
def add(rid,kind,path,claim,refs,locator=None,case=None):
    records.append(dict(occurrence_id=f'C{len(records)+1:05d}',rule_id=rid,kind=kind,path=path,claim=claim,source_refs=refs,source_fingerprints={s:S[s]['document_fingerprint']['sha256'] for s in refs if s in S},declared_locator=locator,scope=dict(mode=RS[rid]['identity']['mode'],diagnosis=RS[rid]['identity']['diagnosis_code'],drug=RS[rid]['identity']['drug_inn'],from_drug=RS[rid]['identity']['from_drug_inn'],to_drug=RS[rid]['identity']['to_drug_inn'],form=RS[rid]['identity']['formulation']),representative_case=case,status='UNREVIEWED',primary_physical_pages=[],independent_primary_norm=None,independent_result_check=None))
def strings(v,path):
    if isinstance(v,str):yield path,v
    elif isinstance(v,dict):
        for k,x in v.items():yield from strings(x,path+'/'+str(k))
    elif isinstance(v,list):
        for j,x in enumerate(v):yield from strings(x,path+'/'+str(j))
for rid,r in RS.items():
    refs=[x['source_id'] for x in r['sources']]
    for j,i in enumerate(r['inputs']):
        add(rid,'input',f'rules/{rid}.yaml/inputs/{j}',{k:i.get(k) for k in ['input_id','question_ru','data_type','unit','allowed_values','source_categories','requirement_predicate','input_role','source_locator','why_needed','changes','action_if_unknown','fact_semantics']},i['source_refs'],i['source_locator'])
    for j,p in enumerate(r['clinical_parameters']):add(rid,'clinical_parameter',f'rules/{rid}.yaml/clinical_parameters/{j}',p,[p['source_ref']],p['source_locator'])
    for path,text in strings(r['applicability'],'applicability'):
        if not path.endswith('source_refs') and '/source_refs/' not in path:add(rid,'applicability_text',f'rules/{rid}.yaml/{path}',text,refs)
    for path,text in strings(r['logic'],'logic'):
        if '/source_refs/' not in path and not any(x in path for x in ['parameter_refs','composite_rule_dependencies','result_contract_ref','input_necessity_policy_ref']):add(rid,'logic_text',f'rules/{rid}.yaml/{path}',text,refs)
    for path,text in strings(r['output'],'output'):
        if '/branches/' not in path and '/source_refs/' not in path:add(rid,'output_text',f'rules/{rid}.yaml/{path}',text,refs)
    c=CS[rid]
    for j,g in enumerate(c['source_gates']):
        for kind,v in g.items():
            if kind in {'source_ref','version','locator'}:continue
            if isinstance(v,list):
                for n,x in enumerate(v):add(rid,'source_gate:'+kind,f'result_contracts.yaml/rules/{rid}/source_gates/{j}/{kind}/{n}',x,[g['source_ref']],g['locator'])
            else:add(rid,'source_gate:'+kind,f'result_contracts.yaml/rules/{rid}/source_gates/{j}/{kind}',v,[g['source_ref']],g['locator'])
    for kind in ['typed_source_conditions','urgent_stop_predicates','ongoing_stop_conditions','conditional_actions','urgent_source_actions','general_result_templates','qualitative_population_scope']:
        v=c.get(kind,[])
        if isinstance(v,dict):v=[dict(name=k,**x) if isinstance(x,dict) else dict(name=k,value=x) for k,x in v.items()]
        for j,x in enumerate(v):
            sid=x.get('source_ref') if isinstance(x,dict) else None
            add(rid,kind,f'result_contracts.yaml/rules/{rid}/{kind}/{j}',x,[sid] if sid else refs,x.get('source_locator') if isinstance(x,dict) else None)
    for j,b in enumerate(c['branches']):add(rid,'branch',f'result_contracts.yaml/rules/{rid}/branches/{j}',b,refs,case=next(x['case_id'] for x in F if x['rule_id']==rid and x['branch_id']==b['branch_id']))
# Unique full expected clinical payload per rule. Negative/unassessed/missing facts are attached
# as complete cases; they are not silently asserted medical negatives or dropped from inspection.
grouped=defaultdict(list)
for case in F:
    e={k:v for k,v in case['expected'].items() if k not in {'confirmed_negatives','unassessed_context','missing_fields'}}
    key=(case['rule_id'],json.dumps(e,ensure_ascii=False,sort_keys=True))
    grouped[key].append(case)
for (rid,key),cases in grouped.items():
    add(rid,'full_expected_payload','full_scenarios.json/cases',json.loads(key),[x['source_id'] for x in cases[0]['source_basis']],case=cases[0]['case_id'])
    records[-1]['all_case_ids']=[x['case_id'] for x in cases]
    records[-1]['case_variant_signature_count']=len({json.dumps(dict(given=c['given'],context=c['external_context']),sort_keys=True,ensure_ascii=False) for c in cases})
save('initial_manifest.json',dict(snapshot=M['snapshot_sha256'],files=M['files'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Used-condition completion; all extracted claims begin UNREVIEWED'))
save('used_condition_occurrences.json',records)
save('inventory_summary.json',dict(snapshot=M['snapshot_sha256'],cards=len(RS),occurrences=len(records),kinds=dict(Counter(x['kind'] for x in records)),status_counts=dict(Counter(x['status'] for x in records)),prepared_cases=len(F),full_expected_payload_groups=len(grouped),grouping='No primary-condition equivalence assumed. Complete expected payload equality grouped only within same rule, all distinct givens/context variants retained.',excluded_payload_keys=['confirmed_negatives','unassessed_context','missing_fields'],exclusion_reason='Technical presence/assessment lists inspected via complete case variants and independent recheck3 projection checks; excluded only from clinical payload grouping, not from case review.'))
save('case_variants.json',[dict(case_id=c['case_id'],rule_id=c['rule_id'],given=c['given'],external_context=c['external_context'],expected=c['expected']) for c in F])
print(len(records),Counter(x['kind'] for x in records),'expected groups',len(grouped))
