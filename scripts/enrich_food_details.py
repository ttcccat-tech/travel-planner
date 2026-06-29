#!/usr/bin/env python3
"""
enrich_food_details.py
為大阪美食景點補足 details{} 區塊，包含 Google Maps / YouTube / Blog 連結
"""

import json
import os

FOOD_DETAILS = {
    "道頓堀 固力果先生（推荐拉麵）": {
        "google_maps": "https://maps.app.goo.gl/7WJfihfFWYEdPsMF8",
        "youtube": "https://www.youtube.com/watch?v=CuiHFkHR_wY",
        "blog_article": "https://www.bigfang.tw/blog/post/41929243",
        "description": "大阪最具代表性的打卡地標，固力果跑跑人與運河全景，建議傍晚拍夜景。",
    },
    "心齋橋·筋吃不踩雷美食": {
        "google_maps": "https://maps.app.goo.gl/4ExnvW6wAkJMJiSM7",
        "youtube": "https://www.youtube.com/watch?v=CuiHFkHR_wY",
        "blog_article": "https://www.tsunagujapan.com/zh-hant/osaka-shopping-streets-recommended-gourmets/",
        "description": "江戶後期餐飲激戰區，推薦北極星蛋包飯、自由軒咖喱飯、串揚專賣店。",
    },
    "鶴橋韓國城": {
        "google_maps": "https://maps.app.goo.gl/KXDZBkJZLRYgs4mb8",
        "youtube": "https://www.youtube.com/watch?v=x5kX5yp7AAM",
        "blog_article": "https://osaka.letsgojp.com/archives/761881/",
        "description": "大阪最大的韓國城，聚集超過100家韓國餐廳、烤肉、韓妝、超市，JR鶴橋站步行3分鐘。",
    },
    "木津批發市場": {
        "google_maps": "https://maps.app.goo.gl/CXZp9h8bNwqL3uNN6",
        "youtube": "https://www.youtube.com/watch?v=YjRYRlpqJoY",
        "blog_article": "https://osaka.letsgojp.com/archives/810413/",
        "description": "日本規模最大民間批發市場，清晨4:00營業，海鮮丼、平價生魚片必吃，附設業務超市。",
    },
    "天滿市場": {
        "google_maps": "https://maps.app.goo.gl/b8QJCMmCKCmHZnZTA",
        "youtube": "https://www.youtube.com/watch?v=YjRYRlpqJoY",
        "blog_article": "https://osaka.letsgojp.com/archives/810413/",
        "description": "大阪人的厨房，餐飲區6:00-14:00營業，串炸、章魚燒、拉麵選擇多元，體驗LOCAL美食文化。",
    },
    "河南市 黑毛和牛燒肉": {
        "google_maps": "https://maps.app.goo.gl/8XWqMWPQEYPKB9hZA",
        "youtube": "https://www.youtube.com/watch?v=YjRYRlpqJoY",
        "blog_article": "https://osaka.letsgojp.com/archives/810413/",
        "description": "關西頂級A5黑毛和牛燒肉，入口即化，建議提前預約套餐。",
    },
}

FOOD_SUB_CATEGORIES = {
    "道頓堀 固力果先生（推荐拉麵）": "ramen",
    "心齋橋·筋吃不踩雷美食": "restaurant_district",
    "鶴橋韓國城": "korean",
    "木津批發市場": "market",
    "天滿市場": "market",
    "河南市 黑毛和牛燒肉": "wagyu_yakiniku",
}

def enrich_food_details(region_path):
    fname = os.path.join(region_path, "attractions.json")
    with open(fname, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 支援 {"attractions": [...]} 或直接 [...]
    data = raw["attractions"] if isinstance(raw, dict) else raw

    updated = 0
    for item in data:
        name = item.get("name", "")
        if item.get("category") == "food" and name in FOOD_DETAILS:
            details = FOOD_DETAILS[name]
            # 只補足沒有 details 或 details 為空的
            if not item.get("details") or not any(v for v in item["details"].values()):
                item["details"] = details
                # sub_category 補正
                if name in FOOD_SUB_CATEGORIES:
                    item["sub_category"] = FOOD_SUB_CATEGORIES[name]
                print(f"  ✅ {name}")
                updated += 1
            else:
                print(f"  ⏭️  {name} (已有 details，跳過)")

    # 寫回：還原外層結構
    if isinstance(raw, dict):
        raw["attractions"] = data
        out = raw
    else:
        out = data

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n完成：{updated} 筆美食已補足 details{{}}")


if __name__ == "__main__":
    # 僅處理大阪，其他地區可擴充
    enrich_food_details("/var/repo/travel-planner/data/osaka")
