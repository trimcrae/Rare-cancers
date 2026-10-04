"""Run the same normal gate at the second completed analysis checkpoint."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'run_preflight.py').read_text(encoding='utf-8')
source=source.replace("normal-preflight.log", "round2-normal-preflight.log").replace("normal-preflight-receipt.json", "round2-normal-preflight-receipt.json")
exec(compile(source,str(base/'run_preflight.py'),'exec'),{'__file__':str(__file__),'__name__':'__main__'})
