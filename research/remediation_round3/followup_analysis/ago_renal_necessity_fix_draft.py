"""Source-specific necessity correction, after preserving the reviewed snapshot."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'caution_necessity_repairs.json').exists(),'One-use correction'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));D=json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'));changes=[]
extra={rid:['alcohol_use','mania','suicide_risk'] for rid in ['switch-esc-ago','switch-parox-ago-selected-example','switch-parox-ago','switch-ser-ago']}
for rid in ['switch-parox-ago-selected-example','switch-parox-ago','switch-ser-ago']:extra[rid].append('bleeding_risk')
extra['switch-ser-ago'].append('hyponatremia_risk')
for p in (O/'rules').glob('*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));rid=r['rule_id']
    selected=[i for i in r['inputs'] if i['input_id'] in extra.get(rid,[]) or i['input_id']=='renal_state' and 'RU-AGO' in i['source_refs']]
    if not selected:continue
    for i in selected:
        k=i['input_id'];old=deepcopy(i['requirement_predicate']);pred=dict(kind='reported_context')
        reason=('RU-AGO §4.2 с.2/§4.4 с.4 задаёт осторожность при умеренной/тяжёлой почечной недостаточности, без числовой поправки, запрета или требования обязательной предлечебной оценки.' if k=='renal_state' else 'Конкретный источниковый анамнез/фактор требует осторожности или наблюдения; первичный источник не задаёт обязательную предварительную оценку, числовую поправку или противопоказание по одному этому фактору. Это не относится к текущим срочным симптомам, лекарственным взаимодействиям, предлечебному печёночному/QT риску.')+' Для выбранной ограниченной дозы/источникового перехода не операнд; сообщённое состояние используется и считается, unknown/отсутствие остаётся not_assessed без клинического допуска.'
        i.update(requirement_predicate=pred,required_for_individual_result=False,input_role='reported_context',required_when='If explicitly supplied',show_when='If explicitly supplied',why_needed=reason,necessity_reason=reason,action_if_unknown='Source caution remains visible; not_assessed, no inferred negative and no clinical clearance')
        con=C['rules'][rid];con['required_inputs']=[x['input_id'] for x in r['inputs'] if x['requirement_predicate']['kind']=='always'];con['input_requirements'][k]=pred
        if k not in con['monitoring_context_fields']:con['monitoring_context_fields'].append(k)
        changed=[]
        for c in F['cases']:
            if c['rule_id']!=rid:continue
            e=c['expected']
            if k in e.get('missing_fields',[]):
                remain=[f for f in e['missing_fields'] if f!=k]
                if remain:e['missing_fields']=remain
                else:
                    others={f:v for f,v in c['given'].items() if f!=k}
                    normal='недостаточность не выявлена после оценки' if k=='renal_state' else False
                    base=next(b for b in F['cases'] if b['rule_id']==rid and b['external_context']==c['external_context'] and {f:v for f,v in b['given'].items() if f!=k}==others and b['expected']['result_type']!='insufficient_data' and b['given'].get(k)==normal)
                    c['expected']=e=deepcopy(base['expected']);e['missing_fields']=[]
                changed.append(c['case_id'])
            e['clinical_clearance']=False
            if c['given'].get(k) in (None,'unknown','not_assessed','неизвестно','не исследовано'):
                e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|{k})
                e['confirmed_negatives']=[f for f in e.get('confirmed_negatives',[]) if f!=k]
        change=dict(rule_id=rid,input_id=k,old=old,new=pred,reason=reason,source_refs=i['source_refs'],locator=i['source_locator'],changed_missing_cases=changed)
        changes.append(change);D['decisions'].append(deepcopy(change))
    p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for n,x in [('result_contracts.yaml',C),('full_scenarios.json',F),('necessity_decisions.json',D),('caution_necessity_repairs.json',changes)]:
    (O/n).write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110) if n.endswith('.yaml') else json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
print('Source-specific renal necessity corrections',len(changes),'no automatic individual source-clearance claim')
