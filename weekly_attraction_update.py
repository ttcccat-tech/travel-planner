#!/usr/bin/env python3
"""每週旅遊景點擴充腳本 - 2026-09-12"""

import sqlite3
import json
import uuid
import os
import sys

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def log(msg):
    print(f"[INFO] {msg}", flush=True)

def log_err(msg):
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)

def generate_id(name, region_code):
    """Generate a short ID from name"""
    # Create a simple slug
    slug = name[:20].lower()
    slug = ''.join(c if c.isalnum() else '_' for c in slug)
    return f"{region_code}_{slug[:15]}"

def check_exists(cur, name, region_code):
    """Check if attraction with same name already exists"""
    cur.execute(
        "SELECT id FROM attractions WHERE region_code=? AND name=?",
        (region_code, name)
    )
    return cur.fetchone() is not None

def insert_attraction(conn, cur, attraction):
    """Insert attraction, return True if inserted, False if skipped (duplicate)"""
    region = attraction['region_code']
    name = attraction['name']
    
    # Check duplicate by name
    if check_exists(cur, name, region):
        log(f"  SKIP (duplicate): {name}")
        return False
    
    # Generate ID
    att_id = generate_id(name, region)
    
    # Handle duplicate ID
    cur.execute("SELECT id FROM attractions WHERE id=?", (att_id,))
    if cur.fetchone():
        att_id = f"{att_id}_{str(uuid.uuid4())[:4]}"
    
    # Build details JSON
    details = {}
    if attraction.get('google_maps'):
        details['google_maps'] = attraction['google_maps']
    if attraction.get('blog_article'):
        details['blog_article'] = attraction['blog_article']
    if attraction.get('youtube'):
        details['youtube'] = attraction['youtube']
    
    # Build sources JSON
    sources = []
    if attraction.get('source_url'):
        sources.append(attraction['source_url'])
    
    # Build nearby_stations JSON
    nearby = []
    if attraction.get('nearby_stations'):
        nearby = attraction['nearby_stations']
    
    # Build tags JSON
    tags = []
    if attraction.get('tags'):
        tags = attraction['tags']
    
    cur.execute("""
        INSERT INTO attractions (
            id, region_code, station_id, name, name_en, category, sub_category,
            zone, location, lat, lng, ticket, stay_duration,
            need_reservation, cash_only, priority, tags, description,
            sources, nearby_stations, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        att_id,
        region,
        attraction.get('station_id'),
        name,
        attraction.get('name_en'),
        attraction.get('category', 'attraction'),
        attraction.get('sub_category'),
        attraction.get('zone'),
        attraction.get('location'),
        attraction.get('lat'),
        attraction.get('lng'),
        attraction.get('ticket'),
        attraction.get('stay_duration'),
        attraction.get('need_reservation', 0),
        attraction.get('cash_only', 0),
        attraction.get('priority', 3),
        json.dumps(tags, ensure_ascii=False),
        attraction.get('description'),
        json.dumps(sources, ensure_ascii=False),
        json.dumps(nearby, ensure_ascii=False),
        json.dumps(details, ensure_ascii=False)
    ))
    conn.commit()
    log(f"  INSERTED: {name} (id: {att_id})")
    return True

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    total_new = 0
    region_counts = {}
    
    # ============================================================
    # SEOUL - 은평구 area attractions
    # ============================================================
    log("\n=== Processing SEOUL attractions ===")
    seoul_stations = {
        'eunpyeong_hanok': None,  # station: None (not in DB)
        'ep_history_museum': None,
        'samgak_art': None,
        'ep_sports_center': None,
    }
    
    seoul_attrs = [
        {
            'name': '은평역사한옥박물관',
            'name_en': 'Eunpyeong Historical Hanok Museum',
            'region_code': 'seoul',
            'category': 'attraction',
            'sub_category': 'museum',
            'zone': '은평',
            'location': '서울특별시 은평구 연서로50길 8 (진관동)',
            'lat': 37.5761,
            'lng': 126.9294,
            'ticket': '성인 1,000원 / 학생 500원',
            'stay_duration': '1.5-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['한옥', '박물관', '은평', '체험'],
            'description': '은평구의 역사와 한옥 문화를 한눈에 볼 수 있는 박물관. 통일신라시대부터 현대에 이르는 은평구의 역사를 다양한 유물과 모형으로 전시. 2층 한옥전시실에서는 한옥의 건축 과정과 과학적 원리를 소개.',
            'source_url': 'https://museum.ep.go.kr/',
            'google_maps': 'https://maps.google.com/?q=은평역사한옥박물관',
            'nearby_stations': [],
            'station_id': None
        },
        {
            'name': '삼각산금암미술관',
            'name_en': 'Samgaksan Geumgang Art Museum',
            'region_code': 'seoul',
            'category': 'hidden_gem',
            'sub_category': 'museum',
            'zone': '은평',
            'location': '서울특별시 은평구 진관길 21-2',
            'lat': 37.5778,
            'lng': 126.9278,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['미술관', '은평', '한옥', '전시'],
            'description': '은평한옥마을 골목을 거닔다 보면 만나는 한옥이 미술관으로 변신한 공간. 사랑방과 대청마루 등 한옥 공간 곳곳에 예술 작품이 전시된 독특한 풍경.',
            'source_url': 'https://museum.ep.go.kr/',
            'google_maps': 'https://maps.google.com/?q=삼각산금암미술관',
            'nearby_stations': [],
            'station_id': None
        },
        {
            'name': '은평구민체육센터',
            'name_en': 'Eunpyeong Public Sports Center',
            'region_code': 'seoul',
            'category': 'attraction',
            'sub_category': 'sports',
            'zone': '은평',
            'location': '서울특별시 은평구 진관1로 40',
            'lat': 37.5794,
            'lng': 126.9228,
            'ticket': '프로그램별 상이',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['체육시설', '수영', '은평', '운동'],
            'description': '은평구민체육센터 수영장은 성인풀(25m) 7레인, 유아풀을 갖춘 공공 스포츠 시설. 지하 1층 수영장과 지상 3층 규모.',
            'source_url': 'https://www.efmc.or.kr/fmcs/8',
            'google_maps': 'https://maps.google.com/?q=은평구민체육센터',
            'nearby_stations': [],
            'station_id': None
        },
        {
            'name': '은평한옥마을 1인1잔 카페',
            'name_en': '1-in-1-jan Hanok Cafe',
            'region_code': 'seoul',
            'category': 'hidden_gem',
            'sub_category': 'cafe',
            'zone': '은평',
            'location': '서울특별시 은평구 연서로 534',
            'lat': 37.5767,
            'lng': 126.9289,
            'ticket': '무료입장 (음료 별도)',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['카페', '은평', '한옥', 'VIEW'],
            'description': '은평한옥마을 언덕에 자리한 인기 카페. 5층짜리 한옥 건물 전체를 카페로 운영하며, 위로 올라갈수록 북한산과 한옥 지붕들이 어우러진 풍경을 한눈에 담을 수 있는 전망 카페.',
            'source_url': 'https://love.seoul.go.kr/articles/10343',
            'google_maps': 'https://maps.google.com/?q=1인1잔+은평한옥마을',
            'nearby_stations': [],
            'station_id': None
        },
        {
            'name': '은평뉴타운도서관',
            'name_en': 'Eunpyeong New Town Library',
            'region_code': 'seoul',
            'category': 'attraction',
            'sub_category': 'library',
            'zone': '은평',
            'location': '서울특별시 은평구 진관2로 111-51',
            'lat': 37.5794,
            'lng': 126.9256,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['도서관', '은평', '북악', '여가'],
            'description': '은평뉴타운 중심에 위치한 현대적 도서관. 밝고 쾌적한 실내에 다양한 서적이 빼곡하고, 창가 자리와 아늑한 소파도 마련. 독서 모임, 북 콘서트, 전시회 등 문화 프로그램도 수시로 진행.',
            'source_url': 'https://love.seoul.go.kr/articles/10343',
            'google_maps': 'https://maps.google.com/?q=은평뉴타운도서관',
            'nearby_stations': [],
            'station_id': None
        },
    ]
    
    region_new = 0
    for att in seoul_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['seoul'] = region_new
    total_new += region_new
    
    # ============================================================
    # BUSAN - 영도 area attractions
    # ============================================================
    log("\n=== Processing BUSAN attractions ===")
    busan_attrs = [
        {
            'name': '깡깡이예술마을',
            'name_en': 'Kangkangi Art Village',
            'region_code': 'busan',
            'category': 'hidden_gem',
            'sub_category': 'culture',
            'zone': '영도',
            'location': '부산광역시 영도구 대평북로 36',
            'lat': 35.0978,
            'lng': 129.0367,
            'ticket': '투어 신청 (유료)',
            'stay_duration': '2-3시간',
            'need_reservation': 1,
            'priority': 3,
            'tags': ['영도', '산업관광', '예술마을', '조선소'],
            'description': "부산 영도의 깡깡이예술마을은 1970~80년대 원양어업 붐을 타고 수리조선업이 번성했던 마을. '깡깡'은 망치로 녹슨 배의 철판을 두드릴 때 나는 소리에서 유래. 8개의 수리조선소와 260여 개의 공장 및 부품 업체가 영위하는 산업관광지.",
            'source_url': 'http://kangkangee.com/',
            'google_maps': 'https://maps.google.com/?q=깡깡이예술마을',
            'blog_article': 'https://korean.visitkorea.or.kr/detail/rem_detail.do?cotid=3f8fe6f5-8674-4dd8-ba2e-a33ea0177052',
            'nearby_stations': ['busan_029', 'busan_027'],
            'station_id': 'busan_029'  # 中央站 is closest
        },
        {
            'name': '국립해양박물관',
            'name_en': 'National Maritime Museum',
            'region_code': 'busan',
            'category': 'attraction',
            'sub_category': 'museum',
            'zone': '영도',
            'location': '부산광역시 영도구 해양로301번길 45',
            'lat': 35.0956,
            'lng': 129.0389,
            'ticket': '무료',
            'stay_duration': '2-3시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['영도', '박물관', '해양', '가족'],
            'description': '부산 영도에 위치한 국립해양박물관. 바다의 역사, 해양생태, 과학 등을 전시하는 종합 해양문화시설. 물방울을 형상화한 외관建筑设计로 유명.',
            'source_url': 'https://www.mmk.or.kr/',
            'google_maps': 'https://maps.google.com/?q=국립해양박물관+부산',
            'blog_article': 'https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=79080',
            'nearby_stations': ['busan_029', 'busan_027'],
            'station_id': 'busan_029'
        },
        {
            'name': '절영해안산책로',
            'name_en': 'Jeolnyeong Coastal Trail',
            'region_code': 'busan',
            'category': 'hidden_gem',
            'sub_category': 'hiking',
            'zone': '영도',
            'location': '부산광역시 영도구 와치로 2-14',
            'lat': 35.0911,
            'lng': 129.0294,
            'ticket': '무료',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['영도', '해안', '산책', '드라마틱'],
            'description': '영도 서쪽 봉래산 아래 해안선을 따라 이어져 있는 3Km의 해안산책로. 원래 군사보호구역으로 접근이 어려웠으나 2001년 산책로가 개설됨. 기암괴석과 푸른 바다가 어우러진 절경.',
            'source_url': 'https://www.yeongdo.go.kr/tour/01462/02205.web',
            'google_maps': 'https://maps.google.com/?q=절영해안산책로',
            'nearby_stations': ['busan_029'],
            'station_id': 'busan_029'
        },
        {
            'name': '감지해변산책로',
            'name_en': 'Gamji Beach Trail',
            'region_code': 'busan',
            'category': 'hidden_gem',
            'sub_category': 'hiking',
            'zone': '영도',
            'location': '부산광역시 영도구 동삼동 639-13',
            'lat': 35.0906,
            'lng': 129.0428,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['영도', '해변', '산책', '자연'],
            'description': '태종대 해안선을 따라 조성된 약 3Km의 산책로. 인공으로 조성된 구절초 야생초 꽃밭과 함께하며, 완만한 경사로 어린이를 동반해도 무리없음.',
            'source_url': 'https://www.yeongdo.go.kr/tour/01462/02205.web',
            'google_maps': 'https://maps.google.com/?q=감지해변산책로',
            'nearby_stations': ['busan_029'],
            'station_id': 'busan_029'
        },
        {
            'name': '아레아식스(AREA6)',
            'name_en': 'AREA6',
            'region_code': 'busan',
            'category': 'hidden_gem',
            'sub_category': 'culture',
            'zone': '영도',
            'location': '부산광역시 영도구 태종로105번길 37-3',
            'lat': 35.0967,
            'lng': 129.0356,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['영도', '문화', '아트', '쇼핑'],
            'description': "삼진어묵의 비영리법인인 삼진이음에서 설립한 지역 문화 플랫폼. '로컬을 밝히는 아티장 골목'이 콘셉트. 부산주당, 송월타올, 취프로젝트 등 지역 대표 브랜드들이 입점.",
            'source_url': 'https://blog.naver.com/area6yeongdo',
            'google_maps': 'https://maps.google.com/?q=AREA6+영도',
            'nearby_stations': ['busan_029', 'busan_027'],
            'station_id': 'busan_029'
        },
    ]
    
    region_new = 0
    for att in busan_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['busan'] = region_new
    total_new += region_new
    
    # ============================================================
    # FUKUOKA - 旦過市場/小倉/柳橋 area attractions
    # ============================================================
    log("\n=== Processing FUKUOKA attractions ===")
    fukuoka_attrs = [
        {
            'name': '旦過市場',
            'name_en': 'Tangaichi Market',
            'region_code': 'fukuoka',
            'category': 'hidden_gem',
            'sub_category': 'market',
            'zone': '小倉',
            'location': '福岡県北九州市小倉北区魚町4-2-18',
            'lat': 33.8847,
            'lng': 130.8744,
            'ticket': '무료입장 (식사 별도)',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['北九州', '市場', 'グルメ', '昭和'],
            'description': '大正時代に魚の荷揚げ場から始まった100年の歴史を持つ市場。北九州の台所として親しまれ、新鮮な野菜や果物、鮮魚、手作りのお惣菜や地元伝統食「ぬか炊き」が所狭しと並んでいる。',
            'source_url': 'https://www.tangaichiba.jp/',
            'google_maps': 'https://maps.google.com/?q=旦過市場',
            'blog_article': 'https://www.crossroadfukuoka.jp/spot/13182',
            'nearby_stations': ['fukuoka_041'],
            'station_id': 'fukuoka_041'
        },
        {
            'name': '柳橋連合市場',
            'name_en': 'Yanagibashi Rengo Market',
            'region_code': 'fukuoka',
            'category': 'attraction',
            'sub_category': 'market',
            'zone': '博多',
            'location': '福岡県福岡市中央区春吉1-5-1',
            'lat': 33.5908,
            'lng': 130.4053,
            'ticket': '무료입장 (식사 별도)',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['博多', '市場', '魚市場', 'グルメ'],
            'description': '昭和初期に始まり、別名「博多の台所」と呼ばれる活気あふれる市場。新鮮な海産物や食材が並び、特に朝市や夜市が人気。玄界灘の鮮魚や辛子明太子、青果や和菓子などが揃う。',
            'source_url': 'https://yanagibashi-rengo.net/',
            'google_maps': 'https://maps.google.com/?q=柳橋連合市場',
            'nearby_stations': ['fukuoka_007'],
            'station_id': 'fukuoka_007'
        },
        {
            'name': '楽水園',
            'name_en': 'Rakusuien Garden',
            'region_code': 'fukuoka',
            'category': 'attraction',
            'sub_category': 'garden',
            'zone': '博多',
            'location': '福岡県福岡市中央区春吉',
            'lat': 33.5903,
            'lng': 130.4044,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['博多', '庭園', '日本庭園', '抹茶'],
            'description': '博多の中心部天神に程近い清流沿いにある池泉回遊式日本庭園。明治39年に豪商が建てた住吉別荘の跡地に整備され、楽水の名は親正の雅号に由来。都会の喧騒を忘れ，静寂と美しい庭園美を堪能できる穴場スポット.',
            'source_url': 'https://rakusuien.fukuoka-teien.com/',
            'google_maps': 'https://maps.google.com/?q=楽水園+福岡',
            'nearby_stations': ['fukuoka_007'],
            'station_id': 'fukuoka_007'
        },
        {
            'name': '石穴稲荷神社',
            'name_en': 'Ishiana Inari Shrine',
            'region_code': 'fukuoka',
            'category': 'shrine',
            'sub_category': 'shrine',
            'zone': '太宰府',
            'location': '福岡県太宰府市石坂2丁目13-1',
            'lat': 33.3144,
            'lng': 130.5478,
            'ticket': '무료',
            'stay_duration': '30분-1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['太宰府', '神社', 'PowerSpot', '歴史'],
            'description': '九州三大稲荷の一つに数えられる古社。静かな神社で地元や各地から商圈繁盛や家内安全を祈願する人々が訪れ、境内にはうつくしい自然が広がる。鳥居をくぐると不思議な雰囲楽しめる奥宮あり.',
            'source_url': 'http://ishiana.com/',
            'google_maps': 'https://maps.google.com/?q=石穴稲荷神社',
            'nearby_stations': ['fukuoka_007'],
            'station_id': 'fukuoka_007'
        },
        {
            'name': '小倉魚町銀天街',
            'name_en': 'Kokura Uomachi Shopping Street',
            'region_code': 'fukuoka',
            'category': 'hidden_gem',
            'sub_category': 'shopping',
            'zone': '小倉',
            'location': '福岡県北九州市小倉北区魚町',
            'lat': 33.8847,
            'lng': 130.8750,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['小倉', '商店街', ' Shopping', '在地'],
            'description': '北九州市小倉北区の銀天街。旦過市場とを結ぶ活気ある商店街で、B級グルメ店铺や，干物屋、台所道具店が轩を連ねる。',
            'source_url': 'https://www.tangaichiba.jp/',
            'google_maps': 'https://maps.google.com/?q=小倉魚町銀天街',
            'nearby_stations': ['fukuoka_041'],
            'station_id': 'fukuoka_041'
        },
    ]
    
    region_new = 0
    for att in fukuoka_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['fukuoka'] = region_new
    total_new += region_new
    
    # ============================================================
    # TOKYO - 赤羽/王子/荒川 area attractions
    # ============================================================
    log("\n=== Processing TOKYO attractions ===")
    tokyo_attrs = [
        {
            'name': '飛鳥山公園',
            'name_en': 'Asukayama Park',
            'region_code': 'tokyo',
            'category': 'attraction',
            'sub_category': 'park',
            'zone': '王子',
            'location': '東京都北区王子1-1-3',
            'lat': 35.7544,
            'lng': 139.7458,
            'ticket': '무료',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['北区', '桜', '公園', '歴史'],
            'description': '約300年前に幕府将軍徳川吉宗が桜を植えて以来，日本最早の民衆開放公園として知られる。約650本の桜が公园を染め、桜の名所として有名。飛鳥山博物館、紙博物館、渋沢史料館も隣接.',
            'source_url': 'https://www.city.kita.lg.jp/ches',
            'google_maps': 'https://maps.google.com/?q=飛鳥山公園',
            'blog_article': 'https://www.gotokyo.org/tc/spot/510/index.html',
            'nearby_stations': ['tokyo_031'],
            'station_id': 'tokyo_031'
        },
        {
            'name': '旧古河庭園',
            'name_en': 'Kyu Furukawa Garden',
            'region_code': 'tokyo',
            'category': 'attraction',
            'sub_category': 'garden',
            'zone': '王子',
            'location': '東京都北区西ケ原1-27-39',
            'lat': 35.7544,
            'lng': 139.7394,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['北区', '庭園', 'バラ', '洋館'],
            'description': '1917年に建築家ジョサイア・コンドルが設計した洋館を囲む美しい日本庭園と洋風庭園。石壁が美しい洋館と5月から初夏のバラ園の美しさで知られ、四季折々の景色を楽しめる.',
            'source_url': 'https://www.gotokyo.org/cn/destinations/northern-tokyo/akabane/index.html',
            'google_maps': 'https://maps.google.com/?q=旧古河庭園',
            'nearby_stations': ['tokyo_031'],
            'station_id': 'tokyo_031'
        },
        {
            'name': '赤羽一番街商店街',
            'name_en': 'Akabane Ichiban Shopping Street',
            'region_code': 'tokyo',
            'category': 'hidden_gem',
            'sub_category': 'shopping',
            'zone': '赤羽',
            'location': '東京都北区赤羽',
            'lat': 35.7622,
            'lng': 139.7208,
            'ticket': '무료',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['北区', '商店街', '居酒屋', 'グルメ'],
            'description': 'JR赤羽駅東口から北に広がる約400mの商店街。終戦直後の黒市から始まった歴史を持ち、今はせんべろの聖地として有名。赤提灯が灯る居酒屋や多种多样的グルメ店铺が轩を連ねる.',
            'source_url': 'https://www.mec-h.com/town/mh-akabane/118',
            'google_maps': 'https://maps.google.com/?q=赤羽一番街商店街',
            'nearby_stations': ['tokyo_031'],
            'station_id': 'tokyo_031'
        },
        {
            'name': '赤羽八幡神社',
            'name_en': 'Akabane Hachimangu',
            'region_code': 'tokyo',
            'category': 'shrine',
            'sub_category': 'shrine',
            'zone': '赤羽',
            'location': '東京都北区赤羽台4-1-6',
            'lat': 35.7603,
            'lng': 139.7247,
            'ticket': '무료',
            'stay_duration': '30분',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['北区', '神社', '神社', ' 승용'],
            'description': '赤羽を代表する神社。鳥居越しに新幹線能看到るという日本でしか見られない光景で有名。勝負の神様を祀り、athleteや不合格祈願の場所で知られる.',
            'source_url': 'https://www.gotokyo.org/cn/destinations/northern-tokyo/akabane/index.html',
            'google_maps': 'https://maps.google.com/?q=赤羽八幡神社',
            'nearby_stations': ['tokyo_031'],
            'station_id': 'tokyo_031'
        },
        {
            'name': '十条銀座商店街',
            'name_en': 'Jujo Ginza Shopping Street',
            'region_code': 'tokyo',
            'category': 'hidden_gem',
            'sub_category': 'shopping',
            'zone': '十条',
            'location': '東京都北区昭和園',
            'lat': 35.7578,
            'lng': 139.7111,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['北区', '商店街', '食べ歩き', '住民'],
            'description': '東京都北区最大規模の商店街で、メディアにもよく取り上げられる食べ歩きスポットとして有名な商店街。活気あふれる氛囲と多种多样的店铺が並ぶ.',
            'source_url': 'https://www.mec-h.com/town/mh-akabane/118',
            'google_maps': 'https://maps.google.com/?q=十条銀座商店街',
            'nearby_stations': ['tokyo_031'],
            'station_id': 'tokyo_031'
        },
    ]
    
    region_new = 0
    for att in tokyo_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['tokyo'] = region_new
    total_new += region_new
    
    # ============================================================
    # OKINAWA - うるま/普天間/北谷 area attractions
    # ============================================================
    log("\n=== Processing OKINAWA attractions ===")
    okinawa_attrs = [
        {
            'name': '伊計ビーチ',
            'name_en': 'Ikei Beach',
            'region_code': 'okinawa',
            'category': 'attraction',
            'sub_category': 'beach',
            'zone': 'うるま',
            'location': '沖縄県うるま市与那城伊計405',
            'lat': 26.3844,
            'lng': 127.9208,
            'ticket': '大人400円，孩子300円',
            'stay_duration': '2-3시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['うるま市', 'ビーチ', 'シュノーケル', '透明度'],
            'description': '海中道路を渡り車で行ける伊計島にあるビーチ。沖縄でも屈指の透明度を誇り、潮の干満に影響を受けることなくいつでも海水浴を楽しめる。マリンスポーツも<delete_file>.',
            'source_url': 'http://www.ikei-beach.com/',
            'google_maps': 'https://maps.google.com/?q=伊計ビーチ',
            'nearby_stations': ['okinawa_station_026'],
            'station_id': 'okinawa_station_026'
        },
        {
            'name': '普天満山神宮寺',
            'name_en': 'Futenma Sanugu Shrine',
            'region_code': 'okinawa',
            'category': 'shrine',
            'sub_category': 'shrine',
            'zone': '宜野湾',
            'location': '沖縄県宜野湾市普天間1-27-10',
            'lat': 26.2758,
            'lng': 127.6794,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['宜野湾市', '神社', '洞窟', 'パワースポット'],
            'description': '琉球八社のひとつに数えられる古宮。1459年に創建された500年以上の歴史を持つ。地域住民が御嶽として信仰していた洞窟があり、普天間洞穴と呼ばれ境内から溥れる.',
            'source_url': 'http://futenmagu.or.jp/',
            'google_maps': 'https://maps.google.com/?q=普天満山神宮寺',
            'nearby_stations': ['okinawa_station_022'],
            'station_id': 'okinawa_station_022'
        },
        {
            'name': '浜比嘉島',
            'name_en': 'Hamahiga Island',
            'region_code': 'okinawa',
            'category': 'hidden_gem',
            'sub_category': 'island',
            'zone': 'うるま',
            'location': '沖縄県うるま市勝連',
            'lat': 26.3414,
            'lng': 127.8997,
            'ticket': '무료',
            'stay_duration': '2-3시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['うるま市', '離島', '神话', 'ビーチ'],
            'description': '琉球神話の舞台とされる神の島。赤瓦屋根の家並みが残る集落にはどこか懐かしい沖縄の風景が広がる。美しいビーチでは海水浴やマリンアクティビティも楽しめ、新鲜なモズク料理も味は Ast.',
            'source_url': 'https://www.okinawastory.jp/news/tourism/4219',
            'google_maps': 'https://maps.google.com/?q=浜比嘉島',
            'nearby_stations': ['okinawa_station_026'],
            'station_id': 'okinawa_station_026'
        },
        {
            'name': '果報バンタ',
            'name_en': 'Kafuku Banta',
            'region_code': 'okinawa',
            'category': 'attraction',
            'sub_category': 'scenic',
            'zone': 'うるま',
            'location': '沖縄県うるま市与那城宮2768',
            'lat': 26.3531,
            'lng': 127.9139,
            'ticket': '、施設利用料あり',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['うるま市', '絶景', '岬', 'フォトジェニック'],
            'description': '约120メートルの崖の上から楽しめる沖縄屈指の絶景スポット。別名「幸せ岬」と呼ばれ Behancerと訳される。 берег岩とエメラルドグリーンの海のパノラマビュー.',
            'source_url': 'https://www.okinawastory.jp/news/tourism/4219',
            'google_maps': 'https://maps.google.com/?q=果報バンタ',
            'nearby_stations': ['okinawa_station_026'],
            'station_id': 'okinawa_station_026'
        },
        {
            'name': '平安座島',
            'name_en': 'Heianza Island',
            'region_code': 'okinawa',
            'category': 'hidden_gem',
            'sub_category': 'island',
            'zone': 'うるま',
            'location': '沖縄県うるま市与那城',
            'lat': 26.3619,
            'lng': 127.9031,
            'ticket': '무료',
            'stay_duration': '1-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['うるま市', '離島', 'アート', '住民'],
            'description': '防波堤に约300mのアーチが描かれ、市の小中学生が描いた护岸アートが海と空に映えるレトロ岛。屁股肉せ釜밥等等の店铺も並ぶ.',
            'source_url': 'https://www.okinawastory.jp/news/tourism/4219',
            'google_maps': 'https://maps.google.com/?q=平安座島',
            'nearby_stations': ['okinawa_station_026'],
            'station_id': 'okinawa_station_026'
        },
    ]
    
    region_new = 0
    for att in okinawa_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['okinawa'] = region_new
    total_new += region_new
    
    # ============================================================
    # OSAKA - 住之江/浪速 area attractions
    # ============================================================
    log("\n=== Processing OSAKA attractions ===")
    osaka_attrs = [
        {
            'name': '天然露天温泉SPA住之江',
            'name_en': 'Spa Suminoe',
            'region_code': 'osaka',
            'category': 'attraction',
            'sub_category': 'onsen',
            'zone': '住之江',
            'location': '大阪府大阪市住之江区泉1-1-82',
            'lat': 34.6011,
            'lng': 135.4903,
            'ticket': '800-900円',
            'stay_duration': '1.5-2시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['住之江区', '温泉', '汕火照', 'リラックス'],
            'description': '大阪唯一の天然露天温泉。住之江区に位置し、岩石を配した野外の浴槽で四季の景色を楽しみながら入るえる。団体でも利用可能.',
            'source_url': 'http://spasuminoe.jp/',
            'google_maps': 'https://maps.google.com/?q=天然露天温泉SPA住之江',
            'nearby_stations': ['osaka_station_058'],
            'station_id': 'osaka_station_058'
        },
        {
            'name': '住之江公園',
            'name_en': 'Suminoe Park',
            'region_code': 'osaka',
            'category': 'attraction',
            'sub_category': 'park',
            'zone': '住之江',
            'location': '大阪府大阪市住之江区',
            'lat': 34.6033,
            'lng': 135.4919,
            'ticket': '무료',
            'stay_duration': '1시간',
            'need_reservation': 0,
            'priority': 3,
            'tags': ['住之江区', '公園', '休闲', '家族'],
            'description': '大阪市の住之江区にある大きな公园。木や緑が茂り、游び場や步道も整備されている。市民の想いの場として愛される.',
            'source_url': 'https://www.city.osaka.lg.jp/',
            'google_maps': 'https://maps.google.com/?q=住之江公園',
            'nearby_stations': ['osaka_station_058'],
            'station_id': 'osaka_station_058'
        },
        {
            'name': 'SPA WORLD 溫泉世界',
            'name_en': 'SPAWORLD HOTEL & RESORT',
            'region_code': 'osaka',
            'category': 'attraction',
            'sub_category': 'onsen',
            'zone': '浪速',
            'location': '大阪府大阪市浪速区恵美須東3-4-24',
            'lat': 34.6486,
            'lng': 135.5072,
            'ticket': '施設による',
            'stay_duration': '3-4시간',
            'need_reservation': 0,
            'priority': 2,
            'tags': ['浪速区', '温泉', 'テーマパーク', '家族'],
            'description': '世界のさまざまなお風呂文化を体験できる温泉テーマパーク。ヨーロッパ・アジアなど各国の風呂を楽しめる。2025年には浴室がリニューアル、日本最大のサウナシアータなども开设.',
            'source_url': 'https://spa-world.jp/',
            'google_maps': 'https://maps.google.com/?q=SPA+WORLD+大阪',
            'nearby_stations': ['osaka_station_058'],
            'station_id': 'osaka_station_058'
        },
    ]
    
    region_new = 0
    for att in osaka_attrs:
        try:
            if insert_attraction(conn, cur, att):
                region_new += 1
        except Exception as e:
            log_err(f"  Failed to insert {att['name']}: {e}")
    region_counts['osaka'] = region_new
    total_new += region_new
    
    # ============================================================
    # Summary
    # ============================================================
    log(f"\n{'='*50}")
    log(f"SUMMARY: 本週新增 {total_new} 筆景點")
    for region, count in region_counts.items():
        log(f"  {region}: {count} 筆")
    log(f"{'='*50}")
    
    conn.close()
    return total_new

if __name__ == '__main__':
    main()
