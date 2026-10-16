"""The evidence store owns all direct index access."""
import sys,sqlite3,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
def main():
 args=sys.argv[1:];st=None;code=0
 try:
  if not args or args[0] not in ['init','upsert','list','get']:raise Invalid('Usage: store.sh init|upsert RUN_DIR|list|get ITEM_ID [VERSION_ID]')
  cmd=args[0]
  if (cmd in ['init','list'] and len(args)!=1) or (cmd=='upsert' and len(args)!=2) or (cmd=='get' and len(args) not in [2,3]):raise Invalid('Invalid store arguments')
  if cmd=='upsert':st=Stage(run_dir(args[1]),'store_upsert')
  elif os.getenv('PIPELINE_RUN_DIR'):st=Stage(run_dir(os.environ['PIPELINE_RUN_DIR']),'store_'+cmd)
  rows=records() if cmd=='upsert' else []
  for r in rows:validate_item(r)
  base=ROOT/'data/evidence';base.mkdir(parents=True,exist_ok=True)
  db=sqlite3.connect(base/'index.sqlite3',timeout=30)
  db.executescript('CREATE TABLE IF NOT EXISTS versions(item_id TEXT,version_id TEXT,record TEXT,first_run TEXT,PRIMARY KEY(item_id,version_id)); CREATE TABLE IF NOT EXISTS latest(item_id TEXT PRIMARY KEY,version_id TEXT); CREATE TABLE IF NOT EXISTS observations(item_id TEXT,version_id TEXT,run_id TEXT,retrieved_at TEXT,UNIQUE(item_id,version_id,run_id));')
  if cmd=='upsert':
   st.inputs=len(rows)
   with db:
    for r in rows:
     previous=db.execute('SELECT version_id FROM latest WHERE item_id=?',(r['item_id'],)).fetchone()
     exists=db.execute('SELECT 1 FROM versions WHERE item_id=? AND version_id=?',(r['item_id'],r['version_id'])).fetchone()
     change='new' if not previous else ('unchanged' if previous[0]==r['version_id'] else 'changed')
     rid=read_json(st.run/'run.json')['run_id']
     db.execute('INSERT OR IGNORE INTO versions VALUES(?,?,?,?)',(r['item_id'],r['version_id'],json.dumps(r),rid))
     db.execute('INSERT OR REPLACE INTO latest VALUES(?,?)',(r['item_id'],r['version_id']))
     db.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?,?)',(r['item_id'],r['version_id'],rid,r['retrieved_at']))
     emit({'item_id':r['item_id'],'version_id':r['version_id'],'change':change});st.outputs+=1
  elif cmd=='list':
   for (s,) in db.execute('SELECT v.record FROM versions v JOIN latest l USING(item_id,version_id) ORDER BY item_id'):
    print(s)
    if st:st.outputs+=1
  elif cmd=='get':
   if len(args)==3:r=db.execute('SELECT record FROM versions WHERE item_id=? AND version_id=?',(args[1],args[2])).fetchone()
   else:r=db.execute('SELECT v.record FROM versions v JOIN latest l USING(item_id,version_id) WHERE item_id=?',(args[1],)).fetchone()
   if not r:raise Failure('Requested evidence version is absent')
   print(r[0])
   if st:st.outputs=1
  db.close()
 except Invalid as e:code=2;print(e,file=sys.stderr)
 except Failure as e:code=1;print(e,file=sys.stderr)
 except Exception:code=1;print('Evidence storage failed',file=sys.stderr)
 finally:
  if st:st.receipt(code)
 return code
if __name__=='__main__':sys.exit(main())
