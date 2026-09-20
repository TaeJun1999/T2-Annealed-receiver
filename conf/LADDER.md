# LADDER — score model 사다리 시도 로그 (append-only)

> `04_SPEC_diffusion.md` §4. **모든 시도를 남긴다. 실패한 시도도 지우지 않는다.**
> 이 로그가 남아 있어야 나중에 "결과를 보고 고르지 않았다"를 보일 수 있다.
>
> 형식:
> `[시각] 칸 | 시도# | 구성 요약 | train/val loss | GA | GB | GC | GD | PASS/FAIL | 비고`

---

[2026-09-20 12:49 KST] L1 | a1 | mlp ve/pixel w256 d4 lr0.0002 ema0.999 (658240 par) | train 7.763e-01 / val 7.690e-01 | GA - | GB - | GC - | GD - | UNGATED | 249 ep (stop: patience), 80 s, 0.32 s/ep, device cuda:0 NVIDIA RTX PRO 6000 Blackwell Server Edition, ckpt /home/HTJ/t2/conf/ckpt/L1_a1_D1.pt (10.6 MB), split 98d6225d67f9c15a
