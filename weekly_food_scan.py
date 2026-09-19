#!/usr/bin/env python3
"""Weekly Station Food Scan — 2026-09-19"""

import sqlite3, json, re, time, sys
sys.path.insert(0, '/var/repo/travel-planner')

from hermes_tools import web_search

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

# ── Helpers ───────────────────────────────────────────────────────────────────

def short_id_for_name(name, region):
    slug = re.sub(r'[^a-zA-Z0-9]', '', name)[:10].lower()
    return f"{region[:2]}_m_{slug}"

def normalize_name(name):
    return re.sub(r'[\s（(].*$', '', name)

def meal_exists(url):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM meals WHERE sources LIKE ?", (f'%{url}%',))
    row = cur.fetchone()
    conn.close()
    return row is not None

def insert_meal(meal):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO meals (
                id, region_code, station_id, name, name_en, category,
                sub_category, zone, location, lat, lng, ticket,
                stay_duration, need_reservation, cash_only, priority,
                tags, description, sources, nearby_stations, details
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            meal['id'],
            meal['region_code'],
            meal.get('station_id'),
            meal['name'],
            meal.get('name_en'),
            'meal',
            meal.get('sub_category'),
            meal.get('zone'),
            meal.get('location'),
            meal.get('lat'),
            meal.get('lng'),
            meal.get('ticket'),
            meal.get('stay_duration'),
            0, 0, 3,
            json.dumps(meal.get('tags', []), ensure_ascii=False),
            meal.get('description'),
            json.dumps(meal.get('sources', []), ensure_ascii=False),
            json.dumps(meal.get('nearby_stations', []), ensure_ascii=False),
            json.dumps(meal.get('details', {}), ensure_ascii=False),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_sub_category(title):
    t = title.lower()
    if any(k in t for k in ['咖啡', 'cafe', 'café']): return '咖啡'
    if any(k in t for k in ['甜點', ' dessert', '蛋糕', '刨冰']): return '甜點'
    if any(k in t for k in ['居酒屋', '燒肉', '拉麵', '壽司', '海鮮', '餐廳']): return '餐廳'
    return '小吃'

# ── Station targets ─────────────────────────────────────────────────────────────
STATIONS = {
    'seoul': [
        ('seoul_042', '仁川機場1號站', '仁川機場', 'large'),
        ('seoul_043', '仁川機場2號站', '仁川機場', 'large'),
        ('seoul_022', '光化門站', '光化門', 'large'),
        ('seoul_017', '會賢站', '南大門', 'large'),
        ('seoul_024', '安國站', '三清洞', 'large'),
        ('seoul_037', '上鳳站', '上鳳', 'minor'),
        ('seoul_035', '九宜站', '九宜', 'minor'),
        ('seoul_045', 'Digital Media City站', '上巿', 'minor'),
        ('seoul_063', 'Euljiro 1-ga Station', '乙支路', 'minor'),
        ('seoul_025', '仁寺洞站', '仁寺洞', 'minor'),
    ],
    'busan': [
        ('busan_001', '釜山站', '中央區', 'large'),
        ('busan_027', '札嘎其站', '南浦區', 'large'),
        ('busan_028', '南浦站', '南浦區', 'large'),
        ('busan_029', '中央站', '南浦區', 'large'),
        ('busan_045', '廣安站', '廣安區', 'large'),
        ('busan_018', '德川站', '北區', 'minor'),
        ('busan_019', '華明站', '北區', 'minor'),
        ('busan_059', '南區廳站', '南區', 'minor'),
        ('busan_023', '石峰站', '北區', 'minor'),
        ('busan_024', '凡內谷站', '北區', 'minor'),
    ],
    'fukuoka': [
        ('fukuoka_001', '博多站', '博多', 'large'),
        ('fukuoka_003', '中洲川端站', '中洲', 'large'),
        ('fukuoka_043', '久留米站', '久留米', 'large'),
        ('fukuoka_039', '折尾站', '八幡西區', 'large'),
        ('fukuoka_040', '黑崎站', '八幡西區', 'large'),
        ('fukuoka_025', '福大前站', '七隈', 'minor'),
        ('fukuoka_049', '田主丸站', '久留米', 'minor'),
        ('fukuoka_045', '基山站', '基山', 'minor'),
        ('fukuoka_026', '六本鬆站', '六本鬆', 'minor'),
        ('fukuoka_027', '別府站', '別府', 'minor'),
    ],
    'osaka': [
        ('osaka_station_030', '大阪上本町', '上本町', 'large'),
        ('osaka_station_007', '京橋（JR）', '京橋', 'large'),
        ('osaka_station_033', '今宮（JR）', '今宮', 'large'),
        ('osaka_station_058', '住之江公園', '住之江', 'large'),
        ('osaka_station_102', '佐野（JR）', '佐野', 'large'),
        ('osaka_station_062', '今里（地下鐵）', '今里', 'minor'),
        ('osaka_station_064', '今里（長堀鶴見）', '今里', 'minor'),
        ('osaka_station_093', '初芝', '初芝', 'minor'),
        ('osaka_station_057', '北加賀屋', '北加賀屋', 'minor'),
        ('osaka_station_076', '北濱（京阪）', '北濱', 'minor'),
    ],
    'tokyo': [
        ('tokyo_005', '上野站', '上野', 'large'),
        ('tokyo_001', '東京站', '丸之內', 'large'),
        ('tokyo_089', '下北澤站', '下北澤', 'large'),
        ('tokyo_065', '五反田站', '五反田', 'large'),
        ('tokyo_035', '九段下站', '九段下', 'large'),
        ('tokyo_088', '三鷹站', '三鷹', 'minor'),
        ('tokyo_079', '中井站', '中井', 'minor'),
        ('tokyo_080', '下落合站', '下落合', 'minor'),
        ('tokyo_078', '代代木公園站', '代代木', 'minor'),
        ('tokyo_054', '住吉站', '住吉', 'minor'),
    ],
    'okinawa': [
        ('okinawa_station_020', '石川站', '中部', 'large'),
        ('okinawa_station_021', '嘉手納站', '中部', 'large'),
        ('okinawa_station_022', '北谷站', '中部', 'large'),
        ('okinawa_station_023', '北谷Perry站', '中部', 'large'),
        ('okinawa_station_024', '勝連城跡站', '中部', 'large'),
        ('okinawa_station_025', '讀谷站', '中部', 'minor'),
        ('okinawa_station_026', '恩納休憩所站', '中部', 'minor'),
        ('okinawa_station_027', '萬座毛站', '中部', 'minor'),
        ('okinawa_station_028', '琉球村站', '中部', 'minor'),
        ('okinawa_station_029', '泡瀨站', '中部', 'minor'),
    ],
}

MINOR_KEYWORDS = ['小吃', '咖啡', '甜點', '居酒屋']

# ── Main ──────────────────────────────────────────────────────────────────────
total_inserted = 0
stations_covered = []

for region in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
    stations = STATIONS[region]
    print(f"\n{'='*55}")
    print(f"  REGION: {region.upper()} ({len(stations)} stations)")
    print(f"{'='*55}")

    for station_id, station_name, zone, stype in stations:
        name_clean = normalize_name(station_name)
        print(f"\n  [{stype.upper():5}] {station_name}")

        queries = []
        if stype == 'large':
            queries.append(f"{name_clean} {zone} 美食 2025 2026 部落格")
            queries.append(f"{name_clean} 車站 周邊 美食 推薦 在地")
        else:
            queries.append(f"{name_clean} 在地美食 隱藏版 2025 2026")
            for kw in MINOR_KEYWORDS[:2]:
                queries.append(f"{name_clean} {kw} 在地 推薦")

        all_results = []
        for q in queries:
            try:
                res = web_search(q, limit=8)
                for item in res.get('data', {}).get('web', []):
                    if item.get('url') and item.get('title'):
                        all_results.append(item)
            except Exception as e:
                print(f"    [WARN] search error: {e}")

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in all_results:
            url = r['url']
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        print(f"    {len(unique)} unique results")

        inserted_this = 0
        for item in unique[:8]:
            url = item['url']
            title = item['title'].strip()

            if not url or not title or len(title) < 3:
                continue
            if meal_exists(url):
                print(f"    [SKIP] already exists: {url[:55]}")
                continue

            sub_cat = get_sub_category(title)
            base = short_id_for_name(title, region)
            # ensure unique id
            meal_id = base
            attempt = 0
            while True:
                conn_t = sqlite3.connect(DB_PATH)
                cur_t = conn_t.cursor()
                cur_t.execute("SELECT 1 FROM meals WHERE id=?", (meal_id,))
                dup = cur_t.fetchone()
                conn_t.close()
                if not dup:
                    break
                attempt += 1
                meal_id = f"{base}_{attempt}"

            meal = {
                'id': meal_id,
                'region_code': region,
                'station_id': station_id,
                'name': title[:80],
                'category': 'meal',
                'sub_category': sub_cat,
                'zone': zone,
                'sources': [url],
                'details': {'blog_article': url},
            }

            try:
                ok = insert_meal(meal)
                if ok:
                    inserted_this += 1
                    stations_covered.append(f"{region}:{station_name}")
                    print(f"    [NEW] ({sub_cat}) {title[:45]}...")
                else:
                    print(f"    [SKIP] dup id: {meal_id}")
            except Exception as e:
                print(f"    [ERROR] {e}")

        if inserted_this > 0:
            print(f"    +{inserted_this} meals")
        total_inserted += inserted_this
        time.sleep(0.5)

print(f"\n{'='*60}")
print(f"  COMPLETE -- inserted {total_inserted} meals")
print(f"  Stations covered: {len(stations_covered)}")
print(f"{'='*60}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for region in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
    cur.execute("SELECT COUNT(*) FROM meals WHERE region_code=?", (region,))
    cnt = cur.fetchone()[0]
    print(f"  {region}: {cnt} meals")
conn.close()
