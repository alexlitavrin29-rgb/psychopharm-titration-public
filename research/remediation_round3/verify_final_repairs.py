"""Regression for independently found phase, population, necessity and order defects."""
from pathlib import Path
from copy import deepcopy
import json,yaml
import verify_contracts
from phase_provenance import selected_phase,owns_selected_action
O=Path(__file__).resolve().parent

def check(d,graphs,paths):
    errors=[]
    def ck(ok,msg):
        if not ok:errors.append(msg)
    con=d['contracts'];cases={c['case_id']:c for c in d['cases']}
    p=con['parox-taper-example']['input_requirements']
    ck(p['current_dose']==dict(kind='field_true',field='example_selected'),'PAR dose required without selected example')
    for k in ['duration','past_withdrawal']:
        ck(p[k]==dict(kind='all_equals',values=dict(example_selected=True,current_dose=40)),'PAR history required outside chosen40 example: '+k)
    for c in d['cases']:
        e=c['expected'];rid=c['rule_id']
        if owns_selected_action(d['rules'][rid],e):ck(selected_phase(d['rules'][rid],c)[0]=='ongoing','Current A action lacks actually consumed ongoing evidence: '+c['case_id'])
        if '--audit-final-A-phase-' in c['case_id']:
            ck(not e.get('source_actions') and not e.get('stop_medication') and e.get('total_daily_dose_mg') is None,'Unknown/notstarted A received current-use action: '+c['case_id'])
        if '--audit-final-qualitative-' in c['case_id']:
            ck(e['result_type']=='clinician_choice' and not e['schedule'] and e['total_daily_dose_mg'] is None,'PAR inactive history blocks qualitative result')
        if rid in {'preg-taper-limit','phen-taper-limit'}:
            ck(e.get('individual_duration_weeks') is None and e.get('individual_taper_schedule') is None,'Source-only cessation assigned individual duration: '+c['case_id'])
            if '--audit-final-age-' in c['case_id']:
                age=c['given'].get('age');state='adult' if type(age) in (int,float) and age>=18 else 'nonadult_plan_not_established' if type(age) in (int,float) else 'not_assessed'
                ck(e.get('population_applicability')==state,'Unknown/child population normalized to adult: '+c['case_id'])
                if state=='not_assessed':ck('age' in e.get('unassessed_context',[]),'Unknown age assessment hidden: '+c['case_id'])
    for rid in ['preg-taper-limit','phen-taper-limit']:
        ck(con[rid]['input_requirements']['age']['kind']=='reported_source_information','Source-only adult reference requires unconditional age: '+rid)
        ck('age' not in con[rid]['required_inputs'],'Source-only age still required: '+rid)
        ck(all(b['expected_output'].get('prior_dose_resumption') is None for b in con[rid]['branches']),'Unsupported prior dose resumption: '+rid)
    phen=next(i for i in d['rules']['phen-taper-limit']['inputs'] if i['input_id']=='withdrawal_severity')
    ck('не устанавливает' in phen['necessity_reason'] and '§4.4 с.4' in phen['source_locator'],'Unsupported PHEN severity hold/resumption/slower claim')
    ck('§4.2 PDF с.2' in d['rules']['phen-taper-limit']['logic']['actions'][0],'PHEN gradual locator incorrect')
    preg=' '.join(d['rules']['preg-taper-limit']['logic']['actions'])
    ck('КР предусматривает более медленную индивидуальную отмену' not in preg and 'не задаёт более медленный протокол прегабалина' in preg,'AD protocol borrowed for PREG')
    for graph in graphs:
        order={n['node_id']:i for i,n in enumerate(graph['nodes'])}
        for i in d['rules'][graph['rule_id']]['inputs']:
            p=i['requirement_predicate'];k=p['kind'];deps=[]
            if k=='field_true':deps=[p['field']]
            if k=='all_equals':deps=list(p['values'])
            if k in {'increase','action_choice','indication_action_choice'}:deps=['clinician_action']
            if k in {'maoi_record','stopped_maoi_record'}:deps=['medicines']
            if k=='ecg_if_cad':deps=['coronary_disease']
            if k=='correction_if_electrolytes':deps=['electrolyte_disturbance']
            for dep in deps:ck(order.get('assess_'+dep,10**9)<order.get('check_'+i['input_id'],-1),'Question control not answered before dependent: '+graph['rule_id']+'/'+i['input_id'])
    for p in paths:
        ctx=p['full_external_context'];r=d['rules'][p['rule_id']]
        explicit=ctx.get('treatment_phase') in {'ongoing','unknown','not_started'} and not (r['identity']['mode']=='start' and ctx.get('treatment_phase')=='not_started')
        ck(('selected_drug_treatment_phase' in p['initial_selections'])==explicit,'Explicit A phase hidden/double inferred from mode: '+p['full_example'])
        c=dict(given=p['full_projected_given'],external_context=ctx)
        phase,origin=selected_phase(r,c)
        ck((p['resolved_selected_phase'],p['selected_phase_provenance'])==(phase,origin),'Projected phase consumes unasked input: '+p['full_example'])
        if owns_selected_action(r,p['full_projected_expected']):ck(phase=='ongoing','Projected current A action without ongoing phase: '+p['full_example'])
    return errors

def run():
    d=verify_contracts.collect();graphs=yaml.safe_load((O/'question_graphs.yaml').read_text(encoding='utf-8'))['graphs'];paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
    errors=check(d,graphs,paths);mutations=[]
    for name in ['PAR_universal_history','PHEN_false_hold_protocol','PREG_borrowed_AD_protocol','unknown_age_as_adult','unknown_A_action','hidden_A_phase','controller_after_dependent','proposed_dose_as_current_use','inactive_dose_as_current_use','zero_dose_as_current_use','unknown_dose_as_current_use']:
        x=deepcopy(d);gg=deepcopy(graphs);pp=deepcopy(paths)
        if name=='PAR_universal_history':x['contracts']['parox-taper-example']['input_requirements']['duration']={'kind':'always'}
        elif name=='PHEN_false_hold_protocol':next(i for i in x['rules']['phen-taper-limit']['inputs'] if i['input_id']=='withdrawal_severity')['necessity_reason']='Тяжесть задаёт hold/resumption/slower по инструкции'
        elif name=='PREG_borrowed_AD_protocol':x['rules']['preg-taper-limit']['logic']['actions'].append('КР предусматривает более медленную индивидуальную отмену')
        elif name=='unknown_age_as_adult':next(c for c in x['cases'] if c['case_id']=='preg-taper-limit--audit-final-age-unknown')['expected']['population_applicability']='adult'
        elif name=='unknown_A_action':next(c for c in x['cases'] if '--audit-final-A-phase-unknown' in c['case_id'])['expected']['source_actions']=[dict(action='discontinue_selected_medication',medication_role='selected_or_A')]
        elif name=='hidden_A_phase':next(p for p in pp if 'selected_drug_treatment_phase' in p['initial_selections'])['initial_selections'].remove('selected_drug_treatment_phase')
        elif name=='controller_after_dependent':
            ns=next(g for g in gg if g['rule_id']=='ser-adult-adjust')['nodes'];node=next(n for n in ns if n['node_id']=='assess_clinician_action');ns.remove(node);ns.append(node)
        else:
            r=x['rules']['ser-adult-adjust'];i=next(i for i in r['inputs'] if i['input_id']=='current_dose')
            if name=='proposed_dose_as_current_use':i['fact_semantics']='proposed_daily_dose'
            elif name=='inactive_dose_as_current_use':i['requirement_predicate']={'kind':'reported_context'}
            else:next(c for c in x['cases'] if c['case_id']=='ser-adult-adjust--audit-recheck-symptomatic_hyponatremia-positive')['given']['current_dose']=0 if name=='zero_dose_as_current_use' else 'unknown'
        found=check(x,gg,pp);caught=bool(found);mutations.append(dict(mutation=name,rejected=caught,evidence=found[:2]))
        if not caught:errors.append('Mutation not rejected: '+name)
    result=dict(status='pass' if not errors else 'fail',negative_mutations=mutations,cases=len(d['cases']),paths=len(paths),scope='Regression for reviewed research contracts; no calculator execution, no exhaustive medical audit or clinical validation',errors=errors)
    (O/'final_repair_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
