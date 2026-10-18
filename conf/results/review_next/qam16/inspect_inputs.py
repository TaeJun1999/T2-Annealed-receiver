from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/home/HTJ/t2_wtE5'); OUT=ROOT/'conf/results/review_next/qam16'
rows=json.loads((OUT/'copied_inputs.json').read_text())
tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
for row in rows:
    rel=str(Path(row['destination']).relative_to(ROOT))
    row['action']='verified-existing-tracked' if rel in tracked else 'cp -L (this session)'
with open(OUT/'copied_inputs.json','w') as f:json.dump(rows,f,indent=2)
with open(OUT/'input_sha256.tsv','w') as f:
    f.write('sha256\taction\tsource\tdestination\n')
    for row in rows:f.write('\t'.join(str(row[k]) for k in ('sha256','action','source','destination'))+'\n')
state={}
for name,base in [('main',Path('/home/HTJ/t2')),('E5',ROOT)]:
    git=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=base,text=True).strip())
    def sha(p):
        with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
    state[name]=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base,text=True).strip(),
                     index_sha256=sha(git/'index'),
                     demo={str(p.relative_to(base)):sha(p) for p in sorted((base/'Demo').glob('*.py'))})
with open(OUT/'protected_before.json','x') as f:json.dump(state,f,indent=2)
print('verified',len(rows),'inputs; copied this session',sum(r['action'].startswith('cp') for r in rows))
