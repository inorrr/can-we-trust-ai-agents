import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
from contracts import *
def main(st):
 rows=records();st.inputs=len(rows)
 if not rows:raise Failure('No eligible evidence for editorial selection')
 cfg=read_json(st.run/'config/project.json')
 if len(rows)>cfg.get('max_editorial_items',36):raise Failure('Eligible set exceeds configured editorial batch limit; narrow sources explicitly')
 payload=[]
 for r in rows:
  x=evidence_payload(r)
  # Bounded context preserves exact excerpt text; full source remains on disk.
  if len(x['text'])>24000:x['text']=x['text'][:24000];x['text_truncated']=True
  if 'segments' in x and len(x['segments'])>300:x['segments']=x['segments'][:300];x['segments_truncated']=True
  payload.append(x)
 decision_fields={k:v for k,v in DECISION['properties'].items() if k not in ['item_id','version_id']}
 # Required keyed slots prevent a model from silently omitting a candidate or
 # changing a long evidence hash. Identity is attached from the input, not invented.
 keyed=obj_schema({r['item_id']:obj_schema(decision_fields) for r in rows})
 result=ai(st,'select_items',payload,obj_schema({'decisions':keyed}))['decisions']
 out=[dict(item_id=r['item_id'],version_id=r['version_id'],**result[r['item_id']]) for r in rows]
 expected={(r['item_id'],r['version_id']) for r in rows}
 if len(out)!=len(rows) or {(r['item_id'],r['version_id']) for r in out}!=expected:raise Failure('Editorial output must cover every eligible item exactly once')
 for r in out:
  if not r['reason'].strip():raise Failure('Decision lacks rationale')
  if (r['decision']=='accept')!=bool(r['piece_ids']):raise Failure('Decision has invalid piece assignment')
 for r in out:emit(r);st.outputs+=1
entry('select_items',main)
