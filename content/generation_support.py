"""Shared evidence assembly; each content component owns its output."""
import sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
from contracts import *
def source_notes(brief):
 notes=[];seen=set()
 for c in brief['claims']:
  for e in c['evidence']:
   r=store_get(e['item_id'],e['version_id']);key=(c['claim_id'],e['item_id'],e['version_id'])
   if key in seen:continue
   seen.add(key);url=r['url'];loc=e['locator'];detail=''
   if loc['type']=='segment':
    seg=next(s for s in read_json(safe_path(r['segments_path'])) if s['segment_id']==loc['segment_id']);t=int(seg['start_seconds']);detail=f' ({t//60}:{t%60:02d})';url+=('&' if '?' in url else '?')+f't={t}' if r['kind']=='youtube' else f'#t={t}'
   notes.append(f'- [{c["claim_id"]}] [{r["title"]}{detail}]({url}) — {r["publisher_id"]}; published {r["published_at"]}; evidence version `{r["version_id"][:12]}`.')
 return '\n'.join(notes)
def generate(st,kind):
 bs=records();st.inputs=len(bs)
 validate_briefs(bs,read_lines(st.run/'eligible.jsonl'),read_lines(st.run/'decisions.jsonl'))
 dirname='articles' if kind=='articles' else 'video_scripts';prompt='write_'+dirname
 results=[]
 for b in bs:
  if os.environ.get('PIPELINE_PIECE_IDS') and b['piece_id'] not in os.environ['PIPELINE_PIECE_IDS'].split(','):continue
  keys={(e['item_id'],e['version_id']) for c in b['claims'] for e in c['evidence']};evidence=[]
  for key in sorted(keys):
   r=store_get(*key);payload_item=dict(r)
   if r['kind']=='feed':payload_item['text']=safe_path(r['text_path']).read_text()
   else:
    segments=read_json(safe_path(r['segments_path']));needed={e['locator']['segment_id'] for c in b['claims'] for e in c['evidence'] if (e['item_id'],e['version_id'])==key};positions={i for i,s in enumerate(segments) if s['segment_id'] in needed};context_positions={j for i in positions for j in range(max(0,i-2),min(len(segments),i+3))}
    payload_item['segments']=[s for i,s in enumerate(segments) if i in context_positions];payload_item['context_note']='Cited segments plus two neighboring cues. Full transcript is retained on disk. Do not infer beyond provided evidence.'
   evidence.append(payload_item)
  role={'01':'Explain what changed and why it matters. Leave detailed claim scrutiny to piece 02 and the implementation checklist to piece 03.','02':'Scrutinize claims and evidence tensions. Do not repeat the developments overview or write the practical checklist.','03':'Explain implications and practical questions to watch. Build on the evidence without repeating the first two articles.'}[b['piece_id']]
  payload={'brief':b,'evidence':evidence,'source_notes':source_notes(b),'piece_role':role,'body_word_target':700 if kind=='articles' else 550}
  def body_words(markdown):
   body=re.split(r'(?im)^#{1,4}\s+(?:references|sources|source notes?|video description)',markdown)[0]
   return len(re.findall(r"\b[\w’'-]+\b",body))
  lo,hi=(600,900) if kind=='articles' else (450,750)
  ids={c['claim_id'] for c in b['claims']}
  payload['required_claim_markers']=[f'[{i}]' for i in sorted(ids)]
  for attempt in range(3):
   replay=os.environ.get('PIPELINE_REPLAY_CONTENT_RESPONSE') if attempt==0 else None
   if replay:
    rp=safe_path(replay)
    if rp.parent.resolve()!=(st.run/'model_calls').resolve():raise Failure('Replay must belong to this run')
    req=read_json(rp.with_name(rp.name.replace('-response.json','-request.json')))
    if req['input']['data']['brief']!=b or req['instructions']!=((st.run/'prompts'/(prompt+'.md')).read_text()+'\n\n'+(st.run/'config/editorial_policy.md').read_text()):raise Failure('Replay does not match this brief and prompt')
    raw=read_json(rp);out=json.loads(next(c['text'] for x in raw['output'] if x['type']=='message' for c in x['content'] if c['type']=='output_text'))
   else:out=ai(st,prompt,payload,CONTENT)
   manual=os.environ.get('PIPELINE_CONTENT_EDIT')
   if manual:
    if not replay:raise Failure('An edited draft requires a matching saved response replay')
    mp=safe_path(manual)
    if not mp.resolve().is_relative_to((st.run/'editorial_edits').resolve()):raise Failure('Edited draft must be retained under this run editorial_edits')
    out['markdown']=mp.read_text()
    st.tools.append('retained_assistant_edit')
   out['markdown']=re.sub(r'(?im)^\*\*(References|Sources|Source notes|Video description):?\*\*:?\s*$',r'### \1',out['markdown'])
   count=body_words(out['markdown'])
   missing=[i for i in sorted(ids) if i not in out['claim_ids'] or f'[{i}]' not in out['markdown']]
   if lo<=count<=hi and not missing and set(out['claim_ids'])==ids:break
   direction='Cut repetition and secondary context. Do not expand or add facts.' if count>hi else 'Expand the explanation of the existing synthesis and limitations without adding unsupported facts.'
   payload.update(previous_draft=out['markdown'],revision_request=f'Rewrite this ONE piece to about {payload["body_word_target"]} words before references. Current measured body length: {count}. {direction} Include ALL required claim markers with their supported claims, including these missing markers: {missing}. Return the exact complete required claim_ids list. Keep the distinct role of this piece. The final permitted body range is {lo}–{hi} words.')
  else:raise Failure('Draft length or claim coverage remains invalid after two bounded revisions')
  ids={c['claim_id'] for c in b['claims']}
  if set(out['claim_ids'])!=ids or any(f'[{i}]' not in out['markdown'] for i in ids):raise Failure('Generated content dropped or changed claim IDs')
  date=read_json(st.run/'run.json')['as_of_date']
  if date not in out['markdown']:out['markdown']=f'*As of {date}*\n\n'+out['markdown']
  out['markdown']+='\n\n### Source notes\n\n'+source_notes(b)+'\n'
  p=st.run/dirname/(b['piece_id']+'.md');p.parent.mkdir(exist_ok=True);p.write_text(out['markdown'].strip()+'\n')
  result={'piece_id':b['piece_id'],'path':rel(p),'claim_ids':sorted(ids)}
  emit(result);st.outputs+=1
