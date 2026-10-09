"""Repair inherited ordinary fixture values; physician plan is not a published ESC ladder."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));fixed=[]
for c in D['cases']:
    rid=c['rule_id'];g=c['given']
    if rid not in ['esc-adult-adjust','esc-taper-limit','switch-esc-ago','switch-esc-ser']:continue
    if type(g.get('current_dose')) in {int,float} and g['current_dose']>20:
        fixed.append(dict(case_id=c['case_id'],old_current_dose=g['current_dose'],new_current_dose=10))
        g['current_dose']=10
    if isinstance(g.get('from_taper_plan'),dict):
        for stage in g['from_taper_plan']['stages']:
            if stage.get('total_daily_mg',0)>10:stage['total_daily_mg']=5
        g['from_taper_plan']['basis']='Synthetic physician-supplied initial reduction10→5, achievable by an equal half of a10mg tablet (§3 с.1). Not a source-authored ESC calendar; subsequent stages remain physician decisions.'
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'fixture_dose_repairs.json').write_text(json.dumps(dict(origin='Independent final review IR2-01',cases=fixed,source='RU-ESC §4.2 с.2 maximum20; ordinary confirmed10; form half10 §3 с.1',clinical_claim=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Ordinary ESC A/current fixtures repaired:',len(fixed))
