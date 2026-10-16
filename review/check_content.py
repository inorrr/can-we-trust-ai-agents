"""Mechanical review with a fingerprint; final editorial judgment stays human."""
import sys,re,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
from contracts import *
def assess(run):
 issues=[];fingerprint={'run':read_json(run/'run.json'),'artifacts':{},'evidence':[]};bs=[];items=[]
 def issue(artifact,message,severity='error'):issues.append({'artifact':artifact,'severity':severity,'explanation':message})
 for filename in ['briefs.jsonl','articles.jsonl','video_scripts.jsonl','eligible.jsonl','decisions.jsonl']:
  p=run/filename
  if not p.is_file():issue(filename,'Required artifact is absent');continue
  fingerprint['artifacts'][filename]=p.read_text()
  try:rows=read_lines(p)
  except Invalid:issue(filename,'Malformed JSONL');continue
  if filename=='briefs.jsonl':bs=rows
  if filename=='eligible.jsonl':items=rows
 try:require_coverage(items)
 except Failure as e:issue('eligible.jsonl',str(e))
 D=parse_date(read_json(run/'run.json')['as_of_date'])
 for r in items:
  try:
   d=parse_date(r['published_at'])
   if not D-dt.timedelta(days=29)<=d<=D:issue(r['item_id'],'Evidence outside run freshness window')
  except (ValueError,TypeError,KeyError):issue(r.get('item_id','evidence'),'Unverified evidence publication date')
 try:validate_briefs(bs,items,read_lines(run/'decisions.jsonl'))
 except (Failure,Invalid,KeyError,OSError) as e:issue('briefs.jsonl',str(e))
 # Compare references against immutable store records and content bytes.
 keys={(e['item_id'],e['version_id']) for b in bs for c in b.get('claims',[]) for e in c.get('evidence',[])}
 for key in sorted(keys):
  try:
   r=store_get(*key);fp={'item':r,'text':safe_path(r['text_path']).read_text()}
   if r['segments_path']:
    segs=read_json(safe_path(r['segments_path']));fp['segments']=segs
    substantive=[s for s in segs if s.get('text','').strip()]
    blank=[s for s in segs if not s.get('text','').strip()]
    cited={e['locator'].get('segment_id') for b in bs for c in b['claims'] for e in c['evidence'] if (e['item_id'],e['version_id'])==key}
    if blank:issue(r['item_id'],f'{len(blank)} empty transcript cue(s) retained; no empty cue may support a claim.','warning')
    if any(s['segment_id'] in cited for s in blank):issue(r['item_id'],'A cited transcript cue is empty')
    if not substantive or any(not isinstance(s.get('start_seconds'),(int,float)) or not isinstance(s.get('end_seconds'),(int,float)) or s['end_seconds']<s['start_seconds'] for s in segs):issue(r['item_id'],'Invalid transcript segment data')
   fingerprint['evidence'].append(fp)
  except (Failure,Invalid,OSError,KeyError):issue(str(key),'Stored evidence or retained assets cannot be resolved')
 for dirname in ['articles','video_scripts']:
  p=run/(dirname+'.jsonl')
  if not p.exists():continue
  manifests=read_lines(p)
  if len(manifests)!=3 or {r.get('piece_id') for r in manifests}!={'01','02','03'}:issue(p.name,'Exactly three manifest records required')
  for m in manifests:
   try:
    file=safe_path(m['path'])
    if file.resolve()!=(run/dirname/(m['piece_id']+'.md')).resolve():raise Invalid('Unexpected draft path')
    text=file.read_text();fingerprint['artifacts'][rel(file)]=text
    b=next(b for b in bs if b['piece_id']==m['piece_id']);ids={c['claim_id'] for c in b['claims']}
    found=set(re.findall(r'\[(\d{2}-c\w+)\]',text))
    if set(m['claim_ids'])!=ids or found!=ids:issue(m['path'],'Claim markers differ from brief or manifest')
    if str(D) not in text:issue(m['path'],'As-of date missing')
    if not re.search(r'\]\(https?://',text):issue(m['path'],'Readable source links missing')
    body=re.split(r'(?im)^#{1,4}\s+(?:references|sources|source notes?|video description)',text)[0]
    words=len(re.findall(r"\b[\w’'-]+\b",body));lo,hi=(600,900) if dirname=='articles' else (450,750)
    if not lo<=words<=hi:issue(m['path'],f'Approximate length {words} words; target {lo}–{hi}', 'warning')
   except (OSError,Invalid,StopIteration,KeyError):issue(m.get('path',p.name),'Draft, manifest or corresponding brief cannot be resolved')
 issue('series','Student must verify interpretation, source independence, original synthesis, factual consistency, dates, and transcript accuracy. Shared claim IDs are only a mechanical consistency check.','warning')
 review_id=digest(fingerprint)
 return {'review_id':review_id,'passed':not any(i['severity']=='error' for i in issues),'issues':issues,'checked_at':now()}
def main(st):
 r=assess(st.run);st.inputs=5;st.outputs=1;emit(r)
if __name__=='__main__':entry('check_content',main)
