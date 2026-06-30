#!/usr/bin/env python3
import sqlite3, json

conn = sqlite3.connect('/var/repo/travel-planner/backend/travel.db')
cur = conn.cursor()

# Define the data inline - each meal as a dict
seoul_meals = [
    {
        "id": "sm_001",
        "region": "seoul_001",
        "station": "seoul_001",
        "name": "FOCAL POINT",
        "name_en": "FOCAL POINT",
        "sub_cat": "咖啡",
        "zone": "龍山",
        "location": "387 Cheongpa-ro, Yongsan-gu, Seoul",
        "ticket": "免費參觀",
        "stay": "1小時",
        "desc": "米其林認證休閒餐廳",
        "tags": ["咖啡", "甜點", "派"],
        "priority": 3,
        "url": "https://creatrip.com/zh-TW/blog/963"
    },
    {
        "id": "sm_002",
        "region": "seoul_001",
        "station": "seoul_001",
        "name": "湖水家",
        "name_en": "Hosujip",
        "sub_cat": "小吃",
        "zone": "龍山",
        "location": "443 Cheongpa-ro, Jung-gu, Seoul",
        "ticket": "免費參觀",
        "stay": "1小時",
        "desc": "1986年開業，首爾站周邊知名本地店",
        "tags": ["辣炒雞", "燒烤", "在地"],
        "priority": 3,
        "url": "https://creatrip.com/zh-TW/blog/963"
    },
]

added = 0
for meal in seoul_meals:
    sources = json.dumps([meal["url"]])
    details = json.dumps({"blog_article": meal["url"], "google_maps": "", "youtube": ""})
    tags_j = json.dumps(meal["tags"])
    try:
        cur.execute("""
            INSERT INTO meals
              (id, region_code, station_id, name, name_en, category, sub_category,
               zone, location, ticket, stay_duration, need_reservation, cash_only,
               priority, tags, description, sources, nearby_stations, details)
            VALUES (?,?,?,?,?,'meal',?,?,?,?,?,0,0,?,?,?,?,json('[]'),?)
        """, (meal["id"], meal["region"], meal["station"], meal["name"], meal["name_en"],
              meal["sub_cat"], meal["zone"], meal["location"], meal["ticket"], meal["stay"],
              meal["priority"], tags_j, meal["desc"], sources, details))
        added += 1
        print(f"OK: {meal['name']}")
    except Exception as e:
        print(f"SKIP: {meal['name']}: {e}")

conn.commit()
cur.execute("SELECT COUNT(*) FROM meals")
print(f"Total: {cur.fetchone()[0]}, added: {added}")
conn.close()
