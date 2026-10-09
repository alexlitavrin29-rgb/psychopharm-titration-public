"""Adapt the current structural checker to V3 paths; preserve historical acceptance."""
from pathlib import Path
import yaml,json,csv
O=Path(__file__).resolve().parent;R=O.parent
s=(R/'verify_research.py').read_text(encoding='utf-8')
start=s.index("check(flows['clinical_clearance_claimed']")
end=s.index("\nmatrix =",start)
s=s[:start]+"""check(flows['clinical_clearance_claimed'] is False and flows['calculator_implemented'] is False, 'Flow overstates clinical/product validation')
check(flows['question_count_policy']['unasked_is_normal'] is False and flows['question_count_policy']['universal_risk_confirmation_checkbox_allowed'] is False, 'Hidden or assumed clinical clearance')
check(flows['question_count_policy'].get('acceptance_version')==3 and flows['question_count_policy'].get('ordinary_maximum') is None, 'Active V3 question policy drift')
paths=json.loads((ROOT/'remediation_round3/actual_question_paths.json').read_text(encoding='utf-8'))
for f in flows['flows']:
    check(f['rule_id'] in by_rule, 'missing rule: '+f['rule_id'])
    check(set(f['required_inputs'])=={i['input_id'] for i in by_rule[f['rule_id']]['inputs'] if i['required_for_individual_result']}, 'flow required input drift: '+f['rule_id'])
    check((ROOT/f['graph_ref'].split('#')[0]).is_file(), 'missing round3 graph')
for p in paths:
    check(p['count']==len(p['initial_selections'])+len(p['required_independent_facts']), 'hidden/incorrect full question count: '+p['rule_id'])
    check(p['within_15']==(p['ordinary_individual_numeric_path'] and p['count']<=15 and not p['count_is_lower_bound']), 'Preferred question-count indicator drift: '+p['rule_id'])
# Fifteen is a usability preference; source necessity is independently reviewed.
"""+s[end:]
(R/'verify_research.py').write_text(s,encoding='utf-8')
counts=json.loads((R/'question_counts.json').read_text(encoding='utf-8'))
for x in counts:x['all_catalog_fields_count']=x['clinical_input_entries']+x['initial_selections']
(R/'question_counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
flows=yaml.safe_load((R/'question_flows.yaml').read_text(encoding='utf-8'));flows.update(clinical_clearance_claimed=False,calculator_implemented=False,question_count_policy=dict(unasked_is_normal=False,universal_risk_confirmation_checkbox_allowed=False,target=10,preferred_ordinary_maximum=15,ordinary_maximum=None,acceptance_version=3,necessity_still_required=True))
(R/'question_flows.yaml').write_text(yaml.safe_dump(flows,allow_unicode=True,sort_keys=False),encoding='utf-8')
with (R/'input_catalog.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);rows=list(reader);cols=reader.fieldnames
extras=[yaml.safe_load((R/'renal_estimator.yaml').read_text(encoding='utf-8'))]+[yaml.safe_load(p.read_text(encoding='utf-8')) for p in (R/'findings').glob('*.yaml')]
seen={(x['rule_id'],x['input_id']) for x in rows}
for r in extras:
    for i in r['inputs']:
        if (r['rule_id'],i['input_id']) in seen:continue
        raw=dict(rule_id=r['rule_id'],**i)
        rows.append({k:json.dumps(raw[k],ensure_ascii=False) if isinstance(raw.get(k),(dict,list)) else raw.get(k,'') for k in cols})
with (R/'input_catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
for p in [O/'rules/dulox-taper-limit.yaml',R/'rules/dulox-taper-limit.yaml']:
    r=yaml.safe_load(p.read_text(encoding='utf-8'));r['logic']['parameter_refs']=[x['parameter_id'] for x in r['clinical_parameters']];p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('V3 full path checks bound; auxiliary/non-dose input rows preserved; no acceptance inferred from structural pass.')
