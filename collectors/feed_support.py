"""RSS/Atom parsing shared by written and podcast collectors."""
import sys,re,datetime as dt,email.utils
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
import requests,feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlsplit,urlunsplit,parse_qsl,urlencode

def fetch(url):
 r=requests.get(url,timeout=35,headers={'User-Agent':'AgentTrustCheckCourseProject/1.0'});r.raise_for_status();return r

def date_iso(raw):
 if not raw:return None
 try:
  try:d=dt.datetime.fromisoformat(raw.replace('Z','+00:00'))
  except ValueError:d=email.utils.parsedate_to_datetime(raw)
  if d.tzinfo is None:d=d.replace(tzinfo=dt.timezone.utc)
  return d.astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')
 except (ValueError,TypeError,OverflowError):return None

def canonical(url):
 p=urlsplit(url);q=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in ['fbclid','gclid']]);return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path,q,''))

def page_metadata(url):
 r=fetch(url);s=BeautifulSoup(r.text,'html.parser');date=None
 for key in ['article:published_time','datePublished','pubdate','date']:
  m=s.find('meta',attrs={'property':key}) or s.find('meta',attrs={'name':key})
  if m and date_iso(m.get('content')):date=date_iso(m['content']);break
 if not date:
  for el in s.find_all('script',type='application/ld+json'):
   try:
    data=json.loads(el.string or el.get_text())
    def walk(x):
     if isinstance(x,dict):
      if x.get('datePublished'):return x['datePublished']
      for v in x.values():
       t=walk(v)
       if t:return t
     if isinstance(x,list):
      for v in x:
       t=walk(v)
       if t:return t
    date=date_iso(walk(data))
    if date:break
   except ValueError:pass
 if not date:
  t=s.find('time',datetime=True)
  if t:date=date_iso(t['datetime'])
 if not date:
  # Date-only bylines scoped to publisher-specific article headers, not arbitrary
  # dates in body text, related-post cards, or copyright footers.
  host=urlsplit(url).netloc
  header=None
  if host.endswith('aisi.gov.uk') and s.find('h1'):header=s.find('h1').parent
  elif host.endswith('salt.security'):header=s.select_one('p.blog-date')
  elif host.endswith('withwillow.ai'):header=s.select_one('.resource_details .text-block-37')
  if header:
   match=re.search(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b',header.get_text(' ',strip=True))
   if match:
    from dateutil.parser import parse
    date=parse(match.group()).date().isoformat()
 title=s.find('h1') or s.title
 return {'title':title.get_text(' ',strip=True) if title else url,'published_at':date,'url':canonical(r.url)},r.text

def collect(st,kind):
 cfg=read_json(st.run/'config/project.json');sources=read_json(st.run/'config/sources.json');st.tools=['requests','feedparser']
 for src in sources:
  if src['kind']!=kind:continue
  st.inputs+=1
  try:
   if src.get('discovery')=='page':
    meta,_=page_metadata(src['url']);entries=[meta]
   else:
    r=fetch(src['url']);parsed=feedparser.parse(r.content)
    if not parsed.entries and parsed.bozo:raise Failure('Endpoint is not a readable feed')
    entries=parsed.entries
   produced=0
   for e in entries:
    title=e.get('title','');pattern=src.get('title_pattern')
    if pattern and not re.search(pattern,title,re.I):continue
    if src.get('titles') and title not in src['titles']:continue
    url=e.get('url') or e.get('link') or next((l.get('href') for l in e.get('links',[]) if l.get('rel')=='alternate' and l.get('href')),None) or src['url']
    media=None
    if kind=='podcast':
     media=next((l['href'] for l in e.get('links',[]) if l.get('rel')=='enclosure' and l.get('type','').startswith('audio')),None)
     if not media:continue
    if kind=='podcast' and url==src['url']:url=media
    identity=src.get('underlying_ids',{}).get(title) or ('podcast:'+digest(src['publisher_id']+':'+str(e.get('id',url)))[:24] if kind=='podcast' else 'web:'+digest(canonical(url))[:24])
    row={'item_id':identity,'source_id':src['source_id'],'publisher_id':src['publisher_id'],'kind':kind,'title':title,'url':canonical(url),'published_at':e.get('published_at') or date_iso(e.get('published')),'retrieved_at':now(),'media_url':media,'discovery_method':src.get('discovery','rss'),'discovery_url':src['url'],'perspective':src.get('perspective'),'commercial_interest':src.get('commercial_interest')}
    # Some feeds expose a publisher-supplied transcript URL.
    for key,values in e.items():
     if 'transcript' in key and isinstance(values,dict) and values.get('url'):row['transcript_url']=values['url']
    emit(row);st.outputs+=1;produced+=1
    if produced>=src.get('max_items',cfg.get('max_items_per_source',12)):break
  except Exception as e:
   st.error(f'{src["source_id"]}: collection failed ({type(e).__name__}); endpoint {src["url"]}')
