# 서버 실험 공통 규칙 (모든 실험 프롬프트가 먼저 읽는다)

작성 2026-10-16 CDT. 이 파일은 실험별 프롬프트 (GMMCAP, SBL32, QAM16, E1MS, COST, FIG_PILOT) 와 함께 쓴다. 각 세션은 자기 프롬프트를 실행하기 전에 이 파일을 끝까지 읽는다.

## 1. 왜 이 실험들을 하는가

ICC 2027 (Signal Processing for Communications 트랙, 6쪽) 제출판을 보강한다. 논문은 채널 표본만으로 학습한 diffusion prior 를, 수신기 전체를 학습하지 않고 coded MIMO EP turbo receiver 의 channel prior 모듈 (module H) 로 연결한다. 제출판의 중심 주장은 세 가지다.

1. 연결 방법과 안정화 (등방 질의 → Tweedie 평균·Jacobian 공분산 → EP site → Hermitian-PSD floor).
2. 같은 training channels 로 학습한 강한 비교 대상보다 coded BLER 이 좋다. D2 8×4 는 통제·귀속, 3GPP UMi 28 GHz 32×4 는 보강한 비교를 갖춘 적용 결과.
3. 설계상 의미: 동결 prior 의 16-QAM 재사용, 파일럿–정보량 교환, 이득의 출처와 실제 수신 비용.

이번 실험은 2와 3의 근거를 보강하거나, 심사자가 제기할 반론 (GMM 용량 부족, SBL 튜닝 부족, 비용 미측정) 을 확인하는 것이다. 결과가 우리에게 불리해도 그대로 원고에 들어간다. 그래서 실험의 가치는 유리한 숫자가 아니라 사전에 정한 비교를 끝까지 깨끗하게 수행하는 데 있다.

## 2. 실험과 우선순위

| 우선 | 실험 | 프롬프트 | 시점 (CDT) |
|---|---|---|---|
| 1 | E2′ UMi32 GMM 용량 확인 | PROMPT_SERVER_GMMCAP.md | 10/17 적합 → 10/19–21 test |
| 1 | E3′ UMi32 SBL-loop 하나 | PROMPT_SERVER_SBL32.md | 10/18 개발 튜닝 → 10/19–21 test |
| 2 | E5 16-QAM, UMi8 주검증 | PROMPT_SERVER_QAM16.md | 10/18 구현·회귀 → 10/19–21 test |
| 3 | E4 실제 수신 비용 | PROMPT_SERVER_COST.md | 10/22–23, 다른 실행이 없을 때 |
| 4 | E5 16-QAM, D2 보조 평가 | PROMPT_SERVER_QAM16.md | UMi8 다음 |
| 5 | E1+ matched-scalar (D2 한 셀) | PROMPT_SERVER_E1MS.md | 핵심 test 실행을 건 뒤 (10/19 이후) |
| — | 파일럿 그림 (새 실행 없음) | PROMPT_FIG_PILOT.md | 아무 때나 |

**새 결과의 원고 반영 마감은 2026-10-24 18:00 CDT 다.** 그 뒤에 나온 결과는 원고에 넣지 않는다. 일정이 밀리면 우선순위가 낮은 것부터 멈추고, 멈춘 사실과 상태를 기록한다. 멈추는 기준은 결과가 좋고 나쁨이 아니라 이 표의 순서와 일정이다.

## 3. 절차 (기존 캠페인 절차 그대로)

등록 문서 `conf/results/review_next/NEXT_EXPERIMENTS_<TAG>.md` (§0–§5) → 적대적 검토 1회 → 반영 → 동결 커밋 = 실행 커밋 → 실행 → 수용 검사 (ACCEPT) → §6 전사 → 기록 감사 1회 → `docs/RESULTS.md` 새 절 → `conf/DECISIONS.md`·`EXPERIMENTS.md` 줄 (KST·CDT 병기, 기존 형식).

시간이 빠듯하므로 검토와 감사는 각각 한 번만 한다. 기존 등록 문서 (예: NEXT_EXPERIMENTS_SCALE16e4.md, NEXT_EXPERIMENTS_SPARSE16e4.md) 의 형식과 문구 규칙을 따른다.

## 4. 공통 규칙

**선택과 test 의 분리.** 모델 선택과 receiver tuning 은 train / validation / development 에서 끝낸다. test BLER 을 보고 checkpoint, fit, 설정을 고르지 않는다. test 를 보기 전에 다음을 등록 문서와 manifest 에 고정한다: 코드 commit, 셀 설정 (채널, 배열, T, T_p, pilot, modulation, payload), checkpoint·GMM fit 의 경로와 SHA-256, trial 범위와 RNG 규칙, SNR 격자, 반복 수, arm 목록, 선택 규칙, 효과량·구간 계산 방식, 예외·중단 규칙.

**평가 규칙 (기존과 같음).** 셀마다 SNR 당 n = 2560 test 블록 (기존 test trial 0..2559, 같은 셀의 기존 arm 과 같은 시행), 외부 반복 16회, BLER@16. 같은 셀의 arm 은 같은 채널·잡음·송신 블록에서 비교한다. 판정은 기존 표 B 규칙 (판정점 자동 선택, 판정점별 exact 양측 부호검정 p < .05, 2/3 규칙, power guard, 라벨 문자열) 과 SNR@0.1 격차의 90% paired bootstrap (B = 2000) 을 쓴다. 교차점이 격자 밖이면 censored 로 보고한다.

**결과와 무관한 보고.** "판정 못함" 도 완료된 결과다. 유의성을 얻으려고 SNR 점이나 표본을 추가하지 않는다. 사전에 정한 비교를 각각 보고하고, 유리한 것만 고르거나 여러 비교를 합쳐 승리 수를 늘리지 않는다. "동등", "비열등", "최적 GMM", "scaling law" 같은 표현은 쓰지 않는다.

**기록 보존.** 기존 raw, fit, checkpoint 를 덮어쓰거나 지우지 않는다. 새 실험은 새 tag 를 쓴다. tag 가 바뀌어도 checkpoint·fit routing 이 바뀌지 않도록 경로와 SHA-256 을 명시적으로 연결하고, 실행 전에 기존 manifest 의 값과 대조한다.

**기록상 값은 확인한 뒤 쓴다.** 프롬프트에 적힌 경로, sha, 격자, 실패 수는 기록에서 옮긴 것이다. 실행 전에 실제 파일·manifest 와 대조하고, 다르면 실행하지 말고 차이를 보고한다.

**계산 자원.** 수신기 BLER 은 기존 규칙대로 CPU 경로로만 잰다. 사용자 지시에 따라 CPU 는 192 코어 중 전체 합 약 96 스레드 이하로 쓴다. 워커 수 제한은 FIGHSYDMI16e4 v3 이후 쓰는 기존 방식을 따른다 (runner 가 os.cpu_count() 만큼 워커를 만들지 않게 확인). 시작 전에 다른 세션의 실행 (`ps`, `uptime`, `nvidia-smi`) 을 확인하고, 합이 96 스레드를 넘으면 기다리거나 사용자에게 순서를 묻는다. GPU 는 비어 있는 것만 쓰고, 다른 프로세스가 쓰는 GPU 에는 접근하지 않는다.

**확인이 필요한 행동.** 등록 범위 밖 변경, 자원 충돌, 되돌리기 어려운 작업 (raw·fit 삭제, force push, 기존 커밋 수정) 은 사용자에게 먼저 묻는다. 미리 정한 중단 규칙은 묻지 않고 적용한 뒤 보고한다.

**원고는 고치지 않는다.** 논문 저장소 (T2-ICC2027-paper) 와 main.tex 는 이 세션들의 범위 밖이다.

## 5. 사용자에게 보고하는 방식

단계가 끝날 때마다 한국어로 짧게 보고한다: 한 일, 핵심 수치 (출처 파일:줄), 다음 단계, 막힌 점. 숫자는 기록 파일에서 옮기고, 추정은 추정이라고 밝힌다. 최종 보고에는 원고에 들어갈 수치 (라벨, 판정점, ΣF, Δ0.1 [90%], 필요한 한정어) 를 표 한 개로 모은다.
