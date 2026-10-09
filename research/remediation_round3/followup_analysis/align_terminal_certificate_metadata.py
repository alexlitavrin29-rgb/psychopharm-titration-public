"""Same facts receive one result; unknown caution is explicitly clarification only."""
from pathlib import Path
from copy import deepcopy
import json,collections
O=Path(__file__).resolve().parent.parent
assert not (O/'terminal_certificate_alignment.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[];groups=collections.defaultdict(list)
for c in F['cases']:
 e=c['expected'];cert=e.get('terminal_source_certificate',{})
 if cert.get('result_type')=='clinician_choice':
  unknown=[k for k,v in cert['causal_values'].items() if v in (None,'unknown','not_assessed')]
  if unknown:
   assert not e.get('source_actions') and e['total_daily_dose_mg'] is None
   e['clarification_only']=True;e['missing_fields']=sorted(set(e['missing_fields'])|set(unknown));e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|set(unknown))
   cert['scope']='Only clarification of the named unknown current-event input; no assertion of this condition, current medication action, dose, clinical admission or target permission'
   rows.append(dict(case_id=c['case_id'],change='Unknown current event remains named/unassessed; explicitly clarification only',fields=unknown))
 groups[json.dumps([c['rule_id'],c['given'],c['external_context']],sort_keys=True,ensure_ascii=False)].append(c)
for group in groups.values():
 if len(group)<2 or all(c['expected']==group[0]['expected'] for c in group):continue
 ref=deepcopy(group[0]['expected']);diff={k for c in group for k in set(c['expected'])|set(ref) if c['expected'].get(k)!=ref.get(k)}
 assert diff<={'terminal_source_certificate','source_condition','reason_ids'},([c['case_id'] for c in group],diff)
 if 'reason_ids' in diff:ref['reason_ids']=sorted({k for c in group for k in c['expected'].get('reason_ids',[])})
 certificates=[c['expected']['terminal_source_certificate'] for c in group]
 ref['additional_sufficient_primary_causes']=list({json.dumps(dict(source_ref=x['source_ref'],source_locator=x['source_locator'],causal_values=x['causal_values'],source_owner_input=x['source_owner_input']),sort_keys=True,ensure_ascii=False):dict(source_ref=x['source_ref'],source_locator=x['source_locator'],causal_values=x['causal_values'],source_owner_input=x['source_owner_input']) for x in certificates}.values())
 condition=next((c['expected']['source_condition'] for c in group if c['expected'].get('source_condition')),None)
 if condition is not None:ref['source_condition']=condition
 for c in group:
  c['expected']=deepcopy(ref);rows.append(dict(case_id=c['case_id'],change='Same typed input/context has identical limited result; alternate sufficient source causes remain explicit, no changed medical action/dose'))
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'terminal_certificate_alignment.json').write_text(json.dumps(dict(rows=rows,medical_action_or_numerical_dose_changed=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Clarification/same-state metadata alignment',len(rows))
