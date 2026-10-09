"""Audit regression checks against source conditions, versions and projected facts."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, re
import fitz
import verify_contracts

O=Path(__file__).resolve().parent
def check_pack(d, paths):
    errors=[]
    S, C = d['sources'], d['contracts']
    def ck(ok, message):
        if not ok:
            errors.append(message)
    bases=[(rid+'/'+b['branch_id'],b['source_basis']) for rid,c in C.items() for b in c['branches']]
    bases += [(c['case_id'],c['source_basis']) for c in d['cases']]
    for owner, items in bases:
        for item in items:
            sid=item['source_id']
            ck(item['version']==S[sid]['version_or_update_date'], 'active source version owner drift: '+owner+'/'+sid)
            ck(item['sha256']==S[sid]['document_fingerprint']['sha256'], 'active source hash owner drift: '+owner+'/'+sid)
    for p in paths:
        g,e=p['full_projected_given'],p['full_projected_expected']
        ck(all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])), 'unasked projected negative: '+p['full_example'])
        ck(not set(e.get('confirmed_negatives',[])) & set(e.get('unassessed_context',[])), 'negative/unassessed contradiction: '+p['full_example'])
    for rid,c in C.items():
        for gate in c['source_gates']:
            if gate['source_ref']=='RU-SER':
                ck('strong_CYP3A4' in gate.get('current_medicines_avoid_standard_combination',[]), 'SER CYP3A4 avoid class missing: '+rid)
            if gate['source_ref']=='RU-DULOX':
                ck({'CNS_depressant','CYP1A2_inhibitor','CYP2D6_substrate','hepatotoxic'}<=set(gate.get('current_medicines_caution',[])), 'DULOX source caution class missing: '+rid)
    by_id={c['case_id']:c for c in d['cases']}
    for rid in ['parox-panic-kr','parox-taper-example','switch-parox-ago','switch-parox-ago-selected-example']:
        p=next((p for p in C[rid].get('urgent_stop_predicates',[]) if p.get('input')=='serotonin_syndrome_signs' and p.get('source_ref')=='RU-PAROX'),None)
        ck(p is not None,'PAROX syndrome stop predicate missing: '+rid)
        case=by_id.get(rid+'--audit-v2-serotonin_syndrome_signs-positive')
        ck(case is not None and {a['action'] for a in case['expected'].get('source_actions',[])}=={'discontinue_selected_medication','start_supportive_symptomatic_treatment_by_clinician'}, 'PAROX complete syndrome action missing: '+rid)
    ck('bipolar_risk_screening' in C['parox-panic-kr']['required_inputs'],'PAROX explicit pretreatment assessment missing')
    for rid in ['venla-xr-gad-start','venla-xr-social-start','venla-xr-panic-form-limit','venla-xr-taper-limit']:
        p=next((p for p in C[rid].get('urgent_stop_predicates',[]) if p.get('input')=='diastolic_BP'),{})
        ck(p.get('operator')=='greater_than' and p.get('value')==100, 'XR strict BP threshold missing/changed: '+rid)
        a,b=[by_id.get(rid+'--audit-v2-diastolic_BP-'+state) for state in ['positive','negative']]
        ck(a is not None and a['given']['diastolic_BP']==100.01 and a['expected']['result_type']=='source_stop_action','XR above100 stop lost: '+rid)
        ck(b is not None and b['given']['diastolic_BP']==100 and b['expected']['result_type']!='source_stop_action','XR boundary100 changed to stop: '+rid)
    for key,extra in [('arrhythmia_signs','obtain_ECG'),('serotonin_syndrome_signs','start_symptomatic_treatment_by_clinician'),('seizure_state',None)]:
        c=by_id.get('switch-esc-ago--audit-v2-'+key+'-positive')
        ck(c is not None and c['expected'].get('stop_medication')=='RU-ESC' and c['expected'].get('no_automatic_target_start') is True,'ESC A stop owner/target start drift: '+key)
        if extra and c:
            ck(extra in {a['action'] for a in c['expected']['source_actions']},'ESC additional source action lost: '+key)
    for rid,fields in [('fluvox-taper-limit',['serotonin_syndrome_signs','new_or_increased_seizures','liver_injury_signs','mania_symptoms']),('parox-taper-example',['serotonin_syndrome_signs','new_seizures']),('venla-xr-taper-limit',['diastolic_BP','current_allergic_reaction'])]:
        ck(set(fields)<=set(C[rid]['input_requirements']) and all(C[rid]['input_requirements'][k]['kind'] in {'always','reported_current_event'} for k in fields),'current taper stop inputs missing: '+rid)
    for rid,prefix in [('switch-esc-ser',''),('switch-ser-esc','target_')]:
        for key in ['arrhythmia_signs','serotonin_syndrome_signs','seizure_state']:
            case=by_id.get(rid+'--audit-v2-'+prefix+key+'-positive')
            ck(case is not None and case['expected'].get('stop_medication')=='RU-ESC','additional ESC transition stop missing: '+rid+'/'+key)
            if prefix:
                pred=C[rid]['input_requirements'].get(prefix+key)
                ck(pred==dict(kind='target_ongoing') or pred==dict(kind='reported_current_event') and bool(C[rid].get('qualitative_result_scope')),'target ESC phase trigger missing: '+key)
                ck(case['external_context'].get('target_treatment_phase')=='ongoing','known ESC target action lacks its own ongoing phase: '+key)
                for phase in ['not_started','unknown']:
                    case=by_id.get(rid+'--audit-v2-'+prefix+key+'-target-phase-'+phase)
                    ck(case is not None and case['expected']['result_type']!='source_stop_action' and case['expected'].get('stop_medication') is None,'ESC target stop invented from A phase: '+key+'/'+phase)
    ck(any(p.get('input')=='new_or_increased_seizures' and p.get('action')=='source_stop_action' for p in C['fluvox-depression-start'].get('urgent_stop_predicates',[])),'FLUVOX increased seizure frequency stop missing')
    return errors

def primary_guards(S):
    definitions=[('RU-PAROX',7,['тщательный скрининг','поддерживающую симптоматическую терапию']),('RU-PAROX',9,['судорожного припадка','необходимо прекратить']),('RU-FLUVOX',5,['активности печеночных ферментов','должно быть прекращено','симптоматическое лечение']),('RU-FLUVOX',7,['маниакальной фазы','прекратить']),('RU-VENLA-XR',9,['выше 100 мм рт. ст.','необходимо прекратить']),('RU-VENLA-XR',13,['крапивницы','прекратить терапию']),('RU-SER',10,['мощных ингибиторов изофермента CYP3A4','следует избегать']),('RU-DULOX',8,['седативные средства','меньших доз дулоксетина','узкий терапевтический индекс']),('RU-DULOX',7,['могут повлиять на состояние печени']),('RU-ESC',4,['первичного развития судорожных припадков','Следует отменить']),('RU-ESC',6,['прекратить терапию и сделать ЭКГ','начать симптоматическое лечение'])]
    rows=[]
    for sid,page,phrases in definitions:
        file=O.parent/S[sid]['local_file']
        with fitz.open(file) as pdf:
            text=re.sub(r'([А-Яа-яЁё])-\s*\n\s*([А-Яа-яЁё])',r'\1\2',pdf[page-1].get_text())
        text=' '.join(text.split())
        rows.append(dict(source_id=sid,physical_page=page,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),source_phrases_present=all(q in text for q in phrases),scope='Specific independently selected source condition/action, not full document review or calculator execution'))
    return rows

if __name__=='__main__':
    d=verify_contracts.collect()
    paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
    errors=check_pack(d,paths)
    primary=primary_guards(d['sources'])
    errors += ['primary source phrase/page guard failed: '+x['source_id']+'/'+str(x['physical_page']) for x in primary if not x['source_phrases_present']]
    mutations=[]
    for name,change in [
        ('source version bound to wrong owner',lambda x,p:x['contracts']['venla-xr-panic-form-limit']['branches'][0]['source_basis'][0].update(version='wrong edition')),
        ('PAROX screening gate removed',lambda x,p:x['contracts']['parox-panic-kr']['required_inputs'].remove('bipolar_risk_screening')),
        ('SER CYP3A4 class removed',lambda x,p:x['contracts']['ser-panic-start']['source_gates'][0].update(current_medicines_avoid_standard_combination=[])),
        ('DULOX CYP2D6 substrate lost',lambda x,p:x['contracts']['dulox-gad-start']['source_gates'][0]['current_medicines_caution'].remove('CYP2D6_substrate')),
        ('XR BP greater_than changed to inclusive',lambda x,p:next(v for v in x['contracts']['venla-xr-gad-start']['urgent_stop_predicates'] if v['input']=='diastolic_BP').update(operator='greater_or_equal')),
        ('unasked value confirmed negative',lambda x,p:p[0]['full_projected_expected'].setdefault('confirmed_negatives',[]).append('audit_unasked_field')),
        ('ESC arrhythmia ECG action removed',lambda x,p:next(c for c in x['cases'] if c['case_id']=='switch-esc-ago--audit-v2-arrhythmia_signs-positive')['expected'].update(source_actions=[])),
        ('PAROX syndrome supportive action removed',lambda x,p:next(c for c in x['cases'] if c['case_id']=='parox-panic-kr--audit-v2-serotonin_syndrome_signs-positive')['expected'].update(source_actions=[]))
    ]:
        dd,pp=deepcopy(d),deepcopy(paths)
        change(dd,pp)
        detected=bool(check_pack(dd,pp))
        mutations.append(dict(mutation=name,detected=detected))
        if not detected:
            errors.append('audit negative mutation undetected: '+name)
    report=dict(status='pass' if not errors else 'fail',active_source_binding_and_projected_fact_checks=True,primary_condition_guards=primary,negative_mutations=mutations,calculator_executed=False,clinical_validation='not_performed',errors=errors)
    (O/'audit_repair_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],primary_condition_guards=len(primary),negative_mutations=len(mutations),errors=errors[:30]),ensure_ascii=False))
    raise SystemExit(bool(errors))
