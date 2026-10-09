"""Exact audited prose locator and source-claim repairs; numbers remain unchanged."""
from pathlib import Path
import json,yaml,re
O=Path(__file__).resolve().parent.parent;A=O.parent/'acceptance_v2_audit/condition_completion'
assert not (O/'condition_locator_repairs.json').exists(),'One-use correction'
rows=json.loads((A/'locator_defects.json').read_text(encoding='utf-8'));rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};changes=[]
for row in rows:
    r=rules[row['rule_id']];parts=row['path'].split('/');parts=parts[2:] if parts[0]=='rules' else parts;parent=r
    for part in parts[:-1]:parent=(parent[int(part)] if part.isdigit() else next(x for x in parent if x.get('parameter_id')==part)) if isinstance(parent,list) else parent[part]
    key=int(parts[-1]) if isinstance(parent,list) else parts[-1];old=parent[key];assert old==row['incorrect_claim'],row['path']
    pp=row['correct_physical_pages'];pages=str(pp[0]) if len(pp)==1 else f'{pp[0]}–{pp[-1]}'
    if row['rule_id'].startswith('ser-') and 'adult_minimum' in row['path']:new='§4.4 с.5, дети и подростки: активные показания, кроме ОКР, не применяются до18'
    else:new=re.sub(r'(с\.)\d+(?:[–-]\d+)?',lambda m:m[1]+pages,old)
    assert new!=old,row['path'];parent[key]=new;changes.append(dict(path=row['path'],old=old,new=new,source_sha256=row['source_sha256']))
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))
r=rules['ser-adult-adjust'];old=r['logic']['conditions'][1]
assert 'использовать соответствующую start-карточку' in old
r['logic']['conditions'][1]='Начальный этап25мг не является обычным шагом+50: при выбранном повышении и выполненных источниковых условиях после не менее недели допустим опубликованный первый переход25→50мг/сут (RU-SER §4.2 с.2–3). Это отдельно от дальнейших шагов+50 и не безусловный будущий этап.'
r['logic']['actions'][1]='Для отдельного первого шага25→50 применять опубликованный режим/минимум недели по RU-SER §4.2 с.2–3. Для последующих подходящих доз вариант=current_dose+step только при выполнении интервала/предела; при превышении максимума не округлять до него как произвольной ступени. Врач выбирает дальнейшую тактику.'
changes.append(dict(path='rules/ser-adult-adjust.yaml/logic/conditions/1 and actions/1',old=old,new=r['logic']['conditions'][1],source_sha256='3694e05ab6037be4b8648d3e0e7f0169998d62c568880f23c96888f088b170ba',scope='Align prose with already source-derived first-step contract and expected; no new dose rule'))
r=rules['esc-hepatic-start'];old=r['logic']['conditions'][1]
assert old=='hepatic = нарушена'
r['logic']['conditions'][1]='Только подтверждённая лёгкая/умеренная печёночная недостаточность Child–Pugh A/B: отдельная опубликованная стартовая ветка. Child–Pugh C требует осторожного титрования/решения врача и не получает автоматически режим A/B. Неизвестную категорию не считать A/B (RU-ESC §4.2 физ.с.3).'
changes.append(dict(path='rules/esc-hepatic-start.yaml/logic/conditions/1',old=old,new=r['logic']['conditions'][1],source_sha256='a1717b48ddde3997d8d7d2d3ae226131a99bfd8566e8bdcef9473e5eafe9d6d6',scope='Align legacy prose with already correct typed A/B versus C contract'))
for rid in ['preg-gad-start','preg-gad-adjust','preg-renal-start']:
    con=C['rules'][rid]
    for gate in con['source_gates']:
        if gate['source_ref']!='RU-PREG':continue
        gate['other']=[s.replace('no splitting/opening capsules','research form policy: only confirmed registered whole units; no source-confirmed fractional capsule dose, no automatic splitting/opening/rounding') if isinstance(s,str) else s for s in gate.get('other',[])]
    con['form_evidence_policy']=dict(source_ref='RU-PREG',source_locator='§1–3 с.1–2; §4.2 с.3–6',source_claim='Registered capsule strengths and oral administration are confirmed. A categorical source prohibition on opening/splitting is not claimed.',model_policy='Only confirmed whole registered units are used to establish dose feasibility. Fractional/opened capsule dose is not source-confirmed and is not automatically produced or rounded.')
    rules[rid]['logic']['form_evidence_policy']=con['form_evidence_policy']
for rid,r in rules.items():(O/'rules'/(rid+'.yaml')).write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'condition_locator_repairs.json').write_text(json.dumps(dict(locator_changes=changes,preg_form_policy_cards=3,medical_numbers_changed=False,primary_audit_ref='research/acceptance_v2_audit/condition_completion/locator_defects.json'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Exact current source locators',len(changes),'PREG source/model-policy separation',3)
