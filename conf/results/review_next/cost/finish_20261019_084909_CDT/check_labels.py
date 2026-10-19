"""Reformat saved development outputs; no receiver/model load or new timing."""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COST = HERE.parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "conf/code"))
import bench_cost as B
import numpy as np
import torch

try:
    import threadpoolctl
except ModuleNotFoundError:
    sys.path.insert(0, str(COST / "deps"))
    import threadpoolctl


def check_code_scope():
    before = ast.parse((HERE / "bench_cost.before.py").read_text())
    after = ast.parse((ROOT / "conf/code/bench_cost.py").read_text())
    for tree in (before, after):
        tree.body = [node for node in tree.body
                     if not (isinstance(node, ast.FunctionDef) and node.name == "write_results")]
    assert ast.dump(before) == ast.dump(after)
    print("UNCHANGED_COUNTERS_TIMERS_HASH_REFUSALS_AST PASS")


def reformat(cell):
    source = COST / f"cost_{cell}_20261018_222512_CDT.npz"
    original_txt = source.with_suffix(".txt")
    target = HERE / f"cost_{cell}_labels_20261019_084909_CDT.npz"
    assert not target.exists() and not target.with_suffix(".txt").exists()
    originals = {p: B.sha256(p) for p in (source, original_txt)}
    with np.load(source, allow_pickle=False) as saved:
        meta = json.loads(str(saved["metadata_json"]))
        source_code_sha = meta["source_sha256"]["conf/code/bench_cost.py"]
        assert source_code_sha == B.sha256(HERE / "bench_cost.before.py")
        assert meta["verification_only"] and meta["measured_trials"] == [2561, 2561]
        meta["report_reformat"] = dict(
            generated_at=B.now(), source=str(source), source_sha256=originals[source],
            renderer_sha256=B.sha256(ROOT / "conf/code/bench_cost.py"),
            receiver_runs=0, note="Saved development data; original measurement metadata retained.")
        rows = []
        ragged = {"h_call_s", "denoise_s", "site_s", "vjp_widths"}
        for key in saved.files:
            if not key.endswith("|trial") or key.startswith("verify|"):
                continue
            prefix = key[:-len("trial")]
            cell_name, snr, name, _ = prefix.split("|")
            fields = [k[len(prefix):] for k in saved.files
                      if k.startswith(prefix) and not k.endswith("_offsets")]
            records = []
            for i in range(len(saved[key])):
                record = {}
                for field in fields:
                    array = saved[prefix + field]
                    if field in ragged:
                        offsets = saved[prefix + field + "_offsets"]
                        record[field] = array[offsets[i]:offsets[i + 1]].tolist()
                    else:
                        record[field] = array[i].item()
                records.append(record)
            kind = "score" if "dscore" in name else "sbl" if name == "SBL-loop" else "gmm"
            k = meta["points"][str(int(snr))][name].get("meta|kron_K")
            rows.append((cell_name, float(snr), name, kind, k, records))
        checks = {k[len("verify|"):]: saved[k] for k in saved.files if k.startswith("verify|")}
        with contextlib.redirect_stdout(io.StringIO()):
            B.write_results(None, meta, rows, checks, target.with_suffix(".txt"), target)
        with np.load(target, allow_pickle=False) as rendered:
            assert set(saved.files) == set(rendered.files)
            for key in saved.files:
                if key == "metadata_json":
                    continue
                a, b = saved[key], rendered[key]
                assert a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes(), key
            array_count = len(saved.files) - 1
    old_rows = [line for line in original_txt.read_text().splitlines() if line.startswith(cell + " | ")]
    text = target.with_suffix(".txt").read_text()
    new_rows = [line for line in text.splitlines() if line.startswith(cell + " | ")]
    assert old_rows == [line.replace("pullback_batches=", "batches=") for line in new_rows]
    assert "H calls/block (score: denoise)" in text
    assert "backbone forward/VJP directions; pullback batches" in text
    assert "This is not the denoise-call or cache-miss count" in text
    assert "observed backbone_forward=32 denoise_calls=16" in text
    assert "forward_match=False vjp_match=True" in text
    for p, digest in originals.items():
        assert B.sha256(p) == digest
    print(f"FORMAT_CHECK {cell}: rows={len(new_rows)} raw_arrays={array_count} byte_identical; numerical table cells unchanged PASS")
    print(f"ORIGINAL_OUTPUT_SHA256_UNCHANGED {cell} PASS")
    print(f"RENDERED {target.with_suffix('.txt')}")


if __name__ == "__main__":
    assert os.sched_getaffinity(0) == {1, 97}
    process_env = dict(item.split(b"=", 1) for item in Path(f"/proc/{os.getpid()}/environ").read_bytes().split(b"\0") if b"=" in item)
    assert process_env[b"CUDA_VISIBLE_DEVICES"] == b""
    print(f"RESOURCE pid={os.getpid()} affinity={sorted(os.sched_getaffinity(0))} CUDA_VISIBLE_DEVICES='' (/proc verified)")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    with threadpoolctl.threadpool_limits(limits=1):
        pools = threadpoolctl.threadpool_info()
        assert all(p["num_threads"] == 1 for p in pools)
        print(f"THREADS torch={torch.get_num_threads()} interop={torch.get_num_interop_threads()} pools=" + json.dumps(pools))
        check_code_scope()
        spec = importlib.util.spec_from_file_location("original_cost_check", COST / "check_cost_20261018_222512_CDT.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        for cell in ("D2", "U32"):
            checker.audit(COST / f"cost_{cell}_20261018_222512_CDT.npz")
            reformat(cell)
    print("LABEL_CHECKS_DONE receiver_runs=0 timing_measurements=0")
