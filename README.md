# motion — 코드로 만드는 모션 그래픽

HTML Canvas로 모든 프레임을 시간 `t`의 함수로 그리고(`frame(t)`), 헤드리스 Chromium으로 캡처해 MP4로 만드는 작업 모음입니다.
사운드도 numpy로 합성해 화면 이벤트와 맞춥니다. 영상 생성 AI 없이 **코드만으로** 만든 결과물입니다.

## 작품 목록

| # | 작품 | 길이 | 스타일 | 사운드 |
|---|---|---|---|---|
| 01 | [디자인하는AI 쇼릴](projects/01-designingi-showreel/NOTES.md) | 15초 | 키네틱 타이포 · 모션 그래픽 쇼릴 | ✔ |
| 02 | [노아의 방주 (플랫)](projects/02-noah-flat/SCENARIO.md) | 10초 | 플랫 일러스트, 원 테이크 | ✔ |
| 03 | [노아의 방주 (잉크)](projects/03-noah-ink/NOTES.md) | 10초 | 크라프트지 · 펜 드로우온 · 6패널 인포그래픽 | ✔ |
| 04 | [노아의 방주 (잉크, 슬로우)](projects/04-noah-ink-slow/NOTES.md) | 15초 | 03을 1.5배 감속 | ✔ |
| 05 | [윤동주 「서시」 (별자리)](projects/05-seosi-stars/NOTES.md) | 16초 | G. 별자리 지도 | — |
| 06 | [윤동주 「서시」 (조각보)](projects/06-seosi-jogakbo/NOTES.md) | 16초 | J. 자수 · 조각보 | — |
| 07 | [다니엘과 사자굴 (쿠르츠게작트풍)](projects/07-daniel-kurzgesagt/NOTES.md) | 15초 | K. 쿠르츠게작트 인포그래픽 | — |
| 08 | [다니엘과 사자굴 (바이블프로젝트풍)](projects/08-daniel-bibleproject/NOTES.md) | 15초 | 크라프트지 · 펜 드로우온 · 6패널 인포그래픽 | — |
| 09 | [다니엘과 사자굴 (단면도 디오라마)](projects/09-daniel-nutshell/LOG.md) | 15초 | K. 쿠르츠게작트풍 단면도 — 07 재제작 (v1·v2 보존) | — |
| 10 | [동성애자인데 천국 갈 수 있을까요?](projects/10-heaven-question/LOG.md) | 76초 | K. 쿠르츠게작트풍 — 연구 리포트, 진지한 톤 | — |

스타일 기호(G·J·K 등)는 [STYLE_LIBRARY.md](STYLE_LIBRARY.md)를 따릅니다. 좋은 결과를 낸 프롬프트·판단·피드백은 [PLAYBOOK.md](PLAYBOOK.md)에 모읍니다. 시리즈 영상에서 스타일을 돌려쓰기 위한 목록과 공통 규칙이 정리되어 있습니다.

## 구조
```
README.md
STYLE_LIBRARY.md        시리즈용 스타일 목록 + 공통 규칙 + 돌려쓰기 방법
PLAYBOOK.md             작업 흐름 · 품질 체크리스트 · 프롬프트→결과 기록 · 배운 것
tools/
  render.py             프로젝트 → MP4 (오디오 생성 → 120fps 캡처 → 모션 블러 → 60fps)
  stills.py             지정 시각의 스틸 PNG 뽑기 (검수용)
  sheet.py              스틸들을 컨택트 시트로 묶기
  compare.py            여러 버전을 같은 시각으로 나란히 비교한 JPG 만들기
  setup_fonts.sh        fonts/ 채우기
fonts/                  (git 제외)
projects/NN-이름/
  index.html            애니메이션 (브라우저로 열면 실시간 재생)
  audio.py              사운드 합성 (없으면 무음으로 렌더)
  NOTES.md / SCENARIO.md  시나리오 · 연출 · 기법 노트
  LOG.md                버전별 사용자 프롬프트 원문 · 해석 · 변경 · 피드백 (재제작한 작품)
  versions/vN.html      사용자에게 보여준 버전 그대로 보존 + compare_*.jpg 비교 이미지
  out/                  렌더 결과 mp4·wav (git 제외)
```

## 시작하기
필요: Python 3 (numpy, scipy, pillow, playwright), ffmpeg(libx264), macOS 기준 경로.

```sh
pip install numpy scipy pillow playwright && playwright install chromium
zsh tools/setup_fonts.sh                     # 폰트 준비 (처음 한 번)
```

## 사용법
```sh
open projects/03-noah-ink/index.html                               # 브라우저 실시간 미리보기
python tools/stills.py projects/03-noah-ink /tmp/st 1,3,5          # 1·3·5초 스틸 뽑기
python tools/sheet.py /tmp/st /tmp/sheet 9                         # 스틸 모아보기
python tools/render.py projects/03-noah-ink --dur 10               # 최종 렌더 → out/03-noah-ink.mp4
python tools/render.py projects/01-designingi-showreel --dur 15 --grain 6 --crf 16
python tools/compare.py --out /tmp/cmp.jpg --times 1,5,9 projects/09-daniel-nutshell/versions/v1.html projects/09-daniel-nutshell/versions/v2.html
```
`--dur`은 각 프로젝트 `index.html`의 `DUR` 값과 맞춥니다(위 작품 목록의 길이).

## 폰트
용량과 배포 조건 때문에 git에 넣지 않고 `tools/setup_fonts.sh`로 채웁니다.

| 폰트 | 용도 | 라이선스 | 출처 |
|---|---|---|---|
| Pretendard | 본문·타이틀 | OFL | 로컬 설치본 복사 |
| Hack Nerd Font Mono | HUD·코드풍 문자 | MIT | 로컬 설치본 복사 |
| Black Han Sans, Gaegu, Nanum Pen Script | 손글씨·레터링 | OFL | Google Fonts 저장소에서 내려받기 |

## 새 프로젝트를 만들 때
- `projects/NN-이름/` 폴더를 만들고, 폰트는 `../../fonts/`로 참조합니다.
- `index.html`은 `window.ready`(폰트 로드 완료 Promise)와 `window.grab(t)`(PNG dataURL 반환)를 노출합니다. `?capture=1`이 없으면 requestAnimationFrame으로 실시간 재생합니다.
- 모든 움직임은 `t`만으로 결정합니다(난수는 `hr(i)` 해시 사용). 어느 프레임이든 같은 결과가 나와야 렌더가 재현됩니다.
- 다시 만들 때는 덮어쓰기 전에 `versions/vN.html`로 보존하고(폰트 경로 `../../../fonts/`), `LOG.md`에 프롬프트 원문과 피드백을 적은 뒤 `tools/compare.py`로 비교 이미지를 남깁니다. 자세한 흐름은 `PLAYBOOK.md`.
- 스타일은 `STYLE_LIBRARY.md`에서 고르고, 새 스타일은 같은 양식으로 추가한 뒤 「지금까지 만든 것」 표와 이 README의 작품 목록을 함께 갱신합니다.
- 렌더 중 화면이 검게 나오면 Chromium GPU 플래그를 끄세요(`render.py`는 기본값으로 실행).

## 레퍼런스와 저작권
일부 작품은 바이블프로젝트(BibleProject), 쿠르츠게작트(Kurzgesagt)의 **스타일을 참고**했습니다. 그림·캐릭터·영상은 복제하지 않았고 모든 그래픽은 코드로 새로 그렸습니다. 각 작품의 레퍼런스 출처는 해당 NOTES 문서에 적혀 있습니다.
