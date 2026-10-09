from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
unknown=[None,'unknown','not_assessed','неизвестно','не исследовано','не помню']
for c in D['cases']:
    if c['rule_id'].startswith('esc') and c['expected']['result_type']=='exact':
        c['expected']['unassessed_context']=[k for k in C[c['rule_id']]['monitoring_context_fields'] if k not in c['given'] or c['given'][k] in unknown]
        c['expected']['clinical_clearance']=False
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
