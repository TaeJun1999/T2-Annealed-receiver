"""Copy only the three required inputs with cp -L; append local fit copies for two regression tags."""
import hashlib
import json
from pathlib import Path
import subprocess
import os

ROOT = Path(__file__).resolve().parents[4]
MAIN = Path('/home/HTJ/t2')
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot():
    paths = ['conf/code/arms.py', 'conf/code/runner.py', 'Demo/t2_route_a.py', 'Demo/t2_trellis.py', 'Demo/t2_gmm.py']
    index = Path(subprocess.check_output(['git', '-C', str(MAIN), 'rev-parse', '--git-path', 'index'], text=True).strip())
    if not index.is_absolute():
        index = MAIN / index
    return dict(head=subprocess.check_output(['git', '-C', str(MAIN), 'rev-parse', 'HEAD'], text=True).strip(),
                index_sha256=sha(index), files={p: sha(MAIN / p) for p in paths})


def main():
    copies = []
    def copy(source, dest):
        assert dest.resolve().is_relative_to(ROOT)
        if dest.exists() or dest.is_symlink():
            raise FileExistsError(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['cp', '-L', str(source), str(dest)], check=True)
        assert not dest.is_symlink() and sha(source) == sha(dest)
        copies.append(dict(source=str(source), destination=str(dest), sha256=sha(dest), bytes=dest.stat().st_size))
    rels = ['conf/raw_SPU28/D2_C2_UMi28_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz',
            'conf/results/gmm_fits_D2_SPU28/fit_UMi28_Nr8_fullK32_n160000.npz',
            'conf/results/gmm_fits_D2_U28NR32GCAPchk/fit_UMi28_Nr32_fullK32_n160000.npz']
    before = snapshot()
    for rel in rels:
        copy(MAIN / rel, ROOT / rel)
    for tag in ('SBL32REG4', 'SBL32REG5OFF'):
        copy(ROOT / rels[1], ROOT / f'conf/results/gmm_fits_D2_{tag}/fit_UMi28_Nr8_fullK32_n160000.npz')
    doc = dict(date=subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], env=dict(os.environ, TZ='America/Chicago'),
                                          text=True).strip(), copies=copies, main_before=before,
               worktree_head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
               lock_id_Demo=subprocess.check_output(['lock', 'id', str(MAIN / 'Demo')], text=True).strip())
    with (HERE / 'input_manifest.json').open('x') as f:
        json.dump(doc, f, indent=2)
    for c in copies:
        print(f"cp -L {c['source']} {c['destination']}\nsha256 {c['sha256']}", flush=True)


if __name__ == '__main__':
    main()
