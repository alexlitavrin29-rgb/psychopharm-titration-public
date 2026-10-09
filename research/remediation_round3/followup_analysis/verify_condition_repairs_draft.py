"""Reviewed locator/claim/witness regression and unchanged numeric parameters."""
from pathlib import Path
from copy import deepcopy
import json,yaml
import verify_contracts
O=Path(__file__).resolve().parent

def check(d,journal):
    errors=[];cases={c['case_id']:c for c in d['cases']}
    for row in journal['rows']:
        for cid in row['new_cases']:
            c=cases.get(cid)
            if c is None:errors.append('Missing source witness: '+cid);continue
            e=c['expected'];sid=row['source_id']
            if e.get('clinical_clearance') is not False or e.get('total_daily_dose_mg') is not None or e.get('schedule'):errors.append('Caution/unknown witness assigns a numerical regimen: '+cid)
            if not any(b['source_id']==sid and b['sha256']==row['source_sha256'] for b in e['source_basis']):errors.append('Witness source owner/hash changed: '+cid)
            if cid.endswith('-unknown') or '-phase-' in cid:
                if e.get('source_actions') or e.get('stop_medication'):errors.append('Unknown/not-started actor receives medication change: '+cid)
            if cid.endswith('-positive') and 'source_condition' not in e:errors.append('Positive source cause hidden: '+cid)
    for rid,r in d['rules'].items():
        old=yaml.safe_load((O/'recheck3_snapshot/research/remediation_round3/rules'/(rid+'.yaml')).read_text(encoding='utf-8'))
        def numeric(p):return {k:v for k,v in p.items() if k!='source_locator'}
        if [numeric(p) for p in r['clinical_parameters']]!=[numeric(p) for p in old['clinical_parameters']]:errors.append('Published numeric parameter changed: '+rid)
    for rid in ['preg-gad-start','preg-gad-adjust','preg-renal-start']:
        con=d['contracts'][rid];policy=con.get('form_evidence_policy',{})
        if 'not claimed' not in policy.get('source_claim',''):errors.append('Unsupported capsule opening prohibition: '+rid)
        if any('no splitting/opening capsules'==s for g in con['source_gates'] for s in g.get('other',[])):errors.append('Capsule policy falsely attributed to source: '+rid)
    return errors

def run():
    d=verify_contracts.collect();journal=json.loads((O/'condition_case_repairs.json').read_text(encoding='utf-8'));errors=check(d,journal);mutations=[]
    for name in ['missing_witness','unknown_drug_stop','invented_caution_dose','wrong_witness_source','changed_parameter','false_capsule_claim']:
        dd=deepcopy(d);cid=journal['rows'][0]['new_cases'][0]
        if name=='missing_witness':dd['cases']=[c for c in dd['cases'] if c['case_id']!=cid]
        elif name=='unknown_drug_stop':next(c for c in dd['cases'] if c['case_id']==journal['rows'][0]['new_cases'][1])['expected']['stop_medication']='RU-ESC'
        elif name=='invented_caution_dose':next(c for c in dd['cases'] if c['case_id']==cid)['expected']['total_daily_dose_mg']=10
        elif name=='wrong_witness_source':next(c for c in dd['cases'] if c['case_id']==cid)['expected']['source_basis'][0]['source_id']='RU-SER'
        elif name=='changed_parameter':dd['rules']['ser-panic-start']['clinical_parameters'][0]['value']=999
        else:dd['contracts']['preg-gad-start']['form_evidence_policy']['source_claim']='The source categorically prohibits opening.'
        found=check(dd,journal);mutations.append(dict(mutation=name,rejected=bool(found),evidence=found[:1]))
        if not found:errors.append('Mutation not caught: '+name)
    result=dict(status='pass' if not errors else 'fail',condition_scopes=journal['unique_condition_scopes'],new_cases=journal['new_cases'],negative_mutations=mutations,scope='Presence/provenance/null actions and unchanged numeric objects. Independent primary medical interpretation is a separate acceptance.',errors=errors)
    (O/'condition_repair_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=result['status'],new_cases=journal['new_cases'],mutations=len(mutations),errors=errors),ensure_ascii=False));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
