# 오류 주입 테스트 결과 (오류유형당 300건, 1셀씩 주입)

**전체 검출률 1311/2400 = 54.6%  |  미검출 1089건**

## 오류 유형별
| 유형 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| decimal_drop | 120 | 300 | 40.0% |
| decimal_shift | 135 | 300 | 45.0% |
| digit_drop | 159 | 300 | 53.0% |
| digit_insert | 153 | 300 | 51.0% |
| digit_swap | 155 | 300 | 51.7% |
| digit_confuse | 133 | 300 | 44.3% |
| cell_merge | 289 | 300 | 96.3% |
| cell_delete | 167 | 300 | 55.7% |

## 셀 종류별
| 셀 | 검출 | 전체 | 검출률 |
|---|---|---|---|
| centers:lcg | 29 | 287 | 10.1% |
| centers:tcg | 0 | 259 | 0.0% |
| centers:vcg | 24 | 284 | 8.5% |
| centers:volume | 92 | 111 | 82.9% |
| centers:weight | 15 | 88 | 17.0% |
| sounding | 1151 | 1371 | 84.0% |

## 미검출 예시 (tank, page, sounding_in, field, 원본 → 변조)
- decimal_drop: Cargo Tank #2 Port p24 s=306 tcg: `16.80` → `1680`
- decimal_drop: Ballast Tank #5 Port & Stbd p36 s=36 lcg: `292.49` → `29249`
- decimal_drop: Cargo Tank #1 Stbd p23 s=306 vcg: `18.56` → `1856`
- decimal_drop: Ballast Tank #2 Port & Stbd p33 s=408 tcg: `26.45` → `2645`
- decimal_drop: Ballast Tank #1 Port & Stbd p32 s=210 weight: `416.0` → `4160`
- decimal_drop: Ballast Tank #5 Port & Stbd p36 s=12 vcg: `0.58` → `058`
- decimal_shift: Cargo Tank #4 Port p28 s=282 tcg: `16.89` → `168.9`
- decimal_shift: Cargo Tank #5 Stbd p31 s=354 vcg: `22.30` → `2.230`
- decimal_shift: Cargo Tank #3 Stbd p27 s=48 vcg: `7.41` → `74.1`
- decimal_shift: Ballast Tank #4 Port & Stbd p35 s=84 tcg: `20.30` → `203.0`
- decimal_shift: Cargo Tank #5 Port p30 s=246 tcg: `16.86` → `1.686`
- decimal_shift: Cargo Tank #4 Port p28 s=204 tcg: `16.87` → `1.687`
- digit_drop: Cargo Tank #4 Stbd p29 s=282 vcg: `17.16` → `17.6`
- digit_drop: Cargo Tank #5 Port p30 s=330 tcg: `16.89` → `16.9`
- digit_drop: Cargo Tank #2 Stbd p25 s=402 tcg: `16.77` → `1.77`
- digit_drop: Ballast Tank #3 Port & Stbd p34 s=126 lcg: `183.33` → `13.33`
- digit_drop: Cargo Tank #1 Port p22 s=174 tcg: `13.82` → `13.2`
- digit_drop: Ballast Tank #3 Port & Stbd p34 s=66 tcg: `19.67` → `19.6`
- digit_insert: Cargo Tank #1 Stbd p23 s=354 tcg: `14.10` → `14.110`
- digit_insert: Fuel Oil Tank (Stbd) p37 s=102 lcg: `244.67` → `2244.67`
- digit_insert: Cargo Tank #5 Stbd p31 s=18 lcg: `280.34` → `2880.34`
- digit_insert: Cargo Tank #5 (Port) p14 s=6 content: `7` → `77`
- digit_insert: Ballast Tank #1 Port & Stbd p32 s=324 vcg: `8.56` → `8.566`
- digit_insert: Fuel Oil Tank p21 s=10 content: `11` → `111`
- digit_swap: Cargo Tank #5 (Stbd) p15 s=125 content: `2042` → `2024`
- digit_swap: Fuel Oil Tank (Stbd) p37 s=108 lcg: `244.67` → `424.67`
- digit_swap: Cargo Tank #2 Port p24 s=366 lcg: `122.15` → `212.15`
- digit_swap: Ballast Tank #2 p17 s=244 content: `496.41` → `496.14`
- digit_swap: Cargo Tank #1 (Stbd) p7 s=275 content: `6664` → `6646`
- digit_swap: Ballast Tank #1 Port & Stbd p32 s=360 lcg: `62.05` → `62.50`
- digit_confuse: Ballast Tank #1 Port & Stbd p32 s=60 vcg: `2.66` → `2.65`
- digit_confuse: Ballast Tank #1 p16 s=31 content: `117.81` → `117.01`
- digit_confuse: Ballast Tank #5 p20 s=430 content: `637.04` → `637.09`
- digit_confuse: Ballast Tank #3 Port & Stbd p34 s=156 weight: `432.4` → `482.4`
- digit_confuse: Cargo Tank #4 (Port) p12 s=143 content: `4346` → `4345`
- digit_confuse: Ballast Tank #2 Port & Stbd p33 s=144 tcg: `21.88` → `21.80`
- cell_merge: Cargo Tank #5 (Port) p14 s=0 content: `1` → `MERGE`
- cell_merge: Fuel Oil Tank p21 s=46 content: `8950` → `MERGE`
- cell_merge: Ballast Tank #3 p18 s=7 content: `8` → `MERGE`
- cell_merge: Ballast Tank #1 p16 s=4 content: `5` → `MERGE`
- cell_merge: Ballast Tank #2 p17 s=3 content: `4` → `MERGE`
- cell_merge: Fuel Oil Tank p21 s=100 content: `19331` → `MERGE`
- cell_delete: Cargo Tank #1 Port p22 s=54 tcg: `12.84` → `DELETE`
- cell_delete: Ballast Tank #2 Port & Stbd p33 s=12 weight: `68.0` → `DELETE`
- cell_delete: Cargo Tank #5 Port p30 s=300 vcg: `19.99` → `DELETE`
- cell_delete: Fuel Oil Tank (Stbd) p37 s=120 vcg: `45.73` → `DELETE`
- cell_delete: Cargo Tank #2 Stbd p25 s=210 tcg: `16.81` → `DELETE`
- cell_delete: Ballast Tank #4 Port & Stbd p35 s=312 lcg: `244.66` → `DELETE`