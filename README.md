# 🌍 旅遊景點與交通查詢系統

> 🎯 這是一個 AI Agent 驅動的旅行資料庫系統，結合互動式前端行程規劃工具。

---

## 📁 專案結構

```
travel-planner/
├── SPEC.md                   # 系統規格文件（含 Phase 規劃）
├── README.md                 # 本文件
├── docker-compose.yml        # 容器化部署
├── Dockerfile                # Nginx 前端 Image
├── docker/
│   └── nginx.conf            # Nginx 設定
├── web/                      # 前端靜態檔（mounted to container）
│   ├── index.html            # 主頁面
│   ├── css/style.css         # 樣式（含 print 樣式）
│   ├── js/app.js             # 前端邏輯
│   └── data/                 # 前端可讀的 JSON 資料
│       └── fukuoka/          # （fukuoka 已啟用）
│           ├── attractions.json
│           ├── stations.json
│           ├── outlets.json
│           ├── itineraries.json
│           └── transport.json
├── data/                     # 完整資料庫（所有地區）
│   ├── regions.json          # 地區清單
│   ├── fukuoka/              # 日本福岡（enabled）
│   ├── kyushu/               # 日本九州（enabled）
│   ├── osaka/                # 日本大阪（enabled）
│   └── tokyo/                # 日本東京（enabled）
├── scripts/                  # 資料處理腳本
│   ├── generate_stations.py
│   ├── link_attractions_to_stations.py
│   ├── extract_outlets.py
│   └── enrich_attractions.py
└── docker/                   # Nginx 設定檔
```

---

## 🚀 快速啟動

```bash
cd /var/repo/travel-planner
docker compose build
docker compose up -d
# 開啟瀏覽器：http://localhost:8080
```

> ⚠️ 修改前端程式碼（web/）後需要 `docker compose build` + `docker compose up -d` 才能生效。
> 修改資料檔（data/）後需要重啟 container：`docker restart travel-planner`

---

## 📊 Phase 開發進度

| Phase | 項目 | 狀態 | 備註 |
|-------|------|------|------|
| Phase 1.1 | 地區資料建立（JSON）| ✅ 完成 | 4 地區（fukuoka/kyushu/osaka/tokyo）|
| Phase 1.2 | 表單邏輯調整 | ✅ 完成 | 8車站/4景點/2outlet；車站自動帶景點；景點自動推薦同站美食 |
| Phase 2 | 前端重構（Autocomplete）| ✅ 完成 | 車站/景點/outlet 均有即時搜尋建議 |
| Phase 3 | 行程輸出格式優化 | ✅ 完成 | 景點顯示來源標註（hostname）+ 三種連結按鈕（Maps/YouTube/部落格）；修復景點消失 Bug |
| Phase 4 | 驗證警告邏輯 | ✅ 完成 | 天數超容警告（⚠️）；父子景點連動自動帶入（ℹ️）|
| Phase 5 | 交通建議模組 | ✅ 完成 | 城市類型/機場交通/市區票卡/現金準備/換乘注意/自駕評估 |
| Phase 6 | Outlet 順路建議 | ✅ 完成 | 使用者選擇的 Outlet 自動加入行程（不佔景點額度）|
| Phase 7 | 列印功能 | ✅ 完成 | `@media print` 樣式強化：全寬、每日分頁、連結顯示 URL、來源標註 |

---

## 🗺️ 現有地區

| 地區 | 顯示名稱 | 景點數 | 車站數 | Outlet數 | 交通資料 |
|------|---------|--------|--------|---------|---------|
| osaka | 日本大阪 | ⚠️ 27（缺口：需補至135）| ⚠️ 31（缺口：需補至98）| 6 | ✅ |
| fukuoka | 日本福岡 | ✅ | ✅ | ✅ | ✅ |
| kyushu | 日本九州 | ✅ | ✅ | ✅ | ✅ |
| tokyo | 日本東京 | ✅ | ✅ | ✅ | ✅ |

> ⚠️ osaka 資料缺口已列入待辦（見下方待辦事項）

---

## 🔧 Phase 1.2 功能說明

### 表單欄位
- **車站錨點**：8 個欄位，支援 autocomplete，選了車站會自動把該車站的景點加入行程
- **必去景點**：4 個欄位，支援 autocomplete
- **Outlet**：2 個欄位，支援 autocomplete
- **用餐喜好**：多選晶片（燒肉/壽司/拉麵/懷石/居酒屋/甜點/海鮮/和牛/B級美食/早餐/宵夜/素食）
- **天數**：Range slider（1-10天）

### 自動推薦邏輯
1. **車站 → 景點**：選擇車站時，自動把同 zone 的景點（最多3個）加入行程
2. **景點 → 同站景點**：選擇景點時，自動推薦同 `station_id` 的其他景點（最多2個）
3. **景點 → 美食**：選擇景點時，自動推薦同 `station_id` 的美食，**優先匹配用餐喜好**（`selectedFoods` 與 `tags`/`sub_category` 匹配），分數最高者勝出
4. **天數不足**：容量公式 `(days-1)*2 + 1`，優先保留使用者選擇的景點，車站自動帶入的景點排在後面，超過容量則截斷

### 美食 Enrichment
所有美食資料均已補上 `details{}` 區塊：
- `google_maps`：Google Maps 連結
- `youtube`：YouTube 影片連結
- `blog_article`：部落格文章連結

---

## 🌐 前端操作說明

1. **選擇地區** → 載入該地區的景點/車站/outlet 資料
2. **填寫車站**（可選）→ 自動推薦該車站 zone 的景點
3. **填寫景點**（可選）→ 自動推薦同車站的景點與美食
4. **選擇用餐喜好** → 美食推薦時會優先匹配
5. **調整天數** → 系統自動計算容量上限
6. **點擊「生成行程」** → 輸出完整行程，含交通 anchor、景點、彈性用餐時段

---

## 📝 資料格式

### attractions.json
```json
{
  "attractions": [
    {
      "id": "osaka_att_001",
      "name": "大阪城",
      "name_en": "Osaka Castle",
      "category": "attraction",
      "zone": "大阪城·京橋",
      "station_id": "osaka_st_001",
      "stay_duration": "1.5-2小時",
      "ticket": "大人600円",
      "description": "豐臣秀吉建造的歷史名城...",
      "tags": ["古城", "賞櫻", "歷史"],
      "priority": 10,
      "details": {
        "google_maps": "https://maps.google.com/...",
        "youtube": "https://youtube.com/...",
        "blog_article": "https://..."
      }
    }
  ]
}
```

### stations.json
```json
{
  "stations": [
    {
      "id": "osaka_st_001",
      "name": "大阪城公園",
      "name_en": "Osaka Castle Park",
      "zone": "大阪城·京橋",
      "company": "JR",
      "lines": ["JR大阪環狀線"],
      "active": true
    }
  ]
}
```

---

## 📌 Commit 規範

```
Update {地區} - {更新項目} ({YYYY-MM-DD})
例：Update osaka - 新增海遊館周邊美食並補齊 details (2026-06-29)
```

---

## 🛠️ 開發指令

```bash
# 重建並啟動
docker compose build && docker compose up -d

# 查看 logs
docker logs -f travel-planner

# 進入 container 確認資料
docker exec -it travel-planner ls /usr/share/nginx/html/data/osaka/

# 強制刷新瀏覽器快取
Ctrl+Shift+R（Windows/Linux）
Cmd+Shift+R（macOS）
```