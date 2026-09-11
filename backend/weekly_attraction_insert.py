#!/usr/bin/env python3
"""Weekly attraction update - insert hidden gem attractions for 6 regions."""

import sqlite3
import json
import os
import sys

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

# New attractions to insert per region
# Format: (id, region_code, station_id, name, name_en, category, sub_category, zone, location, ticket, stay_duration, priority, tags, description, sources, details, nearby_stations)
NEW_ATTRACTIONS = [
    # ── SEOUL ──────────────────────────────────────────────────────────────
    {
        "id": "seoul-sangsu-mural",
        "region_code": "seoul",
        "station_id": "seoul_008",
        "name": "上水洞壁畫街",
        "name_en": "Sangsu-dong Mural Alley",
        "category": "hidden_gem",
        "sub_category": "壁畫/街頭藝術",
        "zone": "麻浦",
        "location": "首爾特別市麻浦區上水洞",
        "ticket": "免費",
        "stay_duration": "1小時",
        "priority": 3,
        "tags": json.dumps(["壁畫", "街頭藝術", "文青", "散步"]),
        "description": "隱藏在弘大周邊上水洞的社區壁畫小巷，與弘大的喧鬧截然不同，這裡保留了更純粹的在地生活感。牆面上的壁畫由當地藝術家創作，色彩繽紛且富有故事性，是喜歡慢遊探索的旅客不可錯過的秘密角落。",
        "sources": json.dumps(["https://chinese.visitseoul.net/editorspicks/2026-Sangsu-dong/CNNvlk68c"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=上水洞壁畫街+首爾",
            "blog_article": "https://chinese.visitseoul.net/editorspicks/2026-Sangsu-dong/CNNvlk68c",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["seoul_008", "seoul_004"]),
    },
    {
        "id": "seoul-yeonnam-gyeongui",
        "region_code": "seoul",
        "station_id": "seoul_008",
        "name": "京義線森林公園",
        "name_en": "Gyeongui Line Forest Park",
        "category": "hidden_gem",
        "sub_category": "公園/綠地",
        "zone": "麻浦",
        "location": "首爾特別市麻浦區弘大入口洞",
        "ticket": "免費",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["森林公園", "鐵道自行車", "散步", "文青"]),
        "description": "由廢棄京義線鐵道改造的線性森林公園，綠蔭夾道，空氣清新，是首爾市區珍貴的綠色走廊。適合悠閒散步或騎單車，沿途可見鐵道遗跡與自然共存的城市景觀。",
        "sources": json.dumps(["https://www.bring-you.info/zh-tw/hongdae"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=京義線森林公園+首爾",
            "blog_article": "https://www.bring-you.info/zh-tw/hongdae",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["seoul_008", "seoul_009", "seoul_004"]),
    },

    # ── BUSAN ─────────────────────────────────────────────────────────────
    {
        "id": "busan-jeonpo-cafe",
        "region_code": "busan",
        "station_id": "busan_000_jeonpo",
        "name": "田浦咖啡街",
        "name_en": "Jeonpo Cafe Street",
        "category": "hidden_gem",
        "sub_category": "咖啡街/文創",
        "zone": "釜山鎮",
        "location": "釜山廣域市釜山鎭區田浦洞",
        "ticket": "免費（消費自費）",
        "stay_duration": "2小時",
        "priority": 3,
        "tags": json.dumps(["咖啡街", "文青", "散步", "老屋改建", "田浦"]),
        "description": "曾是傳統五金工具街的田浦洞，2017年被《紐約時報》選為全球52個必訪旅遊景點之一。如今匯聚超過百間風格各異的咖啡廳，從職人手沖到全球百大咖啡廳都有，是釜山最具代表性的文青散步街區。",
        "sources": json.dumps([
            "https://www.funliday.com/posts/busan_jeonpo_cafe",
            "https://ajtravel.tw/20240327"
        ]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=田浦咖啡街+釜山",
            "blog_article": "https://www.funliday.com/posts/busan_jeonpo_cafe",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["busan_000_jeonpo"]),
    },
    {
        "id": "busan-jeonpo-alley",
        "region_code": "busan",
        "station_id": "busan_000_jeonpo",
        "name": "田理團路",
        "name_en": "Jeonli-gil (田理團路)",
        "category": "hidden_gem",
        "sub_category": "小巷/在地",
        "zone": "釜山鎮",
        "location": "釜山廣域市釜山鎭區田浦洞",
        "ticket": "免費",
        "stay_duration": "1小時",
        "priority": 4,
        "tags": json.dumps(["小巷", "散步", "在地", "老街", "田浦"]),
        "description": "田浦洞一條蜿蜒窄小的巷弄，過去為工人來往的路徑，現化身為穿梭於咖啡店與特色小店之間的秘密小巷。適合喜歡探險、挖掘城市細節的旅人。",
        "sources": json.dumps(["https://lizzzstyle.tw/seomyeon-jeonpo"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=田理團路+釜山",
            "blog_article": "https://lizzzstyle.tw/seomyeon-jeonpo",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["busan_000_jeonpo"]),
    },

    # ── FUKUOKA ────────────────────────────────────────────────────────────
    {
        "id": "fukuoka-yakuin-hidden",
        "region_code": "fukuoka",
        "station_id": "fukuoka_009",
        "name": "藥院散步小巷",
        "name_en": "Yakuin Hidden Alley",
        "category": "hidden_gem",
        "sub_category": "散步小巷/咖啡",
        "zone": "藥院",
        "location": "福岡縣福岡市中央區藥院",
        "ticket": "免費",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["散步", "咖啡", "在地", "小巷", "藥院"]),
        "description": "天神、博多太觀光了？藥院是福岡在地人最推薦的秘密散步區。這裡有作工細膩的選物咖啡廳、質感小店與安靜的住宅區小巷，適合想體驗「另一種福岡」的旅客。",
        "sources": json.dumps(["https://www.threads.com/@bonnies.lifee/post/DOZ6qThEwfQ"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=藥院+福岡+散步",
            "blog_article": "https://www.threads.com/@bonnies.lifee/post/DOZ6qThEwfQ",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["fukuoka_009", "fukuoka_008"]),
    },
    {
        "id": "fukuoka-tenjin-nishi",
        "region_code": "fukuoka",
        "station_id": "fukuoka_004",
        "name": "天神西通",
        "name_en": "Tenjin Nishi-Dori",
        "category": "attraction",
        "sub_category": "商店街/購物",
        "zone": "天神",
        "location": "福岡縣福岡市中央區天神大名地區",
        "ticket": "免費",
        "stay_duration": "1小時",
        "priority": 3,
        "tags": json.dumps(["商店街", "購物", "時尚", "天神"]),
        "description": "從明治通往國道之間的南北向街道，兩旁匯集了時尚精品店、餐廳與建築。岔路小巷中保留了傳統老店與新潮店舖和諧共存的風貌，是感受福岡都會生活感的絕佳散步路線。",
        "sources": json.dumps(["https://www.crossroadfukuoka.jp/en/spot/12672"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=天神西通り+福岡",
            "blog_article": "https://www.crossroadfukuoka.jp/en/spot/12672",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["fukuoka_004", "fukuoka_003"]),
    },

    # ── OSAKA ──────────────────────────────────────────────────────────────
    {
        "id": "osaka-shimmachi",
        "region_code": "osaka",
        "station_id": "osaka_005",
        "name": "新今宮老街散步",
        "name_en": "Shinnikumata Old Town Walk",
        "category": "hidden_gem",
        "sub_category": "老街/在下町",
        "zone": "新今宮",
        "location": "大阪市立浪速區新今宮",
        "ticket": "免費",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["老街", "散步", "在下町", "新今宮", "在地"]),
        "description": "新今宮一帶保留了大阪較少觀光化的傳統下町風情，街道兩旁有老鋪食堂、神社與平房住宅區域。從新今宮站步行可達，適合想遠離人潮、感受眞實大阪生活的旅客。",
        "sources": json.dumps(["https://marukojp.com/hidden-gem-in-osaka"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=新今宮+大阪+散步",
            "blog_article": "https://marukojp.com/hidden-gem-in-osaka",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["osaka_005", "osaka_004"]),
    },
    {
        "id": "osaka-shitennnoji-morning",
        "region_code": "osaka",
        "station_id": "osaka_003",
        "name": "四天王寺晨間散步",
        "name_en": "Shitennoji Morning Walk",
        "category": "attraction",
        "sub_category": "神社/寺廟",
        "zone": "天王寺",
        "location": "大阪天王寺區天王寺町",
        "ticket": "免費（中心伽藍300円）",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["寺廟", "神社", "歷史", "早晨", "四天王寺"]),
        "description": "清晨的天王寺與四天王寺周邊，有一條被稱為「天王寺七坂」的秘密散步路線。趁觀光客還沒出發，走一趟石階小巷、龜池日出，感受大阪最治愈的清晨時光。",
        "sources": json.dumps(["https://japannook.com/zh/articles/shitennoji-morning-walk"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=四天王寺+大阪",
            "blog_article": "https://japannook.com/zh/articles/shitennoji-morning-walk",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["osaka_003"]),
    },

    # ── TOKYO ─────────────────────────────────────────────────────────────
    {
        "id": "tokyo-kiyosumi-shirakawa",
        "region_code": "tokyo",
        "station_id": "tokyo_000_kiyosumi",
        "name": "清澄白河散步區",
        "name_en": "Kiyosumi-Shirakawa Walking District",
        "category": "hidden_gem",
        "sub_category": "文青散步區",
        "zone": "墨田區",
        "location": "東京都墨田區清澄白河",
        "ticket": "免費",
        "stay_duration": "2小時",
        "priority": 3,
        "tags": json.dumps(["文青", "精品咖啡", "畫廊", "倉庫", "清澄白河"]),
        "description": "東京新晉的文青散步聖地，保留了昔日倉庫建築並引入Blue Bottle Coffee等精品咖啡店與現代藝術畫廊。在傳統下町風情中注入年輕創意能量，是東京深度旅遊不可錯過的秘密街區。",
        "sources": json.dumps([
            "https://tokyo.letsgojp.com/archives/697925",
            "https://matcha-jp.com/tw/3749"
        ]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=清澄白河+東京",
            "blog_article": "https://matcha-jp.com/tw/3749",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["tokyo_000_kiyosumi"]),
    },
    {
        "id": "tokyo-kuramae",
        "region_code": "tokyo",
        "station_id": "tokyo_000_kuramae",
        "name": "藏前散步徑",
        "name_en": "Kuramae Walking District",
        "category": "hidden_gem",
        "sub_category": "職人/文具/散步",
        "zone": "台東區",
        "location": "東京都台東區藏前",
        "ticket": "免費",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["文具", "職人工坊", "皮革", "雜貨", "藏前"]),
        "description": "藏前是東京職人工坊與特色文具店聚集的散步小區。從大避神社一帶走進小巷，處處可見堅持傳統工藝的店家與新興設計品牌並存的風景，適合喜歡挖寶與深度散步的旅人。",
        "sources": json.dumps(["https://tokyo.letsgojp.com/archives/697925"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=藏前+東京+散步",
            "blog_article": "https://tokyo.letsgojp.com/archives/697925",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["tokyo_000_kuramae"]),
    },

    # ── OKINAWA ────────────────────────────────────────────────────────────
    {
        "id": "okinawa-makishi-market",
        "region_code": "okinawa",
        "station_id": "okinawa_station_009",
        "name": "第一牧志公設市場",
        "name_en": "Daiichi Makishi Public Market",
        "category": "attraction",
        "sub_category": "市場/美食",
        "zone": "那霸",
        "location": "沖繩縣那霸市牧志3-11-1",
        "ticket": "免費（餐飲自費）",
        "stay_duration": "1.5小時",
        "priority": 3,
        "tags": json.dumps(["市場", "美食", "海鮮", "在地", "牧志", "國際通"]),
        "description": "被稱為「沖繩的廚房」，與那霸國際通相鄰的二樓傳統公設市場。一樓為生鮮區，二樓為開放式餐廳，可現買海產請店家代為烹調，是體驗地道沖繩美食文化的重要景點。",
        "sources": json.dumps([
            "https://mi0424.pixnet.net/blog/posts/7122378938",
            "https://ayaca.tw/naha-attractions"
        ]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=第一牧志公設市場+那霸",
            "blog_article": "https://mi0424.pixnet.net/blog/posts/7122378938",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["okinawa_station_009", "okinawa_station_008"]),
    },
    {
        "id": "okinawa-naha-airport-observation",
        "region_code": "okinawa",
        "station_id": "okinawa_station_001",
        "name": "那霸機場觀景台",
        "name_en": "Naha Airport Observation Deck",
        "category": "attraction",
        "sub_category": "機場/景觀",
        "zone": "那霸",
        "location": "沖繩縣那霸市鏡水 ANA那霸機場国内線航廈4F",
        "ticket": "免費",
        "stay_duration": "30分鐘",
        "priority": 4,
        "tags": json.dumps(["機場", "觀景台", "飛機", "夕陽", "那霸機場"]),
        "description": "那霸機場國內線航廈4樓設有免費觀景台，可觀賞飛機起降與寬闘的停機坪景色，傍晚時分運氣好還能看到夕陽與海景。是自駕或不自駕旅客在機場周邊放鬆等待的好去處。",
        "sources": json.dumps(["https://pfse64289.pixnet.net/blog/posts/15347093785"]),
        "details": json.dumps({
            "google_maps": "https://maps.google.com/?q=那霸機場+觀景台",
            "blog_article": "https://pfse64289.pixnet.net/blog/posts/15347093785",
            "youtube": ""
        }),
        "nearby_stations": json.dumps(["okinawa_station_001"]),
    },
]


def get_station_id(conn, station_id):
    """Check if station exists in DB."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM stations WHERE id=?", (station_id,))
    return cur.fetchone() is not None


def exists_in_db(conn, attraction_id):
    """Check if attraction ID already exists."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM attractions WHERE id=?", (attraction_id,))
    return cur.fetchone() is not None


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = []
    skipped = []
    errors = []

    # Fix station IDs that don't exist — map to nearest valid station
    station_fixes = {
        "busan_000_jeonpo": "busan_000_seomyeon",  # nearest: Seomyeon (西面) is central
        "tokyo_000_kiyosumi": "tokyo_007",  # 押上 - closest to Kiyosumi-Shirakawa via Toei Oedo line
        "tokyo_000_kuramae": "tokyo_007",   # 押上 - Asakusa area
    }

    for attr in NEW_ATTRACTIONS:
        aid = attr["id"]
        sid = attr["station_id"]

        # Apply station fixes
        sid_fixed = station_fixes.get(sid, sid)

        # Check if already exists
        if exists_in_db(conn, aid):
            skipped.append(f"{attr['name']} ({aid}) — 已存在")
            print(f"SKIP: {attr['name']} (already exists)")
            continue

        # Verify station exists
        if not get_station_id(conn, sid_fixed):
            # fallback to region default
            region_defaults = {
                "seoul": "seoul_001",
                "busan": "busan_001",
                "fukuoka": "fukuoka_001",
                "osaka": "osaka_station_001",
                "tokyo": "tokyo_001",
                "okinawa": "okinawa_station_001",
            }
            sid_fixed = region_defaults.get(attr["region_code"], sid_fixed)
            print(f"  WARNING: station {sid} not found, using fallback {sid_fixed}")

        try:
            cur.execute("""
                INSERT INTO attractions (
                    id, region_code, station_id, name, name_en, category, sub_category,
                    zone, location, ticket, stay_duration, priority, tags, description,
                    sources, details, nearby_stations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid,
                attr["region_code"],
                sid_fixed,
                attr["name"],
                attr.get("name_en", ""),
                attr["category"],
                attr.get("sub_category", ""),
                attr.get("zone", ""),
                attr.get("location", ""),
                attr.get("ticket", ""),
                attr.get("stay_duration", ""),
                attr.get("priority", 3),
                attr.get("tags", "[]"),
                attr.get("description", ""),
                attr.get("sources", "[]"),
                attr.get("details", "{}"),
                attr.get("nearby_stations", "[]"),
            ))
            inserted.append(f"{attr['name']} ({sid_fixed})")
            print(f"INSERT: {attr['name']} -> {sid_fixed}")
        except Exception as e:
            errors.append(f"{attr['name']}: {e}")
            print(f"ERROR: {attr['name']}: {e}")

    conn.commit()
    conn.close()

    print("\n=== SUMMARY ===")
    print(f"✅ Inserted: {len(inserted)}")
    for i in inserted:
        print(f"  + {i}")
    print(f"⏭ Skipped: {len(skipped)}")
    for s in skipped:
        print(f"  ~ {s}")
    if errors:
        print(f"❌ Errors: {len(errors)}")
        for e in errors:
            print(f"  ! {e}")
    else:
        print("❌ Errors: 0")

    return len(inserted), len(skipped), len(errors)


if __name__ == "__main__":
    n_insert, n_skip, n_err = main()
    sys.exit(0 if n_err == 0 else 1)
