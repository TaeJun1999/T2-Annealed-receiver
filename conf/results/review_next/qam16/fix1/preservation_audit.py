"""Record a failed preservation check faithfully; never restore concurrently changed files."""
import json
import subprocess
from preservation import ROOT, MAIN, OUT, snapshot

before = json.loads((OUT / 'protected_before.json').read_text())
after = snapshot()
changed = [p for p in before['files'] if after['files'].get(p) != before['files'][p]]
runner = str(ROOT / 'conf/code/runner.py')
after['changed_files'] = changed
after['unexpected_changed_files'] = [p for p in changed if p != runner]
after['new_protected_files'] = sorted(set(after['files']) - set(before['files']))
after['unchanged_original_files'] = len(before['files']) - len(changed)
after['git_unchanged'] = before['roots'] == after['roots']
after['main_files_unchanged'] = not any(path.startswith(str(MAIN) + '/') for path in changed)
after['preservation_passed'] = after['git_unchanged'] and changed == [runner]
tested_sha = next(line.split()[0] for line in (OUT / 'execution_context.txt').read_text().splitlines()
                  if line.endswith('  conf/code/runner.py'))
after['runner_matches_tested_sha256'] = after['files'][runner] == tested_sha
after['note'] = ('Original preservation.py after failed; its stdout/stderr are retained. '
                 'Unexpected protected-file changes were observed during the checks. '
                 'This task did not write those paths. The author/process was not established. '
                 'No files were restored or removed. Functional check results remain separately recorded.')
with (OUT / 'protected_after.json').open('x') as stream:
    json.dump(after, stream, indent=2)
diff = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--no-ext-diff', 'HEAD', '--',
                                *after['unexpected_changed_files']], text=True)
with (OUT / 'concurrent_changes.diff').open('x') as stream:
    stream.write(diff)
status = subprocess.check_output(['git', '-C', str(ROOT), 'status', '--short'], text=True)
with (OUT / 'concurrent_status.txt').open('x') as stream:
    stream.write(after['date'] + '\n' + status)
assert after['runner_matches_tested_sha256'], 'runner changed since the functional checks'
assert after['git_unchanged'] and after['main_files_unchanged'], 'main or git state changed'
print('PRESERVATION FAILED: unexpected changed files =', after['unexpected_changed_files'])
print('Verified unchanged original files =', after['unchanged_original_files'],
      '; main/HEAD/index unchanged; runner matches tested SHA; concurrent edits retained')
