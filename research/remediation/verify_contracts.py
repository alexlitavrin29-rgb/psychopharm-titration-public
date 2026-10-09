"""Static research-contract checks. Does not implement or execute a medical calculator."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,datetime
import yaml
ROOT=Path(__file__).resolve().parents[1]
def collect(root=ROOT):
    return dict(root=root,sources=json.loads((root/'sources.json').read_text(encoding='utf-8')),
        rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (root/'rules').glob('*.yaml')},
        contracts=yaml.safe_load((root/'remediation/result_contracts.yaml').read_text(encoding='utf-8'))['rules'],
        schema=yaml.safe_load((root/'remediation/input_contracts.yaml').read_text(encoding='utf-8')),
        cases=json.loads((root/'remediation/full_scenarios.json').read_text(encoding='utf-8'))['cases'])
UNKNOWN=('unknown','not_assessed','неизвестно','не исследовано','не помню')
def validate(d):
    errors=[]
    def ck(ok,msg):
        if not ok:errors.append(msg)
    S=d['sources'];rs=d['rules'];cs=d['contracts'];cases=d['cases']
    ck(set(rs)==set(cs),'result contract coverage')
    ck(len({c['case_id'] for c in cases})==len(cases),'duplicate full scenario')
    for sid,s in S.items():
        if s.get('latest_registration_revision_confirmed'):
            ck(bool(s.get('latest_registry_document_comparison')),'currency claimed without registry document comparison: '+sid)
        if any(cp.get('byte_identity_to_primary_snapshot') for cp in s.get('document_copies',[])):
            ck(bool(s.get('local_file')),'source copy without local_file: '+sid)
        for cp in s.get('document_copies',[]):
            p=d['root']/cp['local_file']
            ck(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==cp['sha256'],'copy hash mismatch: '+cp['local_file'])
    for rid,r in rs.items():
        ins={i['input_id']:i for i in r['inputs']};con=cs[rid]
        bindings=d['schema']['fragment_bindings'][rid]
        fragment_keys={k for c in r['test_cases'] for k in c['given']}
        ck(fragment_keys<=set(bindings),'unbound legacy fragment key: '+rid)
        ck(set(con['required_inputs'])=={k for k,i in ins.items() if i.get('required_for_individual_result') is True},'required input drift: '+rid)
        for i in ins.values():
            ck(i.get('source_locator') and i['source_refs'],'unlocated input: '+rid+'/'+i['input_id'])
            if i['data_type']=='structured_renal':ck(i.get('required_metric') in {'CLcr','absolute_GFR'} and i['required_unit']=='mL/min','renal type ambiguous: '+rid)
            if i['data_type']=='source_hepatic_category':ck(bool(i.get('source_categories')),'hepatic categories missing: '+rid)
        blocked=any(s['source_id']=='RU-ESC' for s in r['sources'])
        if blocked:
            ck(r['verification']['ready_for_technical_implementation'] is False and r['output']['total_daily_dose'] is None and r['output']['schedule']==[], 'unconfirmed ESC result: '+rid)
            ck(r['logic']['source_blocker']['renal_boundary_operator'] is None and r['logic']['source_blocker']['hepatic_class_mapping'] is None,'unconfirmed ESC predicate: '+rid)
        else:
            ck(r['output']['total_daily_dose'] is None,'branch output has static default dose: '+rid)
            ck(r['output'].get('branches')==con['branches'],'branch contract drift: '+rid)
            for b in con['branches']:
                ck(any(c['rule_id']==rid and c['branch_id']==b['branch_id'] for c in cases),'missing full branch scenario: '+rid+'/'+b['branch_id'])
        for gate in con['source_gates']:
            ck(set(gate.get('exclusions',[])+gate.get('cautions',[])+gate.get('stop',[]))<=set(ins),'source gate without declared input: '+rid)
        if any(s['source_id']=='RU-AGO' for s in r['sources']) and rid!='ago-stop':
            req={'renal_state','elderly_population','dementia','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption','liver_injury_signs','transaminases_rising','mania_symptoms'}
            ck(req<=set(con['required_inputs']),'agomelatine missing source gate: '+rid)
            ck(r['output'].get('liver_monitoring',{}).get('rising_repeat_hours_parameter')=='repeat_liver_tests_hours','agomelatine missing repeat test action: '+rid)
            if not blocked:
                if rid.startswith('switch'):
                    ps=[p for p in con['typed_source_conditions'] if p['input']=='hepatic']
                    ck(bool(ps) and all(p['source_ref']=='RU-AGO' and p['action'].startswith('not_applicable') and '§4.3' in p['source_locator'] for p in ps),'target hepatic owner/action incorrect: '+rid)
                ks=('ALT_ratio','AST_ratio') if rid.startswith('ago') else ('alt_ratio_uln','ast_ratio_uln')
                for k in ks:
                    ck(any(c['rule_id']==rid and c['external_context']['treatment_phase']=='ongoing' and c['given'].get(k,0)>3 and c['expected']['result_type']=='source_stop_action' and c['expected'].get('stop_medication')=='RU-AGO' for c in cases),'ongoing transaminase stop missing: '+rid+'/'+k)
        if 'RU-SER' in [s['source_id'] for s in r['sources']] and 'seizure_state' in ins and r['identity']['mode'] in {'start','adjust','switch'}:
            ck('новые приступы' in ins['seizure_state']['allowed_values'] and any(p['input']=='seizure_state' and p['value']=='новые приступы' and p['source_ref']=='RU-SER' and p['action'].startswith('stop') for p in con['typed_source_conditions']),'sertraline seizure stop missing: '+rid)
        for p in r['clinical_parameters']:
            if p['parameter_id'] in {'source_minimum','reported_duration','source_taper_period'} and rid in {'ser-taper-limit','fluvox-taper-limit','venla-xr-taper-limit','dulox-taper-limit'}:
                ck(p['upper'] is None and p.get('duration_semantics',{}).get('hard_upper_limit_weeks') is None,'minimum taper encoded as ceiling: '+rid)
        if 'maoi_history_contract' in r['logic']:
            ck(ins['maoi_type']['data_type']=='record_map' and ins['maoi_stopped_at']['data_type']=='record_map','MAOI records/timestamps hidden: '+rid)
            ck(ins['maoi_stopped_at']['required_for_individual_result'] is not True,'MAOI timestamp unconditional: '+rid)
    selected=rs['switch-parox-ago-selected-example'];dep=selected['logic']['composite_rule_dependencies']
    ck(selected['verification']['combined_rules_justified'] is True and selected['verification']['russian_applicability_checked'] is True and all(rs[x]['verification']['ready_for_technical_implementation'] for x in dep),'composite readiness/dependency contradiction')
    ck('RU-AGO' in selected['logic']['combination_justification'] and 'RU-PAROX' in selected['logic']['combination_justification'],'composition based only on opt-in')
    def is_unknown(v):return v is None or isinstance(v,str) and v in UNKNOWN
    for c in cases:
        rid=c['rule_id'];r=rs[rid];ins={i['input_id']:i for i in r['inputs']};g=c['given'];e=c['expected'];cid=c['case_id']
        ck(c['not_executed_against_calculator'] is True,'false execution claim: '+cid)
        ck(set(g)<=set(ins),'undeclared full given key: '+cid)
        context=c['external_context'];decl=d['schema']['external_context']
        ck(set(context)<=set(decl),'undeclared external context: '+cid)
        if context['mode']=='switch':ck(context.get('from_drug')==r['identity']['from_drug_inn'] and context.get('to_drug')==r['identity']['to_drug_inn'],'switch identity context missing: '+cid)
        for k,v in g.items():
            if k not in ins:continue
            if is_unknown(v):continue
            i=ins[k];t=i['data_type']
            if t in {'integer','number'}:ck(type(v) in {int,float} and (t!='integer' or isinstance(v,int)),'given numeric type: '+cid+'/'+k)
            elif t=='boolean':ck(type(v) is bool,'given boolean type: '+cid+'/'+k)
            elif t=='enum':ck(v in i['allowed_values'],'given enum type: '+cid+'/'+k)
            elif t=='record_map':
                ck(isinstance(v,dict),'MAOI map type: '+cid+'/'+k)
                if isinstance(v,dict):
                    for ident,x in v.items():
                        if is_unknown(x):continue
                        if k=='maoi_type':ck(x in i['allowed_values'],'MAOI type value: '+cid)
                        else:
                            try:ck(datetime.datetime.fromisoformat(x).tzinfo is not None,'timestamp offset missing: '+cid)
                            except (ValueError,TypeError):ck(False,'bad timestamp: '+cid)
            elif t=='structured_form':
                ck(isinstance(v,dict),'form not object: '+cid)
                if isinstance(v,dict) and e['result_type']!='insufficient_data':
                    ck({'product','registration_number','source_id','source_version','dosage_form','strengths_mg','release','route'}<=set(v),'form fields missing: '+cid)
                    ck(v.get('source_id') in S and v.get('source_version')==S.get(v.get('source_id'),{}).get('version_or_update_date'),'form version drift: '+cid)
            elif t=='structured_renal':ck(isinstance(v,dict) and (e['result_type']=='insufficient_data' or {'metric','value','unit','method','assessment'}<=set(v)),'renal structure incomplete: '+cid)
            elif t=='source_hepatic_category':
                ck(isinstance(v,dict) and (e['result_type']=='insufficient_data' or {'category','assessment','classification','evidence'}<=set(v)),'hepatic structure incomplete: '+cid)
                if isinstance(v,dict) and not is_unknown(v.get('category')):ck(v['category'] in i['source_categories'],'hepatic category outside source domain: '+cid)
            elif t=='medication_list':
                ck(isinstance(v,list),'medication list not list: '+cid)
                if isinstance(v,list):
                    fields=set(d['schema']['structures']['medication_list']['entry_fields'])
                    for record in v:ck(isinstance(record,dict) and {'record_id','inn','status','interaction_class'}<=set(record) and set(record)<=fields,'undeclared/incomplete medication entry: '+cid)
            elif t in {'dose_schedule','clinical_assessment'}:ck(isinstance(v,dict),'structured context not object: '+cid)
        missing=[k for k in cs[rid]['required_inputs'] if k not in g or is_unknown(g[k])]
        if isinstance(g.get('medicines'),list):
            for record in g['medicines']:
                ident=record['record_id']
                if is_unknown(record['interaction_class']):missing.append('medicines.'+ident+'.interaction_class')
                if record['interaction_class']=='maoi' and 'maoi_type' in ins:
                    for k in ('maoi_type','maoi_stopped_at') if record['status']=='stopped' else ('maoi_type',):
                        if not isinstance(g.get(k),dict) or is_unknown(g[k].get(ident)):missing.append(k+'.'+ident)
        for k,v in g.items():
            t=ins[k]['data_type']
            if t in {'structured_renal','source_hepatic_category','structured_form'} and isinstance(v,dict):
                for field in d['schema']['structures'][t]['fields']:
                    # PHEN source has a blank registration number; record the absence instead of inventing it.
                    if field=='registration_number' and 'RU-PHEN' in [s['source_id'] for s in r['sources']] and field in v and v[field] is None:continue
                    if field not in v or is_unknown(v[field]):missing.append(k+'.'+field)
        if missing and e['result_type'] not in {'source_unavailable','not_applicable','source_stop_action'}:
            ck(e['result_type']=='insufficient_data' and set(missing)<=set(e['missing_fields']) and e['total_daily_dose_mg'] is None,'missing field allows dose: '+cid)
        if e['result_type'] in {'not_applicable','insufficient_data','source_unavailable','clinician_choice','form_not_feasible'}:
            ck(e['total_daily_dose_mg'] is None and e['schedule']==[],'blocked/choice result has executable dose: '+cid)
        if c['branch_id']:
            b=next(x for x in cs[rid]['branches'] if x['branch_id']==c['branch_id'])
            ck(all(e.get(k)==v for k,v in b['expected_output'].items()),'full expected branch mismatch: '+cid)
        if '--condition-hepatic-' in cid and rid.startswith('switch') and 'RU-AGO' in [s['source_id'] for s in r['sources']]:
            ck(e['result_type']=='not_applicable' and e.get('source_condition',{}).get('source_ref')=='RU-AGO','target hepatic scenario permits start: '+cid)
        for k,i in ins.items():
            if i['data_type']=='structured_renal' and isinstance(g.get(k),dict) and (g[k].get('metric')!=i['required_metric'] or g[k].get('unit')!=i['required_unit']):
                ck(e['result_type'] in {'insufficient_data','source_unavailable'},'wrong renal metric permits dose: '+cid)
    return errors
def run():
    d=collect();errors=validate(d)
    report=dict(status='pass' if not errors else 'fail',nature='Static typing, completeness, provenance and specified research-contract rejection checks only',
        rule_cards=len(d['rules']),full_synthetic_scenarios=len(d['cases']),calculator_tests_executed=False,medical_currency_proven=False,clinical_validation='not_performed',errors=errors)
    (ROOT/'remediation/contract_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
