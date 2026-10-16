import sys,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
import yt_dlp
class Quiet:
 def debug(self,*a):pass
 def warning(self,*a):pass
 def error(self,*a):pass

def main(st):
 st.tools=['yt-dlp'];cfg=read_json(st.run/'config/project.json')
 for src in read_json(st.run/'config/sources.json'):
  if src['kind']!='youtube':continue
  st.inputs+=1
  try:
   with yt_dlp.YoutubeDL({'quiet':True,'no_warnings':True,'logger':Quiet(),'skip_download':True,'extract_flat':False,'playlistend':src.get('max_items',cfg.get('max_items_per_source',12)),'socket_timeout':25,'retries':0}) as y:
    info=y.extract_info(src['url'],download=False)
   for e in (info.get('entries') or [info]):
    if not e:continue
    published=None
    if e.get('release_timestamp') or e.get('timestamp'):published=dt.datetime.fromtimestamp(e.get('release_timestamp') or e['timestamp'],dt.timezone.utc).isoformat().replace('+00:00','Z')
    elif e.get('upload_date'):published=dt.datetime.strptime(e['upload_date'],'%Y%m%d').replace(tzinfo=dt.timezone.utc).isoformat().replace('+00:00','Z')
    row={'item_id':src.get('underlying_id','youtube:'+e['id']),'source_id':src['source_id'],'publisher_id':src['publisher_id'],'kind':'youtube','title':e['title'],'url':'https://www.youtube.com/watch?v='+e['id'],'published_at':published,'retrieved_at':now(),'media_url':None,'subtitles':e.get('subtitles',{}),'automatic_captions':e.get('automatic_captions',{}),'duration_seconds':e.get('duration'),'perspective':src.get('perspective'),'commercial_interest':src.get('commercial_interest')}
    emit(row);st.outputs+=1
  except Exception as e:st.error(f'{src["source_id"]}: YouTube collection failed ({type(e).__name__}); endpoint {src["url"]}')
entry('fetch_youtube',main)
