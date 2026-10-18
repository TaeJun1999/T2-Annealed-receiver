"""Read-only final integrity checks; write evidence only inside the E5 worktree."""
from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path('/home/HTJ/t2_wtE5');OUT=ROOT/'conf/results/review_next/qam16'
before=json.loads((OUT/'protected_before.json').read_text())
env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(base,*args):return subprocess.check_output(['git','-C',str(base),*args],env=env,text=True).strip()
after={}
for name,base in [('main',Path('/home/HTJ/t2')),('E5',ROOT)]:
    gd=Path(git(base,'rev-parse','--absolute-git-dir'))
    after[name]=dict(head=git(base,'rev-parse','HEAD'),index_sha256=sha(gd/'index'),
                     demo={str(p.relative_to(base)):sha(p) for p in sorted((base/'Demo').glob('*.py'))})
    after[name]['head_unchanged']=after[name]['head']==before[name]['head']
    after[name]['demo_unchanged']=after[name]['demo']==before[name]['demo']
after['main']['index_unchanged']=after['main']['index_sha256']==before['main']['index_sha256']
after['main']['code_demo_diff_empty']=not git('/home/HTJ/t2','diff','--no-ext-diff','HEAD','--','conf/code','Demo')
after['E5']['demo_diff_empty']=not git(ROOT,'diff','--no-ext-diff','HEAD','--','Demo')
after['E5']['staged_diff_empty']=not git(ROOT,'diff','--cached','--no-ext-diff','--')
inputs=json.loads((OUT/'copied_inputs.json').read_text())
changed=[]
for x in inputs:
    p=Path(x['destination'])
    assert p.resolve().is_relative_to(ROOT)
    if sha(p)!=x['sha256']:changed.append(x['destination'])
after['inputs']=dict(count=len(inputs),changed=changed,new_links_created=False)
with (OUT/'protected_after.json').open('x') as f:json.dump(after,f,indent=2)
assert after['main']['head_unchanged'] and after['main']['index_unchanged']
assert after['main']['demo_unchanged'] and after['main']['code_demo_diff_empty']
assert after['E5']['head_unchanged'] and after['E5']['demo_unchanged']
assert after['E5']['demo_diff_empty'] and after['E5']['staged_diff_empty']
assert not changed
print('PASS preservation: main HEAD/index/code/Demo unchanged; E5 HEAD/Demo unchanged; no staged diff;',len(inputs),'input hashes unchanged')
