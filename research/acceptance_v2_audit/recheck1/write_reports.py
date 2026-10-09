"""Independent recheck record. Writes only to this revision's audit directory."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from decimal import Decimal
from datetime import datetime, timezone
import json, yaml, hashlib, re

W=Path(__file__).resolve().parents[3]
O=Path(__file__).resolve().parent
R=W/'research/remediation_round3'
OLD=O.parent
def load(p): return json.loads(p.read_text('utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (O/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),'utf-8')
def md(name,s): (O/name).write_text(s,'utf-8')
M=load(R/'final_manifest.json'); INITIAL=load(O/'initial_manifest.json')
assert M['snapshot_sha256']==INITIAL['snapshot']
assert all(sha(W/x['path'])==x['sha256'] for x in M['files'])
S=load(R/'sources.json')
rules={p.stem:yaml.safe_load(p.read_text('utf-8')) for p in sorted((R/'rules').glob('*.yaml'))}
contracts=yaml.safe_load((R/'result_contracts.yaml').read_text('utf-8'))['rules']
cases=load(R/'full_scenarios.json')['cases']
paths=load(O/'independent_paths.json')
checks=load(O/'independent_checks.json'); extra=load(O/'additional_checks.json')

# Closure concerns the originally stated defect, not the whole drug/module.
closed={1,2,3,4,5,6,7,9,14}
closure_notes={
1:'Все 11076 вложенных source_basis имеют версию и SHA собственного source_id; IR больше не получает XR-версию. Первичное различие IR/XR форм и почечных правил сохранено.',
2:'PAROX bipolar_risk_screening: узкая предлечебная оценка по физ.7–8, не общий clinical clearance. Положительный/negative/unknown контракт присутствует.',
3:'PAROX SS/ЗНС: прекращение принимаемого PAROX и поддерживающая симптоматическая помощь по физ.7; четыре исходно затронутых режима имеют полные ожидания.',
4:'Исходные ser-* и switch-ser-ago получили strong_CYP3A4 avoidance по физ.10. Новые непроверенные ранее два SSRI-перехода выделены в R1-03.',
5:'Исходные четыре недостающих класса DULOX добавлены с различением inhibitor/substrate. Дополнительный известный duplicate product — отдельная R1-04.',
6:'FLUV/PAROX/XR taper получили исходно перечисленные срочные действия; FLUV печёночное событие в taper сформулировано как повышение ферментов с клиническими признаками. Новые условные события — R1-01.',
7:'ESC A/B фазы, прекращение принимаемого актора, ECG и симптоматическое лечение в переходах восстановлены; B не объявляется принимаемым из фазы A.',
8:'Часть typed predicates/stage/readiness исправлена; input/question/necessity/ledger остаются со старыми PAROX страницами, имеются старые ссылки в вопросах DULOX. См. locator_residuals.json.',
9:'Явное greater_than100, физ.9, для четырёх XR режимов;100.01 stop/100 не stop; источник не заменён >=100.',
10:'97 отсутствующих negatives и76 пересечений устранены: в391 проекции таких ошибок нет. Осталась одна потерянная положительная причина medicines в SER taper; см. additional_checks.json.',
11:'02/04/08 согласованы в прочитанной части;01_scope_and_sources.md строки33,44,52,60–65 сохраняют текущий ESC unavailable/F01 и противоречат последней строке о полученном оригинале.',
12:'19 демоций проверены как ограниченные ненумерические результаты. PREG taper три always-поля ещё не обоснованы для source_limit; необходимость всех полей всех результатов не доказана.',
13:'Независимый пересчёт391: обычные AGO20/DULOX-GAD17/PREG17–18 остаются. ESC CAD/electrolyte — реальная источниковая сложная ветка по физ.6 независимо от длины; CYP обычный14/сложный16.',
14:'FLUV new_or_increased_seizures explicitly ongoing и положительный stop; текст физ.5 требует прекращения при возникновении приступов или учащении. Не создаётся universal XR seizure stop.'}
F=deepcopy(load(OLD/'findings.json'))
for f in F:
 n=int(f['id'].split('-')[1]); f['status']='closed_in_original_scope' if n in closed else 'partially_corrected_open'
 f['recheck_evidence']=closure_notes[n]; f['snapshot']=M['snapshot_sha256']

def finding(fid,title,sid,locator,files,fact,fix,criteria,severity='major'):
 source=S.get(sid,{})
 F.append(dict(id=fid,status='open',title=title,severity=severity,source_ref=sid,primary_locator=locator,
   primary_file=str(Path('research')/source['local_file']) if source.get('local_file') else 'psychopharm_codex_pack/ACCEPTANCE_V2.md',
   primary_version=source.get('version_or_update_date','ТЗ V2 08.10.2026'),primary_sha256=source.get('document_fingerprint',{}).get('sha256'),
   files=files,executor_claim='Исправленный frozen кандидат; PASS не объявлен исчерпывающей медицинской проверкой',
   established_fact=fact,impact='Полнота источникового контракта/приёмки не подтверждена; произвольный дозовый коэффициент или числовой экстренный план не требуется.',
   required_fix=fix,reacceptance_condition='Новый SHA; точные source owner/фаза/локатор, известный положительный факт, отсутствие/unknown без ложного отрицания, полные expected и потреблённые факты/count в графе. Не менять этот проверенный снимок задним числом.',criteria=criteria,snapshot=M['snapshot_sha256']))
finding('R1-01','Не представлены четыре известные текущие source-defined события','RU-SER','SER §4.4 физ.6; PREG §4.4 физ.8; DULOX §4.4 физ.4; XR §4.4 физ.8',
 ['result_contracts.yaml: соответствующие ongoing/adjust/taper/SSRI switches','full_scenarios.json','question_graphs.yaml'],
 'SER symptomatic hyponatremia: рассмотреть прекращение + соответствующая медицинская помощь. PREG новые суицидальные мысли/поведение: медицинская помощь, наблюдение и рассмотреть прекращение. DULOX стойкое повышение АД на терапии: рассмотреть коррекцию дозы либо постепенную отмену. XR подозрение SS: рассмотреть снижение/прекращение по тяжести. Generic risk и prestart uncontrolled hypertension этих событий не устанавливают; отдельного typed positive/source action/expected нет.',
 'Добавить обработку именно сообщённого current event без обязательного универсального negative вопроса. Для known positive и явно ongoing актора — точное consider/action, clinical_clearance=false и отсутствие automatic schedule. SER: A switch-ser-esc/ago; B switch-esc-ser только target_ongoing. У остальных активных switch-карт этих INN нет. При unknown B phase запросить фазу, не выдумывать stop. Не переносить universal SER SS stop из других SSRI.',[10,14,15,17,30])
finding('R1-02','XR: остаток взаимодействий и силы avoidance','RU-VENLA-XR','§4.4 физ.10; §4.5 физ.15–17',
 ['result_contracts.yaml#venla-xr-*/source_gates','full_scenarios.json:venla-xr-gad-start--medicine-RU-VENLA-XR-QT_prolonging'],
 'XR cautions CYP2D6 inhibitors/CYP3A4 inhibitors (16), CNS-active drugs (15), metoprolol (17) отсутствуют как source-mapped условия. Weight-loss drugs включая phentermine (10) и serotonin precursors (15) не рекомендуется. QT-prolonging сочетания следует избегать (15–16), но текущий класс назван generic caution; имеющийся clinician_choice уже блокирует числовую ветку и не является contra→allow.',
 'Перенести точные classes/actions при known current комбинации, без PK процентов как dose factors. Назвать QT avoid_standard_combination, не формальную противопоказанность. Для qualitative taper не навязывать prestart medicines, но сохранить/посчитать реально потреблённый known факт.',[10,17,30])
finding('R1-03','SER взаимодействия не перенесены в оба SSRI-перехода','RU-SER','§4.3 физ.3; §4.5 физ.7–10 (strong CYP3A4 физ.10)',
 ['result_contracts.yaml#switch-ser-esc/source_gates','result_contracts.yaml#switch-esc-ser/source_gates'],
 'В обоих source_gates имеется только RU-ESC. Strong CYP3A4 avoidance SER не обрабатывается для A=SER либо B=SER. В этих карточках нет ни одного full medicines positive record. Обычный результат — gap/clinician_choice, поэтому это не доказанная разрешённая числовая опасная комбинация; полнота обоих источников не установлена.',
 'Добавить собственные SER основания/known examples, сохранив A/B фазы и отсутствие парного российского календаря. Противопоказания B до старта не заменять общим target_applicability.',[10,14,17,30])
finding('R1-04','DULOX: дополнительный продукт с тем же МНН','RU-DULOX','§4.4 физ.7, Лекарственные препараты, содержащие дулоксетин',
 ['result_contracts.yaml#dulox-*/source_gates','full_scenarios.json'],
 'Источник требует избегать совместного применения нескольких продуктов с дулоксетином. Нет отдельного известного duplicate_duloxetine_product условия/действия. Один current INN дулоксетина при ongoing сам по себе не доказывает дополнительный продукт.',
 'Определить именно дополнительный идентифицированный продукт, explicit avoid action/clinician_choice без коэффициента; его отдельный факт/происхождение и count при потреблении. Не объявлять single selected current product дубликатом.',[10,17,30])
finding('R1-05','PREG SCAR: неполное условное действие','RU-PREG','§4.4 физ.6, Тяжёлые кожные нежелательные реакции',
 ['full_scenarios.json:preg-...--stop-RU-PREG-severe_skin_reaction','result_contracts.yaml#preg-*'],
 'Scalar stop_medication сохраняет прекращение PREG; полные ожидания не сохраняют источниковое «рассмотреть альтернативное лечение при необходимости» и явную immediate cessation semantics. Это не запрос выбрать/дозировать альтернативный препарат.',
 'Сохранить immediate discontinue PREG + conditional consider alternative treatment if needed с source6, ongoing phase; не выдумывать альтернативу или её дозу.',[10,15,30])
finding('R1-06','PREG/PHEN: неустановленное возобновление прежней дозы','RU-PREG','PREG §4.2 физ.4; §4.4 физ.9; PHEN §4.2 физ.3 и §4.4 физ.4',
 ['result_contracts.yaml#preg-taper-limit/withdrawal','result_contracts.yaml#phen-taper-limit/withdrawal','full_scenarios.json: соответствующие branch-withdrawal'],
 "Ожидания содержат prior_dose_resumption='clinician consideration where source permits'. Самостоятельное чтение этих источников не установило PREG/PHEN разрешение на такое возобновление; AD-оговорка не распространяется на них. Никакая числовая прежняя доза автоматически не выдаётся, но source gap не назван явно.",
 'Явно отметить source_specific_resumption_not_established/индивидуальное решение врача без published option. Не удалять постепенность PREG ≥1 недели или симптомы/срочные события.',[10,15,30],'moderate')
finding('R1-07','Пересекающаяся семантика двух XR pregnancy вопросов','RU-VENLA-XR','§4.3 физ.5; канонический №17–18',
 ['rules/venla-xr-*.yaml#inputs/pregnancy,pregnancy_suspected','input_necessity.csv','actual_question_paths.json'],
 'Pregnancy asks «установлена или возможна?»; pregnancy_suspected отдельно always. При этой OR-семантике false первого уже отвергает подозрение, поэтому объявленная независимость/двойной счёт не обоснованы. Источник отдельно запрещает установленную и предполагаемую беременность.',
 'Развести точные семантические вопросы/домен либо доказать единую source-defined переменную без скрытого независимого подпункта. Сохранить оба source противопоказанных исхода, не снижать count правкой цифры.',[17,18],'moderate')
save('findings.json',F)
md('findings.md','# Независимые находки повторной приёмки\n\nСнимок `'+M['snapshot_sha256']+'`,164 файла. Закрытие старого замечания ограничено его исходным предметом.\n\n'+ '\n\n'.join('## '+f['id']+' — '+f['title']+'\n\nСтатус: **'+f['status']+'**.\n\n'+f.get('recheck_evidence',f['established_fact'])+'\n\nПервичный источник: '+f['source_ref']+', '+f['primary_locator']+'.\n\nУсловие исправления: '+f['required_fix'] for f in F))

residual=[]
for rid,r in rules.items():
 for i in r['inputs']:
  if 'RU-PAROX' in i['source_refs']:
   stale={k:v for k,v in i.items() if isinstance(v,str) and re.search(r'с\.?\s*(16|17|18|19|20|21|22|23|24)',v)}
   if rid=='parox-panic-kr' and i['input_id']=='seizure_state':stale['source_locator']=i['source_locator']
   if stale: residual.append(dict(rule_id=rid,input_id=i['input_id'],fields=stale,primary_file=S['RU-PAROX']['local_file'],primary_sha256=S['RU-PAROX']['document_fingerprint']['sha256'],actual_pages='§4.2 physical3–4; §4.3 physical4–5; §4.4 physical6–11; §4.5 physical11–14; seizures stop9, epilepsy caution8'))
  if 'RU-DULOX' in i['source_refs'] and i['input_id'] in {'mania','seizure_state','diabetes','suicide_risk','bleeding_risk','hyponatremia_risk'}:
   residual.append(dict(rule_id=rid,input_id=i['input_id'],fields={'question_ru':i['question_ru'],'source_locator':i['source_locator']},issue='Question retains old pages while primary locator changed. Diabetes also needs clinical text/label specificity rather than an invented coefficient.'))
save('locator_residuals.json',residual)

verification=deepcopy(load(OLD/'source_verification.json'))
for v in verification['sources']:
 p=Path(v['path']); assert p.exists() and sha(p)==v['sha256']
 v['previous_actual_reading_reused_for_identical_bytes']=True
 if v['source_id']=='RU-VENLA-XR':v['text_physical_pages_actually_read']=sorted(set(v['text_physical_pages_actually_read']+[16]))
 if v['source_id']=='RU-GAD':v['text_physical_pages_actually_read']=sorted(set(v['text_physical_pages_actually_read']+[25]))
 v['recheck_extra_reading']='Дополнительное прямое чтение применимых §4.4–4.5 событий/взаимодействий и сопоставление с новыми inputs/branches/expected. Точная детализация — condition_inventory.json/findings.'
 v['unread_or_unverified']='Полные ЛВ, неиспользуемые разделы4.8/5, неактивные IR/Richter предупреждения; все индивидуальные INN→class mappings и исчерпывающие result-specific necessity контрпримеры не подтверждены. Не заявляется полная медицинская рецензия документа.'
verification['snapshot']=M['snapshot_sha256']
verification['source_original_hash_changes']=[]
save('source_verification.json',verification)
md('source_verification.md','# Первичные источники и реальный объём чтения\n\nИспользовано собственное чтение того же агента из предыдущей приёмки только после совпадения SHA каждой исходной копии. Дополнительно прочитана XR физ.16, GAD физ.25 и повторно существенные current-event/interaction страницы. Никакой актуальности из одного SHA не выводится; ручное получение человеком и provenance текущей реестровой записи отделены от содержания/регистрации/штампа. CAPTCHA-download проверяющий самостоятельно не наблюдал.\n\n'+ '\n\n'.join('### '+v['source_id']+'\n\nФайл: `'+v['path']+'`; SHA `'+v['sha256']+'`.\n\nРедакция: '+v.get('version',S.get(v['source_id'],{}).get('version_or_update_date','see source record'))+'.\n\nТекст физ.страниц: '+str(v.get('text_physical_pages_actually_read',[]))+'; визуально: '+str(v.get('visual_physical_pages_actually_checked',[]))+'. '+v['unread_or_unverified'] for v in verification['sources']))

families={
'RU-AGO':('§4.2 физ.1–2; §4.3–4.4 физ.3–5; §4.5–4.6 физ.5–6','25/50, bedtime once, higherBDR2/GAD4; strict ageGAD>65/BDR>=75; ALT/AST>3; (1,3]caution; hepatic cirrhosis/active/insufficiency; repeat48/monitor3,6,12,24; elderly dementia; 3 lactose exclusions; strong/moderateCYP1A2/hepatotoxic; historymania vs currentstop; injury/rising; renalcaution; pregnancy/lactation/suicide/ECT/alcohol; no mandatory taper; day1 SSRI/SNRI gradual taper B start'),
'RU-DULOX':('§4.2 физ.2–3; §4.3 физ.3–4; §4.4 физ.4–7; §4.5–4.6 физ.7–10','BDR60; GAD30/comorbidBDR60; elderly30 for2weeks before60; conditional60/90/120; CLcr30–80unchanged/<30contra; hepatic disease with insufficiency; uncontrolledHTN/closed-angle uncompensatedglaucoma; 3 sucrose exclusions; mania/seizure/akathisia/bleeding/hyponatremia/diabetes; strongCYP1A2/MAOI14after5before/noMOC-linezolid combo; 4 repairedclasses; pregnancy/lactation; taper§4.2 1–2 vs§4.4>=2 noceiling; BPevent and duplicate gap'),
'RU-PAROX':('§4.2 физ.3–4; §4.3 физ.4–5; §4.4 физ.6–11; §4.5–4.6 физ.11–15','panic10 weekly10/recommended40 andseveralweeks/max60; elderly40 max without agecutoff; renal<30/hepatic lower therapeutic unspecified;20halves10; trial taper10/week until20 hold1; bipolar screening7; SS/ЗНСstop+support7; epilepsy caution8/newseizurestop9; withdrawal slow/resume option10; akathisia/diabetes/glaucoma/bleeding/QT/ECT; MAOIirreversible14/reversible>=24h andbeforeMAOI7; pimozide/thioridazine; serotonergic/bleeding/CYP2D6 substrates; pregnancy/lactation. Inputs retain wrong physical references.'),
'RU-FLUVOX':('§3 физ.1; §4.2–4.3 физ.2–3; §4.4–4.6 физ.4–11','50or100 nightly options; review3–4wk; max300;>150 into2or3; equalhalves; renal/hepatic low unspecified; MAOI14/nextcalendar day/7before; allergy/lactation andnamedcontra; new ORincreasedseizures stop5; SSstop+symptom5; liverenzymeswithclinicalsigns stop5; mania stop7; history/diabetes/glaucoma/ECT/bleeding/pregnancy; CYPsubstrate andserotonergic cautions; taper1–2minimum choice noceil/withdrawalresume clause'),
'RU-PREG':('§4.2 физ.3–5; §4.3 физ.6; §4.4 физ.6–10; §4.5–4.6 физ.11–13','GAD150/300/450/600 weekly byresponse/tolerance;2or3; all renal Table1 rows15/30/60 and25–50 choice; separate dialysis25–100 after4h; published mmol formula blocked; age<18/allergy/3lactose; angioedema immediate stop; SCAR immediate+conditional alternative missing; respiratory/opioid/CNS caution; weightgain diabetes hypoglycaemicreview; misuse pretreatment9; reproductive contraceptive9/12; pregnancy/lactation; suicideevent8 missing; source gradual>=1wk independent indication; withdrawal doseassociation notnumeric ladder/resumption'),
'RU-PHEN':('§3 физ.1; §4.2 физ.2–3; §4.4–4.6 физ.3–5','ODT score not splitting; gradual cessation withoutpercent/ladder/duration; course2wk/up2mo nottaper; unusualreactions stop4; withdrawal warning/no published resumption clause; start pregnancy/lactation/child exclusions outside selected limited cessation'),
'RU-ESC':('§3 физ.1–2; §4.2 физ.2–3; §4.3–4.6 физ.4–10','5/10/15/20; equalhalves10/15/20only; adult10/max20; panic5wk1→10;strictly>65 5/max10; CLcr>30unchanged/<30caution/exact30gap; ChildPughA/B5for2wk→10/Cclosecontrol; weakCYP2C19same separate notmultiply; taper1–2+weeks/months noceil; allergy/MAOI/pimo/QT contraindication; knownmedcautions; unstableepilepsyavoid/newincreasedseizuresstop; maniastop; arrhythmiastop+ECG; SSstopSSRI+currentserotonergic+symptom; baselineECGifCAD/electrolyte correction; MAOI14after7before/MOC>=1day; phaseownership'),
'RU-SER':('§3 физ.1; §4.2 физ.2–3; §4.3–4.4 физ.3–7; §4.5–4.6 физ.7–11','panic/social25→50 after1week; selectedincrease50>=1wk max200; keepcurrent notincreasequestion;50tablethalfonly; hepatic lower/frequency unspecified severeavoid; renalnoadjust;adult anxiety<18notpediatricOCD; MAOI14after7before and reversibleunspecifiedless14; pimo; strongCYP3A4avoid10; currentmania/newseizurestop4/unstableavoid; akathisiaharmbyincrease6; SSsourceonlymonitor; symptomatic hyponatremia6missing; QT/bleeding/suicide/pregnancy/lactation monitoring'),
'RU-VENLA-XR':('§4.2 физ.2–5; §4.3 физ.5; §4.4 физ.5–13; §4.5–4.6 физ.13–18','GAD/social75/max225/increase>=2wk; panic37.5for7d then75/formgap75/150wholecapsfood; absoluteGFR>30unchanged10..30reduce50/<10contra/dialysisseparate; hepaticmild/mod50choice/severecontra; nojointproduct; pregnant/suspected/lactcontra vs4.6conflict;strictBP>100stop9/rashstop13; withdrawal1–2 andweeks/months; priorresume source4–5; MAOI14after7before/reversibleless14sourcechoice; QTavoid; CYP2D6/3A4/CNS/metoprolol caution gaps; precursor/weightlossnotrec gaps; suicidemonitor/risk; diabetes/glaucoma/cardiac/bleeding/renal/ECT/alcohol; suspectedSSconsider8missing'),
'RU-VENLA-IR':('§1–3 физ.1; §4.2 физ.2–3','Form dependency37.5/75tablet, immediate release; indexed GFR and25–50 renal contrast notactive XR factor. Correctownversion/SHA checked allnested. Other IR medical warnings notactive in38cards.'),
'RU-PREG-RICHTER':('§4.2 физ.3; титул физ.1','Auxiliary estimator valid micromol/L factor1.23 andwomen0.85, table/footnotes;25–50 notachievable fromRichter75/150/300. Not a silent correction ofLyrica mmol typo; remaining label warnings notactive estimator.')}
inventory=[dict(source_id=k,primary_locator=v[0],conditions_actually_compared=v[1],review_scope='Source clauses and corresponding shared input/gate/action families, all 38cards; not exhaustive every-INN classifier or all combined patient states') for k,v in families.items()]
save('condition_inventory.json',{'families':inventory,'explicit_remaining_unverified':['All individual INN→interaction-class classification mappings; prepared synthetic source-class examples do not execute a classifier.','Every applicable field/result irreducibility and all present/missing/unknown counterexamples in236 authored decisions are not independently proved.','Opaque target_applicability clinical assessment does not prove all underlying independent target facts; no automatic target start allowed.','All source claims in full PIL and irrelevant4.8/5 sections were not audited.','All5086 full expected were structurally inspected, but not independently derived as5086 separate primary medical assertions.'],'new_source_clause_gaps':[f['id'] for f in F if f['id'].startswith('R1-')]})
md('condition_inventory.md','# Проверенные условия и границы охвата\n\n'+ '\n\n'.join('## '+x['source_id']+'\n\n'+x['primary_locator']+'.\n\n'+x['conditions_actually_compared'] for x in inventory)+'\n\nВсе источниковые семьи38карточек рассмотрены. Исчерпывающая проверка necessity каждого результата и каждого индивидуального INN-class mapping не выполнена. Количество5086 не выдаётся за первичные независимые медицинские проверки.\n')

coverage=deepcopy(load(OLD/'coverage.json'))
coverage['snapshot']=M['snapshot_sha256']; coverage['all_cards_examined']=len(rules)
coverage['scope_limit']='Расширенное чтение всех активных источниковых семей и исправлений; остаётся непроверенная исчерпывающая result-specific necessity/INN-class mapping. Нельзя назвать полный медицинский аудит всех5086expected завершённым.'
for c in coverage['cards']:
 rid=c['rule_id']; c.update(parameters_reviewed=len(rules[rid]['clinical_parameters']),branches_inspected=[b['branch_id'] for b in contracts[rid]['branches']],prepared_case_count=sum(x['rule_id']==rid for x in cases),inputs_inventory_inspected=[i['input_id'] for i in rules[rid]['inputs']],recheck_findings=[f['id'] for f in F if f['status']!='closed_in_original_scope' and (rid.startswith(('preg','phen')) and f['id']=='R1-06' or any(rid in p for p in f['files']))])
save('coverage.json',coverage)
input_rows=[]
for rid,r in rules.items():
 for i in r['inputs']:
  flags=[]
  if rid=='preg-taper-limit' and i['input_id'] in {'current_dose','duration_of_use','prior_withdrawal'}: flags.append('V2-12: qualitative source_limit has no dose operand/calendar; unconditional necessity unproved')
  if rid=='parox-taper-example' and i['input_id'] in {'current_dose','duration','past_withdrawal'}:flags.append('V2-12: selected numerical example needs eligibility; not_selected/qualitative result requires separate proof')
  if i['data_type']=='clinical_assessment':flags.append('Assessment is a separately supplied narrow fact; underlying hidden facts/adequacy not proved by one general clearance flag')
  if i['requirement_predicate']['kind']=='reported_context':flags.append('Known positive must get source action and consumed count; inactive predicate alone only proves omission/no false normalization')
  if any(x['rule_id']==rid and x['input_id']==i['input_id'] for x in residual):flags.append('V2-08 stale/question locator')
  input_rows.append(dict(rule_id=rid,input_id=i['input_id'],source_refs=i['source_refs'],declared_source_locator=i['source_locator'],requirement_predicate=i['requirement_predicate'],type=i['data_type'],source_family_reviewed=True,declared_role_reviewed=True,necessity_all_results_independently_proved=False,remaining_or_result_specific_issue=flags))
save('input_inventory.json',{'scope':'Every active input inventoried and shared source/type/phase role reviewed. Universal necessity is not proved by these flags; use counterexamples/findings.','inputs':input_rows})
counterexamples=[
 dict(rule_id='preg-taper-limit',result='source_limit',fields=['current_dose','duration_of_use','prior_withdrawal'],source='RU-PREG §4.4 физ.9',known='150/24weeks/false',missing_unknown='Each currently forces insufficient_data; source minimum>=1week with no exact calendar does not calculate from these three operands.',required_resolution='Demote for this limited result with explicit unassessed; keep known urgent/current symptom actions. Numerical individualized calendar still needs separate data.'),
 dict(rule_id='parox-taper-example',result='not_selected/withdrawal vs selected40',fields=['current_dose','duration','past_withdrawal'],source='RU-PAROX §4.2 физ.3–4, §4.4 физ.10',known='Selected40 requires current40 and explicit example choice; produces concrete30/20/0.',missing_unknown='Qualitative not_selected gives no calendar; its unconditional current/duration/history necessity cannot be inferred from selected40.',required_resolution='Result-specific trigger and own missing/unknown proof rather than globalalways; retain clinically known withdrawal.'),
 dict(rule_id='ago-gad-start/ago-depression-start',result='already chosen source-bound25 start',fields=['renal_state'],source='RU-AGO §4.2 физ.2 / §4.4 физ.4',known='moderate/severe source caution, no numerical correction; no significant PKdose change',missing_unknown='Generic caution is not an explicit source mandate for a separate universal prestart assessment. Existing model returns choice.',required_resolution='Potential reported_context model with known caution action/unassessed warning/clinical_clearance=false requires a complete rebuilt proof; do not silently remove fact or call current path minimal.'),
 dict(rule_id='ago-gad-start/ago-depression-start',result='selected25 start',fields=['overweight_obesity','fatty_liver','diabetes','alcohol_abuse'],source='RU-AGO §4.4 физ.3',known='Source asks careful benefit/risk assessment in risk patients.',missing_unknown='Explicit narrow clinician hepatic benefit/risk conclusion may be an alternative result fact; four false answers cannot be invented from it.',required_resolution='Source-bound assessment/provenance and all applicable paths, no generalclinicalclearance or claim<=15 from one substitution.'),
 dict(rule_id='ser-adult-adjust',result='keep vs increase vs not_chosen',fields=['time_at_dose','response','tolerability','adherence','akathisia'],source='RU-SER §4.2 физ.2 / §4.4 физ.6',known='keep100 remains100 without future increase data; increase needs>=1week/akathisia; notchosen needs source clinical assessment.',missing_unknown='Own static checks and full prepared examples preserve conditional operands rather than requiring next-step data forkeep.',required_resolution='This selected-action distinction is supported in reviewed source scope; known symptomatic events still need R1-01.'),
 dict(rule_id='preg-gad-start',result='reproductive condition',fields=['reproductive_population','effective_contraception'],source='RU-PREG §4.4 физ.9 / §4.6 физ.12',known='true requires contraception;false does not infer pregnancy/lactation negatives.',missing_unknown='Unknown reproductive trigger blocks; explicit effective contraception missing/unknown undertrue requests it.',required_resolution='Keep separate independent source facts; do not merge pregnancy/lactation/contraception forcount.'),
 dict(rule_id='esc-start variants',result='CAD/electrolytes condition',fields=['coronary_disease','ecg_done','electrolyte_disturbance','electrolytes_corrected'],source='RU-ESC §4.4 физ.6',known='Actual CAD needs ECG; actual disturbance needs correction; all such paths complex by source intervention.',missing_unknown='Unknown trigger notfalse; unknown required followup no automaticdose.',required_resolution='Correct conditional structure; supportscomplex classification, doesnot shortenAGO/DULOX/PREGordinary.'),
 dict(rule_id='ser-taper-limit',result='known strongCYP3A4 caution/avoid',fields=['medicines.INN','medicines.status'],source='RU-SER §4.5 физ.10',known='Full case has knowncurrent strongCYP3A4.',missing_unknown='Projectedgiven losesmedicines yet attributes specific class/action.',required_resolution='Consume/count two recordfacts ifknown; otherwise no specific positive class inference. No mandatory routine prestart screen forqualitative cessation implied.')]
save('necessity_counterexamples.json',counterexamples)
md('coverage.md','# Охват повторной приёмки\n\n38карточек,211вхождений clinical_parameters/104различимых source-value-unit параметров рассмотрены. Самостоятельное первичное чтение и визуальная проверка существенных таблиц/формул отражены вsource_verification. Дополнительно исследованы применимые события/взаимодействия; новые отсутствующие условия конкретно перечислены.\n\n5086full expected: типы/ветви/аритметика/полный одинаковый given проверены; не заявляется5086независимых первичных медицинских выводов.391 suppliedpath восстановлен; это не полнота всех мыслимых сочетаний.\n\nКаждый activeinput имеется вinput_inventory.json, но необходимость каждого поля/результата не считается доказанной только изflag/ledger. Конкретные источниковые контрпримеры —necessity_counterexamples.json. В частности PREGqualitative taper3поля, PARqualitative alternatives иAGOrenal/specifichepaticassessment требуют решения. Все236авторскихnecessity решений не получили исчерпывающего независимого набораpresent/missing/unknown контрпримеров. ИндивидуальныеINN-class классификаторы, полныеЛВ и неиспользуемые§4.8/5 не проверены.\n')

primary=load(O/'primary_expected_checks.json')
fc=[c for c in cases if c['rule_id']=='fluvox-depression-start' and '--reversible-' in c['case_id']]
primary['checks'].append(dict(name='FLUV next calendar day distinct from elapsed24h',passed=all(c['expected']['result_type']==('not_applicable' if c['case_id'].endswith('same-day') else 'exact') for c in fc) and len(fc)==3,source='RU-FLUVOX',locator='§4.3 physical3',cases_checked=[c['case_id'] for c in fc]))
save('primary_expected_checks.json',primary)

A=deepcopy(load(OLD/'acceptance_recheck.json'))
partial={9,10,14,15,17,18,30}
evidence={
1:'Physician-selected diagnosis retained; narrowPARscreening repaired without repeatdiagnosis.',
9:'Current product/version/sourcebases correct; input/question/ledger and main01 physicalclaims still disagree: V2-08/11.',
10:'All source-parameter families compared; numerical boundaries repaired. R1-01..06 show incomplete source conditions/actions; not full medical chain acceptance.',
14:'Directions and A/B phased urgentactions reviewed; Russian pair gaps preserved. SER interaction/symptomatic event scope remains R1-01/03; opaque targetassessment is notcompletefactclearance.',
15:'Minimum/slow withdrawal and no arbitraryuniversalpercent preserved. PREGqualitative operands and PREG/PHENunestablishedresumption/R1-01ongoingevent needfix.',
17:'211parameters, allactiveinputs,2166ledgerrows and236decisions structurally connected; necessity ofall result-specific facts notindependently proved. Concretecounterexamples retained.',
18:'Own391traces: ordinaryAGO20/DULOX-GAD17/PREG17–18. ESC13/CYP14,SER10/XR12; necessary11–15 notpenalized byoldlimit. No false renaming.',
19:'Every actual ESC CAD/electrolyte source intervention classifiedcomplex independentlyofcount; source6. MAOItype/date and A/Bplan phases costexplicit. Complexity doesnot proveordinaryminimum.',
20:'391projections now0absentnegative/0negative-unassessedoverlap; alltypedunknown/missingfullcases retainnoautomaticnumericnorm. Specific consumed-positive loss remains V2-10, not a false-normal negative.',
21:'Mandatory typed/nested unknown scenarios requestnamedmissingfield and no executable dose; conditionalclinical context remains explicitlyunassessed. V2-10knownpositive projection is separatelyopen.',
24:'11 current official productbases linked to human-acquired files/stamps/forms; sameSHA previous actualreadings reuse explicitlyrecorded. Notpretending repeateddownload orfullPILreading.',
29:'Readiness markers corrected; research types/source numericfacts and selectedphysicianresults distinguished from whole medical/clinclearance. Openmedical branches cannotbecarried asfullyreviewed.',
30:'Known new source/action/locator/projection gaps are listed byindependent recheck, but frozen candidate doesnot yet resolve/fulllyenumerate medical chain. No proofabsenceanalogue claimed.'}
mapping={9:['V2-08','V2-11'],10:['R1-01','R1-02','R1-03','R1-04','R1-05','R1-06'],14:['R1-01','R1-03'],15:['R1-01','R1-06','V2-12'],17:['V2-10','V2-12','R1-07'],18:['V2-13'],30:[f['id'] for f in F if f['status']!='closed_in_original_scope']}
for c in A['criteria']:
 n=c['number']; c['status']='частично' if n in partial else 'выполнено'
 if n in evidence:c['evidence']=evidence[n]
 c['finding_ids']=mapping.get(n,[])
 c['limits']='Читаемые первичные семьи/конкретные статические свойства перечислены отдельно. Все uniqueINNclass mappings/каждое result-specific necessity доказательство не объявлены выполненными. Это исследовательская приёмка без калькулятора/клинической валидации.'
 c['effect']='Материально ограничивает приёмку; cap≤6 по№17/18' if n in partial else 'Засчитан критерий в указанном исследовательском объёме; не снимает отдельные открытые критерии'
A.update(snapshot=M['snapshot_sha256'],statuses=dict(Counter(c['status'] for c in A['criteria'])),only_changed_criterion=18,scope_limit=coverage['scope_limit'])
assert len(A['criteria'])==30
save('acceptance_recheck.json',A)
save('requirements_diff.json',load(OLD/'requirements_diff.json'))
md('acceptance_recheck.md','# Все30критериев ТЗV2\n\nСнимок `'+M['snapshot_sha256']+'`. Изменён только исходный№18; exactdiff —requirements_diff.json.\n\nСтатусы: '+str(A['statuses'])+'; не выполнено0, не удалось проверить0. Последнее не означает исчерпывающую первичную проверку всехусловий —неполнота учтена вчастичных№10/17/30.\n\n|№|Дословный критерий|Статус|Свидетельство/ограничение|\n|---:|---|---|---|\n'+ '\n'.join('|'+str(c['number'])+'|'+c['literal_criterion']+'|'+c['status']+'|'+c['evidence']+'|' for c in A['criteria']))

dimensions=[('Источники/версии/РФ',25,'9.0','Все11продуктовых первичных оснований подтверждены для снимка;11076nestedbases owner/version/SHA согласованы. Снижение за оставшиеся неправильныеinput/ledger physicallocators и противоречивыйmain01; не из-за отсутствия самостоятельного CAPTCHAdownload.'),('Правила/воспроизводимость',30,'7.5','Опубликованные дозовые числовые семьи/границы/формы сохранены, старыеurgentconditions исправлены. Новыеknowncurrentevents и взаимодействия/полныедействия ещё отсутствуют; source_limit resumption gap.'),('Входы/пути',20,'6.6','391путь самостоятельно пересчитан,97ложныхnegative проекций исправлены,19демоций допустимы вограниченномscope. Осталась потеряннаяпричина, неправильноразведённаяXRpregnancy и недоказанныйminimum/ordinary20/17/18.'),('Покрытие/приёмка',15,'7.4','Все38/sourcefamilies и30критериев рассмотрены; чтение расширено, первичныеусловияповторносопоставлены. Не доказан каждыйuniqueclass/result necessity;5086prepared неравныполным независимымпервичнымchecks.'),('Техника',10,'8.6','Прочитанные validators безопасноповторены;35+5source-detector mutations,8repairmutations,3авторскихtechnical и12собственныхpropertychecks.0graph/count/branchtypeerrors/0wholegivenconflicts; detectorне ловит lostpositivecause. Appнет/не требуется.')]
raw=sum(Decimal(score)*Decimal(weight)/Decimal(100) for _,weight,score,_ in dimensions)
score=dict(dimensions=[dict(name=n,weight=w/100,score=float(s),reason=r) for n,w,s,r in dimensions],weights=[25,30,20,15,10],raw_unrounded=float(raw),raw_one_decimal=float(raw.quantize(Decimal('.1'))),cap=6.0,cap_basis=['V2-12/№17: every result-specific input necessity unproved, PREG qualitative taper example','V2-13/№18: actual ordinaryAGO20/DULOX-GAD17/PREG17–18','R1-01..05: substantial incomplete source condition/action transfer'],critical_cap4_applied=False,critical_cap4_reason='В проверенной части не установлены изменённые publisheddose/interval/unit или completeknowncontra→allow. Известныеcritical source conflicts/form gaps корректноblocked; непровереннаячасть не названа безопасной.',final_one_decimal=6.0,snapshot=M['snapshot_sha256'],own_expert_score=True,clinical_validation='not_performed and notrequiredclinicalproducttrial forresearchscore')
save('scoring.json',score)
md('scoring.md','# Самостоятельная экспертная оценка\n\n|Измерение|Вес|Оценка|Основание|\n|---|---:|---:|---|\n'+ '\n'.join('|'+n+'|'+str(w)+'%|'+s+'|'+r+'|' for n,w,s,r in dimensions)+'\n\nНеокруглённая сумма **'+str(raw)+'**, с одним знаком **'+str(score['raw_one_decimal'])+'**. Содержательный предел№17/18 инеполного переноса **≤6,0**, итог **6,0/10**. Cap4 вфактическипровереннойчасти не установлен. Это новаяоценка данногоSHA, не пересчёт прежнегоТЗ или обещание10/10.\n')
md('required_fixes.md','# Условия следующей ревизии\n\n'+ '\n'.join('- '+f['id']+': '+f.get('recheck_evidence',f['required_fix']) for f in F if f['status']!='closed_in_original_scope')+'\n\nНовый SHA и сохранение этого заключения обязательны. Исправление текущихнаходок не закрывает№17/18 автоматически; обычные длинныепустопереименованныепути недопустимы. Последующая реализация требуетactual sourceboundary/unknown/form/phase/conditionalstage tests; clinicalvalidation вэтойприёмке невыполнена и непредъявленакакпройденная.\n')
md('summary.md','''# Независимая повторная приёмка ТЗ V2

Снимок **ff00118c08d144f1434869d25aba164234a443b4732f84fe8d481504622cf6ec**,164файла. Новый вывод: **23выполнено /7частично /0невыполнено /0неудалосьпроверить**. Частично№9,10,14,15,17,18,30. Экспертная сумма **7,79** (7,8), после содержательного cap≤6 по№17/18 и неполному переносу — **6,0/10**. Все30дословныхкритериев и пятьсамостоятельныхоценок —acceptance_recheck/scoring.

Девятьисходныхзамечаний закрыты висходномпредмете: V2-01,02,03,04,05,06,07,09,14. Частичнооткрыты V2-08,10,11,12,13. Закрытие узкоговопроса не подтверждает полноту всего препарата. Новые R1-01..07: четыре текущихклинических source-defined события; XR взаимодействия/avoidance; SERусловия вобоихSSRIпереходах; дополнительныйDULOXпродукт; полноеSCARдействиеPREG; непроверенноеPREG/PHENresumption; пересечениеXRpregnancyсемантики. Точныепервичныефизическиестраницы/SHA иусловия закрытия —findings.

Проверены все38карточек и211clinicalparameterвхождений/104различимыеsource-value-unitсемьи; первичныеполученныеоригиналы11продуктовыхоснований, релевантныеКР и формы/таблицы/формулы. Собственноечтение предыдущего прохода использовано только при совпадениибайтов; расширеныприменимыеcurrent-event/interactionучастки. Карта реальнопрочитанных/визуальнопроверенныхстраниц —source_verification. Не выполненоисчерпывающее доказательство каждого индивидуальногоINN-classmapping и каждого result-specificnecessity present/missing/unknownконтрпримера всех236решений. ПолныеЛВ/неиспользуемые§4.8/5 не названыпрочитанными. Исчерпывающий первичный медицинскийаудит всехуникальныхусловий/5086ожиданий завершённым не объявляется.

Независимыйбезопасный rerun: staticcontractbaselinePASS,35+5 авторскихsource-detector мутаций и8 дополнительныхrepairмутаций отвергаются;3авторскихtechnicalграницы/count и12собственныхpropertychecks также выполнены.15выбранныхсобственныхsourceassertions (включаяFLUVследующийкалендарныйдень) и11 повторённыхauthorphraseguards проходят. Все391suppliedtrace/count/predicate/edge пересчитаны;0wholegiven/context→разныхполныхexpected среди5086. Но однапроекция SERtaper теряетmedicines, сохраняяknownstrongCYP3A4причину. PASS проверяетпрочитанныеproperties, анеполнуюмедицинскуюкорректность илиисполнение ненаписанногокалькулятора.

Фактическиеобычныечисловыепути: AGO20, DULOX-GAD17, PREG17/18 остаютсяоткрытыми. ESC13/CYP14, SERstart10, XR12; DULOXdepression15, FLUV12, PARstart13 (новыйsource-requiredscreening), PARselectedtaper11, SERselectedcorrection13/15. РеальныеESC CAD/electrolyteinterventions источниковосложные независимоотcount; CYP16показанотдельно. Ниlowerbound, нипереиспользованиеготовыхданных не названыполнымобычнымминимумом. ВозможныеAGOrenal/narrowhepaticassessment иqualitativetaperсокращения описаны как требующие полного доказательства, неготовое≤15.

Допустим ограниченныйпоследующий техническийперенос проверенныхтипов, источниковыхчисловыхвеличин, отказов/пробелов иусловныхврачебныхвыборов. Ветки с открытыминаходками нельзяпереносить как полностьюмедицинскипроверенныйавтоматическийрежим. Лирика/литий/циталопрам, XR37.5formgap, неустановленныепарныеинтервалы сохраняютблокировкибезиностранногорезерва. Полныйклиническийдопуск и клиническаявалидацияневыполнены; продукт не реализован.

После сохраненияэтогозаключения исполнительможетприменить исправления вновуюревизию с новымSHA и отдельной повторнойпроверкой. Предыдущее заключение/этотснимок не переписывать. Сохранность —preservation_check.json; финальныйотпечаток —final_manifest.json.
''')

# Correct normal prose spacing in narrative reports without modifying quoted source criteria/data.
for name in ['summary.md','scoring.md','coverage.md','condition_inventory.md','required_fixes.md']:
 s=(O/name).read_text('utf-8')
 s=re.sub(r'(?<=[А-Яа-яЁё])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?=[А-Яа-яЁё])',' ',s)
 (O/name).write_text(s,'utf-8')

baseline=load(R/'baseline_manifest.json')['files']; protected=[x for x in baseline if x.get('protected')]
originals=[x for x in baseline if x['path'].startswith(('research/source_downloads/','research/source_snapshots/'))]
bad=[x['path'] for x in {x['path']:x for x in protected+originals}.values() if not (W/x['path']).exists() or sha(W/x['path'])!=x['sha256']]
final_files=[dict(path=x['path'],sha256=sha(W/x['path'])) for x in INITIAL['files'] if (W/x['path']).exists()]
changed=[x['path'] for x in INITIAL['files'] if not (W/x['path']).exists() or sha(W/x['path'])!=x['sha256']]
corebad=[x['path'] for x in M['files'] if sha(W/x['path'])!=x['sha256']]
save('final_manifest.json',dict(utc=datetime.now(timezone.utc).isoformat(),snapshot=M['snapshot_sha256'],core_files=len(M['files']),core_changed=corebad,changed_during_review=changed,files=final_files))
save('preservation_check.json',dict(status='pass' if not bad and not corebad else 'fail',protected_files=len(protected),original_source_files=len(originals),changed_or_missing=bad,core_files=len(M['files']),core_changes=corebad,noncore_changes_during_review=changed,own_write_scope='research/acceptance_v2_audit/recheck1 only'))
print(json.dumps(dict(statuses=A['statuses'],raw=str(raw),final=6.0,closed_original=len(closed),still_open_original=14-len(closed),new_findings=7,inputs=len(input_rows),protected=len(protected),originals=len(originals),preservation_bad=bad,core_changes=corebad,broader_changes=changed),ensure_ascii=False))
