#!/usr/bin/env python3
"""Insert station meals into SQLite meals table."""
import sqlite3
import json
import os
import re
from datetime import datetime

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

# ─── Raw collected meals data ───
# (region_code, station_id, zone, name, sub_category, blog_article, sources)
MEALS = [
    # ── SEOUL (5 major stations) ──
    ("seoul", "seoul_001", "首爾站", "陳玉華一隻雞", "雞肉料理",
     "https://mimigo.tw/darkhanmari/",
     ["https://mimigo.tw/darkhanmari/"]),
    ("seoul", "seoul_004", "弘大入口站", "百年百歲土種蔘雞湯", "雞肉料理",
     "https://mimigo.tw/ginseng-chicken-soup/",
     ["https://mimigo.tw/ginseng-chicken-soup/"]),
    ("seoul", "seoul_004", "弘大入口站", "老房子炭火燒肉", "燒肉",
     "https://mimigo.tw/hongdae-yesnaljib/",
     ["https://mimigo.tw/hongdae-yesnaljib/"]),
    ("seoul", "seoul_016", "明洞站", "百濟蔘雞湯", "雞肉料理",
     "https://mimigo.tw/baekje/",
     ["https://mimigo.tw/baekje/"]),
    ("seoul", "seoul_016", "明洞站", "世宗粥（醬蟹）", "海鮮",
     "https://alinalife.tw/sejong-congee/",
     ["https://alinalife.tw/sejong-congee/"]),
    ("seoul", "seoul_029", "市廳站", "Jojo Kalguksu 市廳店", "麵食",
     "https://hk.trip.com/moments/theme/poi-seoul-city-hall-20905750-restaurant-993134",
     ["https://hk.trip.com/moments/theme/poi-seoul-city-hall-20905750-restaurant-993134"]),

    # ── BUSAN (5 major stations) ──
    ("busan", "busan_001", "釜山站", "真 豬肉湯飯", "豬肉料理",
     "https://helena.tw/jin-dwejigomtang/",
     ["https://helena.tw/jin-dwejigomtang/"]),
    ("busan", "busan_001", "釜山站", "濟州家 釜山站直營店", "海鮮",
     "https://helena.tw/jejuga-busan-station/",
     ["https://helena.tw/jejuga-busan-station/"]),
    ("busan", "busan_027", "札嘎其站", "札嘎其市場33號店", "海鮮",
     "https://hk.trip.com/moments/theme/poi-jagalchi-market-102092-restaurant-993134/",
     ["https://hk.trip.com/moments/theme/poi-jagalchi-market-102092-restaurant-993134/"]),
    ("busan", "busan_035", "西面站", "味贊王鹽烤肉", "燒肉",
     "https://tw.trip.com/travel-guide/foods/busan-432-restaurant/matchandeul-wang-sogeum-gui-seomyeon-33317314/",
     ["https://tw.trip.com/travel-guide/foods/busan-432-restaurant/matchandeul-wang-sogeum-gui-seomyeon-33317314/"]),
    ("busan", "busan_042", "海雲台站", "伍班長", "海鮮",
     "https://tw.trip.com/blog/%E9%87%9C%E5%B1%B1%E7%BE%8E%E9%A3%9F",
     ["https://tw.trip.com/blog/%E9%87%9C%E5%B1%B1%E7%BE%8E%E9%A3%9F"]),

    # ── FUKUOKA (5 major stations) ──
    ("fukuoka", "fukuoka_001", "博多站", "一蘭拉麵 總本店", "拉麵",
     "https://marukoblog.tw/2018-10-18.html",
     ["https://marukoblog.tw/2018-10-18.html"]),
    ("fukuoka", "fukuoka_001", "博多站", "大地烏龍麵", "麵食",
     "https://bobbytravel.tw/fukuoka-foods",
     ["https://bobbytravel.tw/fukuoka-foods"]),
    ("fukuoka", "fukuoka_004", "天神站", "久留米大砲拉麵", "拉麵",
     "https://marukoblog.tw/2018-10-18.html",
     ["https://marukoblog.tw/2018-10-18.html"]),
    ("fukuoka", "fukuoka_003", "中洲川端站", "元祖牛腸鍋 樂天地", "鍋物",
     "https://marukoblog.tw/2018-10-18.html",
     ["https://marukoblog.tw/2018-10-18.html"]),
    ("fukuoka", "fukuoka_041", "小倉站", "資さんうどん 小倉魚町店", "麵食",
     "https://marukoblog.tw/2018-10-18.html",
     ["https://marukoblog.tw/2018-10-18.html"]),

    # ── OSAKA (5 major stations) ──
    ("osaka", "osaka_001", "大阪站", "北極星蛋包飯", "蛋包飯",
     "https://marukojp.com/article/osaka-food",
     ["https://marukojp.com/article/osaka-food"]),
    ("osaka", "osaka_001", "大阪站", "神座拉麵", "拉麵",
     "https://marukojp.com/article/osaka-food",
     ["https://marukojp.com/article/osaka-food"]),
    ("osaka", "osaka_005", "難波站", "串之坊", "串炸",
     "https://marukojp.com/article/osaka-food",
     ["https://marukojp.com/article/osaka-food"]),
    ("osaka", "osaka_005", "難波站", "自由軒咖哩飯", "咖哩",
     "https://marukojp.com/article/osaka-food",
     ["https://marukojp.com/article/osaka-food"]),
    ("osaka", "osaka_008", "心齋橋站", "PABLO 半熟起司蛋糕", "甜點",
     "https://marukojp.com/article/osaka-food",
     ["https://marukojp.com/article/osaka-food"]),

    # ── TOKYO (5 major stations) ──
    ("tokyo", "tokyo_001", "東京站", "敘敘苑燒肉 銀座店", "燒肉",
     "https://hk.trip.com/blog/tokyo-food-recommendation/",
     ["https://hk.trip.com/blog/tokyo-food-recommendation/"]),
    ("tokyo", "tokyo_003", "新宿站", "肉亭Futago", "燒肉",
     "https://tokyo.letsgojp.com/archives/601864/",
     ["https://tokyo.letsgojp.com/archives/601864/"]),
    ("tokyo", "tokyo_007", "池袋站", "燒肉 池袋店", "燒肉",
     "https://hk.trip.com/blog/tokyo-food-recommendation/",
     ["https://hk.trip.com/blog/tokyo-food-recommendation/"]),
    ("tokyo", "tokyo_004", "上野站", "天婦羅 下村", "天婦羅",
     "https://www.bigfang.tw/blog/post/ueno-delicioius",
     ["https://www.bigfang.tw/blog/post/ueno-delicioius"]),
    ("tokyo", "tokyo_004", "上野站", "鰻割烹 伊豆榮 本店", "鰻魚飯",
     "https://www.bigfang.tw/blog/post/ueno-delicioius",
     ["https://www.bigfang.tw/blog/post/ueno-delicioius"]),

    # ── OKINAWA (5 major stations) ──
    ("okinawa", "okinawa_001", "那霸機場站", "豬肉蛋飯糰本店", "小吃",
     "https://ajunfun.tw/naha-airport",
     ["https://ajunfun.tw/naha-airport"]),
    ("okinawa", "okinawa_001", "那霸機場站", "BLUE SEAL 冰淇淋", "甜點",
     "https://ajunfun.tw/naha-airport",
     ["https://ajunfun.tw/naha-airport"]),
    ("okinawa", "okinawa_003", "縣廳前站", "燒肉本部牧場", "燒肉",
     "https://ethanadventures.tw/blogs/1028524",
     ["https://ethanadventures.tw/blogs/1028524"]),
    ("okinawa", "okinawa_003", "縣廳前站", "暖暮拉麵 國際通店", "拉麵",
     "https://ethanadventures.tw/blogs/1028524",
     ["https://ethanadventures.tw/blogs/1028524"]),
    ("okinawa", "okinawa_004", "牧志站", "花笠食堂", "定食",
     "https://ethanadventures.tw/blogs/1028524",
     ["https://ethanadventures.tw/blogs/1028524"]),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── Step 1: Collect existing blog_article URLs from all rows ──
cur.execute("SELECT details FROM meals")
existing_blog_urls = set()
for (details_json,) in cur.fetchall():
    if details_json:
        try:
            d = json.loads(details_json)
            if d.get("blog_article"):
                existing_blog_urls.add(d["blog_article"])
        except Exception:
            pass
print(f"Existing blog URLs in DB: {len(existing_blog_urls)}")

# ── Step 2: Get next numeric suffix for each region ──
def detect_id_pattern(conn, region_code):
    """Detect existing ID prefix pattern for a region.

    Some regions use short prefixes (sm_, tm_, om_) while others use
    full region_code as prefix (fukuoka_, busan_, osaka_). Detect which
    by sampling existing IDs.
    """
    cur.execute(
        "SELECT id FROM meals WHERE region_code = ? ORDER BY id DESC LIMIT 30",
        (region_code,)
    )
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        return f"{region_code}_s001"

    # Try to extract a short prefix like "sm_" or "om_" or "tm_"
    # vs long prefix like "seoul_" or "fukuoka_"
    prefixes = set()
    for rid in ids:
        # e.g. sm_056 -> prefix=sm_, counter=56
        # fukuoka_吳服町站美食_140 -> prefix=fukuoka_
        # osaka_fe003f08 -> no counter, treat as full ID (skip)
        m = re.match(r'^([a-z]+_)(\d+)$', rid, re.IGNORECASE)
        if m:
            prefixes.add(m.group(1))
        else:
            # try long form: region_name_counter
            parts = rid.rsplit("_", 1)
            if len(parts) == 2 and parts[0]:
                prefixes.add(parts[0] + "_")

    # Pick the most common prefix
    if len(prefixes) == 1:
        prefix = list(prefixes)[0]
    elif f"{region_code}_" in prefixes:
        prefix = f"{region_code}_"
    else:
        prefix = list(prefixes)[0] if prefixes else f"{region_code}_"

    # Get max counter
    max_n = 0
    for rid in ids:
        m = re.search(r'(\d+)$', rid)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return f"{prefix}{max_n + 1:03d}"


def get_next_id(conn, region_code):
    return detect_id_pattern(conn, region_code)

inserted = 0
skipped = 0
errors = 0

for (region_code, station_id, zone, name, sub_category, blog_article, sources) in MEALS:
    if blog_article in existing_blog_urls:
        print(f"  SKIP (duplicate): {name}")
        skipped += 1
        continue

    meal_id = get_next_id(conn, region_code)
    details = json.dumps({"blog_article": blog_article}, ensure_ascii=False)
    sources_json = json.dumps(sources, ensure_ascii=False)

    try:
        cur.execute(
            """INSERT INTO meals
               (id, region_code, station_id, zone, name, sub_category, details, sources)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (meal_id, region_code, station_id, zone, name, sub_category, details, sources_json)
        )
        existing_blog_urls.add(blog_article)
        print(f"  INSERT [{meal_id}]: {name}")
        inserted += 1
    except Exception as e:
        print(f"  ERROR [{name}]: {e}")
        errors += 1

conn.commit()

cur.execute("SELECT COUNT(*) FROM meals")
total = cur.fetchone()[0]
print(f"\n✅ Inserted: {inserted}  |  ⏭ Skipped: {skipped}  |  ❌ Errors: {errors}  |  Total meals: {total}")
conn.close()
