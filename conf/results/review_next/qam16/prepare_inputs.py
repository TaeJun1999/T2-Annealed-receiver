"""Copy only frozen E5 inputs; run from the E5 worktree with python -B."""
from pathlib import Path
import hashlib, json, os, subprocess
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
SRC = Path('/home/HTJ/t2')
OUT = Path(__file__).resolve().parent
assert ROOT == Path('/home/HTJ/t2_wtE5')
rows = []
def sha(p):
    with open(p, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
def copy(p):
    target = ROOT / p.relative_to(SRC)
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = sha(p)
    existed = target.exists()
    if target.is_symlink():
        assert target.resolve().is_relative_to(ROOT), 'existing link must stay inside worktree'
    if not existed:
        assert not target.is_symlink(), 'do not write through a dangling link'
        subprocess.run(['cp', '-L', '--', str(p), str(target)], check=True)
    assert sha(target) == expected
    rows.append(dict(source=str(p), destination=str(target), sha256=expected, bytes=target.stat().st_size, action='verified-existing' if existed else 'cp -L', resolved_destination=str(target.resolve())))
    return target
for tag, prior in [('B16e4k', 'S2'), ('U28B16e4', 'UMi28')]:
    snr = '-3' if tag == 'B16e4k' else '12'
    raw = next((SRC / 'conf' / ('raw_' + tag)).glob(f'D2_C2_{prior}_*snr{snr}_skip0_n40.npz'))
    ref = np.load(copy(raw))
    ckpt = Path(str(ref['meta|stagec_ckpt']))
    copy(ckpt)
    if ckpt.stem.endswith('_best'):
        copy(ckpt.with_name(ckpt.name.replace('_best.pt', '.pt')))  # training-cost metadata only
    for p in sorted((SRC / 'conf/results' / ('gmm_fits_D2_' + tag)).glob('*_Nr8_*_n160000.npz')):
        copy(p)
for name in ['sigma_grid_D2.npz', 'sigma_grid_D2_UMi28.npz']:
    copy(SRC / 'conf/results' / name)
with open(OUT / 'copied_inputs.json', 'w') as f:
    json.dump(rows, f, indent=2)
print(f'PASS: {len(rows)} verified input files, sha256 matched; details: {OUT / "copied_inputs.json"}')
