# H5 -- checkpoint / configuration provenance of the D2 supplementary BLER run

Verdict: **REFUTED.**  The supplementary run evaluated exactly the model it claims to have
evaluated.  One real bookkeeping defect was found (see D), but it changes no number and no
conclusion.

All numbers below are measurements made from this session, CPU only, OMP_NUM_THREADS=4.
Artifacts: checkpoint-provenance_{gbprime,hyvarinen,loadpath,table_compare}.json in this directory.

## (a) checkpoint identity

sha256(ckpt/d2sx_N10000_a1.pt) = d94aa99bdc5689067f90895b28d6394e7c61a296ed58ada3f041eb4ad8fdf01a
sha256(ckpt/B3_dscore_D2.pt)   = a76dacca132859ac722b55f11b324c09777b64078fefab56d6b0cdf552fc3402

Checkpoint metadata inside d2sx_N10000_a1.pt:
  rung=D2SX10000 attempt=1 testbed=D2 prior=S2 Nr=8 Nt=4
  split_hash=5340d785c2ad3eb6  best_val=0.3985658 @ep653  epoch=673  wall_sec=672.41867852211
  hp = {arch dit, param vp, domain angle, lr 0.002238046051591068, ema 0.999, batch 256,
        emb 256, width 64, depth 6, heads 8, patch 1}
(no git commit is recorded inside the checkpoint dict -- see D.)

HYVARINEN: reproduced from the checkpoint, n=2048, k=0, sigma=3.3062e-02, identical H/E/grid:
  recomputed SM = -14016.6442   stored in results/hyvarinen_D2_n1e4.npz = -14016.6442   rel dev 0.000e+00
=> results/hyvarinen_D2_n1e4.npz IS ckpt/d2sx_N10000_a1.pt.  Confirmed.

GB': results/gate_D2.txt was NOT produced by this checkpoint.  Recomputed GB' (n_eval=512, D2/S2 8x4,
frozen sigma grid) for every candidate, compared against the gate_D2.txt "nmse_diff" column:

  checkpoint                     max |rel dev| vs gate_D2.txt   worst_excess   diff/gmm range
  ckpt/B3_dscore_D2.pt                    3.7e-06  <== MATCH      -0.121905     0.5204 -> 0.8781
  ckpt/d2sx_N10000_a1.pt                  1.2e-02                 -0.122702     0.5157 -> 0.8773
  ckpt/d2sx_N10000_a2.pt                  1.3e-02                 -0.119890     0.5249 -> 0.8801
  ckpt/d2sx_N10000_a3.pt                  2.1e-02                 -0.121638     0.5268 -> 0.8784
  ckpt/d2sx_N2500_a1.pt                   1.8e-01                 -0.111021     0.5775 -> 0.8890
  ckpt/d2sx_N40000_a1.pt                  1.5e-01                 -0.127805     0.4598 -> 0.8722
  (recomputed nmse_gmm vs the recorded column: max rel dev 3.1e-06 -- table print rounding)

gate_D2.txt = B3_dscore_D2.pt, a SIBLING SEED: same hp dict, same split_hash 5340d785c2ad3eb6,
same testbed/prior/geometry, same 1e4 budget, different attempt (rung B3, 742 ep, val 0.4015161).
The GB' numbers for the checkpoint actually evaluated in BLER are essentially the same
(-0.1227 vs -0.1219; ratio 0.516->0.877 vs 0.520->0.878), so the substantive GB' claim survives
verbatim.  results/d2_gbprime.csv already carries the per-seed GB' at n_eval=4096
(N=1e4 a1: worst_excess -0.126715, ratio_min 0.505247, ratio_max 0.873285).

## (b) geometry vs cell C2

CELLS["C2"] = Nr=8 Nt=4 T=16 Tp=4, prior S2, testbed D2.
Checkpoint says Nr=8 Nt=4 testbed=D2 prior=S2.  MATCH.
ScorePrior built at Nr=8 Nt=4; its sigma window came out 0.033062 -- 0.845156, i.e. the frozen
results/sigma_grid_D2.npz (k=0 3.3062e-02, k=19 8.4516e-01), the same grid gate_D2.txt and the
Hyvarinen diagnostic use.  sigma.load() is NOT tag-aware, so --tag supp could not have swapped it,
and no sigma_grid_D2_supp.* exists.
No geometry mismatch.  This hypothesis's strongest failure mode does not apply.

## (c) what the arm loaded at run time

raw_supp meta recorded, in every one of the 112 point files:
  meta|dscore_ckpt          = 'ckpt/d2sx_N10000_a1.pt'
  meta|fit_sec|M-ours-dscore= 672.41867852  ==  the checkpoint's own wall_sec 672.41867852211,
                              a value unique among all D2 checkpoints
                              (B3 443.6, a2 556.8, a3 649.6, N2500 178.5, N4e4 3982.2, N1.6e5 4414.7)
  meta|dscore_status        = 'built from explicit ckpt ckpt/d2sx_N10000_a1.pt -- caller override,
                               NOT verified against the gate record here (recorded PASS rows: none)'
Replaying score.load_prior("D2","S2",8,4,ckpt="ckpt/d2sx_N10000_a1.pt") reproduces that status
string CHARACTER FOR CHARACTER and loads rung=D2SX10000 attempt=1 wall_sec=672.41867852211.
The pre-registered raw/ records instead 'ABSENT -- no GATE-PASSING checkpoint ...', i.e. the arm
was correctly absent there.  The override path is honest and self-labelling.

## (d) the gmm_fits_D2_supp symlink

results/gmm_fits_D2_supp -> results/gmm_fits_D2 (a symlink, same directory).

All 112 supplementary points exist at the SAME (snr, skip) in the pre-registered raw/.
Compared every shared key: 10528 (file, key) pairs over 112 files.
  keys that DIFFER : meta|dscore_status (112), meta|em_sec_note (112)  <- provenance STRINGS only,
                     the second differing solely by the directory NAME in the note text
  keys only in raw_supp : the 8 M-ours-dscore arrays + meta|dscore_ckpt + meta|fit_sec|M-ours-dscore
  keys only in raw      : none
  EVERY OTHER KEY IS BITWISE IDENTICAL, including meta|em_sec 14280.912514448166,
  meta|ll_val|kron -23.473386564228935, meta|bstar 'kron', meta|kron_K 512.

BLER@16 aggregates (Wilson 95%):
  arm            SNR   supplementary n=640      pre-reg same 640         pre-reg FULL n
  M-ours-bstar    -3   0.2594 (.227,.295)       0.2594 (.227,.295)       0.2523 (.236,.270) n=2560
  M-ours-bstar     0   0.0922 (.072,.117)       0.0922 (.072,.117)       0.0832 (.073,.095) n=2560
  M-ours-bstar   +3..+15  identical to the pre-registered values (same 640 trials)
  M-ours-gmm32    -3   0.2797 (.246,.316)       0.2797 (.246,.316)       0.2762 (.259,.294) n=2560
  M-ours-gmm32     0   0.0875 (.068,.112)       0.0875 (.068,.112)       0.0867 (.076,.098) n=2560
  R2-ours-G       -3   0.3156 (.281,.353)       0.3156 (.281,.353)       0.3285 (.311,.347) n=2560
  M-ours-dscore   -3   0.8047 (.772,.834)       ABSENT                   ABSENT
Where n differs (SNR -3, 0: pre-registered C2 runs n=2560, supplementary n=640) the supplementary
value is the exact first-640 subset of the pre-registered stream and the full-n value sits inside
the subset CI.  The symlink redirect changed nothing.
=> The harness is sound.  M-ours-dscore is the ONLY thing that differs, and it is genuinely new.

Code identity across the runs:
  Demo/ hashes identical in gate_D2.txt, tables_D2.txt and tables_D2_supp.txt
  (t2_route_a.py=95a5408901ec125c t2_trellis.py=31cd0ee9c68e972b t2_gmm.py=d064e58c7510c769).
  git diff 5e2e77a (tables_D2.txt) .. 85f6339 (tables_D2_supp.txt) over conf/code/{score,arms,common,
  runner}.py and Demo/ is EMPTY.
  git diff 86e43ef (gate_D2.txt) .. 85f6339 over conf/code/score.py is 7 lines: an `ntrain` parameter
  threaded into train() for the sample-complexity curve.  Training only; the denoiser / score /
  Tweedie / Jacobian path is untouched.

## D. the one real defect found

results/gate_D2.txt records the date, the git commit, the library versions, the Demo/ hashes, the
architecture dict and the GMM b*, but NOT the checkpoint path or its hash.  Nothing inside the file
distinguishes it from any sibling seed of the same configuration.  The tie to B3_dscore_D2.pt exists
only in logs/B3.log and in the file mtimes, and it took a recomputation to establish here.
That is exactly how the present confusion arose: the supplementary run's GB' evidence is in
results/d2_gbprime.csv, not in gate_D2.txt, and the two are easy to conflate because the numbers
are nearly equal.

Related, latent (NOT triggered here): score.load_model(ckpt, Nr, Nt) falls back to st["Nr"]/st["Nt"]
only when the caller passes None, and ScorePrior never asserts st["testbed"]/st["prior"] against the
cell being run -- st["testbed"] is used only to pick the sigma grid.  A checkpoint trained for the
wrong testbed or prior at the same geometry would load silently.  Here it was the right one.

Recommendation: write the checkpoint path + sha256 into the gate_*.txt header, and have ScorePrior
assert (testbed, prior, Nr, Nt) against the cell.  Neither changes any existing number.

## measurement coverage note (honest limits)

The Hyvarinen reproduction was run at the exact n=2048 of the recorded run and reproduced
k=0 (sigma=3.3062e-02) for ckpt/d2sx_N10000_a1.pt EXACTLY: -14016.6442 vs -14016.6442 recorded,
rel dev 0.000e+00.  The further rows I had queued (a1 at k=19; a2 and B3_dscore at k=0/k=19, as
negative controls) were ABANDONED, not measured: the shared machine hit load average 177 from the
parallel diagnostics plus the running GMM EM fit, and the job was starved.  I stopped it rather
than compete for CPU.

That does not weaken the identification.  A 9-significant-figure exact match pins the checkpoint by
itself, and a separate n=128 pass (different subsample, so not comparable to the stored table, but
comparable ACROSS models on identical samples) already separates the candidates cleanly at k=0:
  a1 -13766.3224   a2 -13391.6303   B3 -13800.8621   N2500 -10858.4820   GMM -2615.5560
i.e. the models are hundreds to thousands apart, far outside any rounding.
The "diff N=1e4 a2" column of hyvarinen_D2_n1e4.npz was therefore NOT independently re-verified;
only the a1 column, which is the one the BLER arm used, was.
