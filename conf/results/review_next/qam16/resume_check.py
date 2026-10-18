from pathlib import Path
import json,sys
ROOT=Path('/home/HTJ/t2_wtE5'); OUT=ROOT/'conf/results/review_next/qam16'
sys.path.insert(0,str(ROOT/'conf/code'))
import runner as R
import numpy as np
p=OUT/'synthetic_existing_qpsk.npz'
np.savez_compressed(p,**{'meta|example':'synthetic schema fixture, no receiver evaluation'})
R.raw_file=lambda *a:str(p)
task=('D2','C2','S2',9.,2560,4,160000,.7,5,16,['R5-genie'],None,None,False,False,None,False,None,None,None,None)
# QPSK original skip remains unchanged, and 16qam cannot silently reuse it.
assert R.run_task(task).startswith('exists')
try:R.run_task(task+('16qam',))
except ValueError as ex:assert 'different modulation/payload/protocol' in str(ex)
else:raise AssertionError('16qam accepted an old QPSK chunk')
assert p.exists()
with open(OUT/'resume_check.json','x') as f:json.dump(dict(qpsk_skip_unchanged=True,qam16_schema_mismatch_refused=True,old_file_preserved=True),f,indent=2)
print('PASS: QPSK skip unchanged; 16qam refuses old raw before receiver construction; fixture preserved')
