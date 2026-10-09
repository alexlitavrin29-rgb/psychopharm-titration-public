"""Prepare and apply the audit's graph projection correction after the initial audit."""
from pathlib import Path

O=Path(__file__).resolve().parent
p=O/'build_graphs.py'
text=p.read_text(encoding='utf-8')
text=text.replace("    if k=='ongoing_selected_drug':return ctx.get('treatment_phase')=='ongoing'", "    if k=='ongoing_selected_drug':return ctx.get('treatment_phase')=='ongoing'\n    if k=='target_ongoing':return ctx.get('target_treatment_phase')=='ongoing'")
text=text.replace("or '--r3-' in c['case_id'])", "or '--r3-' in c['case_id'] or '--audit-v2-' in c['case_id'])")
before="        expected=deepcopy(c['expected'])\n        if numeric:"
after="""        expected=deepcopy(c['expected'])
        # A projected complete path cannot confirm values it did not receive.
        expected['confirmed_negatives']=[k for k in expected.get('confirmed_negatives',[]) if k in projected and projected[k] is False]
        expected['unassessed_context']=[i['input_id'] for i in inputs if i['requirement_predicate']['kind'] in {'reported_context','ongoing_selected_drug'} and (i['input_id'] not in projected or projected[i['input_id']] in (None,'unknown','not_assessed','не исследовано','неизвестно'))]
        if numeric:"""
assert before in text
text=text.replace(before,after)
before="        numeric=c['expected']['result_type'] in {'exact','selected_source_example'}"
after="""        if 'RU-ESC' in [s['source_id'] for s in r['sources']] and r['identity']['mode']=='start' and (c['given'].get('coronary_disease') is True or c['given'].get('electrolyte_disturbance') is True):
            complex_reason.append('RU-ESC §4.4 physical p6: actual coronary disease requires pretreatment ECG, actual electrolyte disturbance requires correction; classified by the source intervention trigger for every such path, independently of question count')
        numeric=c['expected']['result_type'] in {'exact','selected_source_example'}"""
assert before in text
text=text.replace(before,after)
p.write_text(text,encoding='utf-8')
print('Graph projections retain only actually asked/reused confirmed negatives; audit fixtures selected for complete paths.')
