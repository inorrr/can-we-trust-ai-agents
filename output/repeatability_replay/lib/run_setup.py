"""Entry-point metadata and snapshot preparation only."""
from common import *
import shutil

def main():
 cfg=read_json(ROOT/'config/project.json');sources=read_json(ROOT/'config/sources.json')
 for k in ['publication_name','topic','audience','central_question']:
  if not isinstance(cfg.get(k),str) or not cfg[k].strip():raise Invalid(f'Missing project {k}')
 if not isinstance(sources,list) or not sources:raise Invalid('Sources must be a nonempty array')
 for s in sources:
  if not all(isinstance(s.get(k),str) and s[k] for k in ['source_id','publisher_id','kind','url']) or s['kind'] not in ['feed','youtube','podcast']:raise Invalid('Malformed source definition')
 for p in ['config/editorial_policy.md','prompts/select_items.md','prompts/create_briefs.md','prompts/write_articles.md','prompts/write_video_scripts.md']:
  if not (ROOT/p).read_text().strip():raise Invalid(f'Empty required file: {p}')
 stamp=now();rid=stamp.replace('-','').replace(':','').split('.')[0]+'-'+uuid.uuid4().hex[:6];run=ROOT/'runs'/rid
 previous=sorted((ROOT/'runs').glob('*/run.json')) if (ROOT/'runs').exists() else []
 run.mkdir(parents=True)
 for d in ['config','prompts','logs','candidates']: (run/d).mkdir()
 for d in ['config','prompts']:
  for p in (ROOT/d).iterdir():
   if p.is_file() and p.suffix in ['.json','.md']:shutil.copyfile(p,run/d/p.name)
 save_json(run/'run.json',{'run_id':rid,'started_at':stamp,'as_of_date':stamp[:10],'mode':'live','previous_run_id':read_json(previous[-1])['run_id'] if previous else None})
 print(rel(run))
if __name__=='__main__':
 try:main()
 except Invalid as e:print(e,file=sys.stderr);sys.exit(2)
