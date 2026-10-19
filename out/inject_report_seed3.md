# 오류 주입 테스트 결과 (오류유형당 300건, 1셀씩 주입)

정상 데이터에서 검수 후보로 뜨는 셀(오탐): 34/10861 = 0.31%

**전체 검출률 2374/2400 = 98.9%  |  미검출 26건**

## 오류 유형별
| 유형 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| decimal_drop | 300 | 300 | 100.0% |
| decimal_shift | 300 | 300 | 100.0% |
| digit_drop | 299 | 300 | 99.7% |
| digit_insert | 298 | 300 | 99.3% |
| digit_swap | 295 | 300 | 98.3% |
| digit_confuse | 285 | 300 | 95.0% |
| cell_merge | 300 | 300 | 100.0% |
| cell_delete | 297 | 300 | 99.0% |

## 셀 종류별
| 셀 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| centers:lcg | 298 | 301 | 99.0% |
| centers:tcg | 242 | 248 | 97.6% |
| centers:vcg | 255 | 260 | 98.1% |
| centers:volume | 129 | 129 | 100.0% |
| centers:weight | 85 | 85 | 100.0% |
| sounding | 1365 | 1377 | 99.1% |

## 미검출 예시 (tank, page, sounding_in, field, 원본 → 변조)
- digit_drop: Cargo Tank #4 Stbd p29 s=402 tcg: `16.86` → `1.86`
- digit_insert: Ballast Tank #1 Port & Stbd p32 s=12 vcg: `0.55` → `00.55`
- digit_insert: Cargo Tank #5 Stbd p31 s=402 vcg: `23.96` → `223.96`
- digit_swap: Cargo Tank #5 Port p30 s=402 tcg: `16.81` → `61.81`
- digit_swap: Ballast Tank #4 Port & Stbd p35 s=0 tcg: `18.85` → `81.85`
- digit_swap: Cargo Tank #3 Stbd p27 s=0 vcg: `5.31` → `5.13`
- digit_swap: Ballast Tank #1 Port & Stbd p32 s=6 lcg: `67.57` → `67.75`
- digit_swap: Cargo Tank #5 Port p30 s=18 tcg: `14.89` → `14.98`
- digit_confuse: Cargo Tank #3 Stbd p27 s=258 vcg: `16.16` → `16.15`
- digit_confuse: Ballast Tank #5 p20 s=210 content_LT: `478.64` → `478.69`
- digit_confuse: Cargo Tank #4 (Port) p12 s=382 content_BBL: `11676` → `11675`
- digit_confuse: Fuel Oil Tank p21 s=62 content_GAL: `12027` → `12021`
- digit_confuse: Cargo Tank #5 (Stbd) p15 s=285 content_BBL: `6906` → `6905`
- digit_confuse: Ballast Tank #5 p20 s=192 content_LT: `461.82` → `461.87`
- cell_delete: Cargo Tank #4 (Port) p12 s=397 content_BBL: `12011` → `DELETE`
- cell_delete: Cargo Tank #3 Stbd p27 s=402 lcg: `183.33` → `DELETE`
- cell_delete: Ballast Tank #4 Port & Stbd p35 s=0 lcg: `244.03` → `DELETE`