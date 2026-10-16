import sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'review'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'content'))
from common import *
# check_content's entry point is guarded so direct packaging can reassess.
from check_content import assess
from generation_support import source_notes

def main(st):
 if not (st.run/'review.json').is_file() or not (st.run/'approval.json').is_file():raise Failure('Passing review and student approval are required before packaging')
 fresh=assess(st.run);saved=read_json(st.run/'review.json');approval=read_json(st.run/'approval.json')
 if not fresh['passed'] or not saved.get('passed') or saved['review_id']!=fresh['review_id']:raise Failure('Current review is absent, failed, or stale')
 if approval.get('decision')!='approve' or approval.get('review_id')!=fresh['review_id']:raise Failure('Matching student approval is required')
 if not all(approval.get(k) for k in ['reviewer','reviewed_at']) or 'notes' not in approval:raise Invalid('Incomplete human approval record')
 folder=st.run/'package';folder.mkdir(exist_ok=True);assets=[]
 for dirname in ['articles','video_scripts']:
  for m in read_lines(st.run/(dirname+'.jsonl')):
   target=folder/dirname/(m['piece_id']+'.md');target.parent.mkdir(exist_ok=True);shutil.copyfile(safe_path(m['path']),target);assets.append({'piece_id':m['piece_id'],'kind':dirname,'path':rel(target)})
 for b in read_lines(st.run/'briefs.jsonl'):
  target=folder/f'{b["piece_id"]}-sources.md';target.write_text(source_notes(b)+'\n');assets.append({'piece_id':b['piece_id'],'kind':'source_notes','path':rel(target)})
 links=folder/'publication_links.json'
 if not links.exists():save_json(links,[{'piece_id':p,'substack_url':None,'youtube_url':None} for p in ['01','02','03']])
 actions=['Produce each audience video in Google Vids or HeyGen; verify 3–5 minutes and disclosures.','Publish three accessible Substack articles and public/unlisted YouTube videos.','Cross-link each article/video and add readable references to video descriptions.','Fill publication_links.json and test links without paid access.','Record the separate 4–6 minute technical demonstration.']
 if (ROOT/'docs/PROJECT_STATUS.json').exists():actions=read_json(ROOT/'docs/PROJECT_STATUS.json').get('remaining_manual_actions',actions)
 manifest={'run_id':read_json(st.run/'run.json')['run_id'],'review_id':fresh['review_id'],'assets':assets,'remaining_manual_actions':actions,'publication_links_path':rel(links)}
 save_json(folder/'manifest.json',manifest);emit(manifest);st.inputs=6;st.outputs=len(assets)
if __name__=='__main__':entry('prepare_package',main)
