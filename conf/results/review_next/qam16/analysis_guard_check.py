from pathlib import Path
from types import SimpleNamespace
import contextlib,io,json,sys
ROOT=Path('/home/HTJ/t2_wtE5'); OUT=ROOT/'conf/results/review_next/qam16'
sys.path.insert(0,str(ROOT/'conf/code'))
import runner as R
import numpy as np
err=io.StringIO()
try:
 with contextlib.redirect_stderr(err):R.main(['analysis','--mod','16qam','--tag','E5_ANALYSIS_REFUSE'])
except SystemExit as ex:assert ex.code==2
else:raise AssertionError('explicit 16qam analysis accepted')
assert 'legacy analysis assumes QPSK payload' in err.getvalue()
assert not (ROOT/'conf/raw_E5_ANALYSIS_REFUSE').exists()
folder=OUT/'synthetic_analysis';folder.mkdir(exist_ok=True)
fixture=folder/'D2_C2_S2_Nr8_T16_Tp4_dft_snr9_skip2560_n4.npz'
with fixture.open('xb') as f:np.savez_compressed(f,**{'meta|modulation':'16qam','meta|payload_bits':90,'meta|example':'synthetic fixture, no receiver evaluated'})
R.d_raw=lambda:str(folder)
try:R.cmd_analysis(SimpleNamespace(testbed='D2'))
except ValueError as ex:assert 'legacy analysis assumes QPSK payload' in str(ex)
else:raise AssertionError('mod omitted: 16qam raw accepted by legacy analysis')
with (OUT/'analysis_guard_complete.json').open('x') as f:
 json.dump(dict(explicit_mod_refused=True,mod_omitted_raw_refused=True,no_table_generated=True),f,indent=2)
with (OUT/'analysis_guard_complete.stderr.log').open('x') as f:f.write(err.getvalue())
print('PASS analysis guards: explicit 16qam refused; 16qam raw also refused when --mod omitted; no table generated')
