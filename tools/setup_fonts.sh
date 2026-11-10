#!/bin/zsh
# fonts/ 폴더를 채웁니다. 폰트 파일은 용량 때문에 git에 넣지 않습니다.
# - Pretendard, Hack Nerd Font: 이 맥의 ~/Library/Fonts 에서 복사
# - Black Han Sans, Gaegu, Nanum Pen Script: Google Fonts 저장소(OFL)에서 내려받기
set -e
D="${0:A:h}/../fonts"; mkdir -p "$D"
for f in Pretendard-{Black,ExtraBold,Bold,SemiBold,Medium}.otf HackNerdFontMono-{Regular,Bold}.ttf; do
  cp ~/Library/Fonts/$f "$D/" || echo "없음: $f (직접 설치 필요)"
done
B=https://raw.githubusercontent.com/google/fonts/main/ofl
for p in blackhansans/BlackHanSans-Regular.ttf gaegu/Gaegu-Bold.ttf nanumpenscript/NanumPenScript-Regular.ttf; do
  curl -sfL -o "$D/${p:t}" "$B/$p" || echo "다운로드 실패: $p"
done
ls "$D"
