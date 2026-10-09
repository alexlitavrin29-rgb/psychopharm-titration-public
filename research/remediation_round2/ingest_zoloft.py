from pathlib import Path
import json,hashlib,shutil
import fitz
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
downloads=Path('C:/Users/Alex/Downloads')
names=[('1.3.1 Золофт ОХЛП 21.04.26_02002 (1817931491) [0008] штамп МЗ.pdf','Zoloft_current_registry.pdf','SmPC'),('1.3.1 Золофт ЛВ 22.04.26_02001 (1817931561) [0008] штамп МЗ.pdf','Zoloft_current_registry_PIL.pdf','PIL')]
old=R/S['RU-SER']['local_file'];oldhash=hashlib.sha256(old.read_bytes()).hexdigest()
rows=[]
for name,dest,kind in names:
    p=O/dest;shutil.copyfile(downloads/name,p);doc=fitz.open(p)
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    p.with_suffix('.txt').write_text('\n'.join('PAGE '+str(i+1)+'\n'+x.get_text() for i,x in enumerate(doc)),encoding='utf-8')
    rows.append(dict(filename=name,local_file='remediation_round2/'+dest,sha256=sha,pages=len(doc),document_type=kind))
    if kind=='SmPC':
        doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(O/'zoloft_page_1.png')
        rows[-1]['byte_identity_to_previously_read_original']=sha==oldhash
report=dict(download_date='2026-10-08',human_provided=True,registry_url='https://lk.regmed.ru/Register/EAEU_SmPC',old_local_file=S['RU-SER']['local_file'],old_sha256=oldhash,documents=rows,confirmation_pending='Visual stamp and current registry list inspected separately before source status update')
(O/'zoloft_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
