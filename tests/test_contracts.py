"""Offline contract checks in disposable copies; never ingest fixtures into live evidence."""
import unittest,tempfile,shutil,subprocess,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Contracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for d in ['lib','data','processing','review','publishing','content','examples']:
   shutil.copytree(ROOT/d,self.root/d,ignore=shutil.ignore_patterns('evidence','assets','media','__pycache__'))
  self.run=self.root/'runs/example';self.run.mkdir(parents=True)
  shutil.copyfile(self.root/'examples/run.json',self.run/'run.json')
  shutil.copyfile(ROOT/'run.sh',self.root/'run.sh')
  self.env=dict(os.environ,PIPELINE_PYTHON=sys.executable)
 def tearDown(self):self.tmp.cleanup()
 def call(self,script,*args,input=None):
  return subprocess.run(['bash',script,*args],cwd=self.root,env=self.env,input=input,text=True,capture_output=True)
 def rows(self,result):
  self.assertEqual(result.returncode,0,result.stderr)
  return [json.loads(s) for s in result.stdout.splitlines() if s.strip()]
 def test_store_replay_and_history(self):
  self.assertEqual(self.call('data/store.sh','init').returncode,0)
  initial=self.rows(self.call('data/store.sh','upsert','runs/example',input=(self.root/'examples/items.jsonl').read_text()))
  expected=[json.loads(s) for s in (self.root/'examples/initial_changes_expected.jsonl').read_text().splitlines()]
  self.assertEqual(initial,expected)
  replay=self.rows(self.call('data/store.sh','upsert','runs/example',input=(self.root/'examples/replay_items.jsonl').read_text()))
  expected=[json.loads(s) for s in (self.root/'examples/replay_changes_expected.jsonl').read_text().splitlines()]
  self.assertEqual(replay,expected);self.assertEqual(len(self.rows(self.call('data/store.sh','list'))),3)
  old=json.loads((self.root/'examples/items.jsonl').read_text().splitlines()[-1])
  self.assertEqual(self.rows(self.call('data/store.sh','get',old['item_id'],old['version_id']))[0]['version_id'],old['version_id'])
  self.assertEqual(self.call('data/store.sh','get','absent').returncode,1)
 def test_filter_boundaries_unknown_invalid_future(self):
  result=self.call('processing/filter_items.sh','runs/example',input=(self.root/'examples/filter_input.jsonl').read_text())
  eligible=self.rows(result);expected=json.loads((self.root/'examples/filter_expected.json').read_text())
  self.assertEqual(sorted(r['item_id'] for r in eligible),sorted(expected['eligible_item_ids']))
  actual={r['item_id']:r['reason'] for r in map(json.loads,(self.run/'exclusions.jsonl').read_text().splitlines())}
  self.assertEqual(actual,{r['item_id']:r['reason'] for r in expected['exclusions']})
 def test_malformed_input_is_invalid(self):
  self.assertEqual(self.call('data/store.sh','upsert','runs/example',input='{oops}\n').returncode,2)
  self.assertEqual(self.call('processing/filter_items.sh','runs/example',input='[]\n').returncode,2)
 def test_checks_report_missing_artifacts_and_package_blocks(self):
  review=self.rows(self.call('review/check_content.sh','runs/example'))[0]
  self.assertFalse(review['passed']);self.assertTrue(any(r['severity']=='error' for r in review['issues']))
  (self.run/'review.json').write_text(json.dumps(review))
  approval={'review_id':review['review_id'],'decision':'approve','reviewer':'fictional test','reviewed_at':'2026-10-08T00:00:00Z','notes':'test only'}
  (self.run/'approval.json').write_text(json.dumps(approval))
  self.assertNotEqual(self.call('publishing/prepare_package.sh','runs/example').returncode,0)
  self.assertFalse((self.run/'package').exists())
 def test_review_fingerprint_changes(self):
  p=self.run/'eligible.jsonl';p.write_text('')
  first=self.rows(self.call('review/check_content.sh','runs/example'))[0]
  p.write_text((self.root/'examples/items.jsonl').read_text())
  second=self.rows(self.call('review/check_content.sh','runs/example'))[0]
  self.assertNotEqual(first['review_id'],second['review_id'])
 def make_complete_fictional_run(self):
  rows=[]
  for i in range(12):
   kind=['feed','youtube','podcast'][i%3]
   folder=self.root/'examples'/'generated'/str(i);folder.mkdir(parents=True)
   text='Fictional evidence passage for isolated contract testing.'
   (folder/'text.txt').write_text(text)
   segments=[{'segment_id':'s00001','start_seconds':1.0,'end_seconds':3.0,'text':text}]
   (folder/'segments.json').write_text(json.dumps(segments))
   rows.append({'item_id':f'fictional:{i}','source_id':f'source:{i}','publisher_id':f'publisher:{i%6}','kind':kind,'title':f'Fictional source {i}','url':f'https://example.com/{i}','published_at':'2026-10-01T00:00:00Z','retrieved_at':'2026-10-08T00:00:00Z','media_url':None,'version_id':f'v{i}','text_path':f'examples/generated/{i}/text.txt','segments_path':None if kind=='feed' else f'examples/generated/{i}/segments.json'})
  def save(name,rs): (self.run/name).write_text(''.join(json.dumps(r)+'\n' for r in rs))
  save('eligible.jsonl',rows)
  decisions=[{'item_id':r['item_id'],'version_id':r['version_id'],'decision':'accept','reason':'Fictional test','piece_ids':['01','02','03']} for r in rows]
  save('decisions.jsonl',decisions)
  self.rows(self.call('data/store.sh','upsert','runs/example',input=''.join(json.dumps(r)+'\n' for r in rows)))
  briefs=[]
  for piece in ['01','02','03']:
   claims=[]
   for i,r in enumerate(rows[:3]):
    locator={'type':'text','quote':'Fictional evidence passage'} if r['kind']=='feed' else {'type':'segment','segment_id':'s00001'}
    claims.append({'claim_id':piece+f'-c{i+1}','statement':'Fictional statement','type':'source_claim','evidence':[{'item_id':r['item_id'],'version_id':r['version_id'],'locator':locator}]})
   briefs.append({'piece_id':piece,'title':'Fictional','question':'Test?','argument':'Different '+piece,'synthesis':'Fictional synthesis','limitations':'Fictional limitations','claims':claims})
  save('briefs.jsonl',briefs)
  for dirname in ['articles','video_scripts']:
   (self.run/dirname).mkdir()
   manifests=[]
   for b in briefs:
    path=self.run/dirname/(b['piece_id']+'.md')
    path.write_text('As of 2026-10-08. '+' '.join('['+c['claim_id']+']' for c in b['claims'])+' [Fictional reference](https://example.com/)')
    manifests.append({'piece_id':b['piece_id'],'path':str(path.relative_to(self.root)),'claim_ids':[c['claim_id'] for c in b['claims']]})
   save(dirname+'.jsonl',manifests)
  review=self.rows(self.call('review/check_content.sh','runs/example'))[0]
  self.assertTrue(review['passed'],review['issues'])
  (self.run/'review.json').write_text(json.dumps(review))
  (self.run/'approval.json').write_text(json.dumps({'review_id':review['review_id'],'decision':'approve','reviewer':'fictional student','reviewed_at':'2026-10-08T00:00:00Z','notes':'Fictional offline test approval'}))
 def test_packaging_requires_matching_unchanged_approval(self):
  self.make_complete_fictional_run()
  self.rows(self.call('publishing/prepare_package.sh','runs/example'))
  links=self.run/'package/publication_links.json';data=json.loads(links.read_text());data[0]['youtube_url']='https://example.com/test-video';links.write_text(json.dumps(data))
  self.rows(self.call('publishing/prepare_package.sh','runs/example'))
  self.assertEqual(json.loads(links.read_text())[0]['youtube_url'],'https://example.com/test-video')
  p=self.run/'articles/01.md';p.write_text(p.read_text()+' Changed after approval.')
  self.assertEqual(self.call('publishing/prepare_package.sh','runs/example').returncode,1)
 def test_returning_to_a_stored_version_is_a_change_without_duplicate_versions(self):
  initial=(self.root/'examples/items.jsonl').read_text()
  self.rows(self.call('data/store.sh','upsert','runs/example',input=initial))
  self.rows(self.call('data/store.sh','upsert','runs/example',input=(self.root/'examples/replay_items.jsonl').read_text()))
  original=json.loads(initial.splitlines()[-1])
  result=self.rows(self.call('data/store.sh','upsert','runs/example',input=json.dumps(original)+'\n'))
  self.assertEqual(result[0]['change'],'changed')
  self.assertEqual(len(self.rows(self.call('data/store.sh','list'))),3)
 def test_budget_reservations_block_excess_without_api_calls(self):
  (self.run/'config').mkdir();(self.run/'config/project.json').write_text(json.dumps({'max_run_cost_usd':0.1}))
  code="import sys;sys.path.insert(0,'lib');from common import *;s=Stage('runs/example','test');reserve_cost(s,0.06,'fictional');reserve_cost(s,0.06,'fictional')"
  result=subprocess.run([sys.executable,'-c',code],cwd=self.root,env=self.env,capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0)
  ledger=json.loads((self.run/'cost_ledger.json').read_text());self.assertEqual(len(ledger['entries']),1)
 def test_resume_refuses_old_dates_and_approved_drafts(self):
  p=self.run/'run.json';meta=json.loads(p.read_text());meta['as_of_date']='1900-01-01';p.write_text(json.dumps(meta))
  self.assertEqual(self.call('run.sh','--resume','runs/example').returncode,2)
  import datetime
  meta['as_of_date']=datetime.datetime.now(datetime.timezone.utc).date().isoformat();p.write_text(json.dumps(meta))
  (self.run/'approval.json').write_text(json.dumps({'decision':'approve'}))
  self.assertEqual(self.call('run.sh','--resume','runs/example').returncode,2)
if __name__=='__main__':unittest.main()
