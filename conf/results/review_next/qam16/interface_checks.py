"""Read-only or synthetic checks of CLI compatibility; no channel-set receiver evaluation."""
from pathlib import Path
import contextlib, importlib.util, io, json, sys
import numpy as np
ROOT=Path('/home/HTJ/t2_wtE5'); OUT=ROOT/'conf/results/review_next/qam16'
sys.path.insert(0,str(ROOT/'conf/code'))
import common as C
import arms as A
import runner as R
# No block normalization: exact encoded data symbols survive interleaving in transmit().
code=C.QAMCode(C.GENS,C.NU,4,48)
prior=C.GaussianPrior(8,4,np.eye(32))
rx=A.route_a(8,4,16,4,1.,prior,code,C.dft_pilots(4,4),'gaussian')
rng=np.random.default_rng(20261017)
u=np.zeros(90,int); perm=rng.permutation(48)
X,Y=rx.transmit(u,perm,np.zeros((8,4)),rng)
assert np.array_equal(X[:,4:].T.reshape(-1)[perm],code.encode(u))
energy=float(np.mean(np.abs(X[:,4:])**2))
assert energy == float(np.mean(np.abs(code.encode(u))**2)) and energy != 1.
# Legacy diagnostic default takes exactly the same branch and calls as the HEAD implementation.
import diag_sigma_coverage as D
control=OUT/'control_diag.py'
# The control source is captured outside this script before execution.
spec=importlib.util.spec_from_file_location('e5_control_diag',control)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def calls(module, argv):
    seen=[]
    module.SG.load=lambda *a,**k:(np.array([.02,.08]),np.array([.1,.2]))
    module.run=lambda *a,**k:(seen.append(('run',a,k)) or ('res','pil','bstar','sp'))
    module.report=lambda *a,**k:(seen.append(('report',a,k)) or 'sentinel')
    module.os.makedirs=lambda *a,**k:None
    # Shared numpy/os modules are patched temporarily and restored by caller below.
    module.np.savez_compressed=lambda *a,**k:seen.append(('save',a,sorted(k)))
    # Fake empty results keep the legacy flattening path measurable without receivers.
    module.run=lambda *a,**k:(seen.append(('run',a,k)) or ({},'pil','bstar','sp'))
    before=sys.argv;sys.argv=[str(ROOT/'conf/code/diag_sigma_coverage.py')]+argv
    try:
        with contextlib.redirect_stdout(io.StringIO()) as buf: rc=module.main()
    finally:sys.argv=before
    return rc,seen,buf.getvalue()
load=D.SG.load;mkdir=D.os.makedirs;savez=D.np.savez_compressed
try:
    default=calls(old,[])
    omitted=calls(D,[])
    explicit=calls(D,['--mod','qpsk'])
finally:
    D.SG.load=load;D.os.makedirs=mkdir;D.np.savez_compressed=savez
assert default == omitted == explicit
result=dict(transmit_preserves_encoded_symbols=True,example_block_energy=energy,
            block_energy_normalized=False,legacy_diagnostic_default_calls_unchanged=True,
            legacy_diagnostic_explicit_qpsk_calls_unchanged=True,
            note='diagnostic CLI comparison uses sentinels, no legacy test trials evaluated')
with open(OUT/'interface.json','x') as f:json.dump(result,f,indent=2)
print('PASS interface:',result)
