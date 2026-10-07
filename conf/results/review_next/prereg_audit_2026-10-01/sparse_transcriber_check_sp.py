import numpy as np, glob, json, re, os, datetime as dt
from zoneinfo import ZoneInfo
os.chdir("/home/HTJ/t2/conf")
ROWS = [("B16e4k","S2","C2"),("D3","S2c","C2"),("SV","SV8e","C2"),("U28","UMi28","C2"),("MX","MIX3","C2"),("NR16","S2","C6")]
NEW = ("SBL-loop","SBL-pilot","OMP-pilot")
cdt = lambda t: dt.datetime.fromtimestamp(t, ZoneInfo("America/Chicago")).strftime("%m-%d %H:%M:%S")
for suf, pr, cell in ROWS:
    fs = sorted(glob.glob(f"raw_SP{suf}/*.npz")); pick = json.load(open(f"results/sparse/pick_{pr}_{cell}.json"))
    gits, bad, failed_keys, nonfin, nonfin16, ck = set(), 0, 0, {a:0 for a in NEW}, {a:0 for a in NEW}, 0
    per = {}; nm1 = {}; mt = [os.path.getmtime(f) for f in fs]
    for f in fs:
        z = np.load(f); snr = re.search(r"_snr(-?\d+)_", f).group(1); skip = int(z["run|skip"]); n = int(z["run|n"])
        gits.add(str(z["run|git"])); e = pick["per_snr"][snr]
        bad += json.loads(str(z["meta|sparse"])) != dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=e["n_em"], L=e["L"])
        ck += "meta|stagec_ckpt_id" in z.files
        failed_keys += sum(k.endswith("|failed") for k in z.files)
        per.setdefault(snr, []).append((skip, n))
        for a in NEW:
            b = np.asarray(z[a+"|blk_err"], float); nonfin[a] += int((~np.isfinite(b)).sum()); nonfin16[a] += int((~np.isfinite(b[:, -1])).sum())
        for a in ("SBL-pilot","OMP-pilot"):
            nm1.setdefault((a, snr), []).append(np.asarray(z[a+"|nmse"], float)[:, 0])
    cov = {s: (len(v), sum(n for _, n in v), min(k for k, _ in v), max(k for k, _ in v)) for s, v in per.items()}
    print(f"== SP{suf}: files {len(fs)} git {gits} meta|sparse mismatch {bad} stagec_ckpt_id present {ck} '|failed' keys {failed_keys}")
    print(f"   nonfinite blk_err any-iter {nonfin} @16 {nonfin16}")
    print(f"   coverage per SNR (chunks, trials, skip min, skip max): {sorted(cov.items(), key=lambda x:int(x[0]))}")
    print(f"   chunk mtime first {cdt(min(mt))} last {cdt(max(mt))} CDT")
    edge = {s: (pick['per_snr'][s]['edge_sbl'], pick['per_snr'][s]['edge_omp']) for s in pick['per_snr']}
    print(f"   pick rho_sbl {pick['rho_sbl']} rho_omp {pick['rho_omp']} edge_rho {pick['edge_rho_sbl']},{pick['edge_rho_omp']} per-SNR (n_em,L) {[(s, pick['per_snr'][s]['n_em'], pick['per_snr'][s]['L']) for s in pick['per_snr']]} edge flags {edge}")
    for a, key in (("SBL-pilot","nmse_sbl_db"),("OMP-pilot","nmse_omp_db")):
        row = []
        for s in ("-3","0","3","6","9","12","15"):
            v = np.concatenate(nm1[(a, s)]); test = 10*np.log10(v.mean()); dev = pick["per_snr"][s][key]
            row.append(f"{s}: test {test:.2f} dev {dev:.2f} diff {test-dev:+.2f} (finite {np.isfinite(v).all()}, n {v.size})")
        print(f"   {a} NMSE@1: " + "; ".join(row))
