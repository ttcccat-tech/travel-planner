#!/usr/bin/env python3
"""Weekly Station Food Scan — 2026-09-19"""

import sqlite3, json, re, sys, os, time
sys.path.insert(0, '/var/repo/travel-planner')

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

# ── Station selection ──────────────────────────────────────────────────────────
# Large (tourist) stations per region — picked from diverse zones
LARGE_STATIONS = {
    'seoul': [
        ('seoul_042', '仁川機場1號站', '仁川機場'),
        ('seoul_043', '仁川機場2號站', '仁川機場'),
        ('seoul_022', '光化門站', '光化門'),
        ('seoul_017', '會賢站', '南大門'),
        ('seoul_024', '安國站', '三清洞'),
    ],
    'busan': [
        ('busan_001', '釜山站', '中央區'),
        ('busan_027', '札嘎其站', '南浦區'),
        ('busan_028', '南浦站', '南浦區'),
        ('busan_029', '中央站', '南浦區'),
        ('busan_045', '廣安站', '廣安區'),
    ],
    'fukuoka': [
        ('fukuoka_001', '博多站', '博多'),
        ('fukuoka_003', '中洲川端站', '中洲'),
        ('fukuoka_043', '久留米站', '久留米'),
        ('fukuoka_039', '折尾站', '八幡西區'),
        ('fukuoka_040', '黑崎站', '八幡西區'),
    ],
    'osaka': [
        ('osaka_station_030', '大阪上本町', '上本町'),
        ('osaka_station_007', '京橋（JR）', '京橋'),
        ('osaka_station_033', '今宮（JR）', '今宮'),
        ('osaka_station_058', '住之江公園', '住之江'),
        ('osaka_station_102', '佐野（JR）', '佐野'),
    ],
    'tokyo': [
        ('tokyo_005', '上野站', '上野'),
        ('tokyo_001', '東京站', '丸之內'),
        ('tokyo_089', '下北澤站', '下北澤'),
        ('tokyo_065', '五反田站', '五反田'),
        ('tokyo_035', '九段下站', '九段下'),
    ],
    'okinawa': [
        ('okinawa_station_020', '石川站', '中部'),
        ('okinawa_station_021', '嘉手納站', '中部'),
        ('okinawa_station_022', '北谷站', '中部'),
        ('okinawa_station_023', '北谷Perry站', '中部'),
        ('okinawa_station_024', '勝連城跡站', '中部'),
    ],
}

# Minor (local) stations per region — smaller stations, different from large ones
MINOR_STATIONS = {
    'seoul': [
        ('seoul_037', '上鳳站', '上鳳'),
        ('seoul_035', '九宜站', '九宜'),
        ('seoul_045', 'Digital Media City站', '上巿'),
        ('seoul_063', 'Euljiro 1-ga Station', '乙支路'),
        ('seoul_025', '仁寺洞站', '仁寺洞'),
    ],
    'busan': [
        ('busan_018', '德川站', '北區'),
        ('busan_019', '華明站', '北區'),
        ('busan_059', '南區廳站', '南區'),
        ('busan_023', '石峰站', '北區'),
        ('busan_024', '凡內谷站', '北區'),
    ],
    'fukuoka': [
        ('fukuoka_025', '福大前站', '七隈'),
        ('fukuoka_049', '田主丸站', '久留米'),
        ('fukuoka_045', '基山站', '基山'),
        ('fukuoka_026', '六本鬆站', '六本鬆'),
        ('fukuoka_027', '別府站', '別府'),
    ],
    'osaka': [
        ('osaka_station_062', '今里（地下鐵）', '今里'),
        ('osaka_station_064', '今里（長堀鶴見）', '今里'),
        ('osaka_station_093', '初芝', '初芝'),
        ('osaka_station_057', '北加賀屋', '北加賀屋'),
        ('osaka_station_076', '北濱（京阪）', '北濱'),
    ],
    'tokyo': [
        ('tokyo_088', '三鷹站', '三鷹'),
        ('tokyo_079', '中井站', '中井'),
        ('tokyo_080', '下落合站', '下落合'),
        ('tokyo_078', '代代木公園站', '代代木'),
        ('tokyo_054', '住吉站', '住吉'),
    ],
    'okinawa': [
        ('okinawa_station_025', '讀谷站', '中部'),
        ('okinawa_station_026', '恩納休憩所站', '中部'),
        ('okinawa_station_027', '萬座毛站', '中部'),
        ('okinawa_station_028', '琉球村站', '中部'),
        ('okinawa_station_029', '泡瀨站', '中部'),
    ],
}

# Keywords for minor station food searches
MINOR_KEYWORDS = ['小吃', '咖啡', '甜點', '居酒屋']

# ── Helpers ───────────────────────────────────────────────────────────────────

def short_id(base_name, region_code):
    """Generate a short alphanumeric id from a name."""
    slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', base_name)
    slug = re.sub(r'[\u4e00-\u9fff]', '', slug)  # remove CJK for latin slug
    if not slug:
        slug = base_name[:4]
    short = slug[:8].lower()
    return f"{region_code[:2]}_m_{short}"


def normalize_name(name):
    """Strip station suffix for cleaner matching."""
    return re.sub(r'[\s（(].*$', '', name)


def get_station_id(region_code, hint):
    """Fuzzy match station by name hint."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM stations WHERE region_code=? AND name LIKE ? LIMIT 1",
        (region_code, f'%{hint}%')
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def meal_exists(url):
    """Check if a URL is already in the meals table."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM meals WHERE sources LIKE ?", (f'%{url}%',))
    row = cur.fetchone()
    conn.close()
    return row is not None


def insert_meal(meal):
    """Insert a meal record. Returns True if inserted, False if skipped."""
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


def region_code_from_station_id(station_id):
    """Extract region code from station id."""
    return station_id.rsplit('_', 1)[0].replace('station_', '_')


# ── Web search (stub for use with hermes web_search) ──────────────────────────
# The actual search is done via the execute_code below which calls hermes tools

def main():
    from hermes_tools import web_search, terminal

    total_new = 0
    stations_covered = set()

    all_stations = {}
    for region, stations in LARGE_STATIONS.items():
        for sid, sname, zone in stations:
            all_stations.setdefault(region, []).append((sid, sname, zone, 'large'))
    for region, stations in MINOR_STATIONS.items():
        for sid, sname, zone in stations:
            all_stations.setdefault(region, []).append((sid, sname, zone, 'minor'))

    for region in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
        if region not in all_stations:
            continue
        print(f"\n{'='*50}")
        print(f"  REGION: {region.upper()}")
        print(f"{'='*50}")

        for station_id, station_name, zone, stype in all_stations[region]:
            print(f"\n  [{stype.upper()}] {station_name} ({station_id})")
            name_clean = normalize_name(station_name)

            # Build search queries
            queries = []
            if stype == 'large':
                queries.append(f"{name_clean} {zone} 美食 2025 2026 部落格")
                queries.append(f"{name_clean} 車站 周邊 美食 推薦")
            else:
                queries.append(f"{name_clean} 在地美食 隱藏版 2025 2026")
                for kw in MINOR_KEYWORDS[:2]:  # 2 keyword variations for minor
                    queries.append(f"{name_clean} {kw} 在地")

            results = []
            for q in queries:
                try:
                    res = web_search(q, limit=6)
                    for item in res.get('data', {}).get('web', []):
                        results.append(item)
                except Exception as e:
                    print(f"    [WARN] search failed: {e}")

            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for r in results:
                url = r.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)

            print(f"    Found {len(unique_results)} unique results")

            inserted = 0
            for item in unique_results[:8]:  # max 8 per station
                url = item.get('url', '')
                title = item.get('title', '').strip()
                if not url or not title:
                    continue
                if meal_exists(url):
                    print(f"    [SKIP] already exists: {url[:60]}")
                    continue

                # Determine sub_category from title/keywords
                sub_cat = '小吃'
                for kw in ['咖啡', 'cafe', '甜點', ' dessert', '居酒屋', '燒肉', '拉麵', '壽司', '海鮮']:
                    if kw.lower() in title.lower():
                        if kw in ['咖啡', 'cafe']: sub_cat = '咖啡'
                        elif kw in ['甜點', ' dessert']: sub_cat = '甜點'
                        elif kw in ['居酒屋']: sub_cat = '居酒屋'
                        elif kw in ['燒肉', '拉麵', '壽司', '海鮮']: sub_cat = '餐廳'
                        break

                # Generate id
                base = short_id(title, region)
                mid = re.sub(r'[^a-zA-Z0-9]', '', title)[:8].lower()
                meal_id = f"{region[:2]}_m_{mid}" if mid else base

                # Handle duplicate id
                attempt = 0
                original_id = meal_id
                while True:
                    try:
                        conn_test = sqlite3.connect(DB_PATH)
                        cur_test = conn_test.cursor()
                        cur_test.execute("SELECT 1 FROM meals WHERE id=?", (meal_id,))
                        exists = cur_test.fetchone()
                        conn_test.close()
                        if not exists:
                            break
                        attempt += 1
                        meal_id = f"{original_id}_{attempt}"
                    except:
                        break

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
                        inserted += 1
                        stations_covered.add(f"{region}:{station_name}")
                        print(f"    [NEW] {title[:50]}...")
                    else:
                        print(f"    [SKIP] insert failed (dup): {meal_id}")
                except Exception as e:
                    print(f"    [ERROR] insert failed: {e}")

            if inserted > 0:
                print(f"    ✓ Inserted {inserted} meals")
            time.sleep(1)  # be polite

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for region in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
        cur.execute("SELECT COUNT(*) FROM meals WHERE region_code=?", (region,))
        cnt = cur.fetchone()[0]
        print(f"  {region}: {cnt} meals")
    conn.close()

    print(f"\n  Stations covered this run: {len(stations_covered)}")
    print(f"  Done.")


if __name__ == '__main__':
    main()
