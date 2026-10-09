"""Write executor evidence/limitations; independent acceptance has its own unedited files."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import json,re
O=Path(__file__).resolve().parent;R=O.parent
P=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
criteria=re.findall(r'^- \[ \] (.+)$',(R.parent/'psychopharm_codex_pack/ACCEPTANCE_V2.md').read_text(encoding='utf-8'),re.M)
proof={1:'PROJECT_BRIEF.md; physician-selected diagnosis; no diagnostic module',2:'ru_source_policy.yaml; active RU cards',3:'38 selected product cards and per-result contracts',4:'38 cards span start/adjust/taper/switch; coverage.csv and source gaps retained',5:'KR-based top3 findings excluded from individual efficacy ranking',6:'coverage.csv; population boundaries and honest missing pediatric/gestation schemes',7:'No genetics demand; known_cyp2c19 context/conditional source branch; no app/history/ML',8:'identity/applicability in every card; exact product edition binding',9:'current_registry_documents.json; nine exact current originals plus ESC/SER; version_inventory.json',10:'211 located parameter anchors and typed source conditions; primary reading journal; independent full transfer audit pending',11:'Source options/ranges/examples retained; selected source examples need clinician choice',12:'Separate dose/frequency/unit/form; Lyrica typo blocked; current XR vs IR unit distinction',13:'Joint modifiers return choice; no multiplication or averaging',14:'Directional matrix and source-specific pair gaps; A/B owners and target phase checked',15:'Current duloxetine §4.4 minimum2; no universal decrement; source examples and symptoms retained',16:'No new scale-to-mg coefficient; physician action/source decisions',17:'2126 per-result ledger rows and 193 explicit revisions; minimum not proved for all unchanged/result branches',18:'Complete counted ordinary paths still exceed15: AGO20, DULOX GAD17, PREG up to18; not relabelled',19:'Source-triggered complex paths and independent fact/stage/record costs; long paths visible',20:'Nested unknown, optional context with warnings and clinical_clearance=false; exact negatives distinct',21:'4953 prepared full expected; named missing inputs; source-specific gates',22:'Conditional future stages remain conditional; no automatic fabricated step',23:'Minimum intervals distinct from visit schedule; no calendar module',24:'Archived official originals and SHA; actual read scope separate from access/download',25:'Exact RU records, Russian KRs, foreign comparisons excluded',26:'Source types and unvalidated research/product status explicit',27:'No efficacy evidence converted into validation of algorithm',28:'No calculator or clinical validation claimed',29:'Source-bound transfer only; independent acceptance and implementation tests remain separate',30:'Existing renal/lithium/citalopram/pair/form gaps preserved; current source conflicts recorded'}
rows=[dict(number=n,criterion=c,status='частично' if n in {17,18} else 'выполнено',evidence=proof[n],assessment_scope='executor provisional; independent source audit can revise this status') for n,c in enumerate(criteria,1)]
(O/'acceptance_recheck.json').write_text(json.dumps(dict(criteria_version='ACCEPTANCE_V2',criteria_count=30,criteria=rows,status_counts={'выполнено':28,'частично':2},independent_acceptance_pending=True,application_implemented=False,clinical_validation='not_performed'),ensure_ascii=False,indent=2),encoding='utf-8')
dimensions=[('источники',Decimal('9.3'),Decimal('.25')),('правила',Decimal('8.8'),Decimal('.30')),('входы',Decimal('7.8'),Decimal('.20')),('покрытие',Decimal('8.8'),Decimal('.15')),('техника',Decimal('9.1'),Decimal('.10'))]
raw=sum(v*w for _,v,w in dimensions)
(O/'scoring.json').write_text(json.dumps(dict(nature='provisional executor expert assessment; arithmetic reproducible, not independent medical validation',dimensions=[dict(name=n,score=str(v),weight=str(w),contribution=str(v*w)) for n,v,w in dimensions],weighted_unrounded=str(raw),uncapped_rounded=str(raw.quantize(Decimal('.1'),rounding=ROUND_HALF_UP)),cap='6',cap_reason='Substantial unfinished ordinary question limit and unproved complete result-specific necessity; V2 paths11–15 are allowed and do not cause cap',score='6.0',old_uncapped='8.55',raw_delta=str(raw-Decimal('8.55')),independent_acceptance_pending=True),ensure_ascii=False,indent=2),encoding='utf-8')
text='''# Третий проход по ТЗ версии 2

Активные данные: основной research/sources.json и rules/ побайтово согласованы с копиями этого прохода. Контракты, полные expected, графы и фактические пути — remediation_round3/. Канонические критерии: ../../psychopharm_codex_pack/ACCEPTANCE_V2.md. Цель5–10; предел обычного пути15. Приложение не реализовано.

Получены все девять ранее открытых официальных ОХЛП и девять ЛВ; оригиналы сохранены со SHA. ESC/SER из round2 остаются подтверждёнными основаниями. Номер Лирики004450 согласован с новым индексом. Номер в имени файла не заменяет номер/дату штампа. ЛВ не объявлены полностью медицински сверенными.

Изменены193 решения о необходимости/структуре ввода: контекст наблюдения сохранён с предупреждениями; признаки прекращения при уже начатой терапии имеют точный триггер фазы. Метрика и единица почечного вопроса закреплены самим вопросом, метод — необязательная информация о происхождении; неправильная метрика/единица по-прежнему блокируются. Все независимые текущие/недавно отменённые препараты, их статусы, типы/даты ИМАО и фактические этапы плана считаются раздельно. Нет скрытой анкеты или универсального допуска.

Новые существенные условия: равные половины Феварина; запрет деления ородисперсного Феназепама; оценка риска неправильного применения прегабалина и отдельный триггер контрацепции; прекращение при аллергической реакции на XR; полный ответ при серотониновом синдроме на флувоксамине; минимальное снижение Дулоксенты не менее2 недель по §4.4 при отдельной формулировке1–2 в §4.2. Таблеточный и XR Велаксин не смешаны: почечные единицы различаются.

Внутренние проверки:38 карточек,4953 полных подготовленных expected,211 основных числовых якорей; структурные проверки,35 прежних отрицательных мутаций,8 новых проверок,19 непосредственно сопоставленных ключевых expected с оригиналами. Это отдельные виды проверки; совпадение таблиц не заменяет чтение источника. Граф использует подготовленный expected, медицинский калькулятор не исполняется.

Предварительная исполнительская приёмка28 выполнено/2 частично, оценка6,0 при неокруглённой сумме8,755. Статусы и оценки требуют независимой приёмки и могут быть пересмотрены. №17: необходимость всех неизменённых вопросов по каждому конкретному результату ещё не доказана. №18: несколько обычных путей действительно длиннее15. Результат не объявляется10/10.

Исходный снимок:761 файл;575 защищённых и17 старых исходных документов сохраняются. Действующий отпечаток — final_manifest.json. Исторические audit/remediation/round2 и прежние оценки не переписаны. Независимое заключение сохраняется отдельно в ../acceptance_v2_audit/.
'''
(O/'README.md').write_text(text,encoding='utf-8')
limitations='''# Материальные ограничения итогового кандидата

Лимит15 не закрыт. Прямой обычный старт AGO содержит20 независимых выборов/сведений; DULOX при ГТР17, PREG обычный старт17 либо18 при источниковом условии контрацепции. Врачебные оценки не спрятаны в предварительной анкете. Не доказано, что эти числа — глобально минимальная длина любой допустимой модели.

Сохранение четырёх предлечебных печёночных факторов AGO основано на §4.4 с.3. Точно ограниченное врачебное заключение о печёночном риске — возможная альтернативная модель, но само по себе не доказывает весь путь≤15; три независимых наследственных исключения, отдельные АЛТ/АСТ и популяционные ограничения сохраняются. Универсальная отметка «всё проверено» не допускается.

Полный минимум всех вопросов не установлен: ledger связывает каждый вход с конкретной веткой, но неизменённые поля/качественные результаты прекращения и пробелов нуждаются в отдельном доказательстве минимальности. Консервативная обязательность не превращается в доказанный минимум.

Медицинские пробелы: точные универсальные парные календари РФ не найдены; формула Лирики с ммоль/л блокирована; отдельный оценщик Рихтера использует мкмоль/л и не исправляет Лирику молча; единицы лития и конфликт циталопрама остаются вне исполнения. Текущая XR-ОХЛП содержит разные формулировки беременности в §4.3 и §4.6: обычная ветка следует противопоказанию, исключение не автоматизировано. Начальные37,5мг XR не обеспечиваются выбранными целыми капсулами75/150мг. Рексетин в строке реестра20/30мг, текущая ОХЛП подтверждает только20мг.

Проверены указанные терапевтические разделы и дозовые таблицы; непрочитанные части/полные ЛВ не объявлены прочитанными. Содержание190/40/55/51 текстовых дельт DULOX/FLUVOX/PAROX/RICHTER не объявлено исчерпывающе клинически классифицированным только по алгоритмическому diff. Источниковая актуальность подтверждается получением точного оригинала, а полнота медицинского переноса — отдельной проверкой.

Перенос допустим только как исследовательские source-bound контракты с явными пробелами, блокировками и клиническим решением. Полное соответствие исследовательскому ТЗ, короткий обычный интерфейс и готовность клинического применения пока не объявляются.
'''
(O/'limitations.md').write_text(limitations,encoding='utf-8')
summary=[]
for rid in sorted({p['rule_id'] for p in P}):
    ordinary=[p for p in P if p['rule_id']==rid and p['ordinary_individual_numeric_path']]
    if ordinary:summary.append(dict(rule_id=rid,ordinary_counts=sorted(set(p['count'] for p in ordinary)),maximum=max(p['count'] for p in ordinary),examples=[p['full_example'] for p in ordinary]))
(O/'ordinary_path_report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
counts=json.loads((R/'question_counts.json').read_text(encoding='utf-8'))
for x in counts:x['ordinary_complete_counts']=sorted(set(p['count'] for p in P if p['rule_id']==x['rule_id'] and p['ordinary_individual_numeric_path']))
(R/'question_counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Executor report written; independent acceptance pending. Honest V2 ordinary-limit and necessity restrictions retained.')
