"""Apply only the independently identified22 inherited sparse population labels."""
from pathlib import Path
import json
O=Path(__file__).resolve().parent.parent
assert not (O/'sparse_population_metadata_repairs.json').exists(),'One-use correction'
review=json.loads((O.parent/'acceptance_v3_audit/final_recheck/terminal_scope_checks.json').read_text(encoding='utf-8'))
ids={x['case_id'] for x in review['errors'] if x['check']=='population known only if actually adult'};assert len(ids)==22
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));rows=[]
for c in F['cases']:
 if c['case_id'] not in ids:continue
 assert c['given'].get('age') in (None,'unknown','not_assessed') and c['expected']['population_applicability']=='adult_source_population'
 c['expected']['population_applicability']='not_assessed';c['expected']['unassessed_context']=sorted(set(c['expected']['unassessed_context'])|{'age'})
 rows.append(dict(case_id=c['case_id'],old='adult_source_population',new='not_assessed',reason='Source population does not confirm this absent/unknown patient age'))
assert len(rows)==22
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'sparse_population_metadata_repairs.json').write_text(json.dumps(dict(rows=rows,medical_numbers_or_actions_changed=False,scope='Only patient applicability metadata/unassessed age in22 independently named sparse witnesses'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Inherited population labels repaired',len(rows))
