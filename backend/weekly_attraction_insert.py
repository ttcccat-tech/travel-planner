#!/usr/bin/env python3
"""Weekly attraction update script - 2026-09-18"""
import sqlite3
import json
import os

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def make_details(google_maps=None, blog_article=None, youtube=None):
    d = {}
    if google_maps:
        d['google_maps'] = google_maps
    if blog_article:
        d['blog_article'] = blog_article
    if youtube:
        d['youtube'] = youtube
    return json.dumps(d, ensure_ascii=False)

def insert_attraction(conn, cur, attractions_data):
    inserted = []
    for item in attractions_data:
        # Check duplicate by name + station_id
        cur.execute(
            "SELECT id FROM attractions WHERE name=? AND station_id=?",
            (item['name'], item['station_id'])
        )
        if cur.fetchone():
            print(f"  SKIP (duplicate): {item['name']} @ {item['station_id']}")
            continue

        details = make_details(
            item.get('google_maps'),
            item.get('blog_article'),
            item.get('youtube')
        )
        cur.execute("""
            INSERT INTO attractions (id, name, region_code, zone, category, station_id, details, sources, ticket, stay_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['id'],
            item['name'],
            item['region_code'],
            item['zone'],
            item['category'],
            item['station_id'],
            details,
            json.dumps([item['source_url']] if item.get('source_url') else [], ensure_ascii=False),
            item.get('ticket', ''),
            item.get('stay_duration', '')
        ))
        inserted.append(item['name'])
        print(f"  INSERTED: {item['name']} ({item['category']}) @ {item['station_id']}")
    return inserted

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

all_inserted = []

# ── SEOUL ──────────────────────────────────────────────────────────────────
print("\n=== SEOUL ===")
seoul_atts = [
    {
        'id': 'seoul_attr_001',
        'name': '水逾中央市場',
        'region_code': 'seoul',
        'zone': '水逾',
        'category': 'hidden_gem',
        'station_id': 'seoul_040',
        'google_maps': 'https://www.google.com/maps/place/%EC%88%98%EC%9C%A0%EC%A4%91%EC%95%99%EC%8B%9C%EC%9E%A5/data=!3m1!1e3',
        'blog_article': 'https://koreanmedi.com/search/?keyword=%EC%88%98%EC%9C%A0%EC%A4%91%EC%95%99%EC%8B%9C%EC%9E%A5',
        'source_url': 'https://koreanmedi.com/search/?keyword=%EC%88%98%EC%9C%A0%EC%A4%91%EC%95%99%EC%8B%9C%EC%9E%A5',
        'estimated_price': '₩10,000-30,000',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'seoul_attr_002',
        'name': '北部市場',
        'region_code': 'seoul',
        'zone': '水逾',
        'category': 'hidden_gem',
        'station_id': 'seoul_040',
        'google_maps': 'https://www.google.com/maps/place/%EB%B6%81%EB%B6%80%EC%8B%9C%EC%9E%A5/data=!3m1!1e3',
        'blog_article': 'https://blog.naver.com/search/blog?searchType=blog&keyword=%EB%B6%81%EB%B6%80%EC%8B%9C%EC%9E%A5+%EC%88%98%EC%9C%A0',
        'source_url': 'https://blog.naver.com/search/blog?searchType=blog&keyword=%EB%B6%81%EB%B6%80%EC%8B%9C%EC%9E%A5+%EC%88%98%EC%9C%A0',
        'estimated_price': '₩10,000-30,000',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'seoul_attr_003',
        'name': '華溪寺',
        'region_code': 'seoul',
        'zone': '水逾',
        'category': 'attraction',
        'station_id': 'seoul_040',
        'google_maps': 'https://www.google.com/maps/place/%ED%99%94%EA%B3%84%EC%82%AC/data=!3m1!1e3',
        'blog_article': 'https://blog.naver.com/search/blog?searchType=blog&keyword=%ED%99%94%EA%B3%84%EC%82%AC+%EC%88%98%EC%9C%A0+%EA%B4%80%EA%B8%B0',
        'source_url': 'https://blog.naver.com/search/blog?searchType=blog&keyword=%ED%99%94%EA%B3%84%EC%82%AC+%EC%88%98%EC%9C%A0+%EA%B4%80%EA%B8%B0',
        'estimated_price': '免費',
        'estimated_time': '1-2小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, seoul_atts))

# ── BUSAN ──────────────────────────────────────────────────────────────────
print("\n=== BUSAN ===")
busan_atts = [
    {
        'id': 'busan_attr_001',
        'name': '寶水洞二手書店街',
        'region_code': 'busan',
        'zone': '海雲台區',
        'category': 'hidden_gem',
        'station_id': 'busan_038',
        'google_maps': 'https://www.google.com/maps/place/%EB%B0%A1%EC%88%98%EB%93%B1%EC%8B%9C%EC%84%A4%EA%B8%B8',
        'blog_article': 'https://koreanmedi.com/search/?keyword=%EB%B0%A1%EC%88%98%EB%93%B1%EC%8B%9C%EC%84%A4%EA%B8%B8',
        'source_url': 'https://koreanmedi.com/search/?keyword=%EB%B0%A1%EC%88%98%EB%93%B1%EC%8B%9C%EC%84%A4%EA%B8%B8',
        'estimated_price': '免費',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'busan_attr_002',
        'name': '松島海上纜車',
        'region_code': 'busan',
        'zone': '西區',
        'category': 'attraction',
        'station_id': 'busan_033',
        'google_maps': 'https://www.google.com/maps/place/%EC%86%A1%EB%8F%84%ED%95%AD%EC%83%81%EC%9E%90%EB%8F%99%EC%B0%A8',
        'blog_article': 'https://koreanmedi.com/search/?keyword=%EC%86%A1%EB%8F%84%ED%95%AD%EC%83%81%EC%9E%90%EB%8F%99%EC%B0%A8',
        'source_url': 'https://koreanmedi.com/search/?keyword=%EC%86%A1%EB%8F%84%ED%95%AD%EC%83%81%EC%9E%90%EB%8F%99%EC%B0%A8',
        'estimated_price': '₩20,000-35,000',
        'estimated_time': '1-2小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, busan_atts))

# ── FUKUOKA ───────────────────────────────────────────────────────────────
print("\n=== FUKUOKA ===")
fukuoka_atts = [
    {
        'id': 'fukuoka_attr_001',
        'name': '福岡亞洲美術館',
        'region_code': 'fukuoka',
        'zone': '中洲',
        'category': 'attraction',
        'station_id': 'fukuoka_003',
        'google_maps': 'https://www.google.com/maps/place/%ED%94%84%EB%A5%9C%EC%95%84%EC%8B%9C%EC%95%84%EC%97%AD%EC%88%98%EC%84%A4',
        'blog_article': 'https://www.fukuokanow.com/spot/museum/',
        'source_url': 'https://www.fukuokanow.com/spot/museum/',
        'estimated_price': '¥200-500',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'fukuoka_attr_002',
        'name': '博多運河城',
        'region_code': 'fukuoka',
        'zone': '博多',
        'category': 'attraction',
        'station_id': 'fukuoka_002',
        'google_maps': 'https://www.google.com/maps/place/%EB%B0%A4%ED%86%A8%EC%9A%B4%ED%96%89%EC%8B%B1',
        'blog_article': 'https://canalcity.co.jp/',
        'source_url': 'https://canalcity.co.jp/',
        'estimated_price': '免費（演出需購票）',
        'estimated_time': '2-3小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, fukuoka_atts))

# ── OSAKA ─────────────────────────────────────────────────────────────────
print("\n=== OSAKA ===")
osaka_atts = [
    {
        'id': 'osaka_attr_001',
        'name': '仁德天皇陵古填',
        'region_code': 'osaka',
        'zone': '堺',
        'category': 'attraction',
        'station_id': 'osaka_station_103',
        'google_maps': 'https://www.google.com/maps/place/%E4%BB%81%E5%BE%B7%E5%A4%A9%E7%9A%87%E9%99%B5%E5%8F%A4%E5%A3%BD',
        'blog_article': 'https://www.japan.travel/tw/world-heritage/mozu-furuichi-kofun',
        'source_url': 'https://www.japan.travel/tw/world-heritage/mozu-furuichi-kofun',
        'estimated_price': '免費',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'osaka_attr_002',
        'name': '百舌鳥古填群',
        'region_code': 'osaka',
        'zone': '堺',
        'category': 'attraction',
        'station_id': 'osaka_station_103',
        'google_maps': 'https://www.google.com/maps/place/%E7%99%BE%E8%88%8D%E9%B3%8E%E5%8F%A4%E5%A3%BD%E7%BE%A4',
        'blog_article': 'https://www.japan.travel/tw/world-heritage/mozu-furuichi-kofun',
        'source_url': 'https://www.japan.travel/tw/world-heritage/mozu-furuichi-kofun',
        'estimated_price': '免費',
        'estimated_time': '2-3小時'
    },
    {
        'id': 'osaka_attr_003',
        'name': '堺市博物館',
        'region_code': 'osaka',
        'zone': '堺',
        'category': 'attraction',
        'station_id': 'osaka_station_103',
        'google_maps': 'https://www.google.com/maps/place/%E5%A0%BA%E5%B8%82%E5%8D%9A%E5%BF%92%E9%A6%86',
        'blog_article': 'https://www.sakai-tcb.or.jp/zh-tw/spot/detail/70',
        'source_url': 'https://www.sakai-tcb.or.jp/zh-tw/spot/detail/70',
        'estimated_price': '¥200-500',
        'estimated_time': '1-2小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, osaka_atts))

# ── TOKYO (下北澤豐富) ────────────────────────────────────────────────────
print("\n=== TOKYO ===")
tokyo_atts = [
    {
        'id': 'tokyo_attr_001',
        'name': '下北澤一番街',
        'region_code': 'tokyo',
        'zone': '下北澤',
        'category': 'hidden_gem',
        'station_id': 'tokyo_089',
        'google_maps': 'https://www.google.com/maps/place/%E4%B8%8B%E5%8C%97%E6%BE%A4%E4%B8%80%E7%95%AA%E8%A1%97',
        'blog_article': 'https://www.japan.travel/hk/destinations/kanto/tokyo/shibuya-and-shimokitazawa',
        'source_url': 'https://www.japan.travel/hk/destinations/kanto/tokyo/shibuya-and-shimokitazawa',
        'estimated_price': '免費',
        'estimated_time': '1-2小時'
    },
    {
        'id': 'tokyo_attr_002',
        'name': '本屋B&B 下北澤',
        'region_code': 'tokyo',
        'zone': '下北澤',
        'category': 'hidden_gem',
        'station_id': 'tokyo_089',
        'google_maps': 'https://www.google.com/maps/place/%E6%9C%AC%E5%B1%8BBB',
        'blog_article': 'https://www.japan.travel/hk/destinations/kanto/tokyo/shibuya-and-shimokitazawa',
        'source_url': 'https://www.japan.travel/hk/destinations/kanto/tokyo/shibuya-and-shimokitazawa',
        'estimated_price': '¥1,000-2,000',
        'estimated_time': '1小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, tokyo_atts))

# ── OKINAWA ───────────────────────────────────────────────────────────────
print("\n=== OKINAWA ===")
okinawa_atts = [
    {
        'id': 'okinawa_attr_001',
        'name': '山原咖啡',
        'region_code': 'okinawa',
        'zone': '北部',
        'category': 'hidden_gem',
        'station_id': 'okinawa_station_048',
        'google_maps': 'https://www.google.com/maps/place/%E5%B1%B1%E5%8E%9F%E3%82%AB%E3%83%95%E3%82%A7',
        'blog_article': 'https://okinawa.letsgojp.com/archives/853507',
        'source_url': 'https://okinawa.letsgojp.com/archives/853507',
        'estimated_price': '¥800-1,500',
        'estimated_time': '1小時'
    },
]
all_inserted.extend(insert_attraction(conn, cur, okinawa_atts))

conn.commit()
conn.close()

print(f"\n✅ 本週新增 {len(all_inserted)} 筆景點（來自 6 個車站）")
for name in all_inserted:
    print(f"  • {name}")
