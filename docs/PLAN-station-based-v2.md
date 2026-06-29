# 新架構：車站搜尋 + 每日自選行程規劃

> **Hermes:** 使用 subagent-driven-development 技能逐 task 執行。

**目標：** 把現有「地區→天數→自動生成」改為「車站/景點/outlet → 每天自選 → 生成」的互動式行程規劃，並建立以車站為核心的景點資料庫。

**現況：**
- `zone`（行政區名）作為景點分組單位
- 前端：`地區下拉 → 天數下拉 → 自動生成行程`
- 景點隸屬於 zone，行程從 zone pool 抽牌

**新架構：**
- 以「車站」為搜尋/分組核心（每個地鐵站都是一個景點池）
- 景點同時記錄隸屬的 `station_id`
- 前端：Day1~Day10 各自有一個「車站/景點/outlet」輸入框（車站留空=景點或outlet），用戶自填或點選，每天可多個輸入
- 用餐習慣：系統自動依使用者選擇過濾當天車站周邊餐廳
- 資料庫化：日後可遷移到 MongoDB

---

## Phase 1：資料層重構（車站資料庫）

### Task 1：建立 `stations.json` — 大阪

**目標：** 建立大阪主要地鐵站清單，含基本欄位

**檔案：** `data/osaka/stations.json`（新建）

```json
{
  "stations": [
    {
      "id": "osaka_station_ud_01",
      "name": "大阪（梅田）",
      "company": "JR / 地下鐵",
      "line": ["JR大阪線", "地下鐵御堂筋線", "地下鐵四橋線"],
      "zone": "梅田",
      "lat": 34.7024,
      "lng": 135.4959,
      "radius_m": 800,
      "active": true
    }
  ]
}
```

**Step 1：建立 `scripts/generate_stations.py`**
- 使用 OpenStreetMap Nominatim API 自動查詢各站座標
- 輸出大阪 30-40 個主要車站

**驗證：** `python3 scripts/generate_stations.py --region osaka` → 檢查 `data/osaka/stations.json` 是否 30+ 筆

---

### Task 2：建立 `stations.json` — 福岡 / 東京 / 九州

**目標：** 建立其餘三區的 stations.json

**檔案：**
- `data/fukuoka/stations.json`
- `data/tokyo/stations.json`
- `data/kyushu/stations.json`

**Step 1：** 修改 `scripts/generate_stations.py` 加入 `--region` 參數
**Step 2：** 分別執行四個地區
**驗證：** 每個 stations.json ≥ 20 筆

---

### Task 3：建立 `attractions` 的 `station_id` 欄位

**目標：** 現有 attractions.json 的景點新增 `station_id`，對接到最近車站

**檔案：** `data/{region}/attractions.json`

**Step 1：** 撰寫 `scripts/link_attractions_to_stations.py`
- 讀取 attractions.json
- 讀取 stations.json
- 以景點 zone 找最近 station，寫入 `station_id`
- 若找不到 → `station_id: null`（慢慢補）

**驗證：** 統計 `station_id` 非 null 的比例

---

### Task 4：建立 `outlets.json`

**目標：** 把 outlets 從 attractions 分離出來，單獨管理（因為車站留空=outlet）

**檔案：** `data/{region}/outlets.json`（新建）

```json
{
  "outlets": [
    {
      "id": "outlet_001",
      "name": "天神大名潮牌街",
      "type": "outlet",
      "zone": "天神",
      "station_id": "fukuoka_station_01",
      "details": {
        "google_maps": null,
        "youtube": null,
        "blog_article": null,
        "fee": "免費",
        "stay_time": "2-3小時"
      }
    }
  ]
}
```

**驗證：** 每個地區 ≥ 3 筆 outlets

---

## Phase 2：前端 UI 重構

### Task 5：重新設計前端表單（每天自選）

**目標：** 將現有「天數下拉+必去景點輸入框」改為「Day1~Day10 每天各有一組輸入框」

**檔案：** `web/index.html`（修改）

**新 UI 結構：**
```
Day 1：
  [車站輸入框 / 景點名稱 / 留空=outlet]  [+新增] [X刪除]
  [車站輸入框 / 景點名稱 / 留空=outlet]  [+新增] [X刪除]

Day 2：
  [...同上...]

...Day 10

每天最多 3 個輸入， 超過 alert「取前三個」
```

**Step 1：** 修改 `index.html` 佈局
**Step 2：** 修改 `app.js` 的 form binding 邏輯
**Step 3：** 修改 `style.css` 樣式

**驗證：** 打開 http://localhost:8080，確認 Day1~Day10 輸入框都存在

---

### Task 6：車站自動完成（Autocomplete）

**目標：** 輸入車站名時，即時顯示候選車站（根據選擇的地區過濾）

**檔案：** `web/js/app.js`（修改）

**Step 1：** 前端 load `stations.json`（跟隨地區下拉過濾）
**Step 2：** 實作 autocomplete：監聽 input → 比對 station name → 顯示下拉候選
**Step 3：** 選中車站後，自動帶入該站的景點 hint

**驗證：** 地區選「大阪」→ Day1 輸入「難波」，顯示「難波（大阪地下鐵）」等選項

---

### Task 7：景點自動完成（Autocomplete）

**目標：** 輸入景點名稱時，即時顯示候選景點（名稱相似度排序）

**檔案：** `web/js/app.js`（修改）

**邏輯：**
- 選中車站 → 顯示該站半徑內所有景點（從 attractions.json filter）
- 不選車站 → 從全部景點 filter
- 用 `station_id` + `nearby_stations` 欄位做二次過濾
- 多個候選時 → 名稱相似度排序

**驗證：** Day1 輸入「環球」，顯示「日本環球影城（USJ）」

---

### Task 8：outlet 自動完成（車站留空時）

**目標：** 車站輸入框留空時，視為 outlet 模式，顯示 outlets.json 候選

**檔案：** `web/js/app.js`（修改）

**邏輯：**
- 車站 input 為空 → 顯示 outlets.json 的候選
- 景點名稱 input → 從 attractions.json filter（排除 outlets）

**驗證：** 車站框留空、景點框輸入，顯示 outlets 候選

---

### Task 9：用餐習慣多選框

**目標：** 新增「用餐習慣」多選區域，選項包含常見日本料理類型

**檔案：** `web/index.html`（修改）、`web/js/app.js`（修改）

**新增 UI：**
```
📋 用餐習慣（可複選）：
  [ ] 握壽司  [ ] 拉麵  [ ] 豬排飯  [ ] 燒肉
  [ ] 居酒屋  [ ] 定食  [ ] 咖哩飯  [ ] 烏龍麵
  [ ] 懷石料理  [ ] 串炸  [ ] 章魚燒  [ ] 御好燒
```

**資料格式：**
```javascript
const FOOD_PREFERENCES = [
  { id: "sushi",       label: "握壽司"     },
  { id: "ramen",       label: "拉麵"       },
  { id: "tonkatsu",    label: "豬排飯"     },
  { id: "yakiniku",    label: "燒肉"       },
  { id: "izakaya",     label: "居酒屋"     },
  { id: "teishoku",    label: "定食"       },
  { id: "curry",       label: "咖哩飯"     },
  { id: "udon",        label: "烏龍麵"     },
  { id: "kaiseki",     label: "懷石料理"   },
  { id: "kushikatsu",  label: "串炸"       },
  { id: "takoyaki",    label: "章魚燒"     },
  { id: "okonomiyaki", label: "御好燒"     }
];
```

**Step 1：** 在 index.html 的「同行人數」下方加入用餐習慣多選區塊
**Step 2：** 在 app.js 建立 `FOOD_PREFERENCES` 常數陣列
**Step 3：** 表單資料結構加入 `food_preferences: []`
**Step 4：** CSS 樣式（格子排列、選中 highlight）

**驗證：** 打開頁面，確認 12 種用餐習慣 checkbox 都顯示，且可多選

---

## Phase 3：行程生成邏輯重構

### Task 10：行程生成 — 輸入解析 + 車站擴展 + 用餐插入

**目標：** 解析使用者每天輸入的車站/景點/outlet，擴展為完整景點清單，並依用餐習慣插入餐廳

**檔案：** `web/js/app.js`（修改 `generateItinerary` 函數）

**新邏輯：**
```
Input: {
  region,
  days: [{ inputs: [{type: "station"|"attraction"|"outlet", value}] }],
  food_preferences: ["sushi", "ramen", ...]
}

Step 1 — 解析每個輸入：
  - type=station    → 根據 station_id 找半徑內所有 attractions + outlets
  - type=attraction → 直接納入（視為 user 指定景點）
  - type=outlet    → 直接納入（車站留空時用）

Step 2 — 合併同車站群：
  - 同 station 的景點群 → 去重 + 依 stay_time 排（短→長）

Step 3 — 用餐插入：
  - 每天找出 3 個用餐時段（早餐/午餐/晚餐）
  - 從當天已擴展景點的車站範圍內，找出 category=food 的景點
  - 再用 food_preferences 過濾 → 隨機選一個符合的餐廳
  - 插入到對應時段

Step 4 — 輸出：每天的景點清單（帶 details）
```

**驗證：**
- 輸入「難波站 + 道頓堀」→ 確認同一天出現難波周邊景點
- 選擇「拉麵+豬排飯」→ 行程午餐/晚餐出現拉麵或豬排飯選項

---

### Task 11：輸出格式（保留原有 UI）

**目標：** 行程卡片格式不變（景點名、費用、時間、連結），並加入用餐時段卡片

**檔案：** `web/js/app.js`（修改 `renderDayCard`）

**驗證：** 生成的行程卡片格式與現有一致，且用餐時段有餐廳卡片

---

## Phase 4：Enrichment 腳本升級

### Task 12：自動搜尋車站周邊景點

**目標：** 升級 enrichment script，每次執行時對沒有 `station_id` 的景點，自動搜尋最近車站並填入

**檔案：** `scripts/update_attractions.py`（修改）

**新增步驟：**
- 對每個 `station_id: null` 的景點
- 搜尋「景點名 + 最近的站」
- 找到則寫入 `nearby_stations[]` + 更新 `station_id`

**驗證：** 執行 `python3 scripts/update_fukuoka.py`，確認有 `station_id` 為 null 的景點被補上

---

### Task 13：自動發現並新增用餐習慣選項

**目標：** 當 enrichment script 搜尋景點時，若發現美食項目（category=food）且不屬於現有 12 種用餐習慣，自動將其新增至 `FOOD_PREFERENCES` 選單

**邏輯：**
- 美食景點有 `food_tags` 或從 `name` 分析出類型
- 若分析的 food type 不在 `FOOD_PREFERENCES` 內 → 寫入 `data/food_preferences.json`
- 前端 autocomplete 時一併載入動態發現的用餐習慣

**資料格式：** `data/food_preferences.json`
```json
{
  "static": [
    { "id": "sushi", "label": "握壽司" },
    ...
  ],
  "discovered": [
    { "id": "fukuoka_mentaiko", "label": "明太子" },
    { "id": "osaka_takoyaki", "label": "章魚燒" }
  ]
}
```

**驗證：** enrichment 時發現新的食物類型 → 自動寫入 food_preferences.json

---

## Phase 5：資料庫化預備（MongoDB）

### Task 14：建立 MongoDB schema 文件

**目標：** 確立 MongoDB collection 結構，為日後遷移做準備

**檔案：** `docs/mongodb-schema.md`（新建）

```markdown
## Collection: attractions
{
  _id: ObjectId,
  region: String,
  name: String,
  category: String,
  zone: String,
  station_id: String,
  nearby_stations: [String],
  details: { google_maps, youtube, blog_article, fee, stay_time, phone },
  sources: [String],
  last_enriched: Date
}

## Collection: stations
{
  _id: String,
  region: String,
  name: String,
  company: [String],
  line: [String],
  location: { type: "Point", coordinates: [lng, lat] },
  radius_m: Number,
  active: Boolean
}

## Collection: food_preferences
{
  _id: ObjectId,
  id: String,
  label: String,
  source: String,  // "static" | "discovered"
  discovered_at: Date
}
```

---

## 執行順序（Phase 1 → 5）

```
Phase 1（資料重構）→ Task 1~4
    ↓
Phase 2（UI 重構）→ Task 5~9
    ↓
Phase 3（生成邏輯）→ Task 10~11
    ↓
Phase 4（Enrichment）→ Task 12~13
    ↓
Phase 5（DB 預備）→ Task 14
```

---

## 檔案變更摘要

| 檔案 | 動作 |
|------|------|
| `data/*/stations.json` | 新建（4個） |
| `data/*/attractions.json` | 修改（新增 station_id） |
| `data/*/outlets.json` | 新建（4個） |
| `data/food_preferences.json` | 新建 |
| `web/index.html` | 修改（UI） |
| `web/js/app.js` | 修改（邏輯重寫） |
| `web/css/style.css` | 修改（樣式） |
| `scripts/generate_stations.py` | 新建 |
| `scripts/link_attractions_to_stations.py` | 新建 |
| `scripts/update_attractions.py` | 修改（enrich station_id + food type discovery） |
| `docs/mongodb-schema.md` | 新建 |

---

## 已確認規格

1. ✅ **車站 autocomplete 範圍** → 跟隨「選擇的地區」下拉過濾（不混省份）
2. ✅ **每天輸入上限** → 最多 3 個，超過 alert「取前三個，後面自行安排」
3. ✅ **景點 autocomplete 排序** → 名稱相似度（每站景點/餐廳不多，夠用）
4. ✅ **用餐習慣匹配** → 新增「用餐習慣」多選框（握壽司、拉麵、豬排飯…），生成行程時自動從當天車站周邊餐廳中過濾符合習慣的選項，填入用餐時段
5. ✅ **動態發現新食物類型** → enrichment 搜尋景點時若發現新的美食類型，自動新增至 `data/food_preferences.json`，前端載入時一併顯示