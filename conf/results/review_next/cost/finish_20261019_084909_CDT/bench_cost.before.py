"""E4 CPU receiver-cost bench; development trials only, one process, no fitting.

Examples (use an otherwise quiet machine for reportable timings)::

    python conf/code/bench_cost.py --cell D2 --tag cost_d2
    python conf/code/bench_cost.py --cell U32 --tag cost_u32 --gmm both

The historical bench_moduleH_ep.py and all receiver code remain unchanged.
--trials 1 --verify-tap is an implementation check, not a cost experiment.
--force explicitly accepts concurrent compute; this fact stays in the outputs.
"""
import argparse
from contextlib import ExitStack
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time

# Set before numpy/torch/receiver imports. Never create bytecode in shared code.
sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for _name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "conf/results/review_next/cost"
MAIN = Path("/home/HTJ/t2")
V1 = "M-ours-dscore-C-V1"
V1MS = "M-ours-dscore-C-V1ms"
BSTAR = "M-ours-bstar"
NTRAIN, NITER, WARMUP = 160000, 16, 2560
CKPTS = {
    "D2": (MAIN / "conf/ckpt/d2sx_N160000_a1.pt",
           "4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29"),
    # Full digest read from the file; its first 16 digits match the E4 spec.
    "U32": (MAIN / "conf/ckpt/d2sx_UMi28NR32_N160000_a1_best.pt",
            "463da87aa8dbfb614c38ea30bc8cd26e2ade5099a0eb48407dca592b46b854e9"),
}
FIT_SHA = {
    "fit_S2_Nr8_fullK32_n160000.npz": "d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3",
    "fit_S2_Nr8_kronK1024_n160000.npz": "bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997",
    "fit_UMi28_Nr32_fullK32_n160000.npz": "d572e0ac63013a96042a148aa1fceaa6662710ddfdbcfb4a4dd051271704e215",
    "fit_UMi28_Nr32_kronK4096_n160000.npz": "2d72a4349e2700e79aec72b48bebed29e59b0f336091b9a6706dbd70d29ef569",
    "fit_UMi28_Nr32_kronK8192_n160000.npz": "d883afaf2e3e6133685594c5e7eaa892ac371b90c41505b7acd4a2b3fd49f71b",
}


class BenchError(RuntimeError):
    pass


def command(argv, check=True, env=None):
    p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True,
                       timeout=30, env=env)
    if check and p.returncode:
        raise BenchError(f"{argv!r}: {p.stderr.strip()}")
    return (p.stdout + p.stderr).strip()


def now():
    return command(["date", "+%Y-%m-%d %H:%M:%S %Z"],
                   env=dict(os.environ, TZ="America/Chicago"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def checked_hash(path, expected=None):
    actual = sha256(path)
    if expected is not None and actual != expected:
        raise BenchError(f"SHA256 MISMATCH {path}: expected={expected} actual={actual}; no receiver measurement")
    return actual


def inside(path, parent=ROOT):
    path = Path(path).resolve()
    if not path.is_relative_to(parent.resolve()):
        raise BenchError(f"write outside allowed directory: {path}")
    return path


def lock_id(path):
    return command(["lock", "id", str(path)], check=False) if shutil.which("lock") else "lock command unavailable"


def load_snapshot():
    """Read-only process inspection. No worker processes or GPU contexts."""
    top = command(["ps", "-eo", "pid,pcpu,etime,comm", "--sort=-pcpu"])
    own = command(["ps", "-u", str(os.getuid()), "-o", "pid=,ppid=,pcpu=,comm=,args="])
    ancestors = {os.getpid()}
    pid = os.getppid()
    while pid > 1 and pid not in ancestors:
        ancestors.add(pid)
        try:
            pid = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    busy = []
    for line in own.splitlines():
        fields = line.split(None, 4)
        if len(fields) < 5 or int(fields[0]) in ancestors:
            continue
        pid, _, cpu, comm, args = fields
        tokens = args.split()
        python = "python" in comm.lower()
        known = python and any("runner.py" in t or "bench_" in t or "train" in t
                               or "gmm_em" in t or "gpu_hold" in t for t in tokens)
        if known or float(cpu) >= 20:
            busy.append(line.strip())
    gpu = (command(["nvidia-smi", "--query-compute-apps=pid,gpu_uuid,process_name,used_memory", "--format=csv"],
                   check=False) if shutil.which("nvidia-smi") else "nvidia-smi unavailable")
    return dict(date=now(), uptime=command(["uptime"]),
                top="\n".join(top.splitlines()[:20]), busy=busy, gpu=gpu)


def source_groups(a):
    if a.cell == "D2":
        files = sorted(a.d2_fits.glob("*.npz"))
        required = {k for k in FIT_SHA if k.startswith("fit_S2_")}
        if not required.issubset({p.name for p in files}):
            raise BenchError(f"D2 fits missing: {required - {p.name for p in files}}")
        return [(1024, files)]  # entire legacy directory, dereference its links
    full = a.u32_fits / "fit_UMi28_Nr32_fullK32_n160000.npz"
    return [(k, [full, folder / f"fit_UMi28_Nr32_kronK{k}_n160000.npz"])
            for k, folder in ((4096, a.u32_fits), (8192, a.gcap_fits))
            if a.gmm == "both" or a.gmm == {4096: "k4096", 8192: "gcap8192"}[k]]


def check_assets(a):
    checkpoint = a.checkpoint or CKPTS[a.cell][0]
    info = dict(checkpoint=dict(path=str(checkpoint),
                               sha256=checked_hash(checkpoint, CKPTS[a.cell][1]),
                               lock_id=lock_id(checkpoint)), groups=[])
    for k, files in source_groups(a):
        entries = [dict(source=str(p), resolved=str(p.resolve()), name=p.name,
                        sha256=checked_hash(p, FIT_SHA.get(p.name)), lock_id=lock_id(p)) for p in files]
        info["groups"].append(dict(K=k, tag=f"COST_{a.tag}_{a.cell}_K{k}", files=entries))
    return info


def prepare_fits(info):
    """Exclusive byte copies, never symlinks; validate reusable copies in full."""
    for group in info["groups"]:
        folder = inside(ROOT / "conf/results" / f"gmm_fits_D2_{group['tag']}")
        folder.mkdir(exist_ok=True)
        names = {x["name"] for x in group["files"]}
        extra = {p.name for p in folder.iterdir()} - names
        if extra:
            raise BenchError(f"unexpected files in {folder}: {sorted(extra)}")
        for entry in group["files"]:
            target = folder / entry["name"]
            if target.is_symlink():
                raise BenchError(f"fit copy is a symlink: {target}")
            if not target.exists():
                with open(entry["source"], "rb") as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst, 1 << 20)
            checked_hash(target, entry["sha256"])
            entry["copy"] = str(target)
        group["folder"] = str(folder)


class Tap:
    """Temporarily wrap one object's method and retain successful call times."""

    def __init__(self, obj, name, invoke=None, timed=False):
        self.obj, self.name, self.timed = obj, name, timed
        self.original = getattr(obj, name)
        self.had_own = name in vars(obj)
        self.own = vars(obj).get(name)
        self.invoke = invoke
        self.times, self.attempts, self.errors = [], 0, 0

    def __enter__(self):
        setattr(self.obj, self.name, self)
        return self

    def __exit__(self, *exc):
        if self.had_own:
            setattr(self.obj, self.name, self.own)
        else:
            delattr(self.obj, self.name)

    def __call__(self, *a, **kw):
        self.attempts += 1
        t0 = time.perf_counter() if self.timed else None
        try:
            result = (self.invoke(self.original, *a, **kw) if self.invoke else self.original(*a, **kw))
        except Exception:
            self.errors += 1
            raise
        if self.timed:
            self.times.append(time.perf_counter() - t0)
        return result


class Instrumentation(ExitStack):
    """Single-process scope; global torch/numpy wrappers restored even on error.

    VJP means scalar cotangent directions, not Python calls: jacrev vmaps the
    pullback. Read each actual cotangent's hidden batch size, retaining both
    directions and pullback-call counts. Never multiply a configured 2N by 16.
    SBL gamma has one np.linalg.inv per MacKay/EM iteration; wrap inv only while
    that object's gamma runs. The final ep_site inverse is outside this scope.
    """

    def __init__(self, rx, kind):
        super().__init__()
        self.rx, self.kind = rx, kind
        self.forward = self.em_steps = 0
        self.vjp_widths = []
        self.h = []
        self.dtypes = {}

    def wrap(self, obj, name, invoke=None, timed=False):
        return self.enter_context(Tap(obj, name, invoke, timed))

    def inputs(self, original, *a, **kw):
        for i, value in enumerate(a):
            if hasattr(value, "dtype"):
                self.dtypes[f"H_arg{i}"] = str(value.dtype)
        return original(*a, **kw)

    def count_forward(self, original, *a, **kw):
        self.forward += 1
        self.dtypes["network_input"] = str(a[0].dtype)
        return original(*a, **kw)

    def count_vjp(self, original, *a, **kw):
        from torch.utils._pytree import tree_leaves
        import torch
        out = original(*a, **kw)
        pullback = out[1]

        def counted(cotangents, *args, **kwargs):
            ft = torch._C._functorch
            widths = []
            for t in tree_leaves(cotangents):
                width = 1
                while ft.is_batchedtensor(t):
                    dim = ft.maybe_get_bdim(t)
                    t = ft.get_unwrapped(t)
                    width *= t.shape[dim]
                widths.append(width)
            if not widths or len(set(widths)) != 1:
                raise BenchError(f"unrecognised VJP cotangent batch: {widths}")
            result = pullback(cotangents, *args, **kwargs)
            self.vjp_widths.append(int(widths[0]))
            return result

        return (out[0], counted, *out[2:])

    def count_gamma(self, original, *a, **kw):
        import numpy as np

        def count_inverse(inv, *args, **kwargs):
            result = inv(*args, **kwargs)
            self.em_steps += 1
            return result

        with Tap(np.linalg, "inv", count_inverse):
            return original(*a, **kw)

    def __enter__(self):
        super().__enter__()
        try:
            if self.kind == "score":
                import torch._functorch.eager_transforms as eager
                self.wrap(self.rx.prior.model.net, "forward", self.count_forward)
                self.wrap(eager, "_vjp_with_argnums", self.count_vjp)
                self.h = [self.wrap(self.rx.prior, "denoise", self.inputs, timed=True),
                          self.wrap(self.rx, "_matrix_site", timed=True)]
            else:
                self.h = [self.wrap(self.rx.prior, "ep_site", self.inputs, timed=True)]
                if self.kind == "sbl":
                    self.wrap(self.rx.prior, "gamma", self.count_gamma)
            return self
        except BaseException:
            self.close()
            raise

    def h_times(self):
        import numpy as np
        if len({len(t.times) for t in self.h}) != 1:
            raise BenchError("denoise / matrix_site call counts differ")
        return np.sum([t.times for t in self.h], axis=0).tolist()


def build_arms(a, snr, info):
    import common as C
    import runner as R
    import numpy as np
    cell, prior = ("C2", "S2") if a.cell == "D2" else ("C9", "UMi28")
    R.SPARSE = R.parse_sparse_arms("4,3,1,1") if a.cell == "U32" else None
    selected, metadata, reference = {}, {}, None
    for i, group in enumerate(info["groups"]):
        R._init(group["tag"])
        if Path(R.d_fits_d2()).resolve() != Path(group["folder"]):
            raise BenchError("runner fit routing differs from verified directory")
        p = R.build_point("D2", cell, prior, snr, NTRAIN,
                          stagec_ckpt=info["checkpoint"]["path"] if i == 0 else None,
                          ms_arm=a.ms_arm and i == 0)
        meta = p["meta"]
        gmm = p["arms"][BSTAR]
        if (meta.get("bstar"), int(meta.get("kron_K", -1)), gmm.prior.K) != ("kron", group["K"], group["K"]):
            raise BenchError(f"unexpected bstar/K: {meta.get('bstar')}, {meta.get('kron_K')}, {gmm.prior.K}")
        if not gmm.exact_prior or gmm.mode != "colored":
            raise BenchError("GMM is not on the runner ep_site path")
        label = BSTAR if a.cell == "D2" else f"{BSTAR}-K{group['K']}"
        selected[label] = (gmm, "gmm", group["K"])
        metadata[label] = dict(runner_arm=BSTAR, fits_tag=group["tag"],
                               **{"meta|bstar": meta["bstar"], "meta|kron_K": meta["kron_K"]})
        if i == 0:
            for name in [V1] + ([V1MS] if a.ms_arm else []) + (["SBL-loop"] if a.cell == "U32" else []):
                if name not in p["arms"]:
                    raise BenchError(f"{name} absent: {p['stagec']}")
                rx = p["arms"][name]
                kind = "sbl" if name == "SBL-loop" else "score"
                if kind == "sbl" and (rx.prior.n_em != 3 or rx.prior.warm or rx.prior.A.shape[1] != 2048):
                    raise BenchError("SBL differs from frozen rho=4, n_em=3, cold")
                selected[name] = (rx, kind, None)
                metadata[name] = dict(runner_arm=name, fits_tag=group["tag"],
                                      stagec_ckpt_id=meta.get("stagec_ckpt_id"), sparse=meta.get("sparse"))
            reference = {key: p[key] for key in ("gen", "code", "Nr", "Nt", "T", "Tp", "Xp", "pil")}
            reference["transmitter"] = p["arms"]["R5-genie"]
        elif not np.array_equal(reference["Xp"], p["Xp"]):
            raise BenchError("GMM groups have different pilots")
        for fit in p["fits"].values():
            fit.close()
        del p
        gc.collect()
    # Fixed base order, cyclically shifted each block as in bench_moduleH_ep.
    names = [V1] + [k for k in selected if k.startswith(BSTAR)]
    names += [n for n in ("SBL-loop", V1MS) if n in selected]
    selected = {k: selected[k] for k in names}
    if len({id(rx.prior) for rx, _, _ in selected.values()}) != len(selected):
        raise BenchError("arms share a prior instance")
    for name, (rx, kind, _) in selected.items():
        d = {key: str(getattr(rx, key).dtype) for key in ("Xp", "I_N", "I_Nr")}
        d["prior_C"] = str(rx.prior.C.dtype)
        if kind == "score":
            d["parameters"] = sorted({str(t.dtype) for t in rx.prior.model.parameters()})
            d["devices"] = sorted({str(t.device) for t in rx.prior.model.parameters()})
        if kind == "gmm":
            d.update({key: str(getattr(rx.prior, key).dtype) for key in ("U", "lam", "pi")})
        if kind == "sbl":
            d["dictionary"] = str(rx.prior.A.dtype)
        metadata[name]["dtypes"] = d
        metadata[name]["cfg"] = {key: value for key, value in rx.cfg_dump.items() if key != "Xp"}
    reference["prior"], reference["cell"] = prior, cell
    return reference, selected, metadata


def one_block(rx, kind, data, trial, position):
    import numpy as np
    Y, H, u, perm = data
    record = dict(trial=trial, order=position, run_s=float("nan"), h_s=float("nan"),
                  h_calls=0, forward=0, vjp=0, vjp_batches=0, em_steps=0,
                  iterations=0, exception="", early=False, nonfinite=False,
                  h_call_s=[], denoise_s=[], site_s=[], vjp_widths=[])
    result = None
    with Instrumentation(rx, kind) as tap:
        start = time.perf_counter()
        try:
            result = rx.run(Y, H, u, perm, NITER)
        except BenchError:
            raise
        except Exception as exc:
            record["exception"] = f"{type(exc).__name__}: {exc}"
        else:
            record["run_s"] = time.perf_counter() - start
    record.update(forward=tap.forward, vjp=sum(tap.vjp_widths),
                  vjp_batches=len(tap.vjp_widths), vjp_widths=tap.vjp_widths,
                  em_steps=tap.em_steps, h_calls=tap.h[0].attempts)
    if result is not None:
        record["iterations"] = min(len(result[k]) for k in ("blk_err", "nmse"))
        record["early"] = record["iterations"] != NITER
        record["nonfinite"] = any(not np.all(np.isfinite(result[k])) for k in ("blk_err", "nmse"))
        record["h_call_s"] = tap.h_times()
        record["h_s"] = float(sum(record["h_call_s"]))
        record["site_s"] = tap.h[-1].times
        record["denoise_s"] = tap.h[0].times if kind == "score" else []
    return record, result, tap.dtypes


def quantiles(values):
    import numpy as np
    return np.percentile(values, [25, 50, 75, 90]).tolist() if len(values) else [float("nan")] * 4


def write_results(a, metadata, rows, checks, txt, npz):
    import numpy as np
    raw = {"metadata_json": np.asarray(json.dumps(metadata, ensure_ascii=False, default=str))}
    lines = ["# E4 receiver cost — development stream, CPU, batch=1, outer iterations=16",
             "# Durations: milliseconds in table; seconds in NPZ. IQR=[Q25,Q75]; percentile method=linear.",
             "# H: score=prior.denoise + rx._matrix_site (paired calls); GMM=prior.ep_site; SBL=SparsePrior.ep_site (gamma updates + Gaussian site inverse).",
             "# Forward: model.net.forward entries, including the forward inside jacrev. VJP: observed cotangent directions; vjp_batches counts pullback entries.",
             "# SBL EM steps: completed inverses inside SparsePrior.gamma, one per MacKay iteration; the site inverse is excluded from this counter.",
             "# Exception timings are discarded. Early/nonfinite returns remain in raw but are excluded from summaries. Warm-up timings are not saved.",
             "# Timer/counter overhead is included; no overhead subtraction. Timing only; no cost claim or Pareto inference.",
             "# Metadata (including load, hashes, dtype, threadpools, command, seed and git):",
             json.dumps(metadata, ensure_ascii=False, indent=2, default=str), "",
             "cell | SNR | arm | rx median ms [IQR] | H share median | H/call median ms [IQR]; p90 | H/block median ms | H calls | forward/VJP; batches or EM | K | ok/exception/early/nonfinite"]
    for cell, snr, name, kind, k, records in rows:
        prefix = f"{cell}|{snr:+g}|{name}|"
        ragged = {"h_call_s", "denoise_s", "site_s", "vjp_widths"}
        if records:
            for key in records[0]:
                if key in ragged:
                    counts = [len(r[key]) for r in records]
                    raw[prefix + key] = np.asarray([v for r in records for v in r[key]],
                                                  dtype=int if key == "vjp_widths" else float)
                    raw[prefix + key + "_offsets"] = np.r_[0, np.cumsum(counts)]
                else:
                    raw[prefix + key] = np.asarray([r[key] for r in records])
        good = [r for r in records if not (r["exception"] or r["early"] or r["nonfinite"])]
        rq, hq, bq = [quantiles(v) for v in ([r["run_s"] * 1e3 for r in good],
                                            [x * 1e3 for r in good for x in r["h_call_s"]],
                                            [r["h_s"] * 1e3 for r in good])]
        share = quantiles([r["h_s"] / r["run_s"] for r in good])[1]
        counts = lambda key: ",".join(str(x) for x in sorted({r[key] for r in good})) or "NA"
        network = (f"{counts('forward')}/{counts('vjp')}; batches={counts('vjp_batches')}" if kind == "score"
                   else f"EM={counts('em_steps')}" if kind == "sbl" else "—")
        lines.append(f"{cell} | {snr:+g} | {name} | {rq[1]:.3f} [{rq[0]:.3f},{rq[2]:.3f}] | {share:.3%} | "
                     f"{hq[1]:.3f} [{hq[0]:.3f},{hq[2]:.3f}]; {hq[3]:.3f} | {bq[1]:.3f} | {counts('h_calls')} | "
                     f"{network} | {k or '—'} | {len(good)}/{sum(bool(r['exception']) for r in records)}/"
                     f"{sum(r['early'] for r in records)}/{sum(r['nonfinite'] for r in records)}")
        expected_vjp = NITER * 2 * (32 if cell == "D2" else 128)
        if kind == "score":
            lines.append(f"# COUNT_CHECK {cell} {snr:+g} {name}: expected forward=16 VJP={expected_vjp}; "
                         f"observed forward={counts('forward')} VJP={counts('vjp')}; "
                         f"forward_match={bool(good) and all(r['forward'] == 16 for r in good)} "
                         f"vjp_match={bool(good) and all(r['vjp'] == expected_vjp for r in good)}")
    for key, values in checks.items():
        raw["verify|" + key] = np.asarray(values)
    lines += ["", "# Verification arrays: verify|<cell>|<snr>|<arm>|<field>|tap/plain; exact equality required.",
              f"# Raw: {npz}"]
    # x/xb are intentional: refuse overwrite including races and dangling links.
    with npz.open("xb") as f:
        np.savez_compressed(f, **raw)
    with txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    for line in lines:
        if " | " in line or line.startswith("# COUNT_CHECK"):
            print(line, flush=True)
    print(f"OUTPUT {txt}\nOUTPUT {npz}", flush=True)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cell", choices=("D2", "U32"), required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--snr", type=int, nargs="+")
    p.add_argument("--trials", type=int, default=24)
    p.add_argument("--ms-arm", action="store_true")
    p.add_argument("--gmm", choices=("k4096", "gcap8192", "both"), default="both")
    p.add_argument("--force", action="store_true")
    p.add_argument("--verify-tap", action="store_true", help="untimed replay of the first measured development block for every arm")
    p.add_argument("--check-assets-only", action="store_true", help="verify all source hashes and exit without loading receivers")
    p.add_argument("--checkpoint", type=Path, help="alternate path, with the SAME pinned hash (also useful to check rejection)")
    p.add_argument("--out-dir", type=Path, default=OUT)
    p.add_argument("--d2-fits", type=Path, default=MAIN / "conf/results/gmm_fits_D2_B16e4k")
    p.add_argument("--u32-fits", type=Path, default=Path("/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4"))
    p.add_argument("--gcap-fits", type=Path, default=MAIN / "conf/results/gmm_fits_D2_U28NR32GCAP")
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", a.tag):
        p.error("tag must be 1..80 ASCII letters/digits/underscore/hyphen, starting with a letter/digit")
    if not 1 <= a.trials <= 24:
        p.error("trials must be 1..24 (24 is the E4 protocol; fewer is verification only)")
    if a.ms_arm and a.cell != "D2":
        p.error("V1-ms is the auxiliary D2 arm only")
    default_snr = [-3, 6] if a.cell == "D2" else [-3, 3]
    a.snr = a.snr if a.snr is not None else default_snr
    if len(set(a.snr)) != len(a.snr) or not set(a.snr).issubset(default_snr):
        p.error(f"SNRs must be a unique subset of {default_snr}")
    a.out_dir = inside(a.out_dir, OUT)
    return a


def main():
    a = parse_args()
    txt, npz = [a.out_dir / f"cost_{a.tag}.{ext}" for ext in ("txt", "npz")]
    for path in (txt, npz):
        if os.path.lexists(path):
            raise BenchError(f"refusing existing output: {path}")
    before = load_snapshot()
    print(f"START {before['date']}\n{before['uptime']}", flush=True)
    if before["busy"]:
        print(f"WARNING other compute processes: {len(before['busy'])}\n" + "\n".join(before["busy"][:8]), flush=True)
        if not a.force and not a.check_assets_only:
            raise BenchError("busy machine: measurement requires explicit --force; no receiver was loaded")
    info = check_assets(a)
    print("ASSET_SHA256_OK " + json.dumps(info, ensure_ascii=False), flush=True)
    if a.check_assets_only:
        return 0
    # Lazy imports (notably Sionna/matplotlib) must keep caches in this worktree.
    for name, leaf in (("XDG_CACHE_HOME", "xdg"), ("MPLCONFIGDIR", "matplotlib"),
                       ("TORCH_HOME", "torch"), ("TORCHINDUCTOR_CACHE_DIR", "inductor"),
                       ("NUMBA_CACHE_DIR", "numba"), ("TMPDIR", "tmp")):
        cache = inside(OUT / "cache" / leaf)
        cache.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(cache)
    try:
        import threadpoolctl
    except ModuleNotFoundError:
        # A local --target install permits operation under a worktree-only write
        # constraint. Prefer the environment's installation when it exists.
        sys.path.insert(0, str(inside(OUT / "deps")))
        try:
            import threadpoolctl
        except ImportError as exc:
            raise BenchError("threadpoolctl is required in the Python environment or cost/deps") from exc
    import numpy as np
    import torch
    import common as C
    import runner as R
    import score as S
    if C.N_ITER != NITER or C.DEV_SKIP0 != WARMUP:
        raise BenchError("runner defaults differ from pinned E4 iterations/development boundary")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    prepare_fits(info)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    metadata = dict(start=before, end=None, command=shlex.join([sys.executable, *sys.argv]),
                    args=vars(a), cwd=str(ROOT), host=platform.node(), affinity=sorted(os.sched_getaffinity(0)),
                    cpu=next((s.split(":", 1)[1].strip() for s in Path("/proc/cpuinfo").read_text().splitlines()
                              if s.startswith("model name")), "unknown"),
                    git_head=command(["git", "rev-parse", "HEAD"]),
                    git_status=command(["git", "status", "--porcelain=v1", "--untracked-files=all"]),
                    source_sha256={str(p.relative_to(ROOT)): sha256(p) for p in
                                   [Path(__file__), ROOT / "conf/code/runner.py", ROOT / "conf/code/arms.py",
                                    ROOT / "conf/code/score.py", ROOT / "conf/code/common.py",
                                    ROOT / "Demo/t2_route_a.py", ROOT / "Demo/t2_gmm.py", ROOT / "Demo/t2_trellis.py"]},
                    code_lock_ids={str(p): lock_id(p) for p in (ROOT / "conf/code", ROOT / "Demo")},
                    assets=info, python=platform.python_version(), numpy=np.__version__, torch=torch.__version__,
                    threadpoolctl=threadpoolctl.__version__, torch_threads=torch.get_num_threads(),
                    threadpoolctl_path=threadpoolctl.__file__, threadpoolctl_sha256=sha256(threadpoolctl.__file__),
                    torch_interop_threads=torch.get_num_interop_threads(), cuda_visible_devices=os.environ["CUDA_VISIBLE_DEVICES"],
                    threadpools_before=threadpoolctl.threadpool_info(), seed=C.SEED, rng={},
                    warmup_trial=WARMUP, measured_trials=[WARMUP + 1, WARMUP + a.trials],
                    verification_only=a.trials != 24, forced=a.force, concurrent_compute=bool(before["busy"]),
                    warmup_errors=[], points={}, tap_checks=[], status="incomplete")
    metadata["git_dirty"] = bool(metadata["git_status"])
    cid = S.ckpt_identity(info["checkpoint"]["path"])
    metadata["checkpoint_identity"] = cid
    if a.cell == "U32" and (cid["role"], cid["epoch"], cid["best_epoch"]) != ("best", 232, 232):
        raise BenchError(f"unexpected U32 checkpoint identity: {cid}")
    rows, checks = [], {}
    try:
        for snr in a.snr:
            # Build under a limit too; repeat after lazy Sionna/BLAS imports below.
            with threadpoolctl.threadpool_limits(limits=1):
                p, receivers, point_meta = build_arms(a, snr, info)
                metadata["points"][str(snr)] = point_meta
                rng = C.trial_rng("D2", p["prior"], p["Nr"], p["T"], p["Tp"], snr)
                metadata["rng"][str(snr)] = [C.SEED, C.TBID["D2"], C.PID[p["prior"]], p["Nr"], p["T"], p["Tp"], snr + 100]
                by_arm = {name: [] for name in receivers}
                rows.extend((a.cell, snr, name, kind, k, by_arm[name]) for name, (_, kind, k) in receivers.items())
                for trial in range(WARMUP + a.trials + 1):
                    # Exact runner stream replay: skipped inputs are generated then discarded;
                    # no receiver is evaluated on trial 0..2559 and no test raw is read.
                    H = p["gen"].sample(rng)
                    u = rng.integers(0, 2, p["code"].K)
                    perm = rng.permutation(p["code"].Ns)
                    _, Y = p["transmitter"].transmit(u, perm, H, rng)
                    if trial < WARMUP:
                        if trial % 512 == 0:
                            print(f"STREAM {a.cell} {snr:+g} advance={trial}/{WARMUP}", flush=True)
                        continue
                    R.A.CURRENT_TRIAL = trial
                    data = Y, H, u, perm
                    names = list(receivers)
                    shift = (trial - WARMUP) % len(names)
                    order = names[shift:] + names[:shift]
                    with threadpoolctl.threadpool_limits(limits=1):
                        pools = threadpoolctl.threadpool_info()
                        if torch.get_num_threads() != 1 or any(t["num_threads"] != 1 for t in pools):
                            raise BenchError(f"thread limit failed: {pools}")
                        if trial == WARMUP:
                            metadata["points"][str(snr)]["threadpools"] = pools
                            metadata["points"][str(snr)]["input_dtypes"] = dict(H=str(H.dtype), Y=str(Y.dtype))
                            print("THREADS torch=1 " + json.dumps(pools), flush=True)
                            metadata.setdefault("during", []).append(load_snapshot())
                        for position, name in enumerate(order):
                            rx, kind, _ = receivers[name]
                            core = getattr(rx.prior, "sp", rx.prior) if kind == "score" else None
                            cache_before = core._cache if core is not None else None
                            record, result, dtypes = one_block(rx, kind, data, trial, position)
                            metadata["points"][str(snr)][name]["observed_dtypes"] = dtypes
                            if trial == WARMUP:
                                if record["exception"] or record["early"] or record["nonfinite"]:
                                    metadata["warmup_errors"].append(dict(snr=snr, arm=name, error=record["exception"],
                                                                         early=record["early"], nonfinite=record["nonfinite"]))
                                continue
                            by_arm[name].append(record)
                            print(f"BLOCK {a.cell} {snr:+g} trial={trial} {name} H={record['h_calls']} "
                                  f"forward={record['forward']} VJP={record['vjp']} EM={record['em_steps']} "
                                  f"exception={record['exception']!r} early={record['early']}", flush=True)
                            if a.verify_tap and trial == WARMUP + 1:
                                if result is None:
                                    raise BenchError("cannot verify Tap on a failed block")
                                cache_after = core._cache if core is not None else None
                                if core is not None:
                                    core._cache = cache_before
                                plain = rx.run(*data, NITER)
                                if core is not None:
                                    core._cache = cache_after
                                equal = {}
                                for field in ("blk_err", "nmse"):
                                    key = f"{a.cell}|{snr:+g}|{name}|{field}"
                                    checks[key + "|tap"], checks[key + "|plain"] = result[field], plain[field]
                                    equal[field] = np.array_equal(result[field], plain[field], equal_nan=True)
                                metadata["tap_checks"].append(dict(snr=snr, arm=name, trial=trial, **equal))
                                print(f"TAP_CHECK {a.cell} {snr:+g} {name} {equal}", flush=True)
                                if not all(equal.values()):
                                    raise BenchError(f"Tap changed receiver result: {equal}")
            del receivers, p
            gc.collect()
        metadata["status"] = "complete"
    except BaseException as exc:
        metadata["status"] = "aborted"
        metadata["abort_reason"] = repr(exc)
        raise
    finally:
        metadata["end"] = load_snapshot()
        write_results(a, metadata, rows, checks, txt, npz)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BenchError, OSError) as exc:
        print(f"ABORT: {exc}", file=sys.stderr, flush=True)
        sys.exit(2)
