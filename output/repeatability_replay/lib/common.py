"""Shared I/O, receipts, identifiers and model transport; no pipeline orchestration."""
import sys, os, json, hashlib, uuid, datetime as dt, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Invalid(ValueError): pass
class Failure(RuntimeError): pass
def now(): return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
def read_json(path):
 try:return json.loads(Path(path).read_text())
 except (ValueError, OSError) as e:raise Invalid(f'Cannot read JSON: {path}') from e
def save_json(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def records(stream=None):
 out=[]
 for n,line in enumerate(stream or sys.stdin,1):
  if not line.strip():continue
  try:r=json.loads(line)
  except ValueError as e:raise Invalid(f'Malformed JSONL at line {n}') from e
  if not isinstance(r,dict):raise Invalid(f'Expected object at line {n}')
  out.append(r)
 return out
def read_lines(path):
 with Path(path).open() as f:return records(f)
def emit(obj):print(json.dumps(obj,ensure_ascii=False),flush=True)
def save_lines(path,rows):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rel(path):return str(Path(path).resolve().relative_to(ROOT))
def safe_path(path):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT):raise Invalid('Path outside repository')
 return p
def run_dir(arg):
 p=safe_path(arg)
 if not (p/'run.json').is_file():raise Invalid('RUN_DIR must contain run.json')
 return p
def parse_date(value):
 if not isinstance(value,str):raise ValueError('Date must be string')
 d=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 if d.tzinfo is None:
  if len(value)!=10:raise ValueError('Timestamp lacks timezone')
  d=d.replace(tzinfo=dt.timezone.utc)
 return d.astimezone(dt.timezone.utc).date()
def store_get(item_id,version=None):
 cmd=['bash',str(ROOT/'data/store.sh'),'get',item_id]+([version] if version else [])
 p=subprocess.run(cmd,capture_output=True,text=True)
 if p.returncode:raise Failure(f'Evidence not in store: {item_id}')
 return json.loads(p.stdout)
def validate_candidate(r):
 for k in ['item_id','source_id','publisher_id','kind','title','url','retrieved_at']:
  if not isinstance(r.get(k),str) or not r[k]:raise Invalid(f'Invalid candidate field: {k}')
 if r['kind'] not in ['feed','youtube','podcast']:raise Invalid('Invalid kind')
 for k in ['published_at','media_url']:
  if k not in r or (r[k] is not None and not isinstance(r[k],str)):raise Invalid(f'Invalid {k}')
def validate_item(r):
 validate_candidate(r)
 for k in ['version_id','text_path']:
  if not isinstance(r.get(k),str) or not r[k]:raise Invalid(f'Missing {k}')
 if 'segments_path' not in r:raise Invalid('Missing segments_path')
 if r['kind']!='feed' and not isinstance(r['segments_path'],str):raise Invalid('Media requires segments_path')
 safe_path(r['text_path'])
 if r['segments_path']:safe_path(r['segments_path'])
class Stage:
 def __init__(self,run,name):
  self.run=Path(run) if run else None;self.name=name;self.started=now();self.inputs=0;self.outputs=0;self.errors=[];self.tools=[];self.calls=[]
 def error(self,message):self.errors.append(str(message));print(str(message),file=sys.stderr)
 def receipt(self,code):
  if self.run is None:return
  costs=[x.get('cost_usd') for x in self.calls]
  obj={'stage':self.name,'status':'completed' if code==0 else ('invalid' if code==2 else 'failed'),'input_count':self.inputs,'output_count':self.outputs,'started_at':self.started,'finished_at':now(),'tools':sorted(set(self.tools)),'models':sorted(set(x['model'] for x in self.calls)),'cost_usd':sum(costs) if all(c is not None for c in costs) else None,'cost_estimated':bool(self.calls),'model_calls':self.calls,'errors':self.errors}
  save_json(self.run/'logs'/f'{self.name}-{uuid.uuid4().hex}.json',obj)
def entry(name,fn):
 st=None;code=0
 try:
  if len(sys.argv)!=2:raise Invalid('Usage: component RUN_DIR')
  st=Stage(run_dir(sys.argv[1]),name);fn(st)
  if st.errors:code=1
 except Invalid as e:
  code=2
  if st:st.error(e)
  else:print(str(e),file=sys.stderr)
 except Exception as e:
  code=1
  # Avoid raw provider/network exceptions that might expose headers or credentials.
  msg=str(e) if isinstance(e,Failure) else f'{type(e).__name__}: stage failed; inspect source access or configuration'
  if st:st.error(msg)
  else:print(msg,file=sys.stderr)
 finally:
  if st:st.receipt(code)
 sys.exit(code)
def obj_schema(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
STR={'type':'string'}
def array(items):return {'type':'array','items':items}
def ai(st,prompt_name,payload,schema):
 from dotenv import load_dotenv
 from openai import OpenAI
 load_dotenv(ROOT/'.env.local')
 if not os.getenv('OPENAI_API_KEY'):raise Failure('OPENAI_API_KEY is missing')
 cfg=read_json(st.run/'config/project.json'); model=os.getenv('OPENAI_MODEL',cfg['model'])
 instructions=(st.run/'prompts'/f'{prompt_name}.md').read_text()+'\n\n'+(st.run/'config/editorial_policy.md').read_text()
 context={'project':cfg,'as_of_date':read_json(st.run/'run.json')['as_of_date'],'data':payload}
 callid=uuid.uuid4().hex
 save_json(st.run/'model_calls'/f'{callid}-request.json',{'model':model,'instructions':instructions,'input':context,'schema':schema})
 prices=cfg.get('model_prices_usd_per_million')
 if not prices or model!=cfg['model']:raise Failure('Model override requires matching snapshotted pricing before paid execution')
 upper=((len((instructions+json.dumps(context)+json.dumps(schema)).encode())+2000)*prices['input']+cfg.get('max_output_tokens',14000)*prices['output'])/1e6
 reservation=reserve_cost(st,upper,model)
 try:
  response=OpenAI(timeout=180,max_retries=0).responses.create(model=model,instructions=instructions,input=json.dumps(context,ensure_ascii=False),text={'format':{'type':'json_schema','name':prompt_name,'strict':True,'schema':schema}},max_output_tokens=cfg.get('max_output_tokens',14000),store=False)
 except Exception as e:
  settle_cost(st,reservation,None)
  st.calls.append({'model':model,'cost_usd':None,'status':'failed','error_type':type(e).__name__})
  raise Failure(f'OpenAI request failed ({type(e).__name__}); no automatic retry. Check billing/model access/network.') from None
 data=response.model_dump();save_json(st.run/'model_calls'/f'{callid}-response.json',data)
 usage=data.get('usage') or {};prices=cfg.get('model_prices_usd_per_million');cost=None
 if prices and model==cfg['model']:cost=(usage.get('input_tokens',0)*prices['input']+usage.get('output_tokens',0)*prices['output'])/1e6
 settle_cost(st,reservation,cost)
 st.calls.append({'model':model,'response_id':data.get('id'),'usage':usage,'cost_usd':cost,'status':data.get('status'),'request_path':rel(st.run/'model_calls'/f'{callid}-request.json')})
 if data.get('status')!='completed':raise Failure('OpenAI returned incomplete response')
 try:return json.loads(response.output_text)
 except ValueError:raise Failure('OpenAI returned no valid structured content') from None

def evidence_payload(item):
 r=dict(item);r['text']=safe_path(item['text_path']).read_text()
 if item.get('segments_path'):r['segments']=read_json(safe_path(item['segments_path']))
 return r

def reserve_cost(st,upper_bound,model):
 """Local per-run reservation; failed/unknown requests keep their reservation."""
 import fcntl
 cfg=read_json(st.run/'config/project.json');cap=cfg.get('max_run_cost_usd',1.0)
 p=st.run/'cost_ledger.json';lock=st.run/'cost_ledger.lock'
 with lock.open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  ledger=read_json(p) if p.exists() else {'limit_usd':cap,'entries':[]}
  if sum(e['reserved_or_estimated_usd'] for e in ledger['entries'])+upper_bound>cap:raise Failure('Configured run cost cap reached; no request sent')
  key=uuid.uuid4().hex;ledger['entries'].append({'id':key,'stage':st.name,'model':model,'reserved_or_estimated_usd':upper_bound,'cost_usd':None,'state':'reserved','at':now()});save_json(p,ledger)
 return key

def settle_cost(st,key,cost):
 import fcntl
 p=st.run/'cost_ledger.json'
 with (st.run/'cost_ledger.lock').open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX);ledger=read_json(p)
  e=next(e for e in ledger['entries'] if e['id']==key);e['cost_usd']=cost;e['state']='estimated' if cost is not None else 'unknown'
  if cost is not None:e['reserved_or_estimated_usd']=cost
  save_json(p,ledger)
