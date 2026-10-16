import sys,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
def main(st):
 rows=records();st.inputs=len(rows);D=parse_date(read_json(st.run/'run.json')['as_of_date']);ex=[]
 for r in rows:
  validate_item(r);reason=None
  if r['published_at'] is None:reason='unknown_date'
  else:
   try:d=parse_date(r['published_at'])
   except ValueError:reason='invalid_date'
   else:
    if d>D:reason='future_date'
    elif d<D-dt.timedelta(days=29):reason='outside_window'
  if reason:ex.append({'item_id':r['item_id'],'version_id':r['version_id'],'reason':reason,'detail':f'Inclusive UTC window: {D-dt.timedelta(days=29)} through {D}'})
  else:emit(r);st.outputs+=1
 save_lines(st.run/'exclusions.jsonl',ex)
entry('filter_items',main)
