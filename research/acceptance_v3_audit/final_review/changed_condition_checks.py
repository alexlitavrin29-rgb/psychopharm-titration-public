"""Read-only review of the copied research data; writes only this audit directory."""
from pathlib import Path
from copy import deepcopy
import json, yaml, hashlib, collections, sys
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SNAP = ROOT / 'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
OLD = ROOT / 'research/acceptance_v2_audit/condition_completion'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(n, v): (OUT/n).write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
M = read(ROOT/'research/remediation_round3/final_manifest_v3_review1.json')
R = {p.stem: yaml.safe_load(p.read_text(encoding='utf-8')) for p in (SNAP/'rules').glob('*.yaml')}
C = {c['case_id']: c for c in read(SNAP/'full_scenarios.json')['cases']}
P = read(SNAP/'actual_question_paths.json')
J = read(SNAP/'condition_case_repairs.json')
CON = yaml.safe_load((SNAP/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
N = read(OLD/'primary_norms.json')
G = {r['record_id']:r for r in read(OLD/'positive_expected_gaps_exact.json')['rows']}
checks=[]; errors=[]
def ck(label, ok, case=None, detail=None):
    row=dict(check=label, pass_=bool(ok), case_id=case, detail=detail)
    checks.append(row)
    if not ok: errors.append(row)
core_changes=[r['path'] for r in M['files'] if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256']]
ck('copied manifest77 preserved',not core_changes,detail=core_changes)
source_files={n['source_file']:n['source_sha256'] for n in N}
source_checks=[dict(file=p,expected=s,actual=sha(ROOT/p),pass_=sha(ROOT/p)==s) for p,s in source_files.items()]
ck('previous independent primary norm bytes unchanged',all(s['pass_'] for s in source_checks))
save('source_integrity.json',source_checks)
reviewed=[]
for row in J['rows']:
    norms=[G[k] for k in row['record_ids']]
    ck('exact old114 scope represented',all(n['rule_id']==row['rule_id'] and n['source_id']==row['source_id'] and n['source_sha256']==row['source_sha256'] and n['condition_literal']==row['condition_literal'] for n in norms),detail=row['record_ids'])
    sid=row['source_id']; actor=norms[0]['actor']; lit=row['condition_literal']; records=[]
    for cid in row['new_cases']:
        c=C[cid];e=c['expected'];g=c['given'];ctx=c['external_context'];sc=e.get('source_condition',{})
        ck('same card and complete typed synthetic case',c['rule_id']==row['rule_id'] and c.get('case_kind')=='full_synthetic_input_scenario',cid)
        ck('no invented individual dose/schedule/clearance',all(e.get(k) is None for k in ['total_daily_dose_mg','dose_per_administration_mg','administrations_per_day']) and e.get('schedule')==[] and e.get('clinical_clearance') is False,cid)
        forbidden={'target_source_start_mg','overlap_allowed_on_first_day_of_A_reduction','overlap_allowed','duration_constraint','withdrawal_rules','conditional_next_total_mg','published_option_mg','recommended_mg','hold_if','source_initial_mg','initial_days','minimum_interval_days','minimum_interval_weeks','optional_stages_mg'}
        bounded_optional=cid.endswith('-unknown') and e['result_type']=='clinician_choice' and sc=={} and bool(e.get('target_source_start_scope') or e.get('source_reference') or e.get('published_components_scope') or 'unassessed_context' in e)
        permitted_reference={'target_source_start_mg','overlap_allowed_on_first_day_of_A_reduction'} if bounded_optional else set()
        ck('no inherited future/taper/overlap payload in blocked or urgent result',not any(e.get(k) is not None for k in forbidden-permitted_reference),cid,sorted(set(e)&(forbidden-permitted_reference)))
        if bounded_optional:ck('source reference does not assert individual overlap permission',e.get('overlap_allowed_on_first_day_of_A_reduction') is not True,cid)
        ck('expected original owner SHA locator',any(b['source_id']==sid and b['sha256']==row['source_sha256'] and (not cid.endswith('-positive') or b['locator']=='Физ. с.'+','.join(map(str,row['physical_pages']))) for b in e.get('source_basis',c.get('source_basis',[]))),cid)
        ck('actual supplied negatives only',all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])),cid)
        if cid.endswith('-positive'):
            ck('positive cause owner and scope',sc.get('source_ref')==sid and sc.get('actor')==actor and sc.get('primary_norm')==norms[0]['independent_primary_norm'],cid)
            if isinstance(lit,dict):
                v=g.get(lit['input']);v=v.get('category') if isinstance(v,dict) else v
                ck('positive typed condition supplied',v==lit['value'] and sc.get('input')==lit['input'],cid)
            elif sc.get('input')=='medicines':
                ck('positive current interaction record',any(m.get('interaction_class')==lit and m.get('status')=='current' for m in g.get('medicines',[]) if isinstance(m,dict)),cid)
            else: ck('positive explicit condition supplied',g.get(sc.get('input')) is True,cid)
            stop=(sid=='RU-AGO' and lit=='liver_injury_signs') or (isinstance(lit,dict) and lit.get('value') in {'новые приступы','первичные/участившиеся приступы'})
            exclude=(isinstance(lit,dict) and lit.get('input')=='hepatic') or lit in ['galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'] or (sc.get('input')=='medicines' and lit in ['irreversible_maoi','maoi','pimozide'] or sid=='RU-ESC' and lit=='QT_prolonging')
            if stop:
                phase=ctx.get('target_treatment_phase') if actor=='B' else ctx.get('treatment_phase')
                ck('published ongoing source stop',phase=='ongoing' and e['result_type']=='source_stop_action' and e.get('stop_medication')==sid and bool(e.get('source_actions')),cid)
                if sid=='RU-AGO':ck('AGO stop plus followup to normalization',{a['action'] for a in e['source_actions']}=={'immediately_discontinue_agomelatine','monitor_liver_function_until_normalization'},cid)
                else:ck('own seizure stop action only',[a['action'] for a in e['source_actions']]==['discontinue_selected_medication'],cid)
            elif exclude:
                ck('source exclusion no numerical license',e['result_type']==('clinician_choice' if actor=='A' else 'not_applicable') and sc.get('action')=='source_excludes_standard_numeric_application',cid)
            else:ck('source caution retained as physician choice',e['result_type']=='clinician_choice' and sc.get('action')=='source_caution_or_conditional_clinical_decision_without_numeric_coefficient' and not e.get('source_actions') and not e.get('stop_medication'),cid)
        else:
            ck('unknown/phase no medication stop',not e.get('stop_medication') and not e.get('source_actions') and not e.get('schedule') and e.get('total_daily_dose_mg') is None,cid)
            ck('unknown named request or bounded physician choice',e['result_type']=='clinician_choice' and bool(e.get('unassessed_context') or e.get('phase_clarification')) if '-phase-not_started' in cid or bounded_optional else e['result_type']=='insufficient_data' and bool(e.get('missing_fields')),cid)
        if R[c['rule_id']]['identity']['mode']=='switch':ck('pair target not automatically started',e.get('target_start_allowed') is not True and e.get('total_daily_dose_mg') is None and not e.get('schedule'),cid)
        records.append(dict(case_id=cid,given=g,context=ctx,expected=e,status='INDEPENDENT_SOURCE_SCOPE_AND_STATIC_RESULT_REVIEWED'))
    reviewed.append(dict(rule_id=row['rule_id'],source_id=sid,actor=actor,condition_literal=lit,source_sha256=row['source_sha256'],physical_pages=row['physical_pages'],independent_primary_norm=norms[0]['independent_primary_norm'],permitted_result=norms[0]['permitted_result'],cases=records))
save('source_scope_review.json',reviewed)


save('changed_condition_checks.json',dict(checks=checks,errors=errors,scopes=len(reviewed),cases=sum(len(x['cases']) for x in reviewed),scope='Reused prior independently read same-SHA norms; current113 scopes/232 full witnesses independently rechecked; not app execution.'))
print(len(checks),len(errors));print(json.dumps(errors[:10],ensure_ascii=False))
