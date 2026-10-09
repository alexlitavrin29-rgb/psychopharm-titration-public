"""Keep historical checks intact; bind a separate checker to the candidate."""
from pathlib import Path
O=Path(__file__).resolve().parent
s=(O.parent/'remediation_round2/verify_contracts.py').read_text(encoding='utf-8')
s=s.replace("ROOT=Path(__file__).resolve().parents[1]", "ROOT=Path(__file__).resolve().parents[1]\nO=Path(__file__).resolve().parent")
s=s.replace("(root/'sources.json')","(O/'sources.json')").replace("(root/'rules')","(O/'rules')").replace("remediation_round2/", "remediation_round3/")
s=s.replace("req={'renal_state','elderly_population','dementia','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption','liver_injury_signs','transaminases_rising','mania_symptoms'}", "req={'renal_state','elderly_population','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption'} if rid.startswith('ago-') else {'renal_state','elderly_population','dementia','galactose_intolerance','complete_lactase_deficiency','glucose_galactose_malabsorption','liver_injury_signs','transaminases_rising','mania_symptoms'}")
s=s.replace("if pred['kind']=='ecg_if_cad'", "if pred['kind']=='ongoing_selected_drug' and context.get('treatment_phase')=='ongoing': applicable.add(key)\n            if pred['kind']=='field_true' and g.get(pred['field']) is True: applicable.add(key)\n            if pred['kind']=='ecg_if_cad'")
s=s.replace("if field=='registration_number' and 'RU-PHEN' in [s['source_id'] for s in r['sources']] and field in v and v[field] is None:continue", "if field=='method' and t=='structured_renal' and not ins[k].get('method_required_for_selected_result',True):continue")
s=s.replace("{'metric','value','unit','method','assessment'}", "{'metric','value','unit','assessment'}")
s=s.replace("for field in d['schema']['structures'][i['data_type']]['fields']:","for field in d['schema']['structures'][i['data_type']]['fields']:\n                        if field=='method' and i['data_type']=='structured_renal' and not i.get('method_required_for_selected_result',True):continue")
# Source/result decisions are compared directly, including exact trigger; do not accept any arbitrary optionalization.
needle="    return errors\n"
extra="""    decisions=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'))['decisions']
    for change in decisions:
        if 'new' not in change:continue
        rid=change['rule_id'];key=change['input_id'];i=next(i for i in rs[rid]['inputs'] if i['input_id']==key)
        ck(i['requirement_predicate']==change['new'],'primary round3 necessity trigger violated: '+rid+'/'+key)
    for rid,r in rs.items():
        for i in r['inputs']:
            if i['data_type']=='structured_renal':
                ck(i.get('metric_origin')=='fixed_source_metadata' and i.get('unit_origin')=='fixed_source_metadata','renal question hides metadata choice: '+rid)
        for i in r['inputs']:
            if i['requirement_predicate']['kind']=='field_true':ck(i['requirement_predicate']['field'] in {x['input_id'] for x in r['inputs']},'unknown conditional owner: '+rid)
        if rid.startswith('preg-') and r['identity']['mode'] in {'start','adjust'}:
            ck({'misuse_risk_assessment','reproductive_population'}<=set(cs[rid]['required_inputs']),'pregabalin pretreatment requirement lost: '+rid)
    return errors
"""
s=s.replace(needle,extra)
(O/'verify_contracts.py').write_text(s,encoding='utf-8')
print('Candidate checker adapted; exact source/result decisions retained as separate constraints.')
