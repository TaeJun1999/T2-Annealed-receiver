"""Read-only protection snapshots; all evidence is written under fix1/."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path('/home/HTJ/t2_wtE5')
MAIN = Path('/home/HTJ/t2')
OUT = Path(__file__).resolve().parent
QAM = OUT.parent
ENV = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], env=ENV, text=True).strip()


def snapshot():
    paths = set()
    for root in (ROOT, MAIN):
        paths.update(p for p in (root / 'conf/code').iterdir() if p.is_file())
        paths.update((root / 'Demo').glob('*.py'))
        paths.update(root / name for name in ('LOCKED.md', 'conf/DECISIONS.md',
                                             'conf/results/review_next/NEXT_EXPERIMENTS_E5QAM16.md'))
    paths.update(p for p in QAM.rglob('*') if p.is_file() and not p.is_relative_to(OUT))
    for row in json.loads((QAM / 'regression.json').read_text())['comparisons']:
        paths.add(Path(row['reference']))
    for row in json.loads((QAM / 'copied_inputs.json').read_text()):
        paths.add(Path(row['destination']))
    paths = {p for p in paths if p.exists() and '__pycache__' not in p.parts}
    roots = {}
    for name, root in (('E5', ROOT), ('main', MAIN)):
        gd = Path(git(root, 'rev-parse', '--absolute-git-dir'))
        roots[name] = {'head': git(root, 'rev-parse', 'HEAD'), 'index_sha256': sha(gd / 'index')}
    return {'date': subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'],
                                            env={**ENV, 'TZ': 'America/Chicago'}, text=True).strip(),
            'roots': roots, 'files': {str(p): sha(p) for p in sorted(paths)}}


if __name__ == '__main__':
    phase = sys.argv[1]
    assert phase in ('before', 'after')
    data = snapshot()
    if phase == 'before':
        with (OUT / 'runner_before.py').open('x') as stream:
            stream.write((ROOT / 'conf/code/runner.py').read_text())
    else:
        before = json.loads((OUT / 'protected_before.json').read_text())
        changed = [p for p in before['files'] if data['files'].get(p) != before['files'][p]]
        data['changed_files'] = changed
        data['git_unchanged'] = before['roots'] == data['roots']
        assert data['git_unchanged'], 'HEAD or index changed'
        assert changed == [str(ROOT / 'conf/code/runner.py')], changed
        print('PASS preservation: only E5 conf/code/runner.py changed;',
              len(before['files']) - 1, 'protected file hashes unchanged; HEAD/index unchanged', flush=True)
    with (OUT / f'protected_{phase}.json').open('x') as stream:
        json.dump(data, stream, indent=2)
    print(phase, data['date'], 'files=', len(data['files']), flush=True)
