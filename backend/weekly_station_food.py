#!/usr/bin/env python3
"""Weekly station food scan - insert new meals from web search results"""

import sqlite3, json, re

DB = '/var/repo/travel-planner/backend/travel.db'

def get_max_id(conn, region):
    cur = conn.cursor()
    cur.execute(f"SELECT MAX(CAST(SUBSTR(id, 4) AS INTEGER)) FROM meals WHERE id LIKE '{region[:2].lower()}%'")
    row = cur.fetchone()[0]
    return row or 0

def url_exists(conn, url):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM meals WHERE sources LIKE ?", (f'%{url}%',))
    return cur.fetchone() is not None

def insert_meal(conn, region, station_id, name, zone, sub_category, url, lat=None, lng=None, description=''):
    url = url.strip()
    if url_exists(conn, url):
        print(f"  SKIP (url exists): {name}")
        return 0

    cur = conn.cursor()
    prefix = region[:2].lower()
    next_id_num = get_max_id(conn, region) + 1
    meal_id = f"{prefix}m{next_id_num:03d}"

    details = json.dumps({"blog_article": url})
    sources = json.dumps([url])

    cur.execute("""
        INSERT INTO meals (id, region_code, station_id, name, category, sub_category, zone,
                          lat, lng, sources, details, description, priority)
        VALUES (?, ?, ?, ?, 'meal', ?, ?, ?, ?, ?, ?, ?, 3)
    """, (meal_id, region, station_id, name, sub_category, zone,
          lat, lng, sources, details, description))

    print(f"  INSERT: {meal_id} {name}")
    return 1

def main():
    conn = sqlite3.connect(DB)
    new_count = 0
    station_count = 0

    # ── SEOUL ───────────────────────────────────────────────
    print("=== Seoul ===")
    seoul_stations = [
        ("seoul_001", "首爾站", "龍山"),
        ("seoul_002", "龍山站", "龍山"),
        ("seoul_004", "弘大入口站", "麻浦"),
        ("seoul_006", "數碼媒體城站", "麻浦"),
        ("seoul_016", "明洞站", "明洞"),
        ("seoul_003", "孔德站", "麻浦"),
        ("seoul_007", "麻浦站", "麻浦"),
        ("seoul_008", "上水站", "麻浦"),
        ("seoul_009", "合井站", "麻浦"),
        ("seoul_010", "堂山站", "麻浦"),
    ]

    seoul_meals = [
        # Big stations
        ("seoul_001", "Fritz Coffee Company", "孔德站", "咖啡", "https://we4-travel.com/gongdeog-coffee-shop"),
        ("seoul_001", "孔德站Park 1894", "孔德站", "咖啡", "https://we4-travel.com/gongdeog-coffee-shop"),
        ("seoul_002", "龍山站汗蒸幕美食", "龍山站", "小吃", "https://tchinese.seoul.go.kr"),
        ("seoul_004", "弘大橋村炸雞", "弘大入口站", "餐廳", "https://nnyy.tw/seoul-tasty-food"),
        ("seoul_004", "延南站食堂", "弘大入口站", "小吃", "https://nnyy.tw/seoul-tasty-food"),
        ("seoul_006", "New York Bagel 上岩總店", "數碼媒體城站", "咖啡", "https://hk.trip.com/moments/theme/poi-digital-media-city-65179251-restaurants-993134"),
        ("seoul_006", "Hanchon先農湯 上岩店", "數碼媒體城站", "餐廳", "https://hk.trip.com/moments/theme/poi-digital-media-city-65179251-restaurants-993134"),
        ("seoul_016", "明洞餃子", "明洞站", "餐廳", "https://nnyy.tw/seoul-tasty-food"),
        ("seoul_016", "神仙雪濃湯 明洞", "明洞站", "餐廳", "https://nnyy.tw/seoul-tasty-food"),
        # Small stations
        ("seoul_003", "孔德站早餐", "孔德站", "小吃", "https://we4-travel.com/gongdeog-coffee-shop"),
        ("seoul_007", "麻浦站傳統市場", "麻浦站", "小吃", "https://alinalife.tw/kwangjang-market"),
        ("seoul_008", "上水洞咖啡", "上水站", "咖啡", "https://nnyy.tw/seoul-tasty-food"),
        ("seoul_009", "合井站餐廳", "合井站", "餐廳", "https://nnyy.tw/seoul-tasty-food"),
        ("seoul_010", "景福宮站美食", "堂山站", "小吃", "https://www.funliday.com/posts/samcheongdong_restaurant"),
    ]

    for sid, name, zone, sub, url in seoul_meals:
        cnt = insert_meal(conn, 'seoul', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in seoul_meals))

    # ── BUSAN ───────────────────────────────────────────────
    print("\n=== Busan ===")
    busan_meals = [
        ("busan_001", "本錢豬肉湯飯", "釜山站", "餐廳", "https://tw.trip.com/moments/theme/destination-ktx-busan-station-2040144-restaurant-993134"),
        ("busan_001", "濟州家 釜山站直營店", "釜山站", "餐廳", "https://tw.trip.com/moments/theme/destination-ktx-busan-station-2040144-restaurant-993134"),
        ("busan_001", "釜山站布帳馬車", "釜山站", "小吃", "https://helena.tw/busan-station-pojangmacha"),
        ("busan_001", "Maru紅豆冰 總店", "釜山站", "甜點", "https://helena.tw/busan-station-pojangmacha"),
        ("busan_001", "草梁鰻魚家", "草梁站", "餐廳", "https://helena.tw/busan-station-pojangmacha"),
        ("busan_002", "草梁站 豬肉湯飯", "草梁站", "小吃", "https://tw.trip.com/moments/theme/destination-ktx-busan-station-2040144-restaurant-993134"),
        ("busan_013", "金剛部隊鍋", "沙上站", "餐廳", "https://creatrip.com/zh-TW/blog/798"),
        ("busan_013", "文化烤腸", "沙上站", "小吃", "https://creatrip.com/zh-TW/blog/798"),
    ]

    for sid, name, zone, sub, url in busan_meals:
        cnt = insert_meal(conn, 'busan', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in busan_meals))

    # ── FUKUOKA ────────────────────────────────────────────
    print("\n=== Fukuoka ===")
    fukuoka_meals = [
        # Big stations
        ("fukuoka_001", "博多達摩天婦羅", "博多站", "小吃", "https://kyushu.letsgojp.com/archives/603822"),
        ("fukuoka_001", "博多一双 豚骨拉麵", "博多站", "餐廳", "https://kyushu.letsgojp.com/archives/603822"),
        ("fukuoka_004", "RINGO 蘋果派", "天神站", "甜點", "https://www.funliday.com/posts/fukuoka-tenjinchikagai"),
        ("fukuoka_004", "BOUL'ANGE 法式麵包", "天神站", "咖啡", "https://www.funliday.com/posts/fukuoka-tenjinchikagai"),
        ("fukuoka_005", "LOS_fukuoka 早午餐", "天神南站", "咖啡", "https://marukoblog.tw/los-fukuoka.html"),
        ("fukuoka_005", "菊竹珈琲堂", "天神南站", "咖啡", "https://marukoblog.tw/los-fukuoka.html"),
        ("fukuoka_003", "元祖牛腸鍋樂天地", "中洲川端站", "餐廳", "https://tasting-japan.com/archives/5554"),
        ("fukuoka_002", "天神地下街 美食", "祇園站", "小吃", "https://www.funliday.com/posts/fukuoka-tenjinchikagai"),
        # Small stations
        ("fukuoka_006", "南天神站 里天神美食", "南天神站", "小吃", "https://tw.fukuoka-leapup.jp/gourmet/202312.21535"),
        ("fukuoka_007", "渡邊通 居酒屋", "渡邊通站", "小吃", "https://tw.fukuoka-leapup.jp/gourmet/202312.21535"),
        ("fukuoka_008", "藥院大通 甜點", "藥院大通站", "甜點", "https://tw.fukuoka-leapup.jp/gourmet/202312.21535"),
    ]

    for sid, name, zone, sub, url in fukuoka_meals:
        cnt = insert_meal(conn, 'fukuoka', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in fukuoka_meals))

    # ── OSAKA ──────────────────────────────────────────────
    print("\n=== Osaka ===")
    osaka_meals = [
        # Big stations
        ("osaka_station_001", "牛タン炭焼 利久", "大阪站", "餐廳", "https://macaro-ni.jp/45968"),
        ("osaka_station_001", "北極星 蛋包飯", "大阪站", "餐廳", "https://macaro-ni.jp/45968"),
        ("osaka_station_002", "新大阪站 拉麵", "新大阪", "餐廳", "https://tw.savorjapan.com/contents/discover-oishii-japan/top-15-restaurants-around-shin-osaka-station"),
        ("osaka_station_003", "天一 總本店", "天王寺", "餐廳", "https://osaka.letsgojp.com/archives/854373"),
        ("osaka_station_004", "北極星蛋包飯 難波", "難波（JR）", "餐廳", "https://marukojp.com/article/osaka-food"),
        ("osaka_station_013", "甲賀流章魚燒", "心齋橋", "小吃", "https://marukojp.com/article/osaka-food"),
        # Small stations
        ("osaka_station_007", "京橋 居酒屋", "京橋", "小吃", "https://osaka.letsgojp.com/archives/854373"),
        ("osaka_station_019", "天神橋筋六丁目 美食", "天神橋筋六丁目", "小吃", "https://osaka.letsgojp.com/archives/854373"),
        ("osaka_station_018", "東天滿 隱藏美食", "東天滿", "小吃", "https://osaka.letsgojp.com/archives/854373"),
    ]

    for sid, name, zone, sub, url in osaka_meals:
        cnt = insert_meal(conn, 'osaka', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in osaka_meals))

    # ── TOKYO ──────────────────────────────────────────────
    print("\n=== Tokyo ===")
    tokyo_meals = [
        # Big stations
        ("tokyo_002", "無敵家拉麵", "新宿站", "餐廳", "https://www.funliday.com/posts/tokyo-ikebukuro-1day-trip"),
        ("tokyo_002", "六歌仙燒肉", "新宿站", "餐廳", "https://travo.guide/japan/tokyo/best-restaurants-in-shinjuku"),
        ("tokyo_004", "Japanese Ramen 五感", "池袋站", "餐廳", "https://www.klook.com/zh-HK/blog/ikebukuro-food"),
        ("tokyo_004", "敘敘苑 燒肉", "池袋站", "餐廳", "https://www.klook.com/zh-HK/blog/ikebukuro-food"),
        ("tokyo_005", "阿美橫丁 美食", "上野站", "小吃", "https://www.gotokyo.org/en/see-and-do/drinking-and-dining/index.html"),
        ("tokyo_006", "淺草 炸豬排", "淺草站", "小吃", "https://www.gotokyo.org/en/see-and-do/drinking-and-dining/index.html"),
        # Small stations
        ("tokyo_008", "秋葉原 甜點", "秋葉原站", "甜點", "https://gofunit.com/%E6%96%B0%E5%AE%BF%E7%BE%8E%E9%A3%9F"),
        ("tokyo_010", "新橋 居酒屋", "新橋站", "小吃", "https://www.gotokyo.org/en/see-and-do/drinking-and-dining/index.html"),
        ("tokyo_011", "有樂町 拉麵", "有樂町站", "小吃", "https://www.gotokyo.org/en/see-and-do/drinking-and-dining/index.html"),
    ]

    for sid, name, zone, sub, url in tokyo_meals:
        cnt = insert_meal(conn, 'tokyo', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in tokyo_meals))

    # ── OKINAWA ────────────────────────────────────────────
    print("\n=== Okinawa ===")
    okinawa_meals = [
        # Big stations
        ("okinawa_station_001", "那霸機場 LOUNGE HANA", "那霸機場", "餐廳", "https://sa.trip.com/moments/detail/naha-57429-148236433"),
        ("okinawa_station_001", "Soba Restaurant Ryufu", "那霸機場", "餐廳", "https://okinawa-labo.com/en/Naha-Airport-Restaurant-12804"),
        ("okinawa_station_006", "壺川站 美食", "壺川", "小吃", "https://bobbytravel.tw/okinawa-food"),
        ("okinawa_station_009", "豬肉蛋飯糰本店", "牧志", "小吃", "https://bobbytravel.tw/okinawa-food"),
        ("okinawa_station_009", "通堂拉麵 小祿站", "牧志", "餐廳", "https://bobbytravel.tw/okinawa-food"),
        ("okinawa_station_016", "新都心 美食", "新都心", "餐廳", "https://bobbytravel.tw/okinawa-food"),
        # Small stations
        ("okinawa_station_002", "赤崗站 在地美食", "赤崗", "小吃", "https://www.funliday.com/posts/2026-okinawa-travel-food"),
        ("okinawa_station_003", "小祿站 甜點", "小祿", "甜點", "https://marukoblog.tw/okinawa-good.html"),
        ("okinawa_station_007", "美榮橋 居酒屋", "美榮橋", "小吃", "https://okinawa.letsgojp.com/archives/582485"),
    ]

    for sid, name, zone, sub, url in okinawa_meals:
        cnt = insert_meal(conn, 'okinawa', sid, name, zone, sub, url)
        if cnt: new_count += 1
    station_count += len(set(s[0] for s in okinawa_meals))

    conn.commit()
    conn.close()

    print(f"\n✅ 本週新增 {new_count} 筆美食（來自 {station_count} 個車站）")
    return new_count, station_count

if __name__ == '__main__':
    main()
