# 오류 주입 테스트 결과 (오류유형당 300건, 1셀씩 주입)

정상 데이터에서 검수 후보로 뜨는 셀(오탐): 34/10861 = 0.31%

**전체 검출률 2361/2400 = 98.4%  |  미검출 39건**

## 오류 유형별
| 유형 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| decimal_drop | 300 | 300 | 100.0% |
| decimal_shift | 300 | 300 | 100.0% |
| digit_drop | 297 | 300 | 99.0% |
| digit_insert | 298 | 300 | 99.3% |
| digit_swap | 293 | 300 | 97.7% |
| digit_confuse | 278 | 300 | 92.7% |
| cell_merge | 300 | 300 | 100.0% |
| cell_delete | 295 | 300 | 98.3% |

## 셀 종류별
| 셀 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| centers:lcg | 295 | 305 | 96.7% |
| centers:tcg | 241 | 248 | 97.2% |
| centers:vcg | 285 | 292 | 97.6% |
| centers:volume | 105 | 107 | 98.1% |
| centers:weight | 105 | 106 | 99.1% |
| sounding | 1330 | 1342 | 99.1% |

## 미검출 예시 (tank, page, sounding_in, field, 원본 → 변조)
- digit_drop: Cargo Tank #5 Port p30 s=396 tcg: `16.82` → `1.82`
- digit_drop: Cargo Tank #2 Port p24 s=402 lcg: `122.15` → `22.15`
- digit_drop: Cargo Tank #4 Stbd p29 s=0 lcg: `244.67` → `44.67`
- digit_insert: Ballast Tank #2 Port & Stbd p33 s=0 vcg: `0.02` → `00.02`
- digit_insert: Ballast Tank #1 Port & Stbd p32 s=456 lcg: `61.88` → `661.88`
- digit_swap: Cargo Tank #5 Stbd p31 s=402 tcg: `16.84` → `16.48`
- digit_swap: Fuel Oil Tank (Stbd) p37 s=132 tcg: `23.73` → `23.37`
- digit_swap: Cargo Tank #3 Stbd p27 s=0 vcg: `5.31` → `5.13`
- digit_swap: Ballast Tank #5 p20 s=189 content_LT: `458.32` → `458.23`
- digit_swap: Ballast Tank #3 Port & Stbd p34 s=0 tcg: `18.79` → `18.97`
- digit_swap: Cargo Tank #2 Port p24 s=402 tcg: `16.73` → `16.37`
- digit_confuse: Cargo Tank #3 Stbd p27 s=222 vcg: `14.66` → `14.65`
- digit_confuse: Cargo Tank #5 Stbd p31 s=402 tcg: `16.84` → `16.04`
- digit_confuse: Cargo Tank #2 Stbd p25 s=276 lcg: `122.15` → `122.16`
- digit_confuse: Fuel Oil Tank p21 s=7 content_LT: `4.75` → `4.76`
- digit_confuse: Cargo Tank #1 (Port) p6 s=311 content_BBL: `7596` → `7595`
- digit_confuse: Ballast Tank #4 Port & Stbd p35 s=6 lcg: `244.62` → `244.52`
- cell_delete: Ballast Tank #4 Port & Stbd p35 s=450 tcg: `26.91` → `DELETE`
- cell_delete: Cargo Tank #3 (Stbd) p11 s=397 content_BBL: `11987` → `DELETE`
- cell_delete: Cargo Tank #1 (Stbd) p7 s=0 content_BBL: `3` → `DELETE`
- cell_delete: Ballast Tank #5 Port & Stbd p36 s=450 weight: `650.5` → `DELETE`
- cell_delete: Cargo Tank #1 Port p22 s=402 volume: `9702` → `DELETE`