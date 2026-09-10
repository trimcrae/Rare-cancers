"""Read-only verification of the original ATR study scope; no artifact rewriting."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
GENES=('EWSR1','TAF15','FUS','TCF12','TFG','NR4A3')

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def scoped_inputs(inputs, scope):
    """Check every field of the study genes; preserve all other original inputs."""
    expected=set(GENES)
    if not expected.issubset(inputs['genes']):
        raise ValueError('Missing original study gene model')
    extra=set(inputs['genes'])-expected
    if extra-{'PGR'}:
        raise ValueError('Unexpected extra models: '+str(sorted(extra)))
    for gene in GENES:
        if digest(inputs['genes'][gene])!=scope['gene_sha256'][gene]:
            raise ValueError('Study input drift: '+gene)
    if digest(inputs.get('uniprot_sequences'))!=scope['uniprot_sequences_sha256']:
        raise ValueError('Study UniProt sequence drift')
    result=copy.deepcopy(inputs)
    result['genes']={gene:inputs['genes'][gene] for gene in GENES}
    return result,sorted(extra)

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out

def main():
    scope=json.loads((HERE/'study-input-scope.json').read_text(encoding='utf-8'))
    for rel,expected in scope['dependency_sha256'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=expected:
            raise ValueError('Pinned study dependency drift: '+rel)
    inputs=json.loads((ROOT/'research/modalities/emc-construct-inputs.json').read_text(encoding='utf-8'))
    selected,extra=scoped_inputs(inputs,scope)
    producer=module('constructs',ROOT/'research/modalities/emc_fet_construct_designs.py')
    old=json.loads((ROOT/'research/modalities/emc-fet-construct-designs.json').read_text(encoding='utf-8'))
    result=producer.derive(selected)
    if result!=old:
        raise ValueError('Full original-scope artifact differs: '+str([k for k in set(result)|set(old) if result.get(k)!=old.get(k)]))
    print('ORIGINAL STUDY SCOPE REPRODUCES; all artifact fields compared; excluded models: '+str(extra))
    frame=module('frame',ROOT/'research/modalities/emc_fet_frame_and_composition.py')
    if frame.main(['--check'])!=0:raise ValueError('Frame/composition check failed')
    figure=module('figure',ROOT/'research/manuscripts/figures/emc_fusion_frame_figure.py')
    figure.PROVENANCE=str(HERE/'emc-atr-figure-provenance.json')
    if figure.main(['--check'])!=0:raise ValueError('Frozen figure provenance check failed')
    return 0

if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
