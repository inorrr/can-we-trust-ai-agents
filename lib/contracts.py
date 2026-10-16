from common import *
DECISION=obj_schema({'item_id':STR,'version_id':STR,'decision':{'type':'string','enum':['accept','reject','defer']},'reason':STR,'piece_ids':array({'type':'string','enum':['01','02','03']})})
LOCATOR={'anyOf':[obj_schema({'type':{'type':'string','enum':['text']},'quote':STR}),obj_schema({'type':{'type':'string','enum':['segment']},'segment_id':STR})]}
EVIDENCE=obj_schema({'item_id':STR,'version_id':STR,'locator':LOCATOR})
CLAIM=obj_schema({'claim_id':STR,'statement':STR,'type':{'type':'string','enum':['reported_fact','source_claim','inference']},'evidence':array(EVIDENCE)})
BRIEF=obj_schema({'piece_id':{'type':'string','enum':['01','02','03']},'title':STR,'question':STR,'argument':STR,'synthesis':STR,'limitations':STR,'claims':array(CLAIM)})
CONTENT=obj_schema({'markdown':STR,'claim_ids':array(STR)})
def validate_briefs(briefs,items,decisions=None):
 if len(briefs)!=3 or {b['piece_id'] for b in briefs}!={'01','02','03'}:raise Failure('Exactly three distinct pieces required')
 if len({b['argument'].strip().lower() for b in briefs})!=3:raise Failure('Brief arguments must differ')
 index={(r['item_id'],r['version_id']):r for r in items};allkinds=set();allids=set();used_claims=set()
 accepted={(r['item_id'],r['version_id']):r for r in decisions or [] if r['decision']=='accept'}
 for b in briefs:
  pubs=set();piece_items=set()
  if not b['claims']:raise Failure('Brief has no claims')
  for c in b['claims']:
   if c['claim_id'] in used_claims or not c['claim_id'].startswith(b['piece_id']+'-'):raise Failure('Duplicate or invalid claim ID')
   used_claims.add(c['claim_id'])
   if not c['evidence']:raise Failure('Claim lacks evidence')
   for e in c['evidence']:
    key=(e['item_id'],e['version_id'])
    if key not in index:raise Failure('Reference not in eligible evidence')
    if decisions is not None and key not in accepted:raise Failure('Brief uses material not accepted by selection')
    r=index[key];loc=e['locator'];pubs.add(r['publisher_id']);piece_items.add(r['item_id']);allkinds.add(r['kind']);allids.add(r['item_id'])
    if loc['type']=='text':
     if r['kind']!='feed' or not loc['quote'].strip() or loc['quote'] not in safe_path(r['text_path']).read_text():raise Failure('Written quote does not resolve verbatim')
    elif loc['type']=='segment':
     if r['kind']=='feed' or not r['segments_path']:raise Failure('Media locator requires transcript')
     segs=read_json(safe_path(r['segments_path']))
     if not any(s['segment_id']==loc['segment_id'] for s in segs):raise Failure('Transcript segment does not resolve')
    else:raise Failure('Invalid locator')
  if len(pubs)<3:raise Failure(f'Piece {b["piece_id"]} has fewer than three independent publishers')
 if allkinds!={'feed','youtube','podcast'}:raise Failure('Series must use all three evidence kinds')
 return allids

def coverage(rows):
 # Identity reconciliation is done at discovery. A repeated underlying_id counts once.
 unique={r['item_id']:r for r in rows};kinds={k:sum(r['kind']==k for r in unique.values()) for k in ['feed','youtube','podcast']}
 return {'distinct_items':len(unique),'by_kind':kinds,'independent_publishers':sorted({r['publisher_id'] for r in unique.values()}),'publishers_count':len({r['publisher_id'] for r in unique.values()}),'rss_written_items':sum(r['kind']=='feed' and r.get('discovery_method','rss')=='rss' for r in unique.values())}
def require_coverage(rows):
 c=coverage(rows)
 if c['distinct_items']<12 or c['publishers_count']<6 or any(v<2 for v in c['by_kind'].values()) or c['rss_written_items']<2:raise Failure('Insufficient eligible evidence: need 12 items, 6 independent publishers, 2 each kind including 2 substantive RSS-discovered written items')
 return c
