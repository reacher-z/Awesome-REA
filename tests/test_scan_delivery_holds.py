"""Administrative holds and real backoff apply at every candidate delivery gate."""
import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import scan_sources as scanner
import search_frontier as frontier
import scheduled_source_scan as scheduled
from validate import validate_scan_discovery

BASE='topic:reverse-engineering'
ALT='topic:decompiler'
QUERY=BASE+' is:public fork:false archived:false'
STAMP='2026-10-19T00:00:00Z'
INSTANT=frontier.utc_seconds(STAMP)
BODY=b'# Public fixture\n'
OID=hashlib.sha1(b'blob '+str(len(BODY)).encode()+b'\0'+BODY).hexdigest()


def repo(number):
    name=f'example/project-{number}'
    return {'id':number,'node_id':f'R_fixture_{number}','full_name':name,'html_url':'https://github.com/'+name,
            'private':False,'fork':False,'archived':False,'created_at':'2026-01-01T00:00:00Z',
            '_metadata_observed_at':STAMP,'description':'Public reconstruction fixture','topics':[],
            'stargazers_count':0}


def arguments(output,**changes):
    return SimpleNamespace(**{'target':1,'workers':1,'requests_per_second':1,'max_pages':1,'candidate_buffer':0,
        'seed_curated':False,'seed_papers':False,'queries':[],'output':output,'hold_repository_ids':[],**changes})


def pending_snapshot(ids):
    return {'meta':{'schema_version':1,'status':'complete','queries':[],'successful_readme_scans':0,'failed':0,
        'attempted_readme_scans':0,'unique_repos':len(ids),'unattempted_candidates':len(ids),
        'requested_successful_scans':0,'discovered_repository_ids':[f'scan-{i}' for i in ids]},'resources':[],'failures':[]}


def saved_frontier(ids,*,defer=(),open_search=False):
    state=frontier.new_frontier(until=STAMP,approved_queries=[BASE])
    frontier.record_response(state,frontier.next_request(state),{'items':[repo(i) for i in ids],
        'total_count':len(ids),'incomplete_results':False},observed_at=STAMP,run_id=STAMP)
    if defer:frontier.defer_candidates(state,defer,reason='retry',retry_after_seconds=60,observed_at=STAMP)
    if open_search:frontier.add_queries(state,[ALT],approved_queries=[BASE,ALT])
    return state


class API:
    def __init__(self,items=(),identity=None,readme_status=None):
        self.items=list(items);self.calls=[];self.identity=identity or {};self.readme_status=readme_status
    def json(self,path,search=False):
        self.calls.append((path,search))
        if search:return {'items':[repo(i) for i in self.items],'total_count':len(self.items),'incomplete_results':False}
        if path.startswith('/repositories/'):
            number=int(path.rsplit('/',1)[-1]); value=self.identity.get(number,repo(number))
            if isinstance(value,Exception):raise value
            return value
        if path.startswith('/repos/example/project-') and path.endswith('/readme'):
            if self.readme_status:raise scanner.ScanError('http-'+str(self.readme_status),self.readme_status)
            number=int(path.split('project-')[1].split('/')[0]);r=repo(number)
            return {'type':'file','path':'README.md','size':len(BODY),'sha':OID,'encoding':'base64',
                    'content':base64.b64encode(BODY).decode(),'html_url':r['html_url']+'/blob/main/README.md'}
        if path.startswith('/repos/example/project-'):
            return repo(int(path.split('project-')[1]))
        raise AssertionError('Unexpected request')


class Transport:
    batch_size=2
    def __init__(self,status='ok',callback=None):self.ids=[];self.status=status;self.callback=callback
    def fetch_batch(self,rows):
        self.ids.extend(r['id'] for r in rows)
        if self.callback:self.callback(rows)
        return {r['id']:{'status':self.status,'repository':{**repo(r['id']),**r},'content':BODY,
            'metadata':{'path':'README.md','size':len(BODY),'sha':OID,'commit_oid':'a'*40,
                        'html_url':r['html_url']+'/blob/'+'a'*40+'/README.md'}} for r in rows}


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        cache=ROOT/'.cache';cache.mkdir(exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(dir=cache);self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.index=0
    def scan(self,api,args=None,*,resumed=None,state=None,transport=None,instant=INSTANT):
        self.index+=1;output=self.root/f'scan-{self.index}.json';args=args or arguments(output);args.output=output
        cursor=self.root/f'frontier-{self.index}.json'
        with contextlib.redirect_stdout(io.StringIO()),patch.object(frontier,'current_seconds',return_value=instant):
            code=scanner.run_scan(api,args,resumed,'a'*64 if resumed else None,readme_transport=transport,
                frontier=(state,cursor,[BASE,ALT]) if state is not None else None)
        return code,json.loads(output.read_text()),json.loads(cursor.read_text()) if cursor.exists() else None
    def assert_pending_only(self,document,ids):
        self.assertEqual(document['resources'],[]);self.assertEqual(document['failures'],[])
        self.assertEqual(document['meta']['attempted_readme_scans'],0)
        self.assertEqual(document['meta']['unattempted_candidates'],len(ids))
        self.assertEqual(set(document['meta']['discovered_repository_ids']),{f'scan-{i}' for i in ids})
        self.assertEqual(document['meta']['status'],'in-progress')

    def test_unseen_hold_is_policy_only_without_discovery_pending_or_read_counts(self):
        api=API();code,doc,_=self.scan(api,arguments(None,hold_repository_ids=['42']))
        self.assertEqual(code,1);self.assertEqual(api.calls,[])
        self.assertEqual(doc['resources'],[]);self.assertEqual(doc['failures'],[])
        self.assertEqual(doc['meta']['discovered_repository_ids'],[])
        for key in ('unique_repos','unattempted_candidates','attempted_readme_scans'):
            self.assertEqual(doc['meta'][key],0)
        self.assertEqual(doc['meta']['status'],'complete')
        self.assertEqual(doc['meta']['current_run']['held_repository_ids'],['scan-42'])
        self.assertEqual(doc['meta']['current_run']['query_count'],0)

    def test_fresh_search_holds_block_rest_and_graphql_delivery(self):
        for graphql in (False,True):
            with self.subTest(graphql=graphql):
                api=API([42]);transport=Transport() if graphql else None
                _,doc,_=self.scan(api,arguments(None,queries=[QUERY],hold_repository_ids=['42']),transport=transport)
                self.assert_pending_only(doc,[42]);self.assertEqual(len(api.calls),1)
                self.assertEqual(doc['meta']['queries'][0]['held_candidates_skipped'],1)
                if transport:self.assertEqual(transport.ids,[])

    def test_legacy_lookup_skips_held_id_before_budget_and_releases_only_next_explicit_run(self):
        api=API();transport=Transport()
        args=arguments(None,hold_repository_ids=['42'],pending_metadata_budget=1)
        _,doc,_=self.scan(api,args,resumed=pending_snapshot([42,43]),transport=transport)
        self.assertEqual(api.calls,[('/repositories/43',False)]);self.assertEqual(transport.ids,[43])
        self.assertEqual(doc['meta']['unattempted_candidates'],1)
        self.assertEqual(doc['meta']['current_run']['resume_observation_count'],1)
        released=Transport();api2=API()
        _,next_doc,_=self.scan(api2,arguments(None,target=2),resumed=doc,transport=released)
        self.assertEqual(released.ids,[42]);self.assertEqual(api2.calls,[('/repositories/42',False)])
        self.assertEqual(next_doc['meta']['current_run']['held_repository_ids'],[])
        self.assertEqual(next_doc['meta']['resume_history'][-1]['run']['held_repository_ids'],['scan-42'])

    def test_saved_frontier_hold_never_invents_backoff_or_ack(self):
        state=saved_frontier([42,43]);before=copy.deepcopy(state['candidates']['42']);transport=Transport();api=API()
        _,doc,after=self.scan(api,arguments(None,hold_repository_ids=['42']),state=state,transport=transport)
        self.assertEqual(transport.ids,[43]);self.assertEqual(api.calls,[])
        self.assertEqual(after['candidates']['42'],before);self.assertEqual(doc['meta']['unattempted_candidates'],1)

    def test_fresh_search_cannot_bypass_frontier_deferral(self):
        state=saved_frontier([42],defer=[42],open_search=True);before=copy.deepcopy(state['candidates']['42'])
        api=API([42,43]);transport=Transport()
        _,doc,after=self.scan(api,state=state,transport=transport,instant=INSTANT+1)
        self.assertEqual(transport.ids,[43]);self.assertEqual(len(api.calls),1)
        self.assertEqual(doc['meta']['queries'][-1]['deferred_candidates_skipped'],1)
        for key in ['last_attempt_at','next_attempt_at','attempts','defer_reason','checkpoint_sha256']:
            self.assertEqual(after['candidates']['42'][key],before[key])

    def test_curated_and_paper_seed_metadata_reports_hold_without_readme_attempt(self):
        curated={'example/project-42':{'ids':['curated-fixture']}}
        papers={'example/project-42':{'ids':['paper-fixture'],'artifacts':[{'paper_id':'paper-fixture','field':'code_url','url':repo(42)['html_url']}]}}
        api=API();transport=Transport()
        with patch.object(scanner,'curated_references',return_value=curated),patch.object(scanner,'paper_references',return_value=papers):
            _,doc,_=self.scan(api,arguments(None,hold_repository_ids=['42'],seed_curated=True,seed_papers=True),transport=transport)
        self.assert_pending_only(doc,[42]);self.assertEqual(transport.ids,[])
        self.assertEqual(api.calls,[('/repos/example/project-42',False)]*2)
        self.assertEqual([r['status'] for r in doc['meta']['seed_observations']],['held','held'])
        self.assertEqual(doc['meta']['current_run']['seed_observation_count'],2)
        errors=[];validate_scan_discovery(doc['meta'],doc['resources'],errors,doc['failures']);self.assertEqual(errors,[])

    def test_seed_deferral_and_expiry_use_actual_frontier_deadline(self):
        state=saved_frontier([42],defer=[42]);api=API();transport=Transport()
        seeds={'example/project-42':{'ids':['curated-fixture']}}
        with patch.object(scanner,'curated_references',return_value=seeds):
            _,doc,after=self.scan(api,arguments(None,seed_curated=True),state=state,transport=transport,instant=INSTANT+59)
        self.assert_pending_only(doc,[42]);self.assertEqual(transport.ids,[])
        self.assertEqual(doc['meta']['seed_observations'][0]['status'],'frontier-deferred')
        self.assertEqual(after['candidates']['42']['attempts'],1)
        released=Transport();api2=API()
        _,doc2,after2=self.scan(api2,resumed=doc,state=after,transport=released,instant=INSTANT+60)
        self.assertEqual(released.ids,[42]);self.assertEqual(api2.calls,[])
        self.assertEqual(doc2['meta']['successful_readme_scans'],1)
        self.assertEqual(after2['candidates']['42']['attempts'],1)

    def test_pre_dispatch_rechecks_candidates_queued_before_new_backoff(self):
        state=saved_frontier([],open_search=True);api=API([43,42])
        def defer_second(rows):
            if rows[0]['id']==43:frontier.defer_candidates(state,[42],reason='retry',retry_after_seconds=60,observed_at=STAMP)
        transport=Transport(callback=defer_second);transport.batch_size=1
        _,doc,after=self.scan(api,arguments(None,target=2),state=state,transport=transport)
        self.assertEqual(transport.ids,[43]);self.assertEqual(doc['meta']['attempted_readme_scans'],1)
        self.assertEqual(doc['meta']['unattempted_candidates'],1);self.assertIsNone(after['candidates']['42']['checkpoint_sha256'])

    def test_identity_only_failures_stay_pending_but_readme404_is_real_attempt(self):
        identity_outcomes=[{**repo(42),'private':True},scanner.ScanError('http-404',404),scanner.ScanError('http-410',410)]
        for graphql in (False,True):
            for outcome in identity_outcomes:
                with self.subTest(graphql=graphql,outcome=type(outcome).__name__):
                    api=API([42],identity={42:outcome});transport=Transport('fallback') if graphql else None
                    _,doc,_=self.scan(api,arguments(None,queries=[QUERY]),transport=transport)
                    self.assert_pending_only(doc,[42]);self.assertEqual(len(api.calls),2)
                    self.assertEqual(api.calls[-1][0],'/repositories/42')
            api=API([42],readme_status=404)
            _,doc,_=self.scan(api,arguments(None,queries=[QUERY]),transport=Transport('fallback') if graphql else None)
            self.assertEqual(doc['meta']['attempted_readme_scans'],1);self.assertEqual(doc['meta']['failed'],1)
            self.assertEqual(doc['failures'][0]['reason'],'http-404');self.assertEqual(len(api.calls),3)

    def test_identity_rejection_does_not_pause_eligible_sibling(self):
        for graphql in (False,True):
            api=API([42,43],identity={42:{**repo(42),'private':True}})
            _,doc,_=self.scan(api,arguments(None,queries=[QUERY],target=2),transport=Transport('fallback') if graphql else None)
            self.assertEqual([r['id'] for r in doc['resources']],['scan-43'])
            self.assertEqual(doc['failures'],[]);self.assertEqual(doc['meta']['attempted_readme_scans'],1)
            self.assertEqual(doc['meta']['unattempted_candidates'],1)
            self.assertEqual([p for p,_ in api.calls if p.endswith('/readme')],['/repos/example/project-43/readme'])

    def test_hold_does_not_modify_a_retained_success(self):
        _,original,_=self.scan(API([42]),arguments(None,queries=[QUERY]),transport=Transport())
        api=API();_,held,_=self.scan(api,arguments(None,hold_repository_ids=['42']),resumed=original,transport=Transport())
        self.assertEqual(api.calls,[]);self.assertEqual(held['resources'],original['resources'])
        self.assertEqual(held['meta']['current_run']['new_successful_readme_scans'],0)
        errors=[];validate_scan_discovery(held['meta'],held['resources'],errors,held['failures']);self.assertEqual(errors,[])


class HoldValidationTests(unittest.TestCase):
    def test_cli_rejects_noncanonical_ids_before_authentication(self):
        for value in ('0','-1','+42','042','scan-42','4.2','42\n'):
            with self.subTest(value=value),patch.object(sys,'argv',['scan_sources.py','--hold-repository-id',value]), \
                    patch.object(scanner.subprocess,'run') as auth,contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):scanner.main()
                auth.assert_not_called()
        for value in ([True],[42],None,['1']*1001):
            with self.assertRaises(ValueError):scanner.held_repository_ids(value)

    def test_holds_are_strict_in_current_archived_and_reconciled_runs(self):
        run={'run_id':STAMP,'held_repository_ids':['scan-1'],'retained_successful_readme_scans':0,'retained_failed_readme_scans':0}
        meta={'discovered_repository_ids':['scan-1','scan-2'],'queries':[],'current_run':copy.deepcopy(run),
              'resume_history':[{'run':copy.deepcopy(run)}],
              'checkpoint_reconciliations':[{'canonical_current_run':copy.deepcopy(run),'checkpoint_current_run':copy.deepcopy(run)}]}
        targets=[lambda d:d['current_run'],lambda d:d['resume_history'][0]['run'],
                 lambda d:d['checkpoint_reconciliations'][0]['canonical_current_run'],
                 lambda d:d['checkpoint_reconciliations'][0]['checkpoint_current_run']]
        errors=[];validate_scan_discovery(meta,[],errors);self.assertEqual(errors,[])
        unseen=copy.deepcopy(meta);unseen['current_run']['held_repository_ids']=['scan-999']
        errors=[];validate_scan_discovery(unseen,[],errors);self.assertEqual(errors,[])
        for target in targets:
            for bad in ([1],['scan-01'],['scan-1','scan-1'],['scan-2','scan-1'],['scan-0'],{'raw':'invalid'}):
                changed=copy.deepcopy(meta);target(changed)['held_repository_ids']=bad;errors=[]
                validate_scan_discovery(changed,[],errors);self.assertTrue(any('held_repository_ids' in e for e in errors))
        changed=copy.deepcopy(meta);changed['current_run']['held_repository_ids']=[1]
        with self.assertRaises(ValueError):scheduled.validate_shape(changed,scheduled.META_SCHEMA)
        errors=[];validate_scan_discovery(meta,[{'id':'scan-1'}],errors)
        self.assertTrue(any('new README attempts' in e for e in errors))
        meta['current_run']['retained_successful_readme_scans']=1;errors=[]
        validate_scan_discovery(meta,[{'id':'scan-1'}],errors);self.assertEqual(errors,[])


if __name__=='__main__':unittest.main()
