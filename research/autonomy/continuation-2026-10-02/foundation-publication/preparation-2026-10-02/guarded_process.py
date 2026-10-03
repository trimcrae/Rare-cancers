"""Run one finite cloud subprocess, retaining logs and stopping its process group."""
import datetime,os,pathlib,shutil,signal,subprocess,time,zoneinfo
def allowed():
    now=datetime.datetime.now(zoneinfo.ZoneInfo('America/New_York'))
    return not (6<=now.hour<10 or (now.hour==5 and now.minute==59 and now.second>=30))
def run(command,log,seconds):
    assert allowed(),'Daily computer-use restriction'
    assert shutil.disk_usage('.').free>=10.5*1024**3,'Storage reserve'
    with pathlib.Path(log).open('w') as output:
        process=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        start=time.monotonic()
        while process.poll() is None:
            if not allowed() or shutil.disk_usage('.').free<10.5*1024**3 or time.monotonic()-start>seconds:
                # sudo kill also reaches root-owned package-manager descendants.
                subprocess.run(['sudo','kill','-TERM','--',f'-{process.pid}'],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
                subprocess.run(['sudo','kill','-KILL','--',f'-{process.pid}'],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                process.wait(timeout=5)
                raise RuntimeError('Stopped process group at time/storage/daily restriction')
            time.sleep(0.5)
    if process.returncode!=0:raise RuntimeError(f'Command exited{process.returncode}; see{log}')
