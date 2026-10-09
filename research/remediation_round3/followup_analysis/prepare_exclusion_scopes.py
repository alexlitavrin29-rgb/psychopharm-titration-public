"""Propose finite primary-bound cause scopes; does not mutate the frozen core."""
from pathlib import Path
import json,yaml
O=Path(__file__).resolve().parent.parent
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']
N={(x['rule_id'],x['field']):x['primary_norms'] for x in json.loads((O.parent/'acceptance_v2_audit/condition_completion/scoped_input_conditions.json').read_text(encoding='utf-8'))}
rows=[];missing=[]
for c in F:
 e=c['expected'];rid=c['rule_id'];g=c['given'];r=R[rid];ins={i['input_id']:i for i in r['inputs']};cid=c['case_id']
 if e['result_type']!='not_applicable':continue
 sc=e.get('source_condition',{});key=sc.get('input');sid=sc.get('source_ref');fields=[]
 if not key:
  fields=[k for k in e.get('reason_ids',[]) if k in ins]
  if fields:key=fields[0]
  elif '--under18-' in cid or '--age-' in cid or '--current-age-' in cid:key='age'
  elif '--current-alt_ratio_uln-' in cid:key='alt_ratio_uln'
  elif '--current-ast_ratio_uln-' in cid:key='ast_ratio_uln'
  elif '--ALT_ratio-' in cid:key='ALT_ratio'
  elif '--AST_ratio-' in cid:key='AST_ratio'
  elif '--alt_ratio_uln-' in cid:key='alt_ratio_uln'
  elif '--ast_ratio_uln-' in cid:key='ast_ratio_uln'
  elif '--clcr-' in cid or '--absolute-GFR-' in cid:key='renal_metric'
  elif '--round2-seizure-' in cid:key='seizure_state'
  elif any(x in cid for x in ['--medicine-','--maoi-','--reversible-','--current-contra-','--current-target-contra-','--current-maoi-','--current-moclobemide-']):key='medicines'
 if key not in ins or key not in g:missing.append(cid);continue
 if not fields:fields=[key]
 if sid is None:
  sid=next((s for s in ins[key]['source_refs'] if '--exclude-'+s+'-' in cid or '--medicine-'+s+'-' in cid),None)
  if sid is None:sid='RU-AGO' if key in {'ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln','dementia'} or '--age-75' in cid or '--age-66' in cid or '--current-target-contra-' in cid else ins[key]['source_refs'][0]
 if sid not in ins[key]['source_refs']:missing.append(cid+' / wrong owner '+sid);continue
 if key=='dementia':fields.append('elderly_population');assert g.get('elderly_population') is True,cid
 if key=='medicines':
  # Each actually used MAOI type/time is required, no type for an unclassified record.
  if any(m.get('interaction_class')=='maoi' for m in g[key]):
   stopped=any(m.get('interaction_class')=='maoi' and m.get('status')=='stopped' for m in g[key])
   if stopped and 'maoi_type' in ins:fields.append('maoi_type')
   if stopped and 'maoi_stopped_at' in ins:fields.append('maoi_stopped_at')
 fields=sorted(set(fields));assert all(k in g for k in fields),cid
 form=next((i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form' and sid in i['source_refs']),None)
 assert form and g[form]['source_id']==sid,cid
 keys={k:g[k] for k in fields};components={}
 if ins[key]['data_type']=='paired_allergy':
  actor=sc.get('field') or ('B' if form=='to_form' else 'A')
  assert g[key].get(actor) is True,cid
  keys[key]={actor:True};components[key]=[key+'.'+actor]
 norms=[n for n in N[(rid,key)] if n['source_id']==sid];assert norms,cid
 phase={}
 if key in {'ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln'}:
  phase={'target_treatment_phase':c['external_context']['target_treatment_phase']} if r['identity']['mode']=='switch' else {'treatment_phase':c['external_context']['treatment_phase']}
  assert (phase.get('target_treatment_phase')=='not_started' if r['identity']['mode']=='switch' else phase['treatment_phase'] in {'not_started','selected_mode'} and r['identity']['mode']=='start'),cid
 rows.append(dict(case_id=cid,rule_id=rid,source_ref=sid,source_owner_input=form,causal_values=keys,fact_components=components,required_phase_context=phase,primary_norms=norms,original_condition=sc,source_condition_field=key,calculation_at=c['external_context'].get('calculation_at') if 'maoi_stopped_at' in fields else None,scope='Only known source exclusion of the standard numerical branch; no current medication cessation, clinical admission or new treatment permission',review_status='AUTHOR_PROPOSAL_FOR_INDEPENDENT_CAUSAL_CHECK'))
out=dict(rows=rows,missing=missing,nature='Finite sufficient-fact proposals from already independently sourced exclusions; primary norm is not itself automatic necessity proof')
(O/'followup_analysis/exclusion_scope_proposals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Proposals',len(rows),'unmapped',len(missing));print(missing)
