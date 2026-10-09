"""Resolve interaction class before asking a class-specific MAOI question."""
from pathlib import Path
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'maoi_unknown_class_repairs.json').exists(),'One-use correction'
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));changes=[]
for c in F['cases']:
    meds=c['given'].get('medicines');e=c['expected']
    if not isinstance(meds,list):continue
    ids={m['record_id'] for m in meds if m.get('interaction_class')=='unknown'}
    removed=[k for k in e.get('missing_fields',[]) if any(k==f+'.'+ident for f in ['maoi_type','maoi_stopped_at'] for ident in ids)]
    if removed:
        e['missing_fields']=[k for k in e['missing_fields'] if k not in removed]
        e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k.split('.')[0] for k in removed})
        e['interaction_class_clarification']='First resolve each named unknown interaction class. This cannot establish absence of a contraindication. MAOI type/stopped timestamp are requested only for a confirmed MAOI record, with separate record-specific source clocks.'
        changes.append(dict(case_id=c['case_id'],unknown_records=sorted(ids),removed_premature_requests=removed))
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
S=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
S['requirement_predicates']['maoi_record']='Known interaction_class=maoi in a named medicine record. Unknown class requires class clarification first; it is not treated as a negative and does not activate a speculative MAOI-type question.'
S['requirement_predicates']['stopped_maoi_record']='Known interaction_class=maoi and status=stopped in the same named record; type and stop timestamp are separate counted facts. Unknown class cannot establish a source clock.'
(O/'input_contracts.yaml').write_text(yaml.safe_dump(S,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'maoi_unknown_class_repairs.json').write_text(json.dumps(dict(changes=changes,scope='Question ordering and explicit unknown-class handling; known MAOI type, timestamps, directions and published source intervals unchanged'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Unknown-class MAOI ordering corrected',len(changes))
