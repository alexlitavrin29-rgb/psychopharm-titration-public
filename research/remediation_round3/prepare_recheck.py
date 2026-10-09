"""Record the revised candidate without overwriting the first independent review."""
from pathlib import Path
import csv, hashlib, json, shutil, yaml

O=Path(__file__).resolve().parent; R=O.parent
def read(name):
    p=O/name
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.suffix=='.yaml' else json.loads(p.read_text(encoding='utf-8'))
def save(name,data):
    p=O/name
    p.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=110) if p.suffix=='.yaml' else json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

for name in ['README.md','limitations.md','acceptance_recheck.json','scoring.json','ordinary_path_report.json']:
    old=O/('review1_executor_'+name)
    if not old.exists():
        shutil.copyfile(O/name,old)
C=read('result_contracts.yaml')
for con in C['rules'].values():
    for gate in con['source_gates']:
        if 'interaction_scope' in gate:
            gate['interaction_scope']=gate['interaction_scope'].replace('qualitative source-gap result','limited qualitative result')
save('result_contracts.yaml',C)
policy=read('necessity_policy.yaml')
policy['primary_file']=read('sources.json')['RU-SER']['local_file']
policy['taper_scope']['ser_required']=C['rules']['ser-taper-limit']['required_inputs']
policy['taper_scope']['revised_qualitative_scope']='Current dose/duration/prior withdrawal are reported context for non-numerical source limits; urgent facts and current symptoms remain required. See qualitative_necessity_repairs.json.'
save('necessity_policy.yaml',policy)
P=read('actual_question_paths.json')
ordinary=[]
for rid in sorted(C['rules']):
    pp=[p for p in P if p['rule_id']==rid and p['ordinary_individual_numeric_path']]
    if pp:
        ordinary.append(dict(rule_id=rid,ordinary_counts=sorted({p['count'] for p in pp}),maximum=max(p['count'] for p in pp),examples=[p['full_example'] for p in pp]))
save('ordinary_path_report.json',ordinary)
counts=json.loads((R/'question_counts.json').read_text(encoding='utf-8'))
for row in counts:
    row['ordinary_complete_counts']=sorted({p['count'] for p in P if p['rule_id']==row['rule_id'] and p['ordinary_individual_numeric_path']})
(R/'question_counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'input_necessity.csv').open(encoding='utf-8-sig',newline='') as f:
    ledger=list(csv.DictReader(f))
decisions=read('necessity_decisions.json')['decisions']
cases=read('full_scenarios.json')['cases']
response=[]
descriptions={
 'V2-01':('исправлено; повторная независимая проверка ожидается','Вложенные версии/SHA привязаны к владельцу source_id; IR не наследует XR.', ['source_binding_repairs.json']),
 'V2-02':('исправлено; повторная независимая проверка ожидается','Узкий скрининг БАР перед стартом PAR; unknown/missing не дают исполнения старта.', ['medical_condition_repairs.json']),
 'V2-03':('исправлено; повторная независимая проверка ожидается','PAR: прекращение текущего препарата и поддерживающее симптоматическое лечение; календарь B не начинается автоматически.', ['medical_condition_repairs.json']),
 'V2-04':('исправлено; повторная независимая проверка ожидается','SER: опубликованное избегание мощных ингибиторов CYP3A4; без нового коэффициента дозы.', ['medical_condition_repairs.json']),
 'V2-05':('исправлено; повторная независимая проверка ожидается','DULOX: CNS/CYP1A2/CYP2D6-субстраты/гепатотоксичность; для качественной отмены не добавлен допуск нового старта.', ['medical_condition_repairs.json']),
 'V2-06':('исправлено; повторная независимая проверка ожидается','Условия опубликованного прекращения при уже начатой FLUV/PAR/XR терапии перенесены и имеют prepared expected.', ['medical_condition_repairs.json']),
 'V2-07':('исправлено; повторная независимая проверка ожидается','ESC действия A/B раздельны; прекращение принимаемого ESC, ЭКГ/симптоматическое лечение; фаза B не выводится из A.', ['medical_condition_repairs.json','input_contracts.yaml']),
 'V2-08':('исправлено; повторная независимая проверка ожидается','Владелец/страница PAR, текущая идентичность PHEN ODT, ограниченный статус проверенной применимости согласованы.', ['source_binding_repairs.json','medical_condition_repairs.json']),
 'V2-09':('исправлено; повторная независимая проверка ожидается','XR: явный строгий предикат >100 мм рт.ст. только ongoing; граничные 100/100.01 и фазовые сценарии.', ['medical_condition_repairs.json']),
 'V2-10':('исправлено; повторная независимая проверка ожидается','Отрицательные факты и unassessed пересчитаны из именно заданных projected inputs для всех типов результата.', ['build_graphs.py','audit_repair_verification.json']),
 'V2-11':('исправлено; повторная независимая проверка ожидается','Активные Markdown/индексы согласованы; исторические тексты сохранены отдельными копиями.', ['previous_main_documents/','ordinary_path_report.json']),
 'V2-12':('частично','19 полей качественных результатов перестали быть обязательными. Полная необходимость всех оставшихся полей по каждому результату не доказана.', ['qualitative_necessity_repairs.json','input_necessity.csv','necessity_decisions.json']),
 'V2-13':('частично','CAD/electrolyte сложность ESC имеет источник и триггер; ordinary CYP14. AGO20/DULOX-GAD17/PREG17–18 сохраняются честно.', ['actual_question_paths.json','ordinary_path_report.json']),
 'V2-14':('исправлено; повторная независимая проверка ожидается','FLUV прекращение при первичных либо участившихся приступах, включая выбранную отмену.', ['medical_condition_repairs.json'])}
for fid,(state,detail,proof) in descriptions.items():
    response.append(dict(finding_id=fid,executor_status=state,response=detail,evidence=proof))
save('findings_response.json',response)
(O/'findings_response.md').write_text('# Ответ на первую независимую приёмку\n\nПервое заключение и его SHA сохранены; этот ответ не является независимым закрытием замечаний.\n\n'+'\n\n'.join(f"- **{x['finding_id']} — {x['executor_status']}.** {x['response']} Свидетельства: {', '.join(x['evidence'])}." for x in response),encoding='utf-8')
initial=json.loads((R/'acceptance_v2_audit/acceptance_recheck.json').read_text(encoding='utf-8'))
save('acceptance_recheck.json',dict(state='Revised candidate awaiting independent recheck; no new fulfilled claims',previous_independent_snapshot=read('final_manifest_review1.json')['snapshot_sha256'],previous_independent_acceptance=initial,executor_findings_response='findings_response.json',open_material_requirements=[17,18]))
save('scoring.json',dict(state='Revised candidate awaiting independent recheck; no new score assigned',previous_independent_scoring=json.loads((R/'acceptance_v2_audit/scoring.json').read_text(encoding='utf-8')),new_candidate_score=None,reason='Known fixes and PASS are not a complete medical audit or proof of input minimality.'))
(O/'README.md').write_text(f'''# Третий проход: исправленный кандидат на повторную приёмку

Канонические критерии: [ACCEPTANCE_V2](../../psychopharm_codex_pack/ACCEPTANCE_V2.md). Цель 5–10 вопросов, допустимый обычный путь до 15 включительно. Исследование; приложение и клиническая валидация не выполнялись.

Все девять ранее открытых официальных ОХЛП и девять ЛВ получены и сохранены со SHA. ESC/SER второго прохода остаются активными основаниями. Лирика РУ 004450 согласована между индексами. Дата/номер штампа отличаются от номера в имени файла. ЛВ не объявлены полностью медицински сверенными.

Активные sources.json и 38 карточек основного research согласованы с копиями этого прохода. Текущие контракты: {len(cases)} подготовленных полных ожиданий, {len(P)} полных выбранных обходов графа, {len(ledger)} строк связей вход–результат, {len(decisions)} решений о необходимости/структуре ввода. Это исследовательские синтетические сценарии и структурные проверки; медицинский калькулятор не исполняется, глобальная минимальность вопросов не доказана.

Первое независимое заключение сохранило 21 выполненный / 9 частичных критериев; балл 6,0 после содержательного ограничения, исходная сумма 7,35. Его снимок и файлы сохранены в final_manifest_review1.json и review1_snapshot/. Новые исправления перечислены в [ответе на замечания](findings_response.md). Статусы «исправлено» — оценка исполнителя, ожидающая независимой проверки нового снимка; новый балл пока не назначен.

Убраны 19 обязательных полей качественных источниковых результатов, не рассчитывающих индивидуальные ступени. Срочные действия сохранены с точной фазой и владельцем препарата, включая оба компонента перехода. Исправлены вложенные версии/SHA, недостающие классы взаимодействий, скрининг PAR, строгий порог XR, FLUV increased seizures, дополнительные действия ESC/PAR и ошибки negatives/unassessed в проекциях.

№17 и №18 остаются открытыми: полный минимум входов не доказан; обычные AGO20, DULOX-GAD17 и PREG17–18 превышают 15. ESC с реальной ИБС/электролитным вмешательством — источниковая сложная ветка независимо от длины; обычный известный CYP14. Нет скрытой предварительной анкеты или универсального клинического допуска.

Проверки разделены: verify_contracts/verify_graphs — структура и prepared expectations; primary_expected_checks/primary_current_expected_checks — 19+15 ключевых сопоставлений с оригиналами; verify_audit_repairs — 11 дополнительных фраз/страниц первоисточника и 8 отрицательных мутаций. Прежние 35 и отдельные 8 отрицательных проверок также выполнены. Ни один PASS не удостоверяет исчерпывающий медицинский перенос.

Действующий отпечаток данных — final_manifest.json. Независимая повторная приёмка сохраняется отдельно в ../acceptance_v2_audit/recheck1/. Исторические audit/remediation/round2 и первое заключение не переписываются. 575 защищённых файлов и 17 старых исходных документов проверяются по исходному снимку. Ограничения: [limitations.md](limitations.md).
''',encoding='utf-8')
p=O/'limitations.md';t=p.read_text(encoding='utf-8')
t=t.replace('но неизменённые поля/качественные результаты прекращения и пробелов нуждаются в отдельном доказательстве минимальности.','19 полей качественных результатов исправлены, но необходимость всех оставшихся полей каждого результата требует отдельного доказательства.')
t+='\nПервая независимая приёмка охватила все карточки и числовые вхождения, но не объявила исчерпывающую независимую сверку каждого уникального медицинского условия. Исправления и целевые проверки не расширяют этот охват автоматически. Повторная приёмка должна перечислить фактическое чтение и оставшиеся непроверенные условия.\n'
p.write_text(t,encoding='utf-8')
for name in ['00_summary.md','07_acceptance.md']:
    p=R/name;t=p.read_text(encoding='utf-8')
    t=t.replace('Уже выявленные независимым проверяющим пропуски исправляются с повторной проверкой нового снимка.','Ответ на выявленные пропуски и исправления: [findings_response](remediation_round3/findings_response.md). Первое независимое заключение сохранено; повторная проверка нового снимка сохраняется отдельно в acceptance_v2_audit/recheck1/.')
    t=t.replace('Его находки могут изменить статусы и ограничение балла; найденные исправления требуют повторной проверки.','Первое заключение: 21 выполнено / 9 частично, балл 6,0 при исходной сумме 7,35. Исправленный кандидат требует повторной независимой проверки; её результаты сохраняются отдельно в acceptance_v2_audit/recheck1/.')
    p.write_text(t,encoding='utf-8')
print('Recheck candidate recorded:',len(cases),'prepared cases,',len(P),'paths;',len(ledger),'ledger rows. No new score claimed.')
