"""Update research contracts only. Preserve both earlier review directories."""
from pathlib import Path
from copy import deepcopy
import json, csv
import yaml

R = Path(__file__).resolve().parents[1]
O = R / 'remediation_round2'
OLD = R / 'remediation'

def read(p):
    return yaml.safe_load(p.read_text(encoding='utf-8'))

def dump(p, x):
    p.write_text(yaml.safe_dump(x, allow_unicode=True, sort_keys=False, width=110), encoding='utf-8')

def jsave(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')

def csvsave(p, rows):
    with p.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

rules = {p.stem: read(p) for p in sorted((R / 'rules').glob('*.yaml'))}
sources = json.loads((R / 'sources.json').read_text(encoding='utf-8'))
schema = read(OLD / 'input_contracts.yaml')
contracts = read(OLD / 'result_contracts.yaml')
cases = json.loads((OLD / 'full_scenarios.json').read_text(encoding='utf-8'))
policy = read(O / 'necessity_policy.yaml')

sources['RU-PHEN']['dates']['registration'] = '2024-05-07'
sources['RU-PHEN']['registry_observation_round2'] = dict(
    url='https://lk.regmed.ru/Register/EAEU_SmPC', search='Феназепам', observed_on='2026-10-08',
    registration_number='ЛП-№(005387)-(РГ-RU)', registration_date='2024-05-07',
    formulation='таблетки, диспергируемые в полости рта, 0.25/0.5/1 мг', holder='Валента Фарм',
    proves='Registration identity for the exact orodispersible form',
    does_not_prove='Identity of the downloaded PDF with the latest approved registry text')
jsave(R / 'sources.json', sources)

ser_ids = ['ser-adult-adjust', 'ser-panic-start', 'ser-social-start', 'ser-taper-limit']
for rid in ser_ids:
    r = rules[rid]
    if not any(i['input_id'] == 'mania_symptoms' for i in r['inputs']):
        i = deepcopy(next(i for i in r['inputs'] if i['input_id'] == 'mania'))
        i.update(input_id='mania_symptoms', question_ru='Врач отметил текущую маниакальную фазу?',
                 why_needed='При переходе в маниакальную фазу инструкция требует прекратить сертралин.',
                 source_refs=['RU-SER'], source_locator='§4.4 с.4, маниакальная фаза: прекращение сертралина')
        r['inputs'].append(i)
    next(i for i in r['inputs'] if i['input_id']=='mania')['question_ru'] = 'Есть мания/гипомания в анамнезе?'

ledger = []
for rid, r in rules.items():
    con = contracts['rules'][rid]
    blocked = 'RU-ESC' in [s['source_id'] for s in r['sources']]
    for i in r['inputs']:
        k = i['input_id']
        if blocked:
            kind = 'blocked_source'
            reason = 'Current original must be read before necessity or applicability can be established.'
        elif rid in ser_ids and k in policy['ser_fields']:
            p = policy['ser_fields'][k]; kind = p['necessity']; reason = p['effect']
            i['source_locator'] = p['locator']
            if k == 'adherence': i['source_refs'] = ['RU-PANIC']
            if rid != 'ser-adult-adjust' and kind == 'increase': kind = 'reported_context'
            if rid == 'ser-taper-limit':
                kind = 'always' if k in policy['taper_scope']['ser_required'] else 'outside_cessation_scope'
                reason = 'Cessation/withdrawal or urgent-stop predicate; start clearance does not prevent stopping.'
        elif rid == 'preg-taper-limit':
            kind = 'always' if k in policy['taper_scope']['preg_required'] else 'outside_cessation_scope'
            reason = 'Withdrawal or immediate cessation; no individualized reduction amount inferred.'
        elif rid == 'parox-panic-kr' and k in {'response','tolerability','current_dose','time_at_dose'}:
            kind = 'future_adjustment'
            reason = 'RU-PAROX §4.2 с.16: start is 10 mg; these facts concern later response-dependent escalation, not the start dose.'
            i['source_locator']='§4.2 с.16, паническое расстройство: старт и последующее повышение'
        elif i.get('required_for_individual_result') is True:
            kind = 'always'; reason = i['why_needed']
        elif k == 'maoi_type':
            kind = 'maoi_record'; reason = 'Each relevant MAOI type, not one compound clearance answer.'
        elif k == 'maoi_stopped_at':
            kind = 'stopped_maoi_record'; reason = 'Timestamp of each stopped MAOI; no timestamp for an empty assessed history.'
        else:
            kind = 'existing_conditional'; reason = i['why_needed']
        pred = {'kind':kind}
        if kind == 'increase': pred['actions'] = ['increase', 'not_chosen']
        if kind == 'action_choice': pred['actions'] = ['not_chosen', 'unknown', 'not_assessed']
        if kind == 'existing_conditional': pred['original_condition'] = i['required_for_individual_result']
        i['requirement_predicate'] = pred
        i['required_for_individual_result'] = True if kind == 'always' else kind
        i['required_when'] = {
            'always':'для выбранного индивидуального результата: числовой операнд или явно проверяемое источниковое ограничение',
            'increase':'clinician_action in [increase, not_chosen]',
            'action_choice':'clinician_action in [not_chosen, unknown, not_assessed]',
            'reported_context':'если врач сообщил обстоятельство или выявлено релевантное взаимодействие; иначе not_assessed с предупреждением',
            'outside_cessation_scope':'не требуется для выбранного прекращения; известные факты сохранены, нормальность не выводится',
            'future_adjustment':'при отдельном последующем выборе повышения; не условие выдачи стартовой дозы',
            'blocked_source':'не оценивается до проверки текущего первоисточника',
            'maoi_record':'каждая текущая/отменённая запись ИМАО или неизвестный класс взаимодействия',
            'stopped_maoi_record':'каждая отменённая запись ИМАО отдельно',
            'existing_conditional':str(pred.get('original_condition'))}[kind]
        i['show_when'] = 'при выборе результата или использовании уже подтверждённого в этом расчёте факта' if kind=='always' else i['required_when']
        i['input_role'] = 'required_selected_result_operand_or_source_gate' if kind=='always' else kind
        i['action_if_unknown'] = ('insufficient_data; request this specific necessary fact; no individual dose' if kind in {'always','increase','action_choice','maoi_record','stopped_maoi_record'}
                                  else 'retain not_assessed/unknown; no inference of normality; show source-specific limitation; no clinical clearance')
        i['necessity_reason'] = reason
        if i.get('structure_ref'): i['structure_ref'] = i['structure_ref'].replace('remediation/', 'remediation_round2/')
        origin = 'product_metadata' if i['data_type']=='structured_form' else 'patient_fact'
        i['fact_origin'] = origin
        ledger.append(dict(rule_id=rid,input_id=k,question=i['question_ru'],data_type=i['data_type'],unit=i['unit'],
            source_refs=' | '.join(i['source_refs']),version=' | '.join(sources[s]['version_or_update_date'] for s in i['source_refs']),
            source_locator=i['source_locator'],necessity=kind,changed_action=reason,
            origin=origin,derivable_without_new_question='identified product/form/strength determines other form metadata and INN' if origin=='product_metadata' else 'only an explicitly confirmed fact in this calculation, with provenance; never a physician-action checkbox',
            review_depth='primary necessity reconsidered' if rid in ser_ids or rid=='preg-taper-limit' else 'source-linked current full branch; minimum not asserted',
            contract='result_contracts.yaml#rules/'+rid,expected='full_scenarios.json'))
    con['required_inputs'] = [i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='always']
    con['conditional_inputs'] = {i['input_id']:i['required_when'] for i in r['inputs'] if i['requirement_predicate']['kind']!='always'}
    con['input_requirements'] = {i['input_id']:i['requirement_predicate'] for i in r['inputs']}
    con['unassessed_context_policy'] = 'Explicit not_assessed + source warning; never a negative answer or full clinical clearance'
    if rid in ser_ids and rid!='ser-taper-limit':
        for b in con['branches']:
            b['when']=b['when'].replace('all source gates clear','required dose/applicability gates known; no reported unresolved caution').replace('all gates clear','required dose/applicability gates known; no reported unresolved caution').replace('no source cautions','no reported unresolved caution; unassessed monitoring context retained').replace('no caution','no reported unresolved caution; unassessed monitoring context retained')
            b['expected_output']['clinical_clearance']=False
    r['logic']['result_contract_ref'] = 'remediation_round2/result_contracts.yaml#rules/'+rid
    if rid in ser_ids:
        con['monitoring_context_fields'] = [i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='reported_context']
        if rid != 'ser-taper-limit':
            gate = next(g for g in con['source_gates'] if g['source_ref']=='RU-SER')
            gate['stop'] = list(dict.fromkeys(gate.get('stop',[])+['mania_symptoms']))
        con['urgent_stop_predicates'] = [dict(input='mania_symptoms',operator='equals',value=True,action='source_stop_action',stop_medication='RU-SER',source_ref='RU-SER',source_locator='§4.4 с.4')]
        if rid=='ser-taper-limit':
            con['urgent_stop_predicates'].append(dict(input='seizure_state',operator='equals',value='новые приступы',action='source_stop_action',stop_medication='RU-SER',source_ref='RU-SER',source_locator='§4.4 с.4'))
    if not blocked:
        r['output']['branches'] = deepcopy(con['branches'])
    r['sources'] = [sources[s['source_id']] for s in r['sources']]
    dump(R/'rules'/f'{rid}.yaml',r)

# Preserve previous complete scenarios. Reconsider only expected failures whose field no longer belongs to this result.
for c in cases['cases']:
    rid = c['rule_id']; con = contracts['rules'][rid]; g = c['given']; e = c['expected']
    if rid in ser_ids: g['mania_symptoms'] = False
    if e['result_type']=='insufficient_data':
        missing = e['missing_fields']
        inactive = [f for f in missing if con['input_requirements'].get(f.split('.')[0],{}).get('kind') in {'reported_context','outside_cessation_scope','future_adjustment'}]
        if inactive and len(inactive)==len(missing):
            b = con['branches'][0]; c['branch_id'] = b['branch_id']; c['expected'] = deepcopy(b['expected_output'])
            c['expectation_revision'] = 'This omission does not establish absence; not a required operand of this selected result.'
    c['expected']['clinical_clearance'] = False
    if rid in ser_ids:
        fields = con.get('monitoring_context_fields',[])
        c['expected']['unassessed_context'] = [k for k in fields if k not in g or g[k] in ('unknown','not_assessed',None)]
        c['expected']['monitoring_warning_source'] = 'RU-SER §4.4 с.4–6; full clinical review remains separate'

def add_case(rid, suffix, g, e, bid=None):
    r = rules[rid]
    template = next(c for c in cases['cases'] if c['rule_id']==rid and c['branch_id']==contracts['rules'][rid]['branches'][0]['branch_id'])
    c = deepcopy(template); c.update(case_id=rid+'--round2-'+suffix, given=deepcopy(g), expected=deepcopy(e), branch_id=bid)
    c['external_context']['treatment_phase'] = 'ongoing' if e['result_type']=='source_stop_action' else 'selected_mode'
    cases['cases'].append(c)

for rid in ser_ids:
    con = contracts['rules'][rid]
    base = deepcopy(next(c['given'] for c in cases['cases'] if c['rule_id']==rid and c['branch_id']==con['branches'][0]['branch_id']))
    for state in ['omitted','unknown','not_assessed']:
        g = deepcopy(base)
        if state=='omitted': g.pop('mania_symptoms')
        else: g['mania_symptoms']=state
        add_case(rid,'mania-symptoms-'+state,g,dict(result_type='insufficient_data',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=['mania_symptoms'],unconditional_future_stages=False,clinical_clearance=False))
    g=deepcopy(base); g['mania_symptoms']=True
    add_case(rid,'active-mania-stop',g,dict(result_type='source_stop_action',total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],unconditional_future_stages=False,stop_medication='RU-SER',automatic_next_stage=False,source_condition=con['urgent_stop_predicates'][0],clinical_clearance=False))
    if rid != 'ser-taper-limit':
        g=deepcopy(base)
        for i in rules[rid]['inputs']:
            if i['requirement_predicate']['kind']=='reported_context': g.pop(i['input_id'],None)
            if i['requirement_predicate']['kind']=='action_choice': g.pop(i['input_id'],None)
        e=deepcopy(con['branches'][0]['expected_output']); e.update(clinical_clearance=False,unassessed_context=con['monitoring_context_fields'],monitoring_warning_source='RU-SER §4.4 с.4–6')
        add_case(rid,'minimal-selected-action',g,e,con['branches'][0]['branch_id'])
    if rid=='ser-adult-adjust':
        g=deepcopy(base);g['clinician_action']='keep'
        for k in ['time_at_dose','akathisia','response','tolerability','adherence']+con['monitoring_context_fields']:g.pop(k,None)
        b=next(b for b in con['branches'] if b['branch_id']=='keep');e=deepcopy(b['expected_output']);e.update(clinical_clearance=False,unassessed_context=con['monitoring_context_fields'])
        add_case(rid,'keep-without-increase-fields',g,e,'keep')

schema['fact_provenance'] = dict(scope='only within this calculation; no patient history',
    confirmed_patient_fact='explicit answer or supplied current source-specific assessment; action selection is not evidence',
    derived_product_metadata='product/form/strength selection determines INN, release, registration and splitting from the identified edition',
    unknown='retain verbatim missing state; never fabricate a prior assessment')
schema['requirement_predicates'] = policy['definitions']
dump(O/'input_contracts.yaml',schema)
dump(O/'result_contracts.yaml',contracts)
jsave(O/'full_scenarios.json',cases)
csvsave(O/'input_necessity.csv',ledger)

# Refresh only the current input catalogue, retaining auxiliary non-dose inputs.
with (R/'input_catalog.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);oldrows=list(reader);cols=reader.fieldnames
cols=list(dict.fromkeys(cols+['requirement_predicate','necessity_reason','fact_origin']))
rows=[{k:row.get(k,'') for k in cols} for row in oldrows if row['rule_id'] not in rules]
for rid,r in rules.items():
    for i in r['inputs']:
        raw={'rule_id':rid,**i}
        rows.append({k:json.dumps(raw[k],ensure_ascii=False) if isinstance(raw.get(k),(dict,list)) else raw.get(k,'') for k in cols})
csvsave(R/'input_catalog.csv',rows)
oldcounts=json.loads((R/'question_counts.json').read_text(encoding='utf-8'))
for n in oldcounts:
    r=rules[n['rule_id']];n['clinical_input_entries']=len(r['inputs']);n['all_catalog_fields_count']=len(r['inputs'])+n['initial_selections']
    n['required_known_branch_fields']=len(contracts['rules'][r['rule_id']]['required_inputs'])+n.get('independent_renal_subfields_extra',0)+n.get('independent_A_B_allergy_extra',0)+n['initial_selections']
    n['actual_paths_ref']='remediation_round2/question_graphs.yaml; catalogue totals are not a minimal path proof'
jsave(R/'question_counts.json',oldcounts)
flows=read(R/'question_flows.yaml')
for f in flows['flows']:
    r=rules[f['rule_id']];known=set(f['clinical_questions'])
    f['conditional_questions']=[i['input_id'] for i in r['inputs'] if i['input_id'] not in known]
    f['individual_result_required_fields']=contracts['rules'][r['rule_id']]['required_inputs']
    f['individual_result_count_without_maoi_history']=next(n['required_known_branch_fields'] for n in oldcounts if n['rule_id']==r['rule_id'])
    f['actual_graph_ref']='remediation_round2/question_graphs.yaml#'+r['rule_id']
flows['actual_graph_ref']='remediation_round2/question_graphs.yaml'
flows['actual_path_assessment']='Counts in actual graphs distinguish selected actions and clinical reassessment. Criterion 18 remains open; a source-proven lower bound is documented separately.'
dump(R/'question_flows.yaml',flows)
print('Updated 38 contracts and input ledger; earlier review directories untouched.')
