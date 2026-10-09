from pathlib import Path
import json,hashlib,sys,fitz
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]; S=json.loads((ROOT/'research/remediation_round3/sources.json').read_text('utf8'))
sid=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(',')]; p=ROOT/'research'/S[sid]['local_file']; sha=hashlib.sha256(p.read_bytes()).hexdigest(); assert sha==S[sid]['document_fingerprint']['sha256']
d=fitz.open(p); extracts=[]
for n in pages:
    t=d[n-1].get_text(); print('\n=== '+sid+' physical '+str(n)+' ===\n'+t); extracts.append(dict(physical_page=n,text=t))
target=OUT/'primary_read';target.mkdir(exist_ok=True); (target/(sid+'_'+str(pages[0])+'_'+str(pages[-1])+'.json')).write_text(json.dumps(dict(source_id=sid,file=str(p),sha256=sha,pages=extracts,method='Actual independent text reading; extracted text is evidence, no automatic medical verification.'),ensure_ascii=False,indent=2),encoding='utf8')
