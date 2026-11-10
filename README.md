# motion — 코드로 만드는 모션 그래픽

HTML Canvas로 프레임을 결정론적으로 그리고(`frame(t)`), 헤드리스 Chromium으로 캡처해 MP4로 만드는 작업 모음입니다.
사운드도 numpy로 합성해 화면 이벤트와 맞춥니다.

## 구조
```
STYLE_LIBRARY.md        시리즈용 스타일 10종 + 돌려쓰기 규칙
tools/
  render.py             프로젝트 → MP4 (오디오 생성 → 120fps 캡처 → 모션 블러 → 60fps)
  stills.py             지정 시각의 스틸 PNG 뽑기 (검수용)
  sheet.py              스틸들을 컨택트 시트로 묶기
  setup_fonts.sh        fonts/ 채우기 (폰트는 git 제외)
fonts/                  (git 제외)
projects/
  01-designingi-showreel/   유튜브 「디자인하는AI」 15초 쇼릴
  02-noah-flat/             노아의 방주 10초 — 플랫 일러스트, 원 테이크
  03-noah-ink/              노아의 방주 10초 — 잉크 일러스트, 패널 인포그래픽
```
각 프로젝트: `index.html`(애니메이션), `audio.py`(사운드), 문서(`NOTES.md`/`SCENARIO.md`), `out/`(결과물, git 제외).

## 사용법
```sh
zsh tools/setup_fonts.sh                                   # 처음 한 번
open projects/03-noah-ink/index.html                       # 브라우저 실시간 미리보기
python tools/stills.py projects/03-noah-ink /tmp/st 1,3,5  # 스틸 확인
python tools/render.py projects/03-noah-ink --dur 10       # 최종 렌더
python tools/render.py projects/01-designingi-showreel --dur 15 --grain 6 --crf 16
```
필요: Python 3 (numpy, scipy, playwright + chromium), ffmpeg(libx264).

## 새 프로젝트 규칙
- `index.html`은 `window.ready`(폰트 로드 완료 Promise)와 `window.grab(t)`(PNG dataURL 반환)를 노출
- `?capture=1`이 없으면 requestAnimationFrame으로 실시간 재생
- 모든 움직임은 `t`만으로 결정(난수는 `hr(i)` 해시 사용) → 어느 프레임이든 재현 가능
- 스타일은 `STYLE_LIBRARY.md`에서 고르고, 새 스타일은 같은 양식으로 추가
