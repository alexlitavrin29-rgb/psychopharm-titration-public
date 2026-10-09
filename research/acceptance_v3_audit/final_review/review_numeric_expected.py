"""Independent source-bound static expected checks, not an executable dose calculator."""
from pathlib import Path
import json,yaml,hashlib,collections,sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
S=read(R/'sources.json');RULES={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')};C=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules'];F=read(R/'full_scenarios.json')['cases']
errors=[];checks=[]
def check(c,label,ok,details=None):
    checks.append(dict(case_id=c['case_id'],rule_id=c['rule_id'],check=label,pass_=bool(ok),details=details))
    if not ok:errors.append(checks[-1])
def value(v,path):
    for k in path.split('.'):
        if not isinstance(v,dict):return None
        v=v.get(k)
    return v
for c in F:
    e=c['expected'];g=c['given'];rid=c['rule_id'];mode=RULES[rid]['identity']['mode'];typ=e['result_type']
    check(c,'no clinical clearance',e.get('clinical_clearance') is False)
    check(c,'no unconditional future stages',e.get('unconditional_future_stages') is not True)
    if typ=='exact':
        d=e['total_daily_dose_mg'];q=e['administrations_per_day'];u=e['dose_per_administration_mg']
        check(c,'dose division',d==q*u)
        if rid.startswith('ago-'):
            check(c,'AGO current source25 not conditional50',d==25 and q==1)
            check(c,'AGO indication age boundaries',g.get('age',0)>=18 and (g['age']<=65 if rid=='ago-gad-start' else g['age']<75))
        elif rid=='dulox-depression-start':check(c,'DULOX BDR60',d==60 and q==1 and not e.get('automatic_escalation_to_120'))
        elif rid=='dulox-gad-start':
            older=g.get('elderly_population');dep=g.get('comorbid_depression')
            check(c,'DULOX GAD separate four branches',not(older is True and dep is True) and d==(60 if dep is True else 30) and q==1)
            if older is True:check(c,'DULOX elderly2wk',e.get('initial_period_weeks')==2 and e.get('conditional_next_total_mg')==60)
        elif rid.startswith('esc-'):
            check(c,'ESC ordinary max20',0<d<=20 and q==1)
            if rid in {'esc-cyp2c19-start','esc-hepatic-start','esc-elderly-start','esc-panic-start'}:check(c,'ESC source start5',d==5)
            elif rid in {'esc-gad-start','esc-social-start'}:check(c,'ESC source start10',d==10)
            if rid in {'esc-cyp2c19-start','esc-hepatic-start'}:check(c,'ESC special2wk then10 conditional',e.get('initial_period_weeks')==2 and e.get('conditional_next_total_mg')==10)
            if rid=='esc-elderly-start':check(c,'ESC strictlyolder65',g.get('age',0)>65 and e.get('maximum_mg')==10 and e.get('automatic_day_for_increase') is None)
        elif rid=='fluvox-depression-start':check(c,'FLUV selected50/100',d in[50,100] and d==g.get('source_start_choice') and q==1 and e.get('review_period_weeks')==[3,4])
        elif rid=='parox-panic-kr':check(c,'PAR panic10',d==10 and q==1 and e.get('maximum_mg') in[40,60])
        elif rid=='preg-gad-start':check(c,'PREG GAD150/2or3',d==150 and q in[2,3] and q==g.get('frequency') and e.get('optional_stages_mg')==[300,450,600] and e.get('minimum_interval_weeks')==1)
        elif rid=='ser-adult-adjust':
            cur=g.get('current_dose');act=g.get('clinician_action')
            check(c,'SER physician keep/increase primary arithmetic',q==1 and ((act=='keep' and d==cur) or (act=='increase' and d==(50 if cur==25 else cur+50) and d<=200)))
            if act=='increase':check(c,'SER minimum1wk',g.get('time_at_dose',0)>=1)
        elif rid in {'ser-panic-start','ser-social-start'}:check(c,'SER source25→50firstweek',d==25 and q==1 and e.get('schedule',[{},{}])[1].get('day')==8 and e['schedule'][1]['total_daily_mg']==50)
        elif rid.startswith('venla-xr-'):check(c,'XR75/225/min2wk',d==75 and q==1 and e.get('maximum_mg')==225 and e.get('minimum_increase_interval_weeks')==2)
        else:check(c,'exact family explicit oracle',False,rid)
    if rid=='preg-gad-adjust' and e.get('published_option_mg'):
        cur=g['current_dose'];check(c,'PREG next published option',e['published_option_mg']=={150:300,300:450,450:600}.get(cur) and e['minimum_interval_weeks']==1 and e['frequency_option'] in[2,3] and e['per_administration_option_mg']*e['frequency_option']==e['published_option_mg'])
    if rid=='preg-renal-start' and 'source_start_mg' in e:
        cl=g.get('clcr');cl=cl.get('value') if isinstance(cl,dict) else cl
        row=(150,600,[2,3]) if isinstance(cl,(int,float)) and cl>=60 else ((75,300,[2,3]) if isinstance(cl,(int,float)) and cl>=30 else (([25,50],150,[1,2]) if isinstance(cl,(int,float)) and cl>=15 else (25,75,[1])))
        check(c,'PREG independent renal table row and boundaries',isinstance(cl,(int,float)) and cl>=0 and (e['source_start_mg'],e['maximum_mg'],e['frequency_options'])==row)
        check(c,'PREG table no selected endpoint or invented renal interval',e.get('auto_selected_range_endpoint') is None and e.get('source_interval_for_renal_titration') is None)
    if rid=='dulox-gad-adjust' and e.get('published_options_mg'):
        check(c,'DULOX next published options conditional on actual current dose',e['published_options_mg']=={30:[60],60:[90,120]}.get(g.get('current_dose')) and e.get('automatic_interval_days') is None)
    if rid.startswith('venla-xr-') and e.get('published_reduction_percent'):
        check(c,'XR50percent arithmetic vs executability',e['published_reduction_percent']==50 and e.get('arithmetic_total_mg')==37.5 and e.get('executable_dose') is None)
    if rid=='venla-xr-panic-form-limit' and e.get('source_initial_mg') is not None:check(c,'XR37.5first7d/75 noIR',e.get('source_initial_mg')==37.5 and e.get('initial_days')==7 and e.get('source_next_mg')==75 and e.get('IR_substitution_allowed') is False)
    dc=e.get('duration_constraint',{})
    if dc:
        check(c,'taper no hard upper/exact duration',dc.get('hard_upper_limit_weeks') is None and dc.get('exact_taper_duration_weeks') is None)
        if rid=='dulox-taper-limit':check(c,'DULOX min2 reconciles4.2/4.4',dc.get('chosen_minimum_weeks')==2 and dc.get('source_options_weeks')==[1,2])
        if rid=='preg-taper-limit':check(c,'PREG adultreference noindividualduration',e.get('individual_duration_weeks') is None and not e.get('individual_taper_schedule'))
    if rid in {'preg-taper-limit','phen-taper-limit'}:
        check(c,'PREG PHEN no borrowed resumption',e.get('prior_dose_resumption') is None and e.get('slower_step') is None and not e.get('individual_taper_schedule'))
    if typ=='selected_source_example':
        if rid=='parox-taper-example':check(c,'PAR40 selected exactconditionalexample',g.get('example_selected') is True and g.get('current_dose')==40 and [(s['day'],s['total_daily_mg'],s['conditional']) for s in e['schedule']]==[(1,30,True),(8,20,True),(15,0,True)])
        elif rid=='switch-parox-ago-selected-example':
            a=[];b=[]
            for stage in e['schedule']:
                for v in stage['medication_steps']:
                    (a if v['medication_inn']=='пароксетин' else b).append(v['total_daily_dose'])
            check(c,'PAR40 plus AGO independent day1 composition',a==[30,20,0] and b==[25,25,25] and e.get('trial_validated_pair') is False)
    sc=e.get('source_condition')
    if sc and 'input' in sc:
        field=sc['input'];v=value(g,field);op=sc.get('operator');want=sc.get('value')
        if op=='category_equals' and isinstance(v,dict):v=v.get('category') or v.get('source_category')
        if op=='category_equals':check(c,'source condition backed by exact given',v==want,dict(field=field,given=v,claimed=want))
        if op in ['is_true','equals_true']:check(c,'source condition positive given',v is True,field)
        if op in ['>','greater_than']:check(c,'source strict greater inequality',isinstance(v,(int,float)) and v>want,dict(field=field,given=v,claimed=want))
    # Every known caution/exclusion uses its own source gate and scope. Cessation has
    # intentionally narrower scope; do not apply prestart exclusions to it here.
    if mode not in ['taper','stop'] and typ in ['exact','selected_source_example']:
        for gate in C[rid]['source_gates']:
            for f in gate.get('exclusions',[])+gate.get('cautions',[]):
                if g.get(f) is True:check(c,'known source gate never ordinary executable result',False,dict(source=gate['source_ref'],field=f))
    check(c,'non-numeric outcomes no invented dose',typ in ['exact','selected_source_example'] or (e.get('total_daily_dose_mg') is None and e.get('dose_per_administration_mg') is None))
save('all_expected_check_results.json',dict(snapshot=read(ROOT/'research/remediation_round3/final_manifest_v3_review1.json')['snapshot_sha256'],scope='All prepared expected examined against explicitly written independent primary numeric and guard assertions. Assertions do not execute an application or prove all branch selection logic.',cases=len(F),checks=len(checks),errors=errors,rows=checks))
print('cases',len(F),'checks',len(checks),'errors',len(errors));print(json.dumps(errors[:20],ensure_ascii=False,indent=2))
