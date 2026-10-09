"""Do not require numerical-plan operands for a qualitative source-only result."""
from pathlib import Path
from copy import deepcopy
import json,yaml

O=Path(__file__).resolve().parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8')) if p.suffix=='.json' else yaml.safe_load(p.read_text(encoding='utf-8'))
def save(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2) if p.suffix=='.json' else yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
C,F,D=[read(O/n) for n in ['result_contracts.yaml','full_scenarios.json','necessity_decisions.json']]
ids=['ago-stop','dulox-taper-limit','fluvox-taper-limit','venla-xr-taper-limit','phen-taper-limit','ser-taper-limit','esc-taper-limit','preg-taper-limit']
changed={}
for rid in ids:
    p=O/'rules'/(rid+'.yaml');r=read(p);con=C['rules'][rid]
    assert all(b['expected_output']['total_daily_dose_mg'] is None and b['expected_output']['schedule']==[] for b in con['branches'])
    fields={'current_dose','duration','duration_of_use','past_withdrawal','prior_withdrawal'}
    changed[rid]=[]
    for i in r['inputs']:
        if i['input_id'] not in fields or i['requirement_predicate']['kind']=='reported_context':
            continue
        old=deepcopy(i['requirement_predicate']);new=dict(kind='reported_context')
        reason='Результат содержит только опубликованное ограничение/выбор врача, без расчёта индивидуальных ступеней, возобновляемой дозы или числового темпа. Текущая доза/длительность/прошлая отмена не операнды такого результата; известный контекст сохраняется, неизвестный явно not_assessed. Для последующего индивидуального плана эти сведения потребуются в отдельном контракте. Опубликованные условия срочного прекращения и текущие симптомы остаются обязательными.'
        i.update(requirement_predicate=new,required_for_individual_result=False,input_role='reported_context',required_when=reason,show_when='Если врач сообщает контекст; не обязательный этап выдачи ограниченного источникового результата',why_needed=reason,necessity_reason=reason,action_if_unknown='Show explicit not_assessed context warning; do not invent a numerical plan or grant clinical clearance')
        changed[rid].append(i['input_id'])
        # The last source-reviewed decision governs the current snapshot.
        D['decisions']=[x for x in D['decisions'] if not (x.get('rule_id')==rid and x.get('input_id')==i['input_id'] and 'new' in x)]
        D['decisions'].append(dict(rule_id=rid,input_id=i['input_id'],old=old,new=new,reason=reason,source_refs=i['source_refs'],locator=i['source_locator'],result_scope='Qualitative source-only action/limit; no patient-specific dose stages'))
    con['required_inputs']=[i['input_id'] for i in r['inputs'] if i['required_for_individual_result']]
    con['input_requirements']={i['input_id']:i['requirement_predicate'] for i in r['inputs']}
    con['monitoring_context_fields']=[i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind']=='reported_context']
    for b in con['branches']:
        b['when']=b['when'].replace('current dose known','identified current drug; physician chose stop').replace('known current dose/form/duration','identified applicable form; source limit only, no numerical patient plan')
        b['expected_output']['clinical_clearance']=False
    r['output']['branches']=deepcopy(con['branches']);save(p,r)
for c in F['cases']:
    rid=c['rule_id']
    if rid not in changed:
        continue
    e=c['expected'];old_missing=e.get('missing_fields',[])
    if e['result_type']=='insufficient_data':
        remain=[k for k in old_missing if k.split('.')[0] not in changed[rid]]
        if old_missing and not remain:
            branch=C['rules'][rid]['branches'][0]
            # Reuse only the unchanged published qualitative result, never a numerical dose.
            c['expected']=e=deepcopy(branch['expected_output'])
        else:
            e['missing_fields']=remain
    e['clinical_clearance']=False
    if c['branch_id']:
        branch=next(b for b in C['rules'][rid]['branches'] if b['branch_id']==c['branch_id'])
        e['clinical_clearance']=branch['expected_output']['clinical_clearance']
    e['unassessed_context']=sorted({k for k in C['rules'][rid].get('monitoring_context_fields',[]) if k not in c['given'] or c['given'][k] in (None,'unknown','not_assessed','неизвестно','не исследовано')})
    e['confirmed_negatives']=[k for k,v in c['given'].items() if v is False]
save(O/'result_contracts.yaml',C);save(O/'full_scenarios.json',F);save(O/'necessity_decisions.json',D)
save(O/'qualitative_necessity_repairs.json',dict(scope='Specific non-numerical results only; does not certify every remaining input minimal or satisfy the ordinary numerical limit',changes=changed))
print('Qualitative-result inputs corrected:',sum(map(len,changed.values())), '; urgent facts/current symptoms preserved; ordinary numerical starts unchanged.')
