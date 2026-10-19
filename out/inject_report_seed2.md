# 오류 주입 테스트 결과 (오류유형당 300건, 1셀씩 주입)

정상 데이터에서 검수 후보로 뜨는 셀(오탐): 34/10861 = 0.31%

**전체 검출률 2361/2400 = 98.4%  |  미검출 39건**

## 오류 유형별
| 유형 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| decimal_drop | 300 | 300 | 100.0% |
| decimal_shift | 300 | 300 | 100.0% |
| digit_drop | 300 | 300 | 100.0% |
| digit_insert | 299 | 300 | 99.7% |
| digit_swap | 291 | 300 | 97.0% |
| digit_confuse | 277 | 300 | 92.3% |
| cell_merge | 300 | 300 | 100.0% |
| cell_delete | 294 | 300 | 98.0% |

## 셀 종류별
| 셀 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| centers:lcg | 288 | 296 | 97.3% |
| centers:tcg | 247 | 254 | 97.2% |
| centers:vcg | 267 | 274 | 97.4% |
| centers:volume | 126 | 129 | 97.7% |
| centers:weight | 99 | 102 | 97.1% |
| sounding | 1334 | 1345 | 99.2% |

## 미검출 예시 (tank, page, sounding_in, field, 원본 → 변조)
- digit_insert: Cargo Tank #4 Port p28 s=0 lcg: `244.67` → `2444.67`
- digit_swap: Ballast Tank #1 Port & Stbd p32 s=456 lcg: `61.88` → `16.88`
- digit_swap: Cargo Tank #4 Stbd p29 s=402 volume: `11990` → `19190`
- digit_swap: Ballast Tank #2 p17 s=70 content_LT: `367.95` → `367.59`
- digit_swap: Ballast Tank #1 p16 s=2 content_LT: `7.31` → `7.13`
- digit_swap: Cargo Tank #1 Stbd p23 s=48 lcg: `66.21` → `66.12`
- digit_swap: Cargo Tank #5 Port p30 s=396 lcg: `303.67` → `330.67`
- digit_confuse: Ballast Tank #1 p16 s=75 content_LT: `289.69` → `289.59`
- digit_confuse: Cargo Tank #1 Stbd p23 s=42 lcg: `66.53` → `66.58`
- digit_confuse: Cargo Tank #3 (Port) p10 s=352 content_BBL: `10756` → `10755`
- digit_confuse: Cargo Tank #1 Stbd p23 s=6 tcg: `10.87` → `10.81`
- digit_confuse: Ballast Tank #5 p20 s=359 content_LT: `585.96` → `585.95`
- digit_confuse: Ballast Tank #3 p18 s=68 content_LT: `369.01` → `369.07`
- cell_delete: Cargo Tank #1 Stbd p23 s=402 volume: `9678` → `DELETE`
- cell_delete: Cargo Tank #3 Port p26 s=402 volume: `12014` → `DELETE`
- cell_delete: Ballast Tank #5 Port & Stbd p36 s=0 weight: `0.4` → `DELETE`
- cell_delete: Ballast Tank #5 Port & Stbd p36 s=0 weight: `0.4` → `DELETE`
- cell_delete: Cargo Tank #3 Stbd p27 s=0 vcg: `5.31` → `DELETE`
- cell_delete: Cargo Tank #4 Stbd p29 s=0 vcg: `5.31` → `DELETE`