gmm_fits_D2_n16e4_cpuEM -- preserved output of the CPU EM job (logs/fit_D2_n16e4.log, 180 configs, 2593.2 min, EXIT=0)
that finished 2026-09-23 09:14 KST (09-22 19:14 CDT) and OVERWROTE the 24 files of results/gmm_fits_D2_n16e4/, which
had already been produced by the GPU EM port (fit_gpu.py) and committed in cc3d40ab.

Action (review_next, 2026-09-23 12:27 KST): these 24 CPU-EM files were copied here unchanged; results/gmm_fits_D2_n16e4/
was restored to the committed GPU-EM versions (git checkout HEAD), i.e. to the files every B16e4 / B16e4k table used.
The npz files here are NOT committed (23 MB); this README and gmm_fit_D2_n16e4_cpuEM.txt (the CPU job's report) are.

CPU vs GPU EM, same configs (24 fits, Nr 4/8, full/kron, K 16..512, N_train 1.6e5):
  max relative |ll_val| difference 5.65e-04, max relative |covs| difference 5.9e-02 (some fits converged to a different
  EM solution), EM wall time summed: CPU 2,497,280 s vs GPU 95,443 s.
Impact: the headline b* (kron K=1024) lives in results/gmm_fits_D2_K1024n160000/ and was never touched; b* selection by
  ll_val is the same with either set.  The only run made while the CPU files were in place (review_next_A2, 09:25 KST)
  gives per-trial identical failures and NMSE for V1 and M-ours-bstar as the P1 cavity run made before the overwrite
  (same trials, same arms) -- but its meta|em_sec (1,592,046 s) counts CPU EM time and must not be read as the headline
  fit cost (headline: 107,957 s, run_manifest_B16e4k.json).
