# Handoff — Topic T2: Annealed Turbo Receiver — Decoder-as-Score, Learned Channel Diffusion Prior, Bilinear Coupling

> **Document purpose.** Self-contained handoff for starting this research topic in a new Claude project. It records the thesis, notation, technical core, verified prior art (as of 2026-08-25), the novelty gap (and how fast it is closing), a work plan, and operating instructions for the receiving Claude.
>
> **Language protocol.** This document is written in English for precision. **The receiving Claude must conduct all conversation with the user in Korean (한국어).** Keep technical terms in English inside the Korean text (e.g., "외재 정보(extrinsic information)", "점수 함수(score function)"), use LaTeX for all mathematics, and match the user's register: researcher-level, definition → derivation → algorithm, no filler.

---

## 0. Read first — operating instructions for the receiving Claude

**Who the user is.** A wireless-communications researcher (physical layer) targeting IEEE TWC / JSAC / TSP / T-IT and ML venues (NeurIPS / ICML / ICLR). Deep working knowledge of turbo decoding (BCJR, extrinsic information, EXIT charts), JCESD (EM, turbo/code-aided estimation, factor graphs, BiG-AMP/OAMP/VAMP, unfolding, diffusion-based JCESD). Novelty first. The advisor's (Prof. Park) house style is encoded in a `paper-draft` skill; apply it when drafting paper text (never "utilize"/"superior", "optimal" only when proven, quantify, state scope, figures first).

**How this topic was selected.** Flagship of a five-topic portfolio that survived a two-round investigation (Aug 2026). Verdict of the prior-art report: **"appears open, but the gap is closing fast."** Its component on extrinsic coupling is Topic T1 (separate project); its theoretical guarantees are Topic T3 (separate project). Refer to them by name only.

**Standing conventions.** $u_k\in\{+1,-1\}$ with $0\mapsto+1$, $1\mapsto-1$; $L_c=2/\sigma^2$; $L=L_c y^s+L_a+L_e$. Block-fading MIMO $\mathbf Y=\mathbf H\mathbf X+\mathbf W$, $\mathbf X=[\mathbf X_p\ \mathbf X_d]$, $\mathbf H\in\mathbb C^{N_r\times N_t}$, $T$ symbols per block. Soft symbols $\bar x_n$, $v_n$ from LLRs. Reference tags: **[V]** verified in Aug 2026; **[M]** from memory, re-verify.

**Status date and verification duty.** As of 2026-08-25. The single most important action before any work: **read arXiv:2604.19061 (Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels) in full** and record (i) whether its channel is unknown/bilinear or a known nonlinearity, (ii) whether any *learned* channel prior is used, (iii) whether it uses a trellis (BCJR) denoiser or only LDPC BP. The residual novelty of T2 depends on these three answers (§4).

**First-session checklist.** (1) Do the 2604.19061 read and record the three answers. (2) Re-check arXiv for the keywords in §7. (3) Fix the target code family for the first experiment (recommendation: rate-1/2 convolutional code first, because BCJR makes the score exact). (4) Agree the figure list in §6.3.

---

## 1. Thesis

Two facts, combined, give a principled generative receiver for coded transmission over an unknown channel.

**Fact A (decoder = score).** Let $\mathbf x\in\mathcal A^{N}$ be a coded symbol vector and $\tilde{\mathbf x}_t=\mathbf x+\sigma_t\boldsymbol\epsilon$ its Gaussian corruption at noise level $\sigma_t$ (diffusion time $t$). Tweedie's formula gives
$$
\nabla_{\tilde{\mathbf x}_t}\log p_t(\tilde{\mathbf x}_t)=\frac{\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]-\tilde{\mathbf x}_t}{\sigma_t^2}.
$$
For BPSK-mapped bits of a convolutional code, $\mathbb E[x_k\mid\tilde{\mathbf x}_t]=\tanh(L(u_k)/2)$ where $L(u_k)$ is the a-posteriori LLR from **one BCJR pass with channel reliability $L_c(t)=2/\sigma_t^2$ and observations $y_k^s=\tilde x_{t,k}$**. The BCJR output is therefore the *exact* score of the discrete coded-symbol prior at that noise level. For turbo and LDPC codes the iterative decoder gives the corresponding approximation (its accuracy is characterizable by EXIT analysis). For QAM, the soft symbol is assembled from bit LLRs through the mapper. The diffusion time axis and the user's $L_c$ axis are the same axis.

**Fact B (learned channel prior).** A score network $s_\theta(\mathbf H_t,t)$ trained on channel realizations (3GPP CDL/TDL, ray-traced DeepMIMO, or measured data) provides the score of the channel prior at every noise level.

**Combination.** The joint posterior $p(\mathbf H,\mathbf X\mid\mathbf Y)\propto p(\mathbf Y\mid\mathbf H,\mathbf X)\,p(\mathbf H)\,P_{\mathcal C}(\mathbf X)$ is attacked by an annealed, alternating scheme in which the symbol denoiser is the channel decoder, the channel denoiser is $s_\theta$, and the two are coupled through the bilinear likelihood with **extrinsic (Onsager-corrected) messages** so that neither module consumes its own output (Topic T1 supplies the exact extrinsic channel estimate). The turbo iteration index becomes an annealing schedule: the a-priori reliability that grows over turbo iterations is the decreasing $\sigma_t$ of the sampler. The result is an "annealed turbo receiver" for joint channel estimation, detection, and decoding with reduced pilot overhead.

---

## 2. System model and notation

| Symbol | Meaning |
|---|---|
| $\mathbf Y=\mathbf H\mathbf X+\mathbf W$ | block-fading MIMO; $\mathbf W$ i.i.d. $\mathcal{CN}(0,\sigma^2)$ |
| $\mathbf X=[\mathbf X_p\ \mathbf X_d]$ | pilots and coded data; $\mathbf x=\mathrm{vec}(\mathbf X_d)$, $\mathbf x\in\mathcal A^{N}$, $N=N_tT_d$ |
| $P_{\mathcal C}(\mathbf X)$ | code-and-mapping prior (uniform on valid coded sequences, per stream) |
| $p(\mathbf H)$, $s_\theta(\mathbf H_t,t)$ | channel prior and its learned score |
| $\sigma_t$, $L_c(t)=2/\sigma_t^2$ | annealing noise level and the matching channel reliability |
| $\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]$ | code-constrained MMSE denoiser = decoder soft output |
| $\hat{\mathbf H}^{\setminus n}$ | extrinsic (leave-one-out) channel estimate for symbol $n$ (from T1) |

Complex Gaussian convention: for circularly symmetric noise with per-entry variance $\sigma_t^2$, Tweedie reads $\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]=\tilde{\mathbf x}_t+\sigma_t^2\,\nabla_{\tilde{\mathbf x}_t^*}\log p_t(\tilde{\mathbf x}_t)$ with the Wirtinger derivative; state the convention once in the paper and keep it fixed.

---

## 3. Technical core

### 3.1 Exactness of the decoder score (what to prove)

Proposition to write: for a terminated convolutional code (or any code whose bit-MAP decoder is exact), $\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]$ equals the vector of BCJR soft outputs under channel LLRs $L_c(t)\tilde x_{t,k}$; hence the score $\nabla\log p_t$ is computed exactly in $O(N\,2^\nu)$ per evaluation. For turbo/LDPC codes, bound the gap between the iterative decoder's soft output and the true conditional mean via the decoder's EXIT characteristic at input reliability $L_c(t)$; the gap vanishes at large $L_c(t)$ (late annealing) and is small at low $L_c(t)$ because both are near zero. This proposition is the paper's "Fact A" and should be stated as a lemma with proof.

### 3.2 Two instantiations of the coupling

**(a) Deterministic bilinear message passing ("bilinear turbo").** Modules: a linear-estimation module (given current means/variances of $\mathbf H$ and $\mathbf X$; the linear steps of BiG-AMP or BAd-VAMP), the symbol denoiser (decoder), and the channel denoiser ($s_\theta$ via Tweedie). Messages between modules are extrinsic means and variances. The Onsager/divergence terms are: for $\mathbf X$, exact from the decoder's posterior variances; for $\mathbf H$, via the divergence of the learned denoiser (Monte-Carlo trace or the Fisher-information trick of SC-VAMP). The extrinsic channel estimate for each symbol is the T1 leave-one-out estimate. Iterate 5–15 times with the noise level of the symbol denoiser set from the tracked message variance (this is the annealing schedule).

**(b) Sampling (annealed Langevin / stochastic localization on the joint).** As in Zilberstein–Swami–Segarra (2024) but with the decoder score in place of the uncoded constellation score for $\mathbf X$ and $s_\theta$ for $\mathbf H$; noise levels annealed; output the posterior mean (soft) or a MAP-like sample (hard). Each Langevin step on $\mathbf X$ costs one BCJR/BP pass.

Route (a) is the recommended primary; route (b) is the natural baseline/ablation and the bridge to T3's sampling corollary.

### 3.3 Annealing schedule as a turbo schedule

In a turbo receiver, the a-priori LLR reliability grows over iterations; in the sampler, $\sigma_t$ decreases. Define the schedule by the state-evolution-predicted effective SNR of the symbol messages (coordinate with T3): set $\sigma_t^2$ at iteration $i$ to the tracked variance of the extrinsic symbol message. This turns an arbitrary diffusion schedule into a derived quantity and is a distinguishing design element.

### 3.4 What is exact, what is approximate

Exact: decoder score for convolutional codes; leave-one-out extrinsic channel estimate (T1); bilinear likelihood. Approximate: learned $s_\theta$; iterative decoder for turbo/LDPC; Gaussian message approximations in route (a); finite annealing steps. State these boundaries explicitly in the paper.

### 3.5 Complexity

Per iteration: one decoder pass per stream ($O(T_d 2^\nu)$ for BCJR; $O(\text{edges}\times\text{inner iters})$ for LDPC BP) + one score-network evaluation on $\mathbf H$ + linear algebra $O(N_rN_tT)$. Compare against: turbo receiver with LMMSE re-estimation (same decoder passes, no score network) and BiG-AMP+decoder. Report per-block FLOPs and wall-clock separately; count inference only, and say so.

---

## 4. Prior art, the gap, and the residual novelty

| Reference | What it does | Relation |
|---|---|---|
| N. Zilberstein, A. Swami, S. Segarra, "Joint Channel Estimation and Data Detection in Massive MIMO Systems Based on Diffusion Models," ICASSP 2024, arXiv:2311.10311 [V] | Joint posterior sampling with a discrete constellation prior for symbols and a learned prior for channels | **Uncoded.** Direct predecessor; T2 adds the code via the decoder score |
| Generative-diffusion-driven alternating CE–DD frameworks (2024–2025; e.g., arXiv:2505.12382 as listed in the Aug-2026 report) [V] | Alternating channel estimation / data detection with predictor–corrector sampling; symbol score in closed form from the constellation | Uncoded; no decoder in the loop |
| SIC-aided diffusion JCESD, arXiv:2501.11229 [V] | Low-rank channels, SIC ordering | Uncoded |
| Y. Choukroun, L. Wolf, "Denoising Diffusion Error Correction Codes," ICLR 2023, arXiv:2209.13533 [V] | Decoding as a learned diffusion reverse process | Pure decoder, AWGN only |
| "Variational Diffusion Channel Decoder," arXiv:2605.18902 [V]; "Score Based Error Correcting Code Decoder," arXiv:2605.28358 [V] | Diffusion / score-based decoders (2026) | Pure decoders; no channel estimation |
| T. Wadayama, T. Takahashi, "Score-Based VAMP with Fisher-Information-Based Onsager Correction," arXiv:2601.07095 [V] | SISO modules as Tweedie MMSE estimators inside VAMP; Onsager via conditional Fisher information | Linear inverse problems; no bilinear/JCESD; no trellis decoder |
| **T. Wadayama, T. Takahashi, "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels," arXiv:2604.19061 [V, abstract only]** | A denoiser module that incorporates the code constraint via BP decoding; modules exchange extrinsic scalar-Gaussian messages with Onsager corrections | **Closest work.** Takes "BP decoder as score denoiser + Onsager extrinsic exchange". Must be read in full (see §0) |
| Y. Sun et al., "Trainable Joint Channel Estimation, Detection and Decoding for MIMO URLLC Systems," IEEE TWC 23(9), 2024, arXiv:2404.07721 [V] | Unfolded MAP-based JCDD with short LDPC; motivated by positive feedback in turbo receivers | Learned, non-generative; a baseline |
| M. Arvinte, J. I. Tamir, "MIMO Channel Estimation Using Score-Based Generative Models," IEEE TWC 22(6), 2023 [M] | Score-based channel prior for estimation | Channel-prior component |
| J. Ma, L. Ping, "Orthogonal AMP," IEEE Access 2017 [M]; J. Ma, X. Yuan, L. Ping, "Turbo compressed sensing with partial DFT sensing matrix," IEEE SPL 2015 [M] | Turbo-style extrinsic exchange between linear module and denoiser | Coupling template |
| J. T. Parker, P. Schniter, V. Cevher, BiG-AMP, IEEE TSP 2014 [V]; S. Sarkar, A. K. Fletcher, S. Rangan, P. Schniter, "Bilinear recovery using adaptive vector-AMP," IEEE TSP 2019 [M] | Bilinear message passing with Onsager terms | Route (a) skeleton |
| X. Kong, R. Brekelmans, G. Ver Steeg, "Information-Theoretic Diffusion," ICLR 2023, arXiv:2302.03792 [V]; "Random Walks with Tweedie," arXiv:2411.18702 [V] | Tweedie / I-MMSE background | Fact A background |

**Gap as verified (Aug 2026).** Diffusion-based JCESD is uncoded; diffusion/score decoders ignore the channel; 2604.19061 combines a BP-decoder denoiser with Onsager-corrected extrinsic exchange for *LDPC-coded nonlinear channels*. What was **not** found: (i) a *learned* (diffusion) channel prior inside a *bilinear* (unknown-$\mathbf H$) joint receiver with a code-constrained symbol score; (ii) the exact trellis (BCJR) score with the $t\leftrightarrow L_c$ identification; (iii) an annealing schedule derived from message variances / state evolution; (iv) the pilot-overhead-vs-BLER trade-off for coded short packets under such a receiver.

**Residual novelty, by scenario after reading 2604.19061:**
- If 2604.19061 uses a known/parametric nonlinearity and no learned channel prior → T2's novelty is (i)+(ii)+(iii)+(iv); proceed as planned.
- If it already includes an unknown channel with a learned prior → T2 narrows to (ii)+(iii)+(iv) and the short-packet/pilot-reduction regime; consider merging with T3 as the analysis paper.
- If it also includes a trellis decoder → T2 is reduced to (iii)+(iv); stop and reallocate effort to T3/T4/T5.

---

## 5. Contributions to claim (and not to claim)

Claim (conditional on §4 outcome):
1. A lemma establishing the channel decoder's soft output as the exact (convolutional) or EXIT-characterized (turbo/LDPC) score of the coded-symbol prior at every annealing level, with $L_c(t)=2/\sigma_t^2$.
2. A bilinear generative receiver combining that score with a learned channel score under extrinsic coupling; a schedule derived from message variances.
3. Quantified pilot-overhead reduction at fixed BLER on coded short packets, with gains attributed per baseline group (vs turbo receiver + LMMSE: the learned channel prior; vs uncoded diffusion JCESD: the code-aware score; vs 2604.19061-type receivers: the bilinear/learned-prior treatment — verify the last attribution after reading that paper).

Do not claim: Bayes-optimality of the receiver (not proven; T3 may provide asymptotic statements), robustness to prior mismatch unless measured, latency advantages unless measured.

---

## 6. Work plan

### 6.1 Milestones (9–14 months)
- **M1–M2.** Read 2604.19061; write the Fact-A lemma; implement the BCJR-score check (verify $\mathbb E[\mathbf x\mid\tilde{\mathbf x}_t]$ against brute force on a short block). Train a channel score model (start with CDL-B, $N_r\times N_t=8\times4$; angle-delay domain input if it trains faster).
- **M3–M5.** Implement route (a) with T1's extrinsic estimator; implement route (b) as an ablation; baselines (§6.2). First results on the convolutional code.
- **M6–M8.** 5G LDPC and LTE turbo variants; pilot-density sweep; schedule ablation (fixed vs variance-derived); complexity accounting.
- **M9.** ICASSP or GLOBECOM submission (convolutional-code core + one LDPC figure).
- **M10–M14.** Journal version (IEEE TWC/JSAC) with full code families, CDL/ray-traced/measured channels, and the T3 analysis hook.

### 6.2 Experimental design
Setting: Sionna; $N_t=N_r=4$ then $8\times4$ and $8\times8$; 16-QAM; codes: rate-1/2 convolutional ($\nu=6$), 5G LDPC (rate 1/2, $K\in\{512,1024\}$), LTE turbo; block-fading with $T\in\{14,28,56\}$; pilot fractions $T_p/T\in\{1/14,\dots,4/14\}$; channels: i.i.d. Rayleigh (sanity), CDL-B/C (main), DeepMIMO (site-specific), measured if available.
Baselines in groups: (i) pilot-only LMMSE + turbo receiver (code-aided re-estimation, a-posteriori and T1-extrinsic feedback); (ii) message passing: BiG-AMP + decoder; (iii) learned: Sun et al. 2024 JCDD if reproducible; (iv) generative: Zilberstein 2024 (uncoded comparison), a reimplementation of the 2604.19061 structure with a Gaussian channel prior; (v) genie CSI.
Metrics: BLER vs SNR at each pilot fraction; pilots saved at equal BLER (headline, quantified, with SNR range stated); channel NMSE; inference FLOPs/wall-clock; sensitivity to prior mismatch (train on CDL-B, test on CDL-C).

### 6.3 Figures to draft first
- **F1.** Receiver block diagram with three modules and extrinsic messages; the $t\leftrightarrow L_c(t)$ axis drawn along the iteration index.
- **F2.** Score exactness: BCJR soft output vs brute-force conditional mean across $L_c(t)$ (a one-panel sanity figure that also explains Fact A).
- **F3.** BLER vs SNR for three pilot fractions, baseline groups (i)–(v).
- **F4.** Pilots saved at target BLER vs $T$ (short-packet regime).

---

## 7. Risks, scooping watch, decision triggers

- **Scooping (high).** Wadayama–Takahashi (SC-VAMP line), Segarra/Zilberstein (diffusion JCESD), Schniter (bilinear message passing), Nachmani / Choukroun–Wolf (score decoders). Monthly arXiv keywords: `score-based VAMP LDPC channel`, `diffusion joint channel estimation decoding`, `decoder as denoiser diffusion`, `generative receiver coded bilinear`, `Tweedie BCJR`.
- **Technical.** Score-network quality on small $N_r\times N_t$ matrices; divergence estimation for the channel denoiser; BCJR cost per annealing step (mitigate with route (a)'s 5–15 iterations rather than 100-step sampling).
- **Triggers.** See §4 scenarios. Re-evaluate at the end of M2 and after every monthly arXiv check.

---

## 8. Venue plan

ICASSP 2027 / GLOBECOM 2027 (core lemma + convolutional-code results) → IEEE TWC or JSAC. Optional ML-venue workshop framing: "exact discrete-structured denoisers in diffusion posterior sampling" (the decoder as an exact score for a combinatorial prior), if the lemma and the schedule result are strong enough on their own.

---

## 9. Open questions for early discussion (ask one at a time)

1. Convolutional first (exact score) vs LDPC first (5G relevance) for the initial experiment.
2. Pixel-domain vs angle-delay-domain channel score model.
3. Route (a) as primary with route (b) as ablation, or the reverse.

---

## Appendix — Conversation protocol for the receiving Claude

- Reply in Korean; keep math in LaTeX; keep technical terms in English.
- Maintain a "결정 로그(decision log)" and a "스쿠핑 로그(scooping log)" with dates.
- When the user says "다음 단계" or "이어서", continue from the next unchecked milestone in §6.1.
- Ask at most one question per turn; propose a default.
- Apply the `paper-draft` house rules when drafting paper text.
