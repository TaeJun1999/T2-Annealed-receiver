| rho | n_em | gamma step (s, median/5) | block (s) | ep_site calls | max RSS (MiB) | W96 (h) | W119 (h) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 3 | 0.022855 | 4.765 | 16 | 881.8 | 0.247 | 0.199 |
| 4 | 10 | 0.016460 | 12.398 | 16 | 878.4 | 0.643 | 0.519 |
| 4 | 25 | 0.026556 | 39.051 | 16 | 878.0 | 2.025 | 1.633 |
| 8 | 3 | 0.069902 | 33.897 | 16 | 947.9 | 1.758 | 1.418 |
| 8 | 10 | 0.086128 | 43.338 | 16 | 948.5 | 2.247 | 1.813 |
| 8 | 25 | 0.077095 | 122.003 | 16 | 947.1 | 6.326 | 5.103 |
| 16 | 3 | 1.430304 | 124.065 | 16 | 1176.0 | 6.433 | 5.190 |
| 16 | 10 | 0.324233 | 295.339 | 16 | 1174.0 | 15.314 | 12.354 |
| 16 | 25 | 2.973147 | 774.184 | 16 | 1177.0 | 40.143 | 32.384 |

One development packet per row, no decoding outcomes retained. Timing under concurrent server load. Projection = block_sec * 17920 / W, ideal linear scaling, excludes setup/stream regeneration/IO; no parallel scaling or 7-SNR timing measurement. Gamma timing includes flat initialization. RSS is fresh-process high-water including block, five gamma probes and imports.
