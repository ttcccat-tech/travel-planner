# weekly-station-food-update-2026-07-27

## 任務概覽
- Job ID: 8c3b55bc173d（車站美食週報）
- 日期: 2026-07-27
- 目標: 6 地區精選車站美食掃描

## 搜尋策略
- 大站（5個）: 新村周邊、釜山海雲台、福岡天神南、大阪天王寺、東京池袋
- 小站/新類型: 沖繩那霸機場、Osaka 天王寺區域擴充

## 本週來源站台
- `damei17.com`（大妹食旅日常）: Busan 海雲台 4 筆新發現
- `peikie.com`: Fukuoka 天神南 彌太郎烏龍麵（2025年6月新文章）
- `tokyo.letsgojp.com`: Tokyo 池袋 HALAL WAGYU RAMEN（2026年新文章）
- `ajunfun.tw`（阿君的玩食天堂）: 那霸機場/天王寺 跨區域擴充

## 去重分析
- URL 去重: `https://ajunfun.tw/kuukousyokudou/` 已在 om_ia033（空港食堂）存在 → skip
- `https://marukoblog.tw/los-fukuoka.html` 已在 fm_025 → skip
- `https://tokyo.letsgojp.com/archives/650158` 含多店但 URL 去重率高（tm_004/005/007/014 等已占用）

## 新增資料（7筆）
| ID | 名稱 | 地區 | 車站 | 分類 | 站台 |
|----|------|------|------|------|------|
| bm_028 | 百年食堂 | busan | busan_042（海雲台站）| 烤肉 | damei17.com |
| bm_029 | 高飯食堂 | busan | busan_042 | 烤肉 | damei17.com |
| bm_030 | 舒暢鱈魚湯 | busan | busan_042 | 海鮮 | damei17.com |
| bm_031 | 新華樓 | busan | busan_042 | 中菜 | damei17.com |
| fm_027 | 彌太郎烏龍麵 | fukuoka | fukuoka_005（天神南站）| 麵食 | peikie.com |
| tm_026 | HALAL WAGYU RAMEN SHINJUKU-TEI 池袋店 | tokyo | tokyo_004（池袋站）| 拉麵 | letsgojp.com |
| om_025 | 牛排屋88 那霸機場 | osaka | osaka_station_003（天王寺站）| 牛排 | ajunfun.tw |

## meals 表現況（2026-07-27 更新後）
```
seoul:     42 meals（無新增）
busan:     34 meals（+4: bm_028~031）
fukuoka:   27 meals（+1: fm_027）
osaka:     27 meals（+1: om_025）
tokyo:     26 meals（+1: tm_026）
okinawa:   34 meals（無新增）
Total:     190 meals（+7）
```

## 下週建議
- Seoul: 新村站（Sinchon）站點尚缺，需另找其他大站（江南站、教大站）
- Okinawa: 那霸機場站（okinawa_station_001）已有 om_ia016、om_ia033 高覆蓋，可往小祿站/首里站深挖
- Osaka: 天王寺區域高覆蓋（om_025 新增），可往北區（大阪站/淀屋橋）擴充
- Fukuoka: 天神南已有 fm_027，可往博多站/藥院站擴充
