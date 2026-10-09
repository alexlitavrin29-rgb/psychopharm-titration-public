"""Prepare a separate round3 research snapshot; main files and historical audits stay untouched."""
from pathlib import Path
from copy import deepcopy
import json, re, yaml

O=Path(__file__).resolve().parent; R=O.parent
def readj(p): return json.loads(p.read_text(encoding='utf-8'))
def ready(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def savej(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def savey(p,x): p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
oldS=readj(R/'sources.json'); S=deepcopy(oldS)
records={x['source_id']:x for x in readj(O/'current_registry_documents.json')['documents']}
for sid,d in records.items():
    s=S[sid]
    for cp in s.get('document_copies',[]): cp['byte_identity_to_primary_snapshot']=False
    version=f"Официальная ОХЛП реестра: штамп регистрации {d['document_registration_stamp']}; экспертный отчёт {d['expert_stamp']['date']} №{d['expert_stamp']['report_number']}/{d['expert_stamp']['sequence']}; получена 08.10.2026"
    s.update(local_file=d['original_file'],url=d['registry_url'],doi_or_registry_id=d['registration_number'],version_or_update_date=version,exact_locator=d['current_source_locator'],latest_registration_revision_confirmed=True,
        dates=dict(registration=d['registry_first_registration'],revision=None,publication=None,download='2026-10-08',document_registration_stamp=d['document_registration_stamp'],expert_report=d['expert_stamp']['date']),
        document_fingerprint=dict(source_id=sid,url=d['registry_url'],sha256=d['original_sha256'],pages=d['physical_pages'],accessed_on='2026-10-08'),
        latest_registry_document_comparison=dict(record='remediation_round3/current_registry_documents.json#'+sid,original=d['original_file'],sha256=d['original_sha256'],authority_evidence=d['authority_evidence'],comparison_scope='Listed primary sections and dependency review; no inference of byte identity to historical copies'),
        registry_observation=dict(registry=d['registry_url'],query=d['query'],registration_number=d['registration_number'],registration_date=d['registry_first_registration'],forms=d['exact_form'],accessed_on='2026-10-08',read_part=d['authority_evidence']),
        own_read_scope=dict(text_pages=d['actually_read_text_physical_pages'],visual_pages=d['actually_reviewed_visual_physical_pages'],remaining_sections_not_claimed_read=True))
    s.setdefault('document_copies',[]).append(dict(source_id=sid,local_file=d['original_file'],sha256=d['original_sha256'],version=version,url=d['registry_url'],download_date='2026-10-08',byte_identity_to_primary_snapshot=True,latest_registration_revision_confirmed=True))
    s['evidence_limitations']+=' Новая первичная копия получена из указанной строки реестра; старые копии сохранены как исторические. Даты штампов не подменяют незаполненное поле пересмотра. Принадлежность версии и медицинский перенос проверяются раздельно.'

locs={
'RU-DULOX':{'age':'§4.1–4.3 с.1–4','form':'§1–3 с.1','hepatic':'§4.2–4.3 с.3–4','pregnancy':'§4.6 с.9–10','lactation':'§4.6 с.10','medicines':'§4.3 с.3–4; §4.5 с.7–9','allergy':'§4.3 с.3','renal_metric':'§4.2 с.3; §4.3 с.4','comorbid_depression':'§4.2 с.2','elderly_population':'§4.2 с.3','uncontrolled_hypertension':'§4.3 с.4','closed_angle_glaucoma':'§4.3 с.3','maoi_type':'§4.5 с.7','maoi_stopped_at':'§4.5 с.7','fructose_intolerance':'§4.4 с.7','glucose_galactose_malabsorption':'§4.4 с.7','sucrase_isomaltase_deficiency':'§4.4 с.7','akathisia':'§4.4 с.7','mania':'§4.4 с.4','suicide_risk':'§4.4 с.5–6','bleeding_risk':'§4.4 с.6','hyponatremia_risk':'§4.4 с.6','diabetes':'§4.4 с.4','seizure_state':'§4.4 с.4','current_dose':'§4.2 с.2–3','response':'§4.2 с.2','tolerability':'§4.2 с.2','duration':'§4.2 с.3; §4.4 с.6','withdrawal_severity':'§4.2 с.3; §4.4 с.6','past_withdrawal':'§4.4 с.6'},
'RU-VENLA-XR':{'form':'§1–3 с.1; §4.2 с.5','age':'§4.2 с.4; §4.3 с.5','hepatic':'§4.2 с.4; §4.3 с.5','pregnancy':'§4.3 с.5; §4.6 с.17–18 (противоречие формулировок, обычная ветка запрещена)','pregnancy_suspected':'§4.3 с.5','lactation':'§4.3 с.5; §4.6 с.18','medicines':'§4.3 с.5; §4.5 с.13–17','allergy':'§4.3 с.5','renal_metric':'§4.2 с.4; §4.3 с.5','maoi_type':'§4.5 с.13–14','maoi_stopped_at':'§4.5 с.13–14','qt_risk':'§4.4 с.10; §4.5 с.15–16','diastolic_BP':'§4.4 с.9','current_dose':'§4.2 с.4–5','duration':'§4.2 с.4–5; §4.4 с.11–12','withdrawal_severity':'§4.4 с.11–12','past_withdrawal':'§4.4 с.11–12'},
'RU-PHEN':{'age':'§4.2–4.3 с.3','form':'§1–3 с.1; §4.2 с.3','current_dose':'§4.2 с.2','duration':'§4.2 с.2; §4.4 с.4','withdrawal_severity':'§4.4 с.4','past_withdrawal':'§4.4 с.4'},
}
def relocate(text,sid):
    if sid not in records: return text
    if sid in {'RU-PAROX','RU-PREG-RICHTER'}:
        return re.sub(r'(с\.\s*)(\d+)(?:([–-])(\d+))?',lambda m:m[1]+str(int(m[2])-13)+(m[3]+str(int(m[4])-13) if m[3] else '') if int(m[2])>=14 else m[0],text)
    if sid=='RU-DULOX': return records[sid]['current_source_locator']
    if sid=='RU-VENLA-XR':
        if 'контроль АД' in text: return '§4.4 с.9, прекращение при диастолическом АД >100 мм рт.ст.'
        if 'Синдром отмены' in text: return '§4.2 с.4–5; §4.4 с.11–12'
        if 'Панические' in text: return '§4.2 с.3; §4.2 с.5 (целые капсулы)'
        if 'ГТР / социальные' in text: return '§4.2 с.2–3'
        if 'Способ применения' in text: return '§4.2 с.5'
        return records[sid]['current_source_locator']
    if sid=='RU-PHEN': return records[sid]['current_source_locator']
    return text
# A shared old version label (e.g. IR/XR) is not a source identity.
version_owners={}
for s in records: version_owners.setdefault(oldS[s]['version_or_update_date'],[]).append(s)
versions={v:S[owners[0]]['version_or_update_date'] for v,owners in version_owners.items() if len(owners)==1}
hashes={oldS[s]['document_fingerprint']['sha256']:S[s]['document_fingerprint']['sha256'] for s in records if oldS[s].get('document_fingerprint',{}).get('sha256')}
def sync(x):
    if isinstance(x,str): return versions.get(x,hashes.get(x,x.replace('remediation_round2/result_contracts','remediation_round3/result_contracts').replace('remediation_round2/input_contracts','remediation_round3/input_contracts')))
    if isinstance(x,list): return [sync(v) for v in x]
    if not isinstance(x,dict): return x
    if x.get('source_id') in records and 'title' in x and 'source_type' in x: return deepcopy(S[x['source_id']])
    out={k:sync(v) for k,v in x.items()}
    sid=x.get('source_ref',x.get('source_id'))
    if sid in records:
        for k in ('version','source_version'):
            if k in out and isinstance(out[k],str) and out[k] not in {'unknown','not_assessed','неизвестно','не исследовано'}:
                out[k]=S[sid]['version_or_update_date']
        for k in ('source_locator','locator','exact_locator'):
            if k in out: out[k]=relocate(out[k],sid)
    return out
rules={p.stem:sync(ready(p)) for p in (R/'rules').glob('*.yaml')}
C=sync(ready(R/'remediation_round2/result_contracts.yaml'))
F=sync(readj(R/'remediation_round2/full_scenarios.json'))
schema=sync(ready(R/'remediation_round2/input_contracts.yaml'))
for rid,r in rules.items():
    for i in r['inputs']:
        if len(i['source_refs'])==1:
            sid=i['source_refs'][0]
            i['source_locator']=locs.get(sid,{}).get(i['input_id'],relocate(i['source_locator'],sid))
            if sid=='RU-VENLA-XR' and i['input_id'] not in locs[sid]: i['source_locator']='§4.4 с.5–13, осторожность/наблюдение; конкретный подпункт в первичном журнале'
    for p in r['clinical_parameters']:
        if p['source_ref']=='RU-DULOX': p['source_locator']='§4.2 с.3' if p['parameter_id'] in {'elderly_initial_period','renal_no_adjust_lower','source_taper_period'} else '§4.2 с.2'
    # Legacy source examples remain examples and are not converted to universal taper calendars.
    if rid=='fluvox-taper-limit': r['identity']['formulation']='Феварин 50/100 мг; разрешены две равные половины (§3 с.1; §4.2 с.3 текущей ОХЛП)'
    if rid=='phen-taper-limit':
        r['identity']['formulation']='Феназепам, ородисперсные таблетки 0,25/0,5/1 мг; риска не предназначена для деления (§3 с.1)'
        r['logic']['form_split_permitted']=False
    if rid.startswith('preg'):
        # Exact current auxiliary formula locator; never alters the Lyrica mmol/L typo.
        def fix_aux(x):
            if isinstance(x,list):
                for z in x: fix_aux(z)
            if isinstance(x,dict):
                if x.get('source_ref')=='RU-PREG-RICHTER' or x.get('source_id')=='RU-PREG-RICHTER':
                    for k in ('source_locator','locator'):
                        if k in x: x[k]='§4.2 с.3, формула CLcr (мкмоль/л), таблица1 и сноска недостижимых 25–50 мг'
                for z in x.values(): fix_aux(z)
        fix_aux(r['logic'])
    r['verification']['round3_status']='candidate_primary_transfer_and_necessity_review; independent acceptance pending'
for c in F['cases']:
    for v in c['given'].values():
        if isinstance(v,dict) and v.get('source_id')=='RU-PHEN' and 'registration_number' in v and v['registration_number'] is None:
            v['registration_number']=S['RU-PHEN']['doi_or_registry_id']
(O/'rules').mkdir(exist_ok=True)
for rid,r in rules.items(): savey(O/'rules'/ (rid+'.yaml'),r)
savej(O/'sources.json',S); savey(O/'result_contracts.yaml',C); savej(O/'full_scenarios.json',F); savey(O/'input_contracts.yaml',schema)
savej(O/'source_metadata_changes.json',[dict(source_id=s,old_file=oldS[s].get('local_file'),new_file=S[s]['local_file'],old_version=oldS[s]['version_or_update_date'],new_version=S[s]['version_or_update_date'],old_sha=oldS[s].get('document_fingerprint',{}).get('sha256'),new_sha=S[s]['document_fingerprint']['sha256']) for s in records])
print('Candidate source bindings updated: nine originals; 38 cards; existing contracts/scenarios. Main files unchanged.')
