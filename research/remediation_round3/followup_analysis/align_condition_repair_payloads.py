"""Align identical prepared inputs without changing any clinical output."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
changes=[]
for rid,r in R.items():
    for i in r['inputs']:
        kind=i['requirement_predicate']['kind']
        if kind!='always' and i['input_role']!=kind:
            i['result_scope_role']=i['input_role'];i['input_role']=kind
    (O/'rules'/(rid+'.yaml')).write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
P=yaml.safe_load((O/'necessity_policy.yaml').read_text(encoding='utf-8'))
P['ser_fields']['adherence'].update(necessity='indication_action_choice',locator='RU-PANIC физ.с.29–30; RU-PHOB физ.с.29',effect='Required only for F41.0 clinical action selection; explicitly supplied F40.1 context counted, absent/unknown unassessed, no automatic increase')
(O/'necessity_policy.yaml').write_text(yaml.safe_dump(P,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for c in F['cases']:
    e=c['expected'];g=c['given'];r=R[c['rule_id']]
    if c['case_id'].startswith('switch-esc-ago--audit-final-primary-RU-AGO-hepatic-') and c['case_id'].endswith('-unknown'):
        e['missing_fields']=['hepatic.category','hepatic.assessment'];changes.append(dict(case_id=c['case_id'],change='Name unknown nested hepatic operands'))
    if e['result_type'] in {'exact','selected_source_example'}:
        optional={i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_current_event','reported_source_information','indication_action_choice'}}
        e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k for k in optional if g.get(k) in (None,'unknown','not_assessed','неизвестно','не исследовано')})
    if c['case_id'].startswith(('ser-panic-start--','ser-social-start--')) and e.get('monitoring_warning_source'):
        e['monitoring_warning_source']='RU-SER §4.4 с.4–6; full clinical review remains separate'

groups={}
for c in F['cases']:
    key=json.dumps([c['rule_id'],c['given'],c['external_context']],sort_keys=True,ensure_ascii=False)
    groups.setdefault(key,[]).append(c)
for group in groups.values():
    old=next((c for c in group if '--audit-final-primary-' not in c['case_id']),None)
    if old is None:continue
    for c in group:
        if '--audit-final-primary-' not in c['case_id'] or not c['case_id'].endswith('-unknown'):continue
        e=c['expected'];prior=old['expected']
        for k in ['result_type','total_daily_dose_mg','dose_per_administration_mg','administrations_per_day','schedule','stop_medication']:
            assert prior.get(k)==e.get(k),(c['case_id'],k)
        assert not prior.get('source_actions') and not prior.get('source_condition'),c['case_id']
        aligned=deepcopy(prior)
        aligned['unassessed_context']=sorted(set(prior.get('unassessed_context',[]))|set(e.get('unassessed_context',[])))
        aligned['source_basis']=deepcopy(c['source_basis'])
        aligned['source_actions']=[];aligned['clinical_clearance']=False
        aligned['no_automatic_target_start']=R[c['rule_id']]['identity']['mode']=='switch'
        aligned['no_automatic_medication_change']=True
        if aligned.get('target_source_start_mg') is not None:
            aligned['target_source_start_scope']='Published product reference only; target applicability not established and no automatic target start/overlap/pair calendar'
        c['expected']=aligned
        # The same typed state receives the same bounded reference metadata.
        for peer in group:peer['expected']=deepcopy(aligned)
        changes.append(dict(case_id=c['case_id'],change='Reuse independently reviewed identical unknown medical result, retaining bounded source reference and adding explicit unassessed/provenance metadata'))
allowed={'unassessed_context','confirmed_negatives','reason_ids','source_basis','source_actions','no_automatic_target_start','no_automatic_medication_change','unconditional_future_stages','monitoring_warning_source','start_allowed'}
for group in groups.values():
    if len(group)<2:continue
    ref=deepcopy(group[0]['expected'])
    for c in group[1:]:
        e=c['expected'];diff={k for k in set(e)|set(ref) if e.get(k,'ABSENT')!=ref.get(k,'ABSENT')}
        assert diff<=allowed,(c['case_id'],diff)
        for k in diff:
            if k in {'source_actions'}:assert not e.get(k) and not ref.get(k),'Cannot merge different medical actions'
            if k in {'unassessed_context','reason_ids'}:ref[k]=sorted(set(ref.get(k,[]))|set(e.get(k,[])))
            elif k=='confirmed_negatives':ref[k]=sorted(set(ref.get(k,[]))&set(e.get(k,[])))
            elif k in {'no_automatic_target_start','no_automatic_medication_change'}:ref[k]=bool(ref.get(k) or e.get(k))
            elif k=='unconditional_future_stages':assert not e.get(k) and not ref.get(k);ref[k]=False
            elif k=='start_allowed':assert not e.get(k) and not ref.get(k);ref[k]=False
            else:ref[k]=deepcopy(e.get(k,ref.get(k)))
    for c in group:
        if c['expected']!=ref:changes.append(dict(case_id=c['case_id'],change='Identical input/context: align explicit no-action, primary locator and unassessed metadata only'));c['expected']=deepcopy(ref)
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'condition_payload_alignment.json').write_text(json.dumps(dict(changes=changes,numerical_dose_or_medical_action_changed=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Exact metadata/unknown alignment',len(changes),'no changed clinical payload')
