# 新地區建檔流程（2026-06-29 確立）

## 流程架構

每次新增一個地區，依序執行以下 4 個步驟：

```
Step 1 → 完善車站 stations.json
Step 2 → 完善景點 attractions.json
Step 3 → 自動推薦美食連結（系統已實作）
Step 4 → 補上景點連結（blog / youtube / gmaps）
```

---

## Step 1：完善車站 stations.json

### 目標
每個地區至少 40+ 站，覆蓋主要觀光zone

### 操作
```bash
# 已有腳本（大阪為範本）
python3 /var/repo/travel-planner/scripts/generate_stations.py

# 或手動建立 /var/repo/travel-planner/data/<region>/stations.json
# 格式：
{
  "region": "<region>",
  "updated": "YYYY-MM-DD",
  "stations": [
    {
      "id": "tokyo-keitokusita",
      "name": "惠比壽站",
      "name_en": "Ebisu",
      "zone": "東京",
      "lat": 35.6466,
      "lng": 139.7100,
      "lines": ["JR山手線","Metro日比谷線"]
    },
    ...
  ]
}
```

### 質檢
```bash
python3 -c "
import json
d = json.load(open('/var/repo/travel-planner/data/<region>/stations.json'))
print(f'{len(d[\"stations\"])} 站')
# 確認 all 有 lat/lng/lines
"
```

---

## Step 2：完善景點 attractions.json

### 目標
每個地區湊齊以下 4 類，參考大阪數量比例：
- attraction（景點）：目標 10-25 個
- hidden_gem（秘境）：目標 3-12 個
- food（美食）：目標 4-10 個
- shrine（神社）：目標 3-8 個

### 操作
```bash
# 執行生成腳本（需要先完成 stations.json）
python3 /var/repo/travel-planner/scripts/build_attractions.py
```

### 結構定義
Attractions.json 格式：
```json
{
  "region": "<region>",
  "updated": "YYYY-MM-DD",
  "attractions": [
    {
      "id": "tokyo_disney",
      "name": "東京迪士尼度假區",
      "name_en": "Tokyo Disney Resort",
      "category": "attraction",
      "sub_category": "theme_park",
      "location": "Disney Land站",
      "station": "JR武藏野線Disney Land站",
      "ticket": "自由通行券 9400円 / 指定日 9900円",
      "need_reservation": true,
      "stay_duration": "整天",
      "cash_only": false,
      "description": "...",
      "tags": ["主題樂園","親子","迪士尼"],
      "priority": 3,
      "zone": "Disney Land站",
      "station_id": "<stations.json 中的 id>",
      "nearby_stations": ["<station_id>"],
      "details": {
        "blog_article": [],
        "google_maps": "https://...",
        "youtube": []
      }
    }
  ]
}
```

### 質檢
```bash
python3 -c "
import json
d = json.load(open('/var/repo/travel-planner/data/<region>/attractions.json'))
att = d['attractions']
cats = {}
for a in att:
    cats[a['category']] = cats.get(a['category'],0)+1
null_sid = [a['name'] for a in att if not a.get('station_id')]
print(f'{len(att)} 景點 | categories={cats} | null_station_id={null_sid}')
"
```

---

## Step 3：自動推薦美食連結（系統實作，前端已上線）

前端 `app.js` 已實作：
- 使用者選車站 → 自動帶入同站景點（最多 2 個）+ 美食（最多 1 個）
- 使用者選景點 → 自動帶入同 zone 其他景點 + 美食
- 美食自動匹配用餐喜好（燒肉/壽司/拉麵等 checkbox）

此步驟**無需手動操作**，系統自動處理。

---

## Step 4：補上景點連結（blog / youtube / gmaps）

### 目標
所有景點 attractions.json 的 `details{}` 區塊要有：
- `blog_article[]`：官方網站或優質遊記（最少 1 個 URL）
- `google_maps`：Google Maps 搜尋 URL
- `youtube[]`：YouTube 搜尋 URL（可用 search_query 形式）

### 操作
```bash
# 執行補連結腳本
python3 /var/repo/travel-planner/scripts/build_links.py
```

### 質檢
```bash
python3 -c "
import json
d = json.load(open('/var/repo/travel-planner/data/<region>/attractions.json'))
att = d['attractions']
blog_ok = sum(1 for a in att if a['details']['blog_article'])
yt_ok   = sum(1 for a in att if a['details']['youtube'])
gmaps_ok = sum(1 for a in att if 'google.com' in a['details']['google_maps'])
print(f'blog={blog_ok}/{len(att)} yt={yt_ok}/{len(att)} gmaps={gmaps_ok}/{len(att)}')
"
```

---

## Git 提交範例

```bash
cd /var/repo/travel-planner

# Step 1 完成
git add data/<region>/stations.json
git commit -m "feat(<region>): add stations.json (N stations)"

# Step 2 完成
git add data/<region>/attractions.json
git commit -m "feat(<region>): add attractions (attraction/hidden/food/shrine)"

# Step 4 完成
git add scripts/build_links.py
git commit -m "feat(<region>): patch details{} links (blog/youtube/gmaps)"

git push
```

---

## 參考：現有資料統計（2026-06-29）

| 地區 | 車站 | Attraction | Hidden | Food | Shrine | 合計 |
|------|------|-----------|--------|------|--------|------|
| 大阪 | 98 | 62 | 66 | 6 | - | 134 |
| 東京 | 100 | 24 | 12 | 9 | 8 | 53 |
| 福岡 | 50 | 10 | 1 | 4 | 3 | 18 |
| 首爾 | 80 | 17 | 5 | 6 | 4 | 32 |
| 釜山 | 60 | 10 | 4 | 4 | 3 | 21 |
| 沖繩 | 40 | 10 | 3 | 4 | 3 | 20 |
