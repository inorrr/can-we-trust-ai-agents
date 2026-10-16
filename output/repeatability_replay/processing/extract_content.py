"""Retain substantive written sources or media plus timestamped transcripts."""
import sys,os,re,html,subprocess,tempfile,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'collectors'))
from common import *
from feed_support import fetch,page_metadata
import requests,trafilatura,yt_dlp

def download(url,target):
 target.parent.mkdir(parents=True,exist_ok=True)
 tmp=target.with_suffix(target.suffix+'.part');size=0
 try:
  with requests.get(url,stream=True,timeout=40,headers={'User-Agent':'AgentTrustCheckCourseProject/1.0'}) as r:
   r.raise_for_status()
   with tmp.open('wb') as f:
    for chunk in r.iter_content(1024*256):
     size+=len(chunk)
     if size>200*1024*1024:raise Failure('Media exceeds 200 MB limit')
     f.write(chunk)
  tmp.replace(target)
 finally:tmp.unlink(missing_ok=True)
 return target

def caption_segments(data,ext):
 out=[]
 if ext=='json3':
  for e in data.get('events',[]):
   t=''.join(x.get('utf8','') for x in e.get('segs',[])).strip()
   if t:out.append({'start_seconds':e.get('tStartMs',0)/1000,'end_seconds':(e.get('tStartMs',0)+e.get('dDurationMs',0))/1000,'text':t})
 else:
  # Standard WebVTT/SRT cues; exact cue times are retained.
  def seconds(s):
   nums=[float(x) for x in s.replace(',','.').split(':')]
   return sum(v*60**i for i,v in enumerate(reversed(nums)))
  for block in re.split(r'\n\s*\n',data):
   lines=block.strip().splitlines()
   for i,line in enumerate(lines):
    m=re.match(r'([\d:.,]+)\s+-->\s+([\d:.,]+)',line)
    if m:
     t=html.unescape(re.sub('<[^>]+>','', ' '.join(lines[i+1:]))).strip()
     if t:out.append({'start_seconds':seconds(m[1]),'end_seconds':seconds(m[2]),'text':t})
     break
 return [dict(segment_id=f's{i:05d}',**r) for i,r in enumerate(out,1)]

def transcribe(st,media,cfg):
 if not cfg.get('allow_paid_transcription'):raise Failure('No accessible timestamped transcript; paid transcription is disabled')
 from dotenv import load_dotenv
 from openai import OpenAI
 import imageio_ffmpeg
 load_dotenv(ROOT/'.env.local');client=OpenAI(timeout=180,max_retries=0)
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=[];offset=0
 # Re-encode at 48 kbps; 10 minute chunks stay under provider file limits.
 with tempfile.TemporaryDirectory() as td:
  result=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(media),'-vn','-ar','16000','-ac','1','-c:a','libmp3lame','-b:a','48k','-f','segment','-segment_time','600',str(Path(td)/'part%03d.mp3')],capture_output=True)
  if result.returncode:raise Failure('Audio conversion failed')
  for i,p in enumerate(sorted(Path(td).glob('part*.mp3'))):
   cache=ROOT/'data/assets/transcription_cache'/hashlib.sha256(media.read_bytes()).hexdigest()/f'{cfg.get("transcription_model","whisper-1")}-part-{i:03d}.json'
   if cache.exists():
    raw=read_json(cache)
   else:
    reservation=reserve_cost(st,0.061,cfg.get('transcription_model','whisper-1'))
    try:
     with p.open('rb') as f:r=client.audio.transcriptions.create(model=cfg.get('transcription_model','whisper-1'),file=f,response_format='verbose_json',timestamp_granularities=['segment'])
    except Exception as e:
     settle_cost(st,reservation,None)
     st.calls.append({'model':cfg.get('transcription_model','whisper-1'),'cost_usd':None,'status':'failed','error_type':type(e).__name__})
     raise Failure(f'Transcription failed ({type(e).__name__}); no automatic retry') from None
    raw=r.model_dump();save_json(cache,raw)
    duration=raw.get('duration');cost=duration/60*0.006 if duration is not None else None;settle_cost(st,reservation,cost);st.calls.append({'model':cfg.get('transcription_model','whisper-1'),'cost_usd':cost,'audio_seconds':duration,'status':'completed'})
   save_json(st.run/'transcriptions'/digest(rel(media))[:20]/f'part-{i:03d}-{uuid.uuid4().hex[:8]}.json',raw)
   for s in raw.get('segments',[]):
    if not s['text'].strip():continue
    out.append({'segment_id':f's{len(out)+1:05d}','start_seconds':i*600+s['start'],'end_seconds':i*600+s['end'],'text':s['text'].strip()})
 return out

def main(st):
 cfg=read_json(st.run/'config/project.json');rows=records();st.inputs=len(rows);st.tools=['requests','trafilatura','yt-dlp'];seen=set();D=parse_date(read_json(st.run/'run.json')['as_of_date'])
 for c in rows:
  validate_candidate(c)
  if c['item_id'] in seen:continue
  seen.add(c['item_id'])
  try:
   old=None
   try:old=store_get(c['item_id'])
   except Failure:pass
   # Stable media identity + publication metadata allows replay reuse. Force refresh
   # can detect publisher edits to transcripts; written pages are re-fetched each run.
   if old and c['kind']!='feed' and not os.getenv('PIPELINE_REFRESH_MEDIA') and all(c.get(k)==old.get(k) for k in ['title','url','published_at','media_url']):
    row=dict(old,retrieved_at=c['retrieved_at']);emit(row);st.outputs+=1;continue
   segments=None;media=None;provenance={}
   if c['kind']=='feed':
    meta,raw=page_metadata(c['url'])
    text=trafilatura.extract(raw,include_comments=False,include_tables=True,deduplicate=True)
    if not text or len(text.split())<100:raise Failure('Source has fewer than 100 extracted words; not substantive')
    # Feed dates are preserved; page metadata is separately inspectable.
    if c['published_at'] is None:c['published_at']=meta['published_at']
    provenance={'page_published_at':meta['published_at'],'retrieval_url':meta['url']}
   if c['kind']=='youtube':
    class Quiet:
     def debug(self,*a):pass
     def warning(self,*a):pass
     def error(self,*a):pass
    folder=ROOT/'data/media'/digest(c['item_id'])[:20];folder.mkdir(parents=True,exist_ok=True)
    with yt_dlp.YoutubeDL({'quiet':True,'logger':Quiet(),'no_warnings':True,'format':'bestaudio[ext=m4a]/bestaudio','outtmpl':str(folder/'%(id)s.%(ext)s'),'socket_timeout':30,'retries':0,'noplaylist':True,'max_filesize':200*1024*1024}) as y:
     info=y.extract_info(c['url'],download=True);media=Path(y.prepare_filename(info))
    caps=info.get('subtitles',{}) or info.get('automatic_captions',{})
    choices=caps.get('en',[]) or caps.get('en-orig',[]) or next((v for k,v in caps.items() if k.startswith('en')),[])
    choice=next((x for x in choices if x.get('ext')=='json3'),None) or next((x for x in choices if x.get('ext')=='vtt'),None)
    if choice:
     try:
      r=fetch(choice['url']);segments=caption_segments(r.json() if choice['ext']=='json3' else r.text,choice['ext']);provenance={'transcript_method':'youtube_captions','automatic':not bool(info.get('subtitles'))}
     except requests.RequestException:segments=None
    if not segments:segments=transcribe(st,media,cfg);provenance={'transcript_method':'openai_transcription'}
    text='\n'.join(s['text'] for s in segments)
   elif c['kind']=='podcast':
    folder=ROOT/'data/media'/digest(c['item_id'])[:20];media=folder/'episode.mp3'
    if not media.exists():download(c['media_url'],media)
    if c.get('transcript_url'):
     r=fetch(c['transcript_url']);segments=caption_segments(r.text,'vtt');provenance={'transcript_method':'publisher_transcript','transcript_url':c['transcript_url']}
    if not segments:segments=transcribe(st,media,cfg);provenance={'transcript_method':'openai_transcription'}
    text='\n'.join(s['text'] for s in segments)
   if not text or len(text.split())<100:raise Failure('Substantive transcript unavailable')
   version=digest({'title':c['title'],'url':c['url'],'published_at':c['published_at'],'text':text,'segments':segments,'publisher_id':c['publisher_id'],'kind':c['kind']})
   base=ROOT/'data/assets'/digest(c['item_id'])[:20]/version
   base.mkdir(parents=True,exist_ok=True)
   tp=base/'text.txt';sp=base/'segments.json'
   if not tp.exists():tp.write_text(text+'\n')
   if segments and not sp.exists():save_json(sp,segments)
   # Keep a bounded excerpt of raw written HTML only locally, not in logs.
   if c['kind']=='feed' and not (base/'source.html').exists():(base/'source.html').write_text(raw)
   row={k:v for k,v in c.items() if k not in ['subtitles','automatic_captions']}
   row.update(version_id=version,text_path=rel(tp),segments_path=rel(sp) if segments else None,media_path=rel(media) if media else None,extraction=provenance)
   validate_item(row);emit(row);st.outputs+=1
  except Exception as e:st.error(f'{c["item_id"]}: extraction incomplete: {str(e) if isinstance(e,Failure) else type(e).__name__}')
entry('extract_content',main)
