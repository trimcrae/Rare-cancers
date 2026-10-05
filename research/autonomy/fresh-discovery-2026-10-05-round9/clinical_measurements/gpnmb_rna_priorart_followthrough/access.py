import json,pathlib,urllib.request,urllib.error,datetime,hashlib,sys,time,signal
P=pathlib.Path(__file__).resolve().parent
n=int(sys.argv[1]);r=json.loads((P/f'ROUTE-{n:02}-FROZEN.json').read_text())
now=datetime.datetime.now(datetime.timezone.utc)
if now>=datetime.datetime.fromisoformat('2026-10-05T22:15:00+00:00'):raise RuntimeError('deadline')
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
out={'utc':now.isoformat(),**r};start=time.monotonic();p=P/'raw-cache';p.mkdir(exist_ok=True)
try:
 def alarm_handler(signum,frame):raise TimeoutError('strict overall 10second alarm')
 signal.signal(signal.SIGALRM,alarm_handler);signal.alarm(10)
 req=urllib.request.Request(r['url'],headers={'User-Agent':'EMC-source-eligibility-research/1.0','Accept':'application/xml'})
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=10) as f:
  out['status']=f.status;out['content_type']=f.headers.get('Content-Type');b=f.read(r['cap_bytes']+1)
  if len(b)>r['cap_bytes']:raise RuntimeError('over cap')
  if time.monotonic()-start>10:raise RuntimeError('elapsed timeout guard')
  target=p/f'stage-{n:02}.source';target.write_bytes(b);out.update({'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'path':str(target.resolve()),'complete_response':True})
except Exception as e:out.update({'error_type':type(e).__name__,'error':str(e),'complete_response':False})
signal.alarm(0)
out['actual_elapsed_seconds']=time.monotonic()-start
out['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(P/f'ACCESS-{n:02}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k in ['status','bytes','sha256','error','complete_response','completed_utc']}))
