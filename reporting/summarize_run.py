import sys,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from common import *
from contracts import coverage

def main(st):
 run=read_json(st.run/'run.json');logs=[read_json(p) for p in sorted((st.run/'logs').glob('*.json'))]
 latest={}
 for r in sorted(logs,key=lambda r:r['finished_at']):latest[r['stage']]=r
 def rows(name):return read_lines(st.run/name) if (st.run/name).exists() else None
 cs=rows('candidates.jsonl');items=rows('items.jsonl');changes=rows('changes.jsonl');eligible=rows('eligible.jsonl');ex=rows('exclusions.jsonl');ds=rows('decisions.jsonl');arts=rows('articles.jsonl');vids=rows('video_scripts.jsonl')
 counts={'discovered':len(cs) if cs is not None else None,'extracted':len(items) if items is not None else None,'eligible':len(eligible) if eligible is not None else None,'excluded':len(ex) if ex is not None else None,'articles':len(arts) if arts is not None else None,'video_scripts':len(vids) if vids is not None else None}
 for k in ['new','changed','unchanged']:counts[k]=sum(r['change']==k for r in changes) if changes is not None else None
 for k,label in [('accepted','accept'),('rejected','reject'),('deferred','defer')]:counts[k]=sum(r['decision']==label for r in ds) if ds is not None else None
 failed=[{'stage':k,'status':r['status'],'errors':r['errors']} for k,r in latest.items() if r['status']!='completed' and k not in ['summarize_run','store_get','run','collect_sources','create_series']]
 expected=['fetch_feeds','fetch_youtube','fetch_podcasts','extract_content','store_upsert','filter_items','select_items','create_briefs','write_articles','write_video_scripts','check_content']
 missing=[k for k in expected if k not in latest];review=read_json(st.run/'review.json') if (st.run/'review.json').exists() else None
 status='failed'
 if not failed and not missing and review and review['passed'] and counts['articles']==3 and counts['video_scripts']==3:status='awaiting_review'
 package=st.run/'package/manifest.json'
 if status=='awaiting_review' and package.exists() and latest.get('prepare_package',{}).get('status')=='completed':
  approval=read_json(st.run/'approval.json') if (st.run/'approval.json').exists() else {}
  if read_json(package).get('review_id')==review['review_id']==approval.get('review_id') and approval.get('decision')=='approve':status='ready_for_production'
 calls=[c for r in logs for c in r.get('model_calls',[])];known=[c['cost_usd'] for c in calls if c.get('cost_usd') is not None]
 actions=['Student editorial review and approval','Second live run on a different UTC date','Policy revision and comparison of at least 3 accepted + 3 rejected/deferred items','Google Vids/HeyGen video production','Substack and YouTube publication','Technical demonstration and final submission']
 if status=='ready_for_production':actions=read_json(package)['remaining_manual_actions']
 progress=read_json(ROOT/'docs/PROJECT_STATUS.json') if (ROOT/'docs/PROJECT_STATUS.json').exists() else {}
 if progress.get('remaining_manual_actions') is not None:actions=progress['remaining_manual_actions']
 summary={'run_id':run['run_id'],'status':status,'mode':run['mode'],'as_of_date':run['as_of_date'],'counts':counts,'source_coverage':coverage(eligible or []),'duplicate_observations':len(cs)-len({r['item_id'] for r in cs}) if cs is not None else None,'failed_or_incomplete_stages':failed,'stages_not_run':missing,'elapsed_seconds':(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(run['started_at'].replace('Z','+00:00'))).total_seconds(),'tools':sorted({t for r in logs for t in r.get('tools',[])}),'models':sorted({c['model'] for c in calls}),'known_or_estimated_cost_usd':sum(known) if known else (0 if not calls else None),'unknown_cost_calls':sum(c.get('cost_usd') is None for c in calls),'remaining_manual_actions':actions,'publication_links':read_json(st.run/'package/publication_links.json') if (st.run/'package/publication_links.json').exists() else (read_json(ROOT/'docs/publication_links.json') if (ROOT/'docs/publication_links.json').exists() else None),'workflow_attempts':{k:{'status':r['status'],'finished_at':r['finished_at'],'errors':r['errors']} for k,r in latest.items() if k in ['run','collect_sources','create_series']},'expected_lookup_misses':sum(r['stage']=='store_get' and r['status']=='failed' for r in logs),'historical_failures':sum(r['status']!='completed' and r['stage'] not in ['store_get'] for r in logs),'coverage_note':'Counts describe retained eligible evidence, not independent corroboration of every claim. Source independence and substantive dates require student review.'}
 emit(summary);st.inputs=len(logs);st.outputs=1
entry('summarize_run',main)
