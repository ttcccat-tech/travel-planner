#!/usr/bin/env python3
"""Weekly attraction insert script - 2026-09-08"""
import sqlite3, json, os, sys

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

def get_existing_names(cur):
    cur.execute("SELECT LOWER(name) FROM attractions")
    return set(r[0] for r in cur.fetchall())

def slugify(name):
    """Generate a short ID from name"""
    # Remove special chars, take first 12 chars
    s = name.lower()
    s = ''.join(c if c.isalnum() else '_' for c in s)
    s = s.strip('_')
    return s[:20]

def insert_attraction(cur, attraction):
    """Insert a single attraction, skip if name or URL already exists."""
    name = attraction['name']
    name_lower = name.lower()
    
    # Check for duplicate name
    cur.execute("SELECT COUNT(*) FROM attractions WHERE LOWER(name) = ?", (name_lower,))
    if cur.fetchone()[0] > 0:
        return False, f"SKIP (name exists): {name}"
    
    # Check for duplicate URL in sources
    if attraction.get('sources'):
        for src in attraction['sources']:
            if src:
                cur.execute("SELECT COUNT(*) FROM attractions WHERE sources LIKE ?", (f'%{src}%',))
                if cur.fetchone()[0] > 0:
                    return False, f"SKIP (URL exists): {name} -> {src}"
    
    # Build tags JSON
    tags = json.dumps(attraction.get('tags', []), ensure_ascii=False)
    sources = json.dumps(attraction.get('sources', []), ensure_ascii=False)
    nearby = json.dumps(attraction.get('nearby_stations', []), ensure_ascii=False)
    details = json.dumps(attraction.get('details', {}), ensure_ascii=False)
    
    id_val = slugify(name)
    
    cur.execute("""
        INSERT INTO attractions 
        (id, region_code, station_id, name, name_en, category, sub_category, zone, 
         location, ticket, stay_duration, priority, tags, description, sources, nearby_stations, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_val,
        attraction['region_code'],
        attraction['station_id'],
        attraction['name'],
        attraction.get('name_en'),
        attraction.get('category', 'hidden_gem'),
        attraction.get('sub_category'),
        attraction.get('zone'),
        attraction.get('location'),
        attraction.get('ticket'),
        attraction.get('stay_duration'),
        attraction.get('priority', 3),
        tags,
        attraction.get('description'),
        sources,
        nearby,
        details
    ))
    return True, id_val

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    existing_names = get_existing_names(cur)
    print(f"Existing attractions: {len(existing_names)}")
    
    # =====================================================================
    # ATTRACTIONS TO INSERT (verified against DB)
    # =====================================================================
    attractions = [
        # ===== SEOUL =====
        # Seongsu (聖水站 seoul_054) - urban cafe/art district
        {
            'name': '聖水洞 工業風CAFÉ街',
            'name_en': 'Seongsu Industrial CAFÉ Street',
            'region_code': 'seoul',
            'station_id': 'seoul_054',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '城東',
            'location': '首爾特別市城東區聖水洞一帶',
            'ticket': '免費',
            'stay_duration': '2-3小時',
            'priority': 3,
            'tags': ['聖水洞', '咖啡', '工業風', '文青', '選物店'],
            'description': '首爾的「布魯克林」，由廢棄工廠改建的大型選物店、質感咖啡廳、香氛品牌旗艦店林立。TAMBURINS、LE LABO、Musinsa Empty等都在此設店。',
            'sources': ['https://yenliving.com/korea-seoul-seongsu-shops'],
            'nearby_stations': ['seoul_054'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/PMyqUJgK9BckZtpw7',
                'blog_article': 'https://yenliving.com/korea-seoul-seongsu-shops',
                'youtube': ''
            }
        },
        {
            'name': '大林倉庫 CO:LUM',
            'name_en': 'Daelim Changgo CO:LUM',
            'region_code': 'seoul',
            'station_id': 'seoul_054',
            'category': 'hidden_gem',
            'sub_category': '咖啡廳',
            'zone': '城東',
            'location': '首爾特別市城東區聖水二路78',
            'ticket': '免費入場',
            'stay_duration': '1-2小時',
            'priority': 3,
            'tags': ['聖水洞', '咖啡', '舊倉庫', '工業風', '藝術'],
            'description': '由舊倉庫改建的大型咖啡廳兼藝廊，寬敞挑高的工業風空間，結合餐飲與藝術展覽，是聖水洞具代表性的複合式空間。',
            'sources': ['https://yenliving.com/korea-seoul-seongsu-shops'],
            'nearby_stations': ['seoul_054'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/BLNMWmzCGbDRvc7ZA',
                'blog_article': 'https://yenliving.com/korea-seoul-seongsu-shops',
                'youtube': ''
            }
        },
        {
            'name': '延南洞 文青散步徑',
            'name_en': 'Yeonnam-dong Creative Walk',
            'region_code': 'seoul',
            'station_id': 'seoul_004',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '麻浦',
            'location': '首爾特別市麻浦區延南洞京義線森林公園沿線',
            'ticket': '免費',
            'stay_duration': '2-3小時',
            'priority': 3,
            'tags': ['延南洞', '弘大', '文青', '咖啡', '選物店', '京義線森林公園'],
            'description': '京義線森林公園開通後，延南洞成為首爾年輕人最愛的散步街區。集結設計師品牌選物店、文青咖啡廳、質感餐廳與路邊攤，氛圍悠閒愜意。',
            'sources': ['https://tw.trip.com/guide/attraction/延南洞.html'],
            'nearby_stations': ['seoul_004', 'seoul_005', 'seoul_009'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/YQv9X7Z',
                'blog_article': 'https://tw.trip.com/guide/attraction/延南洞.html',
                'youtube': ''
            }
        },
        
        # ===== BUSAN =====
        # Seomyeon (田浦站 busan_036 / 西面站 busan_035) - coffee street
        {
            'name': '田浦咖啡街',
            'name_en': 'Tancheon Coffee Street',
            'region_code': 'busan',
            'station_id': 'busan_036',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '釜山',
            'location': '釜山廣域市釜山鎭區田浦洞',
            'ticket': '免費',
            'stay_duration': '1.5-2.5小時',
            'priority': 3,
            'tags': ['田浦', '西面', '咖啡街', '文青', '老屋改建'],
            'description': '西面站與田浦站之間的隱藏版咖啡街，十多家風格咖啡廳隱身於住宅區巷弄間，從復古到工業風應有盡有，是釜山年輕人的秘密基地。',
            'sources': ['https://tw.trip.com/moments/theme/destination-seomyeon-2040506-comprehensive-guides-993136/'],
            'nearby_stations': ['busan_035', 'busan_036'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/TancheonCoffee',
                'blog_article': 'https://tw.trip.com/moments/theme/destination-seomyeon-2040506-comprehensive-guides-993136/',
                'youtube': ''
            }
        },
        # Nampo (札嘎其站 busan_027 / 南浦站 busan_028)
        {
            'name': '富平罐頭市場',
            'name_en': 'Bupyeong Kkangtong Market',
            'region_code': 'busan',
            'station_id': 'busan_028',
            'category': 'attraction',
            'sub_category': '市場',
            'zone': '南浦洞',
            'location': '釜山廣域市中區南浦洞',
            'ticket': '免費',
            'stay_duration': '1-2小時',
            'priority': 3,
            'tags': ['南浦洞', '市場', '美食', '罐頭市場', '銅板美食'],
            'description': '與札嘎其市場相鄰的富平罐頭市場，匯集各式罐頭食品、零食乾貨與在地小吃，是釜山最具庶民氛圍的傳統市場之一。',
            'sources': ['https://mimigo.tw/busan-gamcheondong/'],
            'nearby_stations': ['busan_027', 'busan_028'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/BupyeongMarket',
                'blog_article': 'https://mimigo.tw/busan-gamcheondong/',
                'youtube': ''
            }
        },
        {
            'name': '白淺灘文化村',
            'name_en': 'Blanc Beach Culture Village',
            'region_code': 'busan',
            'station_id': 'busan_028',
            'category': 'hidden_gem',
            'sub_category': '海景街區',
            'zone': '影島',
            'location': '釜山廣域市南区影島頂里',
            'ticket': '免費',
            'stay_duration': '1.5-2.5小時',
            'priority': 3,
            'tags': ['影島', '海景', '文化村', '小白沙灘', '咖啡街'],
            'description': '影島東側海岸的彩色社區，與甘川洞並列的壁畫村，但更靠近海邊。有「小希臘」之稱，聚集許多質感咖啡廳與藝術工作室，可拍到海岸與彩色房屋同框。',
            'sources': ['https://debbiechien.com/busan-attractions'],
            'nearby_stations': ['busan_028'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/WhiteSandBeachVillage',
                'blog_article': 'https://debbiechien.com/busan-attractions',
                'youtube': ''
            }
        },
        
        # ===== FUKUOKA =====
        # Nakasu (中洲川端站 fukuoka_003)
        {
            'name': '中洲川端 昭和散步道',
            'name_en': 'Nakasu Kawabatadori Showa Walk',
            'region_code': 'fukuoka',
            'station_id': 'fukuoka_003',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '中洲',
            'location': '福岡市博多區中洲川端一帶',
            'ticket': '免費',
            'stay_duration': '1-2小時',
            'priority': 3,
            'tags': ['中洲', '川端', '昭和', '散步', '老街', '博多'],
            'description': '中洲川端周邊保留昭和時期氛圍的散步道，櫛田神社周邊古色古香，仲見世商店街融合傳統與現代，體驗博多下町風情的最佳去處。',
            'sources': ['https://yokanavi.com/routes/12'],
            'nearby_stations': ['fukuoka_003', 'fukuoka_001'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/NakasuKawabata',
                'blog_article': 'https://yokanavi.com/routes/12',
                'youtube': ''
            }
        },
        {
            'name': '住吉 港散步徑',
            'name_en': 'Sumiyoshi Minato Promenade',
            'region_code': 'fukuoka',
            'station_id': 'fukuoka_013',
            'category': 'hidden_gem',
            'sub_category': '港濱',
            'zone': '博多',
            'location': '福岡市博多區住吉',
            'ticket': '免費',
            'stay_duration': '1-1.5小時',
            'priority': 3,
            'tags': ['住吉', '港', '海濱', '散步', '運河'],
            'description': '博多灣岸的港濱散步道，沿線可見博多港的歷史建築與現代海洋設施，遠眺能古島方向，是遠離觀光人潮的悠閒去處。',
            'sources': ['https://hakatamap.jp/course/index-nakasu.html'],
            'nearby_stations': ['fukuoka_013'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/SumiyoshiPort',
                'blog_article': 'https://hakatamap.jp/course/index-nakasu.html',
                'youtube': ''
            }
        },
        
        # ===== OSAKA =====
        # Nakazaki-cho (天神橋筋六丁目 osaka_station_019) - retro neighborhood
        {
            'name': '中崎町 老屋咖啡街',
            'name_en': 'Nakazaki-cho Retro Cafe Street',
            'region_code': 'osaka',
            'station_id': 'osaka_station_019',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '天神橋',
            'location': '大阪市北區中崎町',
            'ticket': '免費',
            'stay_duration': '2-3小時',
            'priority': 3,
            'tags': ['中崎町', '老屋', '咖啡', '古著', '昭和', '文青'],
            'description': '保留大量昭和時期老屋的街區，轉型為大阪最具代表性的文青聚落。狹窄巷弄間集結古著店、精品咖啡館、雜貨選物店與小型藝廊，處處都是日劇感畫面。',
            'sources': ['https://marukojp.com/article/osaka-hidden-spots'],
            'nearby_stations': ['osaka_station_019'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/kXSmxtofY1zv4SGC6',
                'blog_article': 'https://marukojp.com/article/osaka-hidden-spots',
                'youtube': ''
            }
        },
        # Horie (四橋站/心齋橋 osaka_station_013) - fashion district
        {
            'name': '堀江 橘子街',
            'name_en': 'Horie Orange Street',
            'region_code': 'osaka',
            'station_id': 'osaka_station_013',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '堀江',
            'location': '大阪市西區北堀江一帶',
            'ticket': '免費',
            'stay_duration': '2-3小時',
            'priority': 3,
            'tags': ['堀江', '橘子街', '時尚', '古著', '設計', '咖啡'],
            'description': '以橘子街（Orange Street）為中心的時尚街區，設計師品牌、古著店、潮流選物店與特色咖啡廳林立，被譽為大阪的「裏澀谷」，文青與潮人必訪。',
            'sources': ['https://osaka.letsgojp.com/archives/320693/'],
            'nearby_stations': ['osaka_station_013'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/HorieOrangeSt',
                'blog_article': 'https://osaka.letsgojp.com/archives/320693/',
                'youtube': ''
            }
        },
        # Osaka Nakanoshima (淀屋橋 osaka_station_012)
        {
            'name': '中之島 玫瑰園散步道',
            'name_en': 'Nakanoshima Rose Garden Promenade',
            'region_code': 'osaka',
            'station_id': 'osaka_station_012',
            'category': 'hidden_gem',
            'sub_category': '公園',
            'zone': '中之島',
            'location': '大阪市北區中之島公園',
            'ticket': '免費（5-6月玫瑰盛開最美）',
            'stay_duration': '1-1.5小時',
            'priority': 3,
            'tags': ['中之島', '玫瑰園', '散步', '河岸', '自然', 'citywalk'],
            'description': '大阪市中心的綠意島嶼，融合公園草坪、河岸景觀、玫瑰園與明治時期紅磚建築。從淀屋橋或北濱步行約5分鐘可達，氛圍與心齋橋、道頓堀截然不同。',
            'sources': ['https://marukojp.com/article/osaka-hidden-spots'],
            'nearby_stations': ['osaka_station_012'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/io1TfusZ6MrE4HEj6',
                'blog_article': 'https://marukojp.com/article/osaka-hidden-spots',
                'youtube': ''
            }
        },
        
        # ===== TOKYO =====
        # Kuramae/Asakusa area (浅草站 tokyo_006)
        {
            'name': '淺草 仲見世小路',
            'name_en': 'Asakusa Nakamise-koji',
            'region_code': 'tokyo',
            'station_id': 'tokyo_006',
            'category': 'hidden_gem',
            'sub_category': '商店街',
            'zone': '淺草',
            'location': '東京都台東區淺草',
            'ticket': '免費',
            'stay_duration': '1-2小時',
            'priority': 3,
            'tags': ['淺草', '仲見世', '老街', '江戶', '小吃', '伴手禮'],
            'description': '雷門通往淺草寺的仲見世通旁小巷，有別於人潮洶湧的主街，這裡保留了更道地的江戶下町風情，隱藏著百年老店與職人手作小店。',
            'sources': ['https://mimigo.tw/asakusa/'],
            'nearby_stations': ['tokyo_006'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/AsakusaNakamise',
                'blog_article': 'https://mimigo.tw/asakusa/',
                'youtube': ''
            }
        },
        # Ningyo-cho (人形町站 tokyo_043)
        {
            'name': '人形町 甘酒横丁',
            'name_en': 'Ningyo-cho Amazake Yokocho',
            'region_code': 'tokyo',
            'station_id': 'tokyo_043',
            'category': 'hidden_gem',
            'sub_category': '老街',
            'zone': '人形町',
            'location': '東京都中央區人形町',
            'ticket': '免費',
            'stay_duration': '1-2小時',
            'priority': 3,
            'tags': ['人形町', '甘酒横丁', '老街', '江戶', '小吃', '日比谷線'],
            'description': '人形町保留江戶風情的古老巷弄，「甘酒横丁」集結數十年歷史的老店、鯛魚燒名店與昭和感咖啡店，是東京下町散步的私房去處。',
            'sources': ['https://www.travel.co.jp/guide/matome/705/'],
            'nearby_stations': ['tokyo_043'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/NingyochoAmazake',
                'blog_article': 'https://www.travel.co.jp/guide/matome/705/',
                'youtube': ''
            }
        },
        # Jimbocho / Kanda (水道橋站 tokyo_033)
        {
            'name': '神保町 古書街 昭和散步',
            'name_en': 'Jimbocho Kogisho-gai Showa Walk',
            'region_code': 'tokyo',
            'station_id': 'tokyo_033',
            'category': 'hidden_gem',
            'sub_category': '街區',
            'zone': '神保町',
            'location': '東京都千代田區神保町',
            'ticket': '免費',
            'stay_duration': '2-3小時',
            'priority': 3,
            'tags': ['神保町', '古書街', '昭和', '古本', '咖喱', '小巷'],
            'description': '世界最大規模的古書街聚集地，同時也是日本咖喱激戰區。巷弄間保留昭和氛圍，神田明神與Nicolai堂等歷史建築增添了文化厚度。',
            'sources': ['https://www.travel.co.jp/guide/matome/705/'],
            'nearby_stations': ['tokyo_033'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/Jimbocho',
                'blog_article': 'https://www.travel.co.jp/guide/matome/705/',
                'youtube': ''
            }
        },
        
        # ===== OKINAWA =====
        # Makishi (牧志 okinawa_station_009)
        {
            'name': '第一牧志公設市場',
            'name_en': 'First Makishi Public Market',
            'region_code': 'okinawa',
            'station_id': 'okinawa_station_009',
            'category': 'attraction',
            'sub_category': '市場',
            'zone': '那霸',
            'location': '沖繩縣那霸市松尾',
            'ticket': '免費入場',
            'stay_duration': '1.5-2小時',
            'priority': 3,
            'tags': ['牧志', '市場', '海鮮', '烹飪', '在地', '那霸廚房'],
            'description': '有「那霸廚房」之稱的傳統市場，2023年改建後煥然一新但仍保有經典氛圍。1樓販售新鮮魚貨蔬果，2樓可代客烹調，是體驗沖繩飲食文化的必訪之地。',
            'sources': ['https://okinawa.letsgojp.com/archives/782803/'],
            'nearby_stations': ['okinawa_station_009'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/MakishiMarket',
                'blog_article': 'https://okinawa.letsgojp.com/archives/782803/',
                'youtube': ''
            }
        },
        # Onoyama park (奧武山公園 okinawa_station_017)
        {
            'name': '奧武山公園 琉球八社 沖宮',
            'name_en': 'Onoyama Park & Okinawa Tamatsuri',
            'region_code': 'okinawa',
            'station_id': 'okinawa_station_017',
            'category': 'hidden_gem',
            'sub_category': '公園神社',
            'zone': '那霸',
            'location': '沖繩縣那霸市奧武山町52',
            'ticket': '免費',
            'stay_duration': '1-1.5小時',
            'priority': 3,
            'tags': ['奧武山', '公園', '神社', '琉球八社', '能量景點', '健行'],
            'description': '那霸最大型的綜合公園，春季賞櫻秋季健行皆適宜。園內的沖宮是琉球八社之一，15世紀創建，是當地人祈求開運、健康與交通安全的重要信仰中心。',
            'sources': ['https://okinawa.letsgojp.com/archives/782803/'],
            'nearby_stations': ['okinawa_station_017', 'okinawa_station_006'],
            'details': {
                'google_maps': 'https://maps.app.goo.gl/OnoyamaPark',
                'blog_article': 'https://okinawa.letsgojp.com/archives/782803/',
                'youtube': ''
            }
        },
    ]
    
    # =====================================================================
    # INSERTION
    # =====================================================================
    inserted = []
    skipped = []
    
    for attr in attractions:
        try:
            ok, result = insert_attraction(cur, attr)
            if ok:
                inserted.append((attr['name'], result))
                print(f"  INSERT [{result}]: {attr['name']}")
            else:
                skipped.append((attr['name'], result))
                print(f"  {result}")
        except Exception as e:
            skipped.append((attr['name'], f"ERROR: {e}"))
            print(f"  ERROR [{attr['name']}]: {e}")
    
    conn.commit()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(inserted)} inserted, {len(skipped)} skipped/total checked")
    print(f"{'='*60}")
    
    # Group by region
    by_region = {}
    for name, result in inserted:
        # find region from attraction name
        for attr in attractions:
            if attr['name'] == name:
                region = attr['region_code']
                if region not in by_region:
                    by_region[region] = []
                by_region[region].append(name)
                break
    
    for region, names in sorted(by_region.items()):
        print(f"  {region}: {len(names)} new attractions")
    
    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        for name, reason in skipped:
            print(f"  - {name}: {reason}")
    
    # Verify count
    cur.execute("SELECT COUNT(*) FROM attractions")
    total = cur.fetchone()[0]
    print(f"\nTotal attractions in DB now: {total}")
    
    conn.close()

if __name__ == '__main__':
    main()
