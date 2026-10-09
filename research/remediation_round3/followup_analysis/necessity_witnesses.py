"""Locate candidate functional witnesses; primary reading must establish necessity."""
from pathlib import Path
from collections import defaultdict,Counter
import json,yaml,hashlib
O=Path(__file__).resolve().parent.parent
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']
rs={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
unknown={'unknown','not_assessed','неизвестно','не исследовано','не помню'}
def known(v):
    if v is None or isinstance(v,str) and v in unknown:return False
    if isinstance(v,dict):return all(known(x) for x in v.values())
    if isinstance(v,list):return all(known(x) for x in v)
    return True
keys=['result_type','total_daily_dose_mg','dose_per_administration_mg','administrations_per_day','schedule','stop_medication','source_actions','source_condition','published_option_mg','minimum_interval_days','duration_constraint','automatic_next_reduction','prior_dose_resumption','population_applicability']
rows=[]
for rid,r in rs.items():
    cases=[c for c in F if c['rule_id']==rid]
    for i in r['inputs']:
        k=i['input_id'];groups=defaultdict(list);witnesses=[]
        for c in cases:
            if k not in c['given'] or not known(c['given'][k]):continue
            others={a:v for a,v in c['given'].items() if a!=k}
            sig=hashlib.sha256(json.dumps([others,c['external_context']],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            groups[sig].append(c)
        for group in groups.values():
            for a in group:
                b=next((b for b in group if a['given'][k]!=b['given'][k] and any(a['expected'].get(x)!=b['expected'].get(x) for x in keys)),None)
                if b:
                    changed=[x for x in keys if a['expected'].get(x)!=b['expected'].get(x)]
                    witnesses.append(dict(case_a=a['case_id'],value_a=a['given'][k],case_b=b['case_id'],value_b=b['given'][k],changed_output_fields=changed));break
            if witnesses:break
        rows.append(dict(rule_id=rid,input_id=k,predicate=i['requirement_predicate'],source_refs=i['source_refs'],source_locator=i['source_locator'],authored_reason=i['necessity_reason'],candidate_same_other_inputs_witness=witnesses,primary_verified=False,limitation='A prepared expected difference only locates a candidate; it neither proves medical truth nor establishes that the chosen result scope requires this question. Absence is not proof of redundancy.'))
report=dict(snapshot=json.loads((O/'final_manifest.json').read_text(encoding='utf-8'))['snapshot_sha256'],nature='Preparatory evidence inventory, not acceptance or a clinical engine',rows=rows)
(O/'followup_analysis/necessity_witness_candidates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(inputs=len(rows),always=sum(x['predicate']['kind']=='always' for x in rows),always_with_candidate=sum(x['predicate']['kind']=='always' and bool(x['candidate_same_other_inputs_witness']) for x in rows),by_kind=dict(Counter(x['predicate']['kind'] for x in rows))),ensure_ascii=False))
