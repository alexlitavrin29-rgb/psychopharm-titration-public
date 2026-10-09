"""Repeat current main baseline/detectors with in-memory read overrides, no core writes."""
from pathlib import Path
from copy import deepcopy
import ast,json,yaml,sys
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research'
tree=ast.parse((R/'verify_research.py').read_text(encoding='utf8'))
body=[x for x in tree.body if not (isinstance(x,ast.Expr) and x.lineno>=300)]
# Explicitly omit report writing, printing and exiting; retain report construction/checks.
body=[x for x in tree.body if not (isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and
      (isinstance(x.value.func,ast.Attribute) and x.value.func.attr in ['write_text','exit'] or isinstance(x.value.func,ast.Name) and x.value.func.id=='print'))]
code=compile(ast.Module(body=body,type_ignores=[]),'current_main_read_only','exec')
original_read=Path.read_text
def execute(changed):
 def reader(p,*a,**kw):return changed[p.resolve()] if p.resolve() in changed else original_read(p,*a,**kw)
 Path.read_text=reader
 try:
  ns={'__file__':str(R/'verify_research.py'),'__name__':'read_only_import'};exec(code,ns);return ns['errors']
 finally:Path.read_text=original_read
baseline=execute({});rows=[]
for kind,expected in {'foreign_parameter':'foreign clinical parameter','unsupported_calendar':'incomplete RU switch returned a dose calendar',
 'hidden_question_count':'hidden/incorrect full question count','changed_anchor':'differs from manually reviewed source anchor','mixed_renal_units':'Mixed renal formula version/units'}.items():
 if kind in ['foreign_parameter','changed_anchor']:
  p=R/'rules/ser-panic-start.yaml';d=yaml.safe_load(p.read_text(encoding='utf8'))
  if kind=='changed_anchor':d['clinical_parameters'][0]['value']=999
  else:
   foreign=next(s for s in json.loads((R/'sources.json').read_text(encoding='utf8')).values() if s['jurisdiction'] not in ['RU','RU/EAEU'])
   d['clinical_parameters'][0]['source_ref']=foreign['source_id'];d['sources'].append(foreign)
 elif kind=='unsupported_calendar':
  p=R/'rules/switch-ser-esc.yaml';d=yaml.safe_load(p.read_text(encoding='utf8'));d['output']['schedule']=[{'day':1,'unsupported':True}]
 elif kind=='hidden_question_count':
  p=R/'remediation_round3/actual_question_paths.json';d=json.loads(p.read_text(encoding='utf8'));d[0]['count']-=1
 else:
  p=R/'renal_estimator.yaml';d=yaml.safe_load(p.read_text(encoding='utf8'));d['formula']='CLcr = (140 - age_years) * mass_kg / (72 * serum_creatinine_mg_dL)'
 changed={p.resolve():json.dumps(d,ensure_ascii=False) if p.suffix=='.json' else yaml.safe_dump(d,allow_unicode=True,sort_keys=False)}
 errors=execute(changed);matching=[x for x in errors if expected in x];rows.append(dict(mutation=kind,rejected=bool(matching),matching_errors=matching))
result=dict(baseline_errors=baseline,mutations=rows,all_rejected=all(x['rejected'] for x in rows),
 scope='Actually executed current main structural checks and finite five in-memory mutations; report-writing statements removed, no clinical evaluator or application.',core_modified=False)
(OUT/'main_detectors_repeat.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
