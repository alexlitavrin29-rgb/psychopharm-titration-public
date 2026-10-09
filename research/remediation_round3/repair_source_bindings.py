"""Repair active source ownership; preserve historical copies and unknown fixtures."""
from pathlib import Path
import json, yaml

O = Path(__file__).resolve().parent
S = json.loads((O / 'sources.json').read_text(encoding='utf-8'))
unknown = {None, 'unknown', 'not_assessed', 'неизвестно', 'не исследовано'}
changes = []

def visit(x, path):
    if isinstance(x, list):
        for n, v in enumerate(x):
            visit(v, f'{path}/{n}')
    elif isinstance(x, dict):
        sid = x.get('source_id', x.get('source_ref'))
        if isinstance(sid, str) and sid in S:
            for key in ['version', 'source_version']:
                if key in x and isinstance(x[key], str) and x[key] not in unknown:
                    new = S[sid]['version_or_update_date']
                    if x[key] != new:
                        changes.append(dict(path=path, source_id=sid, field=key, before=x[key], after=new))
                        x[key] = new
            if 'sha256' in x and isinstance(x['sha256'], str):
                x['sha256'] = S[sid]['document_fingerprint']['sha256']
            if sid in {'RU-VENLA-IR', 'RU-VENLA-XR'}:
                for key in ['locator', 'source_locator']:
                    if isinstance(x.get(key), str) and x[key].startswith('HTML'):
                        x[key] = S[sid]['exact_locator']
        for key, v in x.items():
            # Supplied counterfixture metadata may intentionally be wrong or unknown.
            if key not in {'document_copies', 'given'}:
                visit(v, path + '/' + key)

for p in [O / 'result_contracts.yaml', O / 'full_scenarios.json', *sorted((O / 'rules').glob('*.yaml'))]:
    is_json = p.suffix == '.json'
    data = json.loads(p.read_text(encoding='utf-8')) if is_json else yaml.safe_load(p.read_text(encoding='utf-8'))
    visit(data, p.name)
    if p.stem == 'phen-taper-limit':
        data['identity']['registration_identity_source'] = 'Точная запись ЛП-№(005387)-(РГ-RU); текущая официальная ОХЛП §1–3 с.1, регистрационный штамп07.05.2026, экспертный отчёт05.05.2026 №9041/0004. Ородисперсная форма0,25/0,5/1мг; риска не предназначена для деления.'
    text = json.dumps(data, ensure_ascii=False, indent=2) if is_json else yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110)
    p.write_text(text, encoding='utf-8')

for sid in ['RU-VENLA-IR', 'RU-VENLA-XR']:
    S[sid]['evidence_limitations'] = S[sid]['evidence_limitations'].replace('Снимок оригинальной страницы производителя, не PDF реестра.', 'Предыдущая копия была HTML производителя. Активное основание — полученный текущий официальный PDF реестра точного РУ/формы.')
for sid, old in [('RU-PREG-RICHTER', 'Последняя редакция ГРЛС побайтово не подтверждена.'), ('RU-FLUVOX', 'Последняя редакция реестрового PDF не сопоставлена побайтово.'), ('RU-PHEN', 'Прочитанная копия не доказывает последнее реестровое содержание.')]:
    S[sid]['evidence_limitations'] = S[sid]['evidence_limitations'].replace(old, 'Текущий официальный оригинал получен и сохранён со SHA; несовпадение со старой копией отделено от медицинского сравнения содержания.')
(O / 'sources.json').write_text(json.dumps(S, ensure_ascii=False, indent=2), encoding='utf-8')
for p in (O / 'rules').glob('*.yaml'):
    data = yaml.safe_load(p.read_text(encoding='utf-8'))
    for source in data['sources']:
        sid = source['source_id']
        for key in ['version_or_update_date', 'exact_locator', 'evidence_limitations', 'document_fingerprint', 'own_read_scope']:
            if key in source:
                source[key] = S[sid][key]
    product_sources=[S[x['source_id']] for x in data['sources'] if S[x['source_id']]['source_type']=='label']
    if product_sources and all(x.get('latest_registration_revision_confirmed') for x in product_sources):
        verification=data['verification']
        verification['source_transfer_check']='Current exact Russian product originals obtained and active owner/version/hash/locators synchronized; listed primary sections reviewed. Full independent medical acceptance and question necessity remain separate; calculator_not_implemented.'
        verification['russian_applicability_checked']=True
        verification['russian_applicability_scope']='Identity of the exact registered Russian product/form and published indication scope; does not grant patient clearance or prove every transferred condition.'
        verification['transfer_scope']='Explicit source-bound branch contracts and prepared expectations only. Current originals obtained; pending independent findings, result-specific necessity and V2 ordinary-question limit are not inferred complete from download. No clinical validation.'
        obsolete=['Последняя регистрационная редакция','Текущая регистрационная редакция','Последняя реестровая редакция','F12: other active product edition currencies']
        verification['unresolved_items']=[x for x in verification.get('unresolved_items',[]) if not any(term in x for term in obsolete)]
        verification['unresolved_items'].append('Минимальность входов/полные обычные пути и повторная независимая проверка медицинских исправлений остаются отдельными условиями приёмки V2.')
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), encoding='utf-8')
(O / 'source_binding_repairs.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
print('Active owner-bound source repairs:', len(changes), '; historical document_copies and unknown/omitted fixture states retained.')
