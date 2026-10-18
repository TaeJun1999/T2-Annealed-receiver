"""Confirm the patch boundary without running any receiver or writing bytecode."""
from pathlib import Path
import ast
import json
import subprocess

ROOT = Path('/home/HTJ/t2_wtE5')
OUT = Path(__file__).resolve().parent
old = ast.parse((OUT / 'runner_before.py').read_text())
new = ast.parse((ROOT / 'conf/code/runner.py').read_text())
changed = []
assert len(old.body) == len(new.body)
for left, right in zip(old.body, new.body):
    if ast.dump(left) != ast.dump(right):
        assert isinstance(left, ast.FunctionDef) and left.name == right.name
        changed.append(left.name)
assert changed == ['run_task', 'cmd_smoke'], changed


def new_chunk_path(tree):
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run_task')
    guard = next(i for i, node in enumerate(fn.body)
                 if isinstance(node, ast.If) and ast.unparse(node.test) == 'os.path.exists(out)')
    return [ast.dump(node) for node in fn.body[guard + 1:]]


assert new_chunk_path(old) == new_chunk_path(new)
for path in (OUT / 'checks.py', OUT / 'preservation.py', OUT / 'static_checks.py'):
    ast.parse(path.read_text(), filename=str(path))
subprocess.run(['bash', '-n', str(OUT / 'run_checks.sh')], check=True)
subprocess.run(['git', '-C', str(ROOT), 'diff', '--check', '--', 'conf/code/runner.py'], check=True)
result = {'changed_functions': changed, 'new_chunk_path_ast_identical': True,
          'python_syntax': 'PASS', 'bash_syntax': 'PASS', 'git_diff_check': 'PASS'}
with (OUT / 'static_checks.json').open('x') as stream:
    json.dump(result, stream, indent=2)
print('PASS static: only run_task/cmd_smoke changed; new-chunk computation/serialization AST identical; syntax/diff clean')
