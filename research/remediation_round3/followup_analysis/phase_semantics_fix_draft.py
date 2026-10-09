"""Apply source actor provenance after preserving the completed frozen review."""
from pathlib import Path
from copy import deepcopy
import json,yaml,shutil
O=Path(__file__).resolve().parent.parent
assert not (O/'phase_semantics_repairs.json').exists(),'One-use correction'
shutil.copyfile(Path(__file__).with_name('phase_provenance_draft.py'),O/'phase_provenance.py')
import sys
sys.path.insert(0,str(O))
from phase_provenance import selected_phase,owns_selected_action
rs={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
changes=[];new=[]
for rid,r in rs.items():
    for i in r['inputs']:
        if i['input_id']=='current_dose':
            i['fact_semantics']='actually_taken_current_daily_dose'
            i['question_ru']='Какую общую суточную дозу выбранного препарата A пациент фактически принимает сейчас (мг/сут)? Предлагаемая доза или план не являются текущим приёмом.'
            i['fact_origin']='Explicit actual current daily dose of selected/A product; proposed/planned/unknown/zero dose never establishes ongoing treatment. Only a consumed active known positive operand can establish A phase.'
    C['rules'][rid]['selected_phase_policy']=dict(current_use_evidence='Explicit treatment_phase=ongoing, or active consumed actually_taken_current_daily_dose with a known positive value',selected_mode='Selection only; start means first administration, other desired actions do not establish current use',explicit_unknown_or_not_started='Overrides a derived current-dose phase; conflicting facts require physician clarification, no cessation source action',qualitative_without_consumed_current_dose='Separate phase required only for a current-treatment source action; every supplied phase fact is counted')
    (O/'rules'/ (rid+'.yaml')).write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for c in F['cases']:
    r=rs[c['rule_id']];e=c['expected']
    if not owns_selected_action(r,e):continue
    phase,origin=selected_phase(r,c)
    if phase!='ongoing':
        assert c['external_context'].get('treatment_phase')=='selected_mode',c['case_id']
        c['external_context']['treatment_phase']='ongoing'
        changes.append(dict(case_id=c['case_id'],old='selected_mode',new='ongoing',reason='Synthetic positive source-action fixture now explicitly supplies current A use; separate counted fact, no inference from requested mode'))
    # Both explicit unknown and not-started prevent this current A action.
    for phase in ['unknown','not_started']:
        n=deepcopy(c);n.update(case_id=c['case_id']+'--audit-final-A-phase-'+phase,branch_id=None)
        n['external_context']['treatment_phase']=phase
        ee=n['expected'];ee.update(result_type='insufficient_data' if phase=='unknown' else 'clinician_choice',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],source_actions=[],missing_fields=['external_context.treatment_phase'] if phase=='unknown' else [],clinical_clearance=False,no_automatic_medication_change=True,no_automatic_target_start=True)
        ee.pop('stop_medication',None);ee.pop('source_condition',None)
        ee['phase_clarification']='Unknown or inconsistent/not-started source actor: no current-treatment cessation action; physician assesses the reported event.'
        new.append(n)
F['cases']+=new
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
s=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
s['external_context']['treatment_phase']['origin']='Explicit selected/A status. selected_mode is only desired mode; for start it means first administration. For other modes, active consumed known positive actual current_dose may establish ongoing at the final action gate after that input is received. Proposed/planned/unknown/zero or inactive dose cannot. Explicit unknown/not_started overrides derivation and needs clinical clarification for a current-use action. B phase is never inferred from A.'
(O/'input_contracts.yaml').write_text(yaml.safe_dump(s,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
p=O/'build_graphs.py';t=p.read_text(encoding='utf-8');t=t.replace('import json,csv,yaml','import json,csv,yaml\nfrom phase_provenance import selected_phase')
t=t.replace("if r['identity']['mode']=='start' and ctx.get('treatment_phase') in {'ongoing','unknown'}:init.append('selected_drug_treatment_phase')","if ctx.get('treatment_phase') in {'ongoing','unknown','not_started'} and not (r['identity']['mode']=='start' and ctx.get('treatment_phase')=='not_started'):init.append('selected_drug_treatment_phase')")
t=t.replace("ask_policy='ongoing or explicitly unknown selected phase costs one additional fact; first start derives not_started from explicit start selection; B phase remains separate'","ask_policy='Every explicit selected/A status costs one fact except first-start not_started derived from start selection. Nonstart selected_mode alone has no current-use evidence; final source action may use consumed known positive actual current_dose; B remains separate'")
t=t.replace("p=dict(rule_id=rid,branch_id=c['branch_id']","p=dict(resolved_selected_phase=selected_phase(r,c)[0],selected_phase_provenance=selected_phase(r,c)[1],rule_id=rid,branch_id=c['branch_id']")
p.write_text(t,encoding='utf-8')
p=O/'verify_contracts.py';t=p.read_text(encoding='utf-8');t=t.replace('import yaml','import yaml\nfrom phase_provenance import selected_phase,owns_selected_action',1)
a="        rid=c['rule_id'];con=cs[rid];g=c['given'];e=c['expected']"
t=t.replace(a,a+"\n        if owns_selected_action(rs[rid],e):ck(selected_phase(rs[rid],c)[0]=='ongoing','selected/A current-treatment source action lacks phase evidence: '+c['case_id'])",1)
p.write_text(t,encoding='utf-8')
(O/'phase_semantics_repairs.json').write_text(json.dumps(dict(changed_fixtures=changes,new_counter_fixtures=len(new),scope='Explicit actor evidence, actual consumed dose provenance and honest phase counts; no new medical dose or source action'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Explicit A fixture phase fixes',len(changes),'counterfixtures',len(new))
