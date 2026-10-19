"""Small analytical counter/guard checks and saved development-output audit.

Written by the implementer; these are NOT an independent golden review.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "conf/code"))
import bench_cost as B
import numpy as np
import torch
import torch._functorch.eager_transforms as eager


def counters():
    counter = B.Instrumentation(None, "score")
    original = eager._vjp_with_argnums
    with B.Tap(eager, "_vjp_with_argnums", counter.count_vjp):
        for dim, chunk, widths in [(3, None, [3]), (5, 2, [2, 2, 1]), (2, 1, [1, 1])]:
            counter.vjp_widths.clear()
            jac = torch.func.jacrev(lambda x: x*x, chunk_size=chunk)(torch.ones(dim, dtype=torch.float64))
            assert torch.equal(jac, 2*torch.eye(dim, dtype=torch.float64))
            assert counter.vjp_widths == widths
            print(f"VJP_COUNTER dim={dim} chunk={chunk} observed={widths} PASS")
    assert eager._vjp_with_argnums is original

    class Prior:
        def ep_site(self):
            return 1

    class Receiver:
        prior = Prior()

        def run(self, *args):
            self.prior.ep_site()
            raise ValueError("intentional receiver failure")

    record, result, _ = B.one_block(Receiver(), "gmm", (None,)*4, 2561, 0)
    assert result is None and record["exception"] == "ValueError: intentional receiver failure"
    assert np.isnan(record["run_s"]) and np.isnan(record["h_s"])
    assert record["h_call_s"] == [] and record["h_calls"] == 1
    assert "ep_site" not in vars(Receiver.prior)
    print("FAILED_BLOCK_TIMING_EXCLUSION / TAP_RESTORATION PASS")


def audit(path):
    with np.load(path, allow_pickle=False) as raw:
        meta = json.loads(str(raw["metadata_json"]))
        assert meta["status"] == "complete"
        assert meta["affinity"] == [66, 67]
        assert meta["torch_threads"] == meta["torch_interop_threads"] == 1
        assert meta["cuda_visible_devices"] == ""
        assert meta["measured_trials"] == [2561, 2561]
        assert meta["forced"] and meta["verification_only"]
        for snr, point in meta["points"].items():
            assert all(pool["num_threads"] == 1 for pool in point["threadpools"])
            for name, arm in point.items():
                if "bstar" in name:
                    expected = 1024 if meta["args"]["cell"] == "D2" else int(name.split("-K")[-1])
                    assert arm["meta|bstar"] == "kron" and arm["meta|kron_K"] == expected
        checked = 0
        for key in raw.files:
            if not key.endswith("|trial"):
                continue
            pre = key[:-len("trial")]
            assert raw[key].tolist() == [2561]
            assert raw[pre + "h_calls"].tolist() == [16]
            assert raw[pre + "iterations"].tolist() == [16]
            assert raw[pre + "exception"].tolist() == [""]
            assert not raw[pre + "early"].any() and not raw[pre + "nonfinite"].any()
            np.testing.assert_allclose(raw[pre + "h_s"][0], raw[pre + "h_call_s"].sum(), rtol=1e-14)
            assert raw[pre + "h_s"][0] <= raw[pre + "run_s"][0]
            if "dscore" in pre:
                expected_vjp = 1024 if pre.startswith("D2|") else 4096
                assert raw[pre + "vjp"].tolist() == [expected_vjp]
                # The measured implementation evaluates f(x) twice per query.
                assert raw[pre + "forward"].tolist() == [32]
                assert raw[pre + "vjp_batches"].tolist() == [16]
                assert raw[pre + "vjp_widths"].sum() == expected_vjp
                np.testing.assert_array_equal(raw[pre + "h_call_s"],
                                              raw[pre + "denoise_s"] + raw[pre + "site_s"])
            if "SBL-loop" in pre:
                assert raw[pre + "em_steps"].tolist() == [48]
            print(f"RAW_COUNTS {pre} H={raw[pre+'h_calls'].tolist()} "
                  f"forward={raw[pre+'forward'].tolist()} VJP={raw[pre+'vjp'].tolist()} "
                  f"EM={raw[pre+'em_steps'].tolist()} PASS")
            checked += 1
        for key in raw.files:
            if key.startswith("verify|") and key.endswith("|tap"):
                np.testing.assert_array_equal(raw[key], raw[key[:-3] + "plain"])
        assert len(meta["tap_checks"]) == checked and checked > 0
        assert all(x["blk_err"] and x["nmse"] for x in meta["tap_checks"])
        print(f"AUDIT {path.name}: rows={checked}, all Tap/plain trajectories exact, one thread PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args()
    counters()
    for file in args.files:
        audit(file)
