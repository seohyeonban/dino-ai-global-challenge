# OCR 벤치마크 (합성 열화)

원본: `11103-Sounding-Tables _sample1.pdf` 의 데이터 페이지 32쪽(6~37쪽). 시드 7.
정답 = PDF 텍스트 레이어의 단어+좌표를 각 이미지 좌표로 변환한 것(회전 포함, 눈으로 정렬 확인함).

| 변형 | 해상도 | 블러 | 노이즈 | JPEG | 기울기 | 대비 |
|---|---|---|---|---|---|---|
| clean_200 | 200dpi | – | – | PNG | 0 | 1.0 |
| scan_mild | 150dpi | 0.6 | 6 | q60 | ±0.6° | 0.95 |
| scan_hard | 100dpi | 1.0 | 12 | q35 | ±1.5° | 0.75 |
| scan_lowres | 70dpi | 0.8 | 8 | q50 | ±1.0° | 0.9 |

규모: 변형당 32쪽, 단어 15,898 / 숫자 11,651 / **소수점 숫자 6,050**.

## 구조
```
images/<variant>/pNN.(png|jpg)      OCR 입력
labels/<variant>/pNN.json           {w,h,dpi,angle,words:[{text,quad,is_number,has_decimal}]}
manifest.json                       생성 조건 · 통계
```

## 사용
```
# 생성 (재생성 약 1분)
.venv\Scripts\python.exe src\make_ocr_bench.py "11103-Sounding-Tables _sample1.pdf" out\ocr_bench

# 채점: OCR 결과를 pNN.json (= [{"text":"30.77","box":[x0,y0,x1,y1]}, ...]) 로 저장한 폴더 지정
.venv\Scripts\python.exe src\bench_score.py out\ocr_bench scan_hard <ocr_결과_폴더>
```
채점 항목: `exact / decimal_lost(30.77→3077) / merged(셀 붙음) / digit_error / other_wrong / missing`,
그리고 소수점 숫자만의 exact 비율.

## 채점기 자체 검증 (scan_hard, 가짜 OCR 출력)
정답 그대로 → exact 100%. 소수점 10% 삭제 → decimal_lost 5.12%(596). 인접 셀 5% 병합 → merged 8.46%.
끝자리 5% 변조 → digit_error 5.00%. 3% 누락 → missing 2.92%. 각 오류가 올바른 항목으로 집계됨.

## 한계
- 열화는 합성이다. 실제 스캔(구겨짐, 그림자, 스캐너 압축, 손글씨 메모, 표 선 번짐)은 더 거칠다.
- 원본 PDF가 1종 양식이라 양식 다양성은 측정하지 못한다.
- 아직 **실제 OCR 엔진을 돌리지 않았다** (설치 필요). 이 폴더는 입력과 채점 도구까지다.
- 정답에는 표 밖 단어(제목·도면 정보)도 있으나 채점은 숫자 토큰만 쓴다.
