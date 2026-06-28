# 旅遊景點與交通查詢系統

> 🎯 這是一個旅行資料庫系統，收錄各旅遊地區的景點、美食、交通與行程建議，供 AI Agent 查詢與行程規劃使用。

---

## 📁 專案結構

```
travel-planner/
├── SPEC.md                   # 系統規格文件
├── attractions/              # 景點資料
│   ├── fukuoka-attractions.md    # 大眾景點
│   └── fukuoka-hidden-gems.md    # 小眾秘境
├── restaurants/             # 美食資料
│   └── fukuoka-food.md
├── transport/               # 交通資料
│   └── fukuoka-transport.md
├── itineraries/             # 行程範例
│   ├── fukuoka-5days.md
│   ├── fukuoka-6days.md
│   └── fukuoka-7days.md
└── fukuoka/                 # 地區設定
    └── region.json          # 更新開關設定
```

---

## 🌍 現有地區

| 地區 | 顯示名稱 | 自動更新 | 最後更新 |
|------|---------|---------|---------|
| fukuoka | 日本福岡 | ✅ 開啟 | 2026-06-12 |

---

## 🔄 更新機制

- 每個已建立的地区，每月自動更新一次
- 透過 `region.json` 中的 `enabled` 欄位控制是否參與自動更新
- 更新範圍：航班價格、景點資訊、美食动态、行程調整

---

## 📝 新增地區

請口頭或文字告知要新增的地區，系統將自動建立完整六維度資料：
- 🛫 航班交通
- 📍 景點資料
- 🍜 美食推薦
- 🏨 住宿建議
- 🚇 當地交通
- 📅 行程範例（5/6/7天）
