# 旅遊行程規劃系統 — 專案規格書

> 📌 版本：v0.2
> 🎯 更新日期：2026-07-22
> 🔖 基於 v0.1（2026-06-12）重寫

---

## 1. 系統定位

**目標**：建立一個「AI 驅動的旅行資料庫系統」，以 **景點資料庫** 為核心，結合行程模板自動生成使用者個人化的旅遊行程。

**核心價值**：
- **資料優先**：景點、美食、交通、行程資料齊備，且附有來源連結（Maps/YouTube/部落格）
- **模板 + 實資料**：行程以模板為骨架，真實 DB 資料為血肉
- **區域感知**：以「車站」為錨點，自動理解景點所屬 Zone，生成合理的路線

**使用情境**：
- 使用者選擇地區 → 系統自動生成含 5 個時段的每日行程
- 使用者可指定必經車站（最多 8 個）和必去景點（最多 4 個）
- 系統結合使用者用餐偏好與 DB 資料，自動推薦餐廳

---

## 2. 系統架構

### 2.1 元件架構

```
┌─────────────────────────────────────────────────────────────┐
│                     使用者瀏覽器                              │
│              http://localhost:8080/ (nginx)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ reverse proxy /api/
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              travel-api  (FastAPI :8001)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  REST API    │  │   SQLite     │  │  travel.db       │  │
│  │  /api/{region}│  │              │  │  • regions       │  │
│  │  /attractions│  │              │  │  • stations      │  │
│  │  /meals      │  │              │  │  • attractions   │  │
│  │  /stations   │  │              │  │  • meals         │  │
│  │  /outlets    │  │              │  │  • outlets       │  │
│  │  /itineraries│  │              │  │  • itineraries   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 部署方式

**Docker Compose**（兩容器）：
| 容器 | 技術 | Port | 職責 |
|------|------|------|------|
| `travel-planner` | nginx (靜態檔案) | 8080 | 前端靜態 HTML/CSS/JS |
| `travel-api` | FastAPI + SQLite | 8001 | REST API + 資料庫 |

**開發模式**：前端直接存取 `http://localhost:8001/api`（繞過 nginx）

### 2.3 資料隔離原則

- 靜態資料（HTML/JS/CSS）：透過 `docker-compose` mount `./web`
- 資料庫 `travel.db`：掛在 `./backend` volume，資料永久保存
- `web/data/` 僅含 `regions.json`（下拉選單用）和 `food_preferences.json`

---

## 3. 資料模型（Schema）

### 3.1 Entity Relationship

```
Region (1) ─── (N) Station
                    │
                    ├── (N) Attraction  ── category: attraction / hidden_gem / shrine / hotel
                    ├── (N) Meal
                    └── (N) Outlet
       (1) ─── (N) Itinerary
```

### 3.2 各資料表欄位

#### `regions`
| 欄位 | 類型 | 說明 |
|------|------|------|
| `code` | TEXT PK | 'seoul', 'osaka', 'tokyo'... |
| `name` | TEXT | 顯示名稱 |
| `name_en` | TEXT | 英文名稱 |

#### `stations`
| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | TEXT PK | 'seoul_001', 'osaka_001'... |
| `region_code` | TEXT FK | 關聯地區 |
| `name` | TEXT | 車站名（中文） |
| `name_en` | TEXT | 英文名 |
| `company` | TEXT | 經營者：MRT / JR / KTX... |
| `lines` | TEXT (JSON) | 路線陣列：["1號線","2號線"] |
| `zone` | TEXT | 所屬區域：龍山/弘大/麻浦... |
| `lat / lng` | REAL | 座標 |
| `radius_m` | INTEGER | 服務半徑（預設 600m） |
| `active` | INTEGER | 0=停用, 1=啟用 |

#### `attractions`
| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | TEXT PK | UUID 或短 ID |
| `region_code` | TEXT FK | 關聯地區 |
| `station_id` | TEXT FK | 主要車站（最近/地鐵優先） |
| `name / name_en` | TEXT | 名稱 |
| `category` | TEXT | `attraction` / `hidden_gem` / `shrine` / `hotel` |
| `sub_category` | TEXT | 細分類 |
| `zone` | TEXT | 所屬分區 |
| `location` | TEXT | 地址/描述 |
| `lat / lng` | REAL | 座標 |
| `ticket` | TEXT | 免費/付費/約XXX |
| `stay_duration` | TEXT | '1.5小時', '2小時' |
| `need_reservation` | INTEGER | 0/1 是否需預約 |
| `cash_only` | INTEGER | 0/1 是否只收現金 |
| `priority` | INTEGER | 1=必去, 3=普通, 5=閒逛 |
| `tags` | TEXT (JSON) | 標籤陣列：["市場","美食"] |
| `description` | TEXT | 敘述 |
| `sources` | TEXT (JSON) | 來源 URL 陣列 |
| `nearby_stations` | TEXT (JSON) | 附近車站 ID 陣列 |
| `details` | TEXT (JSON) | ```{google_maps, youtube, blog_article}``` |

#### `meals`
與 `attractions` 結構相同，額外欄位：
| 欄位 | 類型 | 說明 |
|------|------|------|
| `sub_category` | TEXT | '小吃' / '餐廳' / '咖啡' |

#### `outlets`
| 欄位 | 類型 | 說明 |
|------|------|------|
| `category` | TEXT | `outlet` / `shopping` / `convenience` |

#### `itineraries`
| 欄位 | 類型 | 說明 |
|------|------|------|
| `region_code` | TEXT FK | 關聯地區 |
| `day_key` | TEXT PK | 'day1', 'day2', ... |
| `name` | TEXT | 行程名稱 |
| `suitable_for` | TEXT | '商務/轉機客' / '家庭' / '情侶' |
| `layout` | TEXT | '單區精華' / '多區漫遊' |
| `days_json` | TEXT | 完整 JSON array（含所有天數 activities） |

---

## 4. API 端點

### 4.1 地區
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/regions` | 列出所有地區 |
| GET | `/api/regions/{code}` | 取得單一地區 |
| POST | `/api/regions` | 新增地區 |

### 4.2 車站
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/{region}/stations` | 列出地區所有車站（支援 `?zone=` / `?station_id=` 過濾） |
| GET | `/api/{region}/stations/{id}` | 取得單一車站 |
| POST | `/api/{region}/stations` | 新增或更新車站（upsert） |

### 4.3 景點
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/{region}/attractions` | 列出（支援 `?zone=` / `?category=` / `?station_id=` 過濾） |
| GET | `/api/{region}/attractions/{id}` | 取得單一景點 |
| POST | `/api/{region}/attractions` | 新增或更新景點 |
| DELETE | `/api/{region}/attractions/{id}` | 刪除景點 |

### 4.4 美食
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/{region}/meals` | 列出（支援 `?zone=` / `?station_id=` 過濾） |
| POST | `/api/{region}/meals` | 新增或更新美食 |

### 4.5 Outlets
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/{region}/outlets` | 列出（支援 `?zone=` / `?station_id=` 過濾） |
| POST | `/api/{region}/outlets` | 新增或更新 |

### 4.6 行程模板
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/{region}/itineraries` | 列出地區所有行程模板 |
| GET | `/api/{region}/itineraries/{day_key}` | 取得單一天模板 |
| POST | `/api/{region}/itineraries` | 新增或更新行程模板 |
| DELETE | `/api/{region}/itineraries/{day_key}` | 刪除 |

### 4.7 健康檢查
| Method | 端點 | 說明 |
|--------|------|------|
| GET | `/api/health` | 服務狀態確認 |

---

## 5. 前端功能規格

### 5.1 輸入欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| 地區 | Select 下拉 | 讀取 `data/regions.json`，動態顯示 `display_name` |
| 天數 | Range Slider | 1-10 天，即時顯示「X天Y夜」 |
| 同行人數 | Number | 目前未實際運用（預留） |
| 必經車站 | 8 個文字輸入（Autocomplete） | 輸入自動補齊車站名稱 |
| 必去景點 | 4 個文字輸入（Autocomplete） | 輸入自動補齊景點 |
| Outlet | 2 個文字輸入（Autocomplete） | 輸入自動補齊 |
| 用餐習慣 | 12+ 個 Checkbox | 燒肉/壽司/拉麵/懷石/居酒屋/甜點/海鮮/和牛/B級美食/早餐/宵夜/素食 |
| 其他需求 | Textarea | 自由文字敘述（年齡/親子/特殊需求） |

### 5.2 Autocomplete 機制

- **觸發**：200ms debounce 後發送
- **比對欄位**：`name` + `name_en`（以名稱為主）
- **優先順序**：`attraction` > `hidden_gem` > `outlet` > `meal`
- **車站 autocomplete**：僅比對 `state.stations`
- **封閉**：點擊 dropdown 外部或按 `Escape` 關閉

### 5.3 行程生成流程（核心邏輯）

```
使用者點擊「🚀 生成行程」
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 1：收集使用者輸入                   │
│  • wantStations（必經車站）               │
│  • wantItems（必去景點，4個）             │
│  • wantOutlets（想去的Outlet）           │
│  • selectedFoods（用餐偏好）             │
│  • selectedDays（天數）                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 2：建立 Zone Pool                 │
│  • 找出 wantStations 對應的 zone         │
│  • 找出 wantItems 所在 zone              │
│  • 找出 template activities 的 zone      │
│  • 合併去重 → enrichedZones             │
│  • 從 state.attractions/stations        │
│    建立 zone → items 對照表              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 3：比對模板景點名稱 → DB 實體      │
│  • 模板景點名（景福宮、北村韓屋村...）    │
│    → 比對 state.attractions[name]        │
│  • 匹配成功 → 加入 chosen 清單           │
│  • 匹配失敗 → 嘗試部分名稱匹配           │
│  • wantItems（用戶指定）→ 優先加入       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 4：Zone Pool 補充                  │
│  • 如果景點不足 2 個                     │
│  • 從 finalZones 隨機抽取 attractions   │
│  • 依舊去除已選過的（planned Set）       │
│  • Deep Fallback：若 pool 仍空，         │
│    擴大到全部可用 zone 隨機取            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 5：填充每個時段（5 slots）         │
│  • 上午 / 中午 / 下午 / 傍晚 / 晚上      │
│  • ① 模板有指定 → 使用模板（標記）        │
│  • ② 無模板 → 從 state.meals           │
│     按 zone 匹配未選過的                 │
│  • ③ 無合適 → Fallback 彈性用餐文字      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 6：車站錨點標記                    │
│  • 找出與 finalZones 對應的車站          │
│  • 插入 transport_anchor 活動             │
│  • 標記「必經車站：XXX」                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Step 7：繪製 UI                         │
│  • renderActivity() 處理每個活動         │
│  • 景點：📍 + 名稱 + 時間 + 票價         │
│    + 描述 + Maps/YouTube/部落格連結     │
│  • 餐廳：🍽️ + 名稱 + 連結（按鈕）       │
│  • 交通：🚇 + 說明文字                   │
│  • 購物：🛍️ + 名稱                     │
└─────────────────────────────────────────┘
```

### 5.4 每日時段結構

每個 Day 皆有 5 個時段：
| 時段 | 說明 |
|------|------|
| 上午 | 09:00-12:00 |
| 中午 | 12:00-14:00 |
| 下午 | 14:00-17:00 |
| 傍晚 | 17:00-19:00 |
| 晚上 | 19:00-21:00 |

**排程原則（不趕路）**：
1. 每日主要景點不超過 2 個
2. 必去項目優先排入
3. 秘境/Outlet 排在對應景點同一半天
4. 最後一天（離開日）只排半天（12:00 前），下午保留給機場/最後採買

### 5.5 連結呈現（Details 區塊）

每個景點/餐廳的 `details{}` 最多含三個連結：
| 連結類型 | 顯示文字 | 條件 |
|----------|---------|------|
| `google_maps` | 📍 Maps | 有值時顯示 |
| `youtube` | 🎬 YouTube | 有值時顯示 |
| `blog_article` | 📖 部落格 | 有值時顯示 |

**來源標註**（Attraction 限定）：
- 若 `sources[]` 有值，則顯示「📎 來源：」並列出各 URL 的 hostname

### 5.6 交通建議面板

選擇地區後，右側面板顯示：
| 項目 | 內容 |
|------|------|
| 城市類型 | 都會型（建議大眾交通）/ 郊區型（建議自駕） |
| 機場進入市區 | 方式、路線、時間、費用 |
| 市區交通 | 主交通、建议票卡、優惠票券 |
| 自駕評估 | 是否建議自駕 |

### 5.7 列印功能

- 按鈕：`🖨️ 列印行程`
- 機制：喚起瀏覽器 `window.print()`
- 樣式：去除裝飾，保留行程正文，適合 A4 紙張

---

## 6. 資料完整性分級

### 6.1 欄位分級（Data Completeness）

| 等級 | 欄位 | 說明 |
|------|------|------|
| **A（必填）** | `id`, `region_code`, `name`, `category` | 無法降級 |
| **B（重要）** | `station_id`, `zone`, `description`, `details{}` | 影響推薦品質 |
| **C（可選）** | `lat/lng`, `ticket`, `stay_duration`, `tags` | 增強體驗 |

### 6.2 連結充實度目標

每個景點/餐廳的 `details{}` 應逐步達到：
```
details {
  google_maps: "https://www.google.com/maps/place/xxx",   // ✅ 標配
  youtube: "https://www.youtube.com/results?search_query=xxx", // ✅ 標配
  blog_article: "https://xxx"  // ✅ 標配
}
```
- **景點**：`build_attractions.py` 自動建立 `details{}` 結構，`build_links.py` 補連結
- **美食**：`build_links.py` 補連結（逐步進行中）

---

## 7. 現有地區狀態

| 地區 | Attractions | Meals | Stations | Outlets | 狀態 |
|------|-----------|-------|---------|---------|------|
| seoul（韓國首爾） | 66 | 41 | 80 | 3 | ✅ |
| busan（韓國釜山） | 29 | 26 | 60 | 2 | ✅ |
| okinawa（日本沖繩） | 62 | 32 | 56 | 2 | ✅ |
| fukuoka（日本福岡） | 92 | 26 | 50 | 6 | ✅ |
| osaka（日本大阪） | 146 | 25 | 118 | 6 | ✅ |
| tokyo（日本東京） | 75 | 24 | 100 | 4 | ✅ |

---

## 8. 自動化腳本

### 8.1 建檔腳本（已完成）

| 腳本 | 功能 |
|------|------|
| `build_attractions.py` | 工廠模式生成 attractions.json（A/F/H/Sh 四類工廠） |
| `build_links.py` | 補 `details{}` 連結（blog/youtube/gmaps） |

### 8.2 資料庫遷移腳本

| 腳本 | 功能 |
|------|------|
| `migrate_region.py` | 將 JSON 資料寫入 SQLite |
| `migrate_seoul.py` | 首爾專用遷移腳本 |

### 8.3 cron 維運腳本

| 腳本 | 功能 |
|------|------|
| `attraction-updater.py` | 每週自動更新景點資料 |

---

## 9. Repo 結構

```
/var/repo/travel-planner/
├── SPEC.md                      # 本規格文件（v0.2）
├── README.md                    # 專案總覽
├── docker-compose.yml           # 容器编排
├── docker/
│   └── nginx.conf               # nginx 配置（API reverse proxy）
├── backend/
│   ├── app.py                   # FastAPI 主程式（384 行）
│   ├── schema.sql               # SQLite Schema
│   ├── requirements.txt         # Python 依賴
│   ├── Dockerfile
│   └── travel.db                # SQLite 資料庫（volume mount）
├── web/
│   ├── index.html               # 主頁（173 行）
│   ├── css/style.css            # 樣式（含 print 樣式）
│   ├── js/app.js                # 前端邏輯（1056 行）
│   └── data/
│       ├── regions.json          # 地區清單（6 區）
│       └── food_preferences.json # 用餐偏好
├── data/
│   └── {region}/                # 地區資料（JSON）
│       ├── attractions.json
│       ├── stations.json
│       ├── meals.json
│       ├── outlets.json
│       ├── itineraries.json
│       └── transport.json
├── scripts/
│   ├── build_attractions.py     # 景點建檔工廠
│   ├── build_links.py           # 連結充實腳本
│   ├── migrate_region.py         # DB 遷移
│   └── attraction-updater.py    # 每週 cron 更新
└── docs/
    ├── SESSION.md               # 工作流程會議記錄
    └── PLAN-station-based-v2.md # Phase 2 技術方案
```

---

## 10. 已知限制與未完成事項

### 10.1 已知的資料缺口

- **Tokyo attractions.json**：需全面重建（Phase 1 期間因需求變更中斷）
- **Meals 連結充實度**：部分 meals 缺少 `google_maps` 和 `youtube`，`blog_article` 已由 `build_links.py` 補上
- **同行人數**：輸入欄位存在但未實際運用

### 10.2 邏輯缺口

| 項目 | 說明 |
|------|------|
| 美食自動推薦 | `buildNormalDay` 的 meals 匹配邏輯需加強（Phase 1.2 已知問題） |
| Autocomplete 多人支援 | `wantStations` 與 `wantItems` 尚未真正支援多人不同路線 |

### 10.3 未來擴展方向

- [ ] 串接機票 API（Skyscanner / Google Flights）自動拉取航班價格
- [ ] 串接天氣 API，行程中標注建議攜帶物品
- [ ] 支援多語系輸出（繁中/簡中/英文/日文）
- [ ] 景點詳細頁（點擊景點展開完整資訊）
- [ ] 行程儲存/分享（URL 參數化）
- [ ] 使用者回饋（景點喜好學習）

---

## 11. 更新日誌

| 日期 | 版本 | 異動內容 |
|------|------|---------|
| 2026-06-12 | v0.1 | 初版：純靜態 Markdown 規劃 |
| 2026-07-22 | v0.2 | **全面重寫**：FastAPI + SQLite + Docker，前後端重構，行程生成邏輯實作 |
