#!/usr/bin/env python3
"""
每週車站美食掃描任務
- 大站（每週5個）：主要觀光/轉乘大站
- 小站（每兩週5個）：周邊隱藏版美食
"""

import sqlite3, json, re, time, random, os
from datetime import datetime

DB_PATH = "/var/repo/travel-planner/backend/travel.db"
REGIONS = ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']

# ============================================================
# Station selection
# ============================================================

# 大站：主要觀光/轉乘大站（固定每週）
LARGE_STATIONS = {
    'seoul': [
        ('seoul_001', '首爾站'),
        ('seoul_004', '弘大入口站'),
        ('seoul_002', '龍山站'),
        ('seoul_009', '合井站'),
        ('seoul_010', '堂山站'),
    ],
    'busan': [
        ('busan_001', '釜山站'),
        ('busan_002', '草梁站'),
        ('busan_009', '金堂站'),
        ('busan_010', '冷井站'),
        ('busan_006', '溫泉場站'),
    ],
    'fukuoka': [
        ('fukuoka_001', '博多站'),
        ('fukuoka_003', '中洲川端站'),
        ('fukuoka_004', '天神站'),
        ('fukuoka_005', '天神南站'),
        ('fukuoka_007', '渡邊通站'),
    ],
    'osaka': [
        ('osaka_station_001', '大阪站'),
        ('osaka_station_002', '新大阪'),
        ('osaka_station_003', '天王寺'),
        ('osaka_station_004', '難波'),
        ('osaka_station_007', '京橋'),
    ],
    'tokyo': [
        ('tokyo_001', '東京站'),
        ('tokyo_002', '新宿站'),
        ('tokyo_003', '澀谷站'),
        ('tokyo_004', '池袋站'),
        ('tokyo_005', '上野站'),
    ],
    'okinawa': [
        ('okinawa_station_001', '那霸機場'),
        ('okinawa_station_002', '赤崗'),
        ('okinawa_station_005', '旭橋'),
        ('okinawa_station_008', '縣廳前'),
        ('okinawa_station_009', '牧志'),
    ],
}

# 小站：隨機抽取非大站（每兩週一次）
SMALL_STATION_POOL = {
    'seoul': [
        ('seoul_037', '上鳳站'), ('seoul_039', '忠岩站'), ('seoul_028', '惠化站'),
        ('seoul_019', '會賢站'), ('seoul_014', '乙支路4街站'),
        ('seoul_042', '新增站A'), ('seoul_043', '新增站B'),
    ],
    'busan': [
        ('busan_056', '巨堤站'), ('busan_047', 'MOOP站'), ('busan_021', '龜賢站'),
        ('busan_054', '上唐站'), ('busan_022', '梵魚寺站'),
        ('busan_060', '海雲台站'), ('busan_061', '廣安站'),
    ],
    'fukuoka': [
        ('fukuoka_024', '梅林站'), ('fukuoka_019', '築約站'), ('fukuoka_035', '周船寺站'),
        ('fukuoka_039', '折尾站'), ('fukuoka_018', '箱崎站'),
        ('fukuoka_040', '姪濱站'), ('fukuoka_041', '別府站'),
    ],
    'osaka': [
        ('osaka_station_089', '河内松原'), ('osaka_station_056', '長田'),
        ('osaka_station_050', '長柄橋'), ('osaka_station_097', '和泉中央'),
        ('osaka_station_104', 'LR鳳'),
        ('osaka_station_105', '臨空城站'), ('osaka_station_106', '關西機場站'),
    ],
    'tokyo': [
        ('tokyo_032', '芝公園站'), ('tokyo_099', '千歲船橋站'), ('tokyo_038', '本鄉三丁目站'),
        ('tokyo_028', '日暮里站'), ('tokyo_031', '赤羽橋站'),
        ('tokyo_100', '高輪Gateway站'), ('tokyo_101', '豐洲站'),
    ],
    'okinawa': [
        ('okinawa_station_019', '市立病院前'), ('okinawa_station_056', '阿嘉'),
        ('okinawa_station_029', '泡瀨'), ('okinawa_station_038', '平和祈念資料館'),
        ('okinawa_station_050', '運天港'),
        ('okinawa_station_060', '讀谷站'), ('okinawa_station_061', '北谷站'),
    ],
}

# ============================================================
# Search query templates
# ============================================================

REGION_NAME = {'seoul':'首爾','busan':'釜山','fukuoka':'福岡','osaka':'大阪','tokyo':'東京','okinawa':'沖繩'}

def get_large_queries(station_name, region):
    r = REGION_NAME[region]
    return [
        f"{station_name} {r} 美食 2025 2026 部落格",
        f"{station_name} {r} 美食 推薦 在地",
        f"{station_name} 火車站 美食 隱藏版",
    ]

def get_small_queries(station_name, region):
    r = REGION_NAME[region]
    return [
        f"{station_name} {r} 在地美食 隱藏版 2025 2026",
        f"{station_name} {r} 小吃 早餐 豆腐鍋",
        f"{station_name} {r} 咖啡 甜點 下午茶",
    ]

# ============================================================
# URL extraction from search results (mock - to be replaced with real web_search calls)
# ============================================================

def extract_urls_from_search(results_json):
    """Extract URLs from web_search results structure."""
    urls = []
    try:
        if isinstance(results_json, dict) and 'data' in results_json:
            for item in results_json['data'].get('web', []):
                url = item.get('url', '')
                if url and url.startswith('http'):
                    urls.append(url)
        elif isinstance(results_json, list):
            for item in results_json:
                if isinstance(item, dict):
                    url = item.get('url', '') or item.get('link', '')
                    if url and url.startswith('http'):
                        urls.append(url)
    except Exception as e:
        print(f"  [WARN] URL extraction error: {e}")
    return urls

# ============================================================
# Database helpers
# ============================================================

def get_existing_urls(conn):
    """Return set of all existing meal sources URLs."""
    cur = conn.cursor()
    cur.execute("SELECT sources FROM meals WHERE sources IS NOT NULL")
    existing = set()
    for (sources,) in cur.fetchall():
        if sources:
            try:
                arr = json.loads(sources)
                for u in arr:
                    if isinstance(u, str) and u.startswith('http'):
                        existing.add(u)
            except:
                pass
    return existing

def meal_exists_by_url(conn, url):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM meals WHERE sources LIKE ?", (f'%{url}%',))
    return cur.fetchone()[0] > 0

def get_station_zone(conn, station_id):
    cur = conn.cursor()
    cur.execute("SELECT zone FROM stations WHERE id=?", (station_id,))
    row = cur.fetchone()
    return row[0] if row else None

def generate_id(name, region_code):
    """Generate a short unique ID from name."""
    # Remove non-CJK alphanumeric, take first 8 chars, add region suffix
    clean = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
    short = clean[:6]
    return f"{region_code}_{short}"

def insert_meal(conn, meal):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR IGNORE INTO meals (
                id, region_code, station_id, name, category, sub_category,
                zone, location, ticket, description, sources, details,
                created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            meal['id'],
            meal['region_code'],
            meal['station_id'],
            meal['name'],
            'meal',
            meal.get('sub_category', '小吃'),
            meal.get('zone', ''),
            meal.get('location', ''),
            meal.get('ticket', ''),
            meal.get('description', ''),
            json.dumps(meal.get('sources', []), ensure_ascii=False),
            json.dumps({'blog_article': meal.get('blog_article', '')}, ensure_ascii=False),
            datetime.now().isoformat(),
        ))
        return cur.rowcount > 0
    except Exception as e:
        print(f"  [WARN] Insert error for {meal['name']}: {e}")
        return False

# ============================================================
# Stub: search_web — calls web_search via terminal curl
# We use subprocess + hermes_tools via terminal to call web_search
# Actually we need to call web_search tool directly
# This is a stub that will be replaced with actual search logic
# ============================================================

def search_and_extract_venues(station_id, station_name, region, existing_urls, week_is_even):
    """
    For a station, run searches and return list of dicts:
    {name, blog_article, sub_category, description}
    """
    results = []
    queries = (get_large_queries if week_is_even else get_small_queries)(station_name, region)
    
    # Also include extra queries for diversity
    extra_queries = [
        f"{station_name} 居酒屋 美食",
        f"{station_name} 拉麵 沾麵",
        f"{station_name} 燒肉 韓牛",
    ]
    all_queries = queries + extra_queries[:2]  # limit to 5 total queries per station
    
    all_urls = []
    for query in all_queries[:5]:
        # Use web_search via terminal (we'll implement a simple HTTP search)
        # For now, we'll accumulate URLs from searches
        pass
    
    return results

# ============================================================
# Main logic: uses web_search from hermes_tools via execute_code
# We'll build this as a comprehensive script below
# ============================================================

def main():
    week_num = datetime.now().isocalendar()[1]
    week_is_even = week_num % 2 == 0
    print(f"Week {week_num} ({'even' if week_is_even else 'odd'}) — {'including small stations' if week_is_even else 'large stations only'}")

    conn = sqlite3.connect(DB_PATH)
    existing_urls = get_existing_urls(conn)
    print(f"Existing meal URLs in DB: {len(existing_urls)}")

    new_meals_count = 0
    new_meals_by_station = {}

    for region in REGIONS:
        rname = REGION_NAME[region]
        large = LARGE_STATIONS[region]
        small = SMALL_STATION_POOL[region] if week_is_even else []

        stations_to_process = large + (small[:5] if small else [])

        for station_id, station_name in stations_to_process:
            try:
                zone = get_station_zone(conn, station_id) or rname
                
                # Build search queries
                queries = get_large_queries(station_name, region) if station_id in [s[0] for s in large] else get_small_queries(station_name, region)
                
                # Add diversity queries
                extra_q = [
                    f"{station_name} {rname} 居酒屋",
                    f"{station_name} {rname} 咖啡 甜點",
                    f"{station_name} {rname} 拉麵 小吃",
                ]
                all_q = queries[:3] + extra_q[:2]

                # We collect URLs and metadata but for a cron script
                # we rely on the search results we can gather
                # Since we can't do interactive web_search in a loop here,
                # we'll mark the pattern and collect what we can
                
                if station_id not in new_meals_by_station:
                    new_meals_by_station[station_id] = {'name': station_name, 'meals': []}

            except Exception as e:
                print(f"[ERROR] Station {station_id}: {e}")
                continue

    conn.close()
    print(f"\nSearches completed. Writing to DB...")
    # Note: actual web_search calls are done in the cron runner
    # This script is the template/structure

if __name__ == '__main__':
    main()
