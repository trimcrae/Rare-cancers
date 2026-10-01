import time,urllib.error,http.client
import spatial_cellpose_reference_sensitivity_actual as ref
class RetryingRangeFile(ref.RangeFile):
 def read(self,n=-1):
  start=self.pos
  for attempt in range(3):
   try:self.pos=start;return super().read(n)
   except (urllib.error.HTTPError,urllib.error.URLError,http.client.RemoteDisconnected,TimeoutError,ConnectionResetError,RuntimeError) as exc:
    if isinstance(exc,urllib.error.HTTPError) and exc.code not in (403,408,429,500,502,503,504):raise
    if isinstance(exc,RuntimeError) and not str(exc).startswith(('Range not exact:','Content-Range mismatch:')):raise
    self.receipts.append({'transport_retry':attempt+1,'requested_read_start':start,'requested_read_bytes':n,'error_type':type(exc).__name__,'error':str(exc),'absence_claim':False});self.pos=start
    if attempt==2:raise
    time.sleep(2*(attempt+1))
