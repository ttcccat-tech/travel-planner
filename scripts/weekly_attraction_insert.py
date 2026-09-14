#!/usr/bin/env python3
"""Weekly attraction insert script - 2026-09-14"""
import sqlite3
import json
import os
import sys

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def existing_names(conn):
    """Return set of lowercase existing attraction names."""
    cur = conn.execute('SELECT LOWER(name) FROM attractions')
    return {r[0] for r in cur.fetchall()}

def existing_sources(conn):
    """Return set of lowercase existing source URLs."""
    cur = conn.execute('SELECT sources FROM attractions WHERE sources IS NOT NULL')
    urls = set()
    for (src_json,) in cur.fetchall():
        try:
            urls.update({u.lower() for u in json.loads(src_json)})
        except Exception:
            pass
    return urls

def slugify(name):
    """Generate a short ID from name."""
    import re
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', name)
    s = s[:20].lower()
    return s or 'attr'

def make_id(base_id, name, existing_ids):
    """Generate unique ID."""
    candidate = slugify(name)
    if candidate not in existing_ids:
        return candidate
    for i in range(1, 100):
        cand = f'{candidate}_{i}'
        if cand not in existing_ids:
            return cand
    return f'{candidate}_{len(existing_ids)}'

def get_existing_ids(conn):
    cur = conn.execute('SELECT id FROM attractions')
    return {r[0] for r in cur.fetchall()}

def insert_attraction(conn, attraction):
    cur = conn.execute(
        '''INSERT INTO attractions
        (id, region_code, station_id, name, name_en, category, sub_category, zone,
         location, lat, lng, ticket, stay_duration, need_reservation, cash_only,
         priority, tags, description, sources, nearby_stations, details)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (
            attraction['id'],
            attraction['region_code'],
            attraction.get('station_id'),
            attraction['name'],
            attraction.get('name_en'),
            attraction.get('category', 'attraction'),
            attraction.get('sub_category'),
            attraction.get('zone'),
            attraction.get('location'),
            attraction.get('lat'),
            attraction.get('lng'),
            attraction.get('ticket'),
            attraction.get('stay_duration'),
            0,
            0,
            attraction.get('priority', 3),
            json.dumps(attraction.get('tags', []), ensure_ascii=False) if attraction.get('tags') else None,
            attraction.get('description'),
            json.dumps(attraction.get('sources', []), ensure_ascii=False) if attraction.get('sources') else None,
            json.dumps(attraction.get('nearby_stations', []), ensure_ascii=False) if attraction.get('nearby_stations') else None,
            json.dumps(attraction.get('details', {}), ensure_ascii=False) if attraction.get('details') else None,
        )
    )
    return cur.lastrowid

# ============================================================================
# NEW ATTRACTIONS
# Format:
#   name, region_code, station_id, zone, category, details_google_maps,
#   details_blog, details_youtube, tags, description, location, stay_duration,
#   ticket, priority
# ============================================================================

NEW_ATTRACTIONS = [
    # ---- SEOUL ----
    {
        'id': 'lcdc-seoul',
        'region_code': 'seoul',
        'station_id': 'seoul_045',
        'name': 'LCDC Seoul',
        'name_en': 'LCDC Seoul',
        'category': 'attraction',
        'zone': '聖水洞',
        'location': '서울 성동구 연무장17길 10',
        'lat': 37.5665,
        'lng': 127.0465,
        'ticket': '免費（各店鋪消費）',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['文創', '設計', '咖啡', '聖水洞'],
        'description': '聖水洞複合文化空間，由時裝品牌LE CONTE DES CONTES創立的LCDC Seoul，樓高4層含咖啡店、服裝店、飾品店、酒吧及藝術家工作室。',
        'sources': ['https://m.lcdc-seoul.com/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=연무장17길+10+LCDC+Seoul',
            'blog_article': 'https://meet.eslite.com/tw/sc/article/202605110003',
        }
    },
    {
        'id': 'seongsu-federation',
        'region_code': 'seoul',
        'station_id': 'seoul_045',
        'name': '聖水聯邦',
        'name_en': 'Seongsu Yeonbang',
        'category': 'attraction',
        'zone': '聖水洞',
        'location': '서울특별시 성동구 성수동2가 322-4',
        'lat': 37.5655,
        'lng': 127.0455,
        'ticket': '免費（各店鋪消費）',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['文創', '書店', '聖水洞', '老屋改建'],
        'description': '聖水聯邦以舊工廠建築改建而成的綜合文化空間，匯聚書店、精品店、生活家品店「Thingool」及多間人氣咖啡。',
        'sources': ['https://sites.google.com/view/ssyb'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=성수동2가+322-4',
            'blog_article': 'https://tw.trip.com/blog/%E8%81%96%E6%B0%B4%E6%B4%9E',
        }
    },
    {
        'id': 'onion-seongsu',
        'region_code': 'seoul',
        'station_id': 'seoul_045',
        'name': 'Onion 聖水店',
        'name_en': 'Cafe Onion Seongsu',
        'category': 'attraction',
        'zone': '聖水洞',
        'location': '서울 성동구 아차산로9길 8',
        'lat': 37.5647,
        'lng': 127.0448,
        'ticket': '免費',
        'stay_duration': '1小時',
        'priority': 2,
        'tags': ['咖啡', '聖水洞', '老屋改建', '甜點'],
        'description': 'Onion聖水店是首爾知名咖啡品牌，聖水店在具有50年歷史的工廠空間展現原貌，廢墟工業風格，搭配多款精緻甜點。',
        'sources': ['https://www.instagram.com/cafe.onion/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=아차산로9길+8+onion',
            'blog_article': 'https://damei17.com/songsu',
        }
    },
    {
        'id': 'ssamziegil',
        'region_code': 'seoul',
        'station_id': 'seoul_025',
        'name': '人人廣場',
        'name_en': 'Ssamziegil',
        'category': 'attraction',
        'zone': '仁寺洞',
        'location': '서울특별시 종로구 인사동길 44',
        'lat': 37.5702,
        'lng': 126.9852,
        'ticket': '免費（各店鋪消費）',
        'stay_duration': '2小時',
        'priority': 2,
        'tags': ['文創', '仁寺洞', '傳統工藝', '逛街'],
        'description': '仁寺洞最大地標，旋轉坡道設計的立體文創商場，聚集數十家手工藝品、銀飾和文青小店，牆上處處可愛塗鴉，頂樓可俯瞰仁寺洞屋頂景致。',
        'sources': ['https://www.ssamzigil.com/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=인사동길+44+Ssamziegil',
            'blog_article': 'https://www.kkday.com/zh-hk/blog/65128/seoul-insa-dong',
        }
    },
    {
        'id': 'color-pool-museum',
        'region_code': 'seoul',
        'station_id': 'seoul_025',
        'name': '仁寺洞繽紛色彩展',
        'name_en': 'Color Pool Museum',
        'category': 'attraction',
        'zone': '仁寺洞',
        'location': '서울특별시 종로구 인사동길 49 (안녕인사동 6층)',
        'lat': 37.5705,
        'lng': 126.9855,
        'ticket': '需購票',
        'stay_duration': '1小時',
        'priority': 3,
        'tags': ['博物館', '仁寺洞', '打卡', '色彩'],
        'description': '仁寺洞繽紛色彩展 Color Pool Museum，分為9個主題展區，每區有各自色彩和香氣，設有粉紅色波波池，是閨蜜打卡好去處。',
        'sources': ['https://www.colorpool.co.kr/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=인사동길+49+Color+Pool+Museum',
            'blog_article': 'https://www.kkday.com/zh-hk/blog/65128/seoul-insa-dong',
        }
    },
    # ---- BUSAN ----
    {
        'id': 'yeongdodaegyo-bridge',
        'region_code': 'busan',
        'station_id': 'busan_029',
        'name': '影島大橋',
        'name_en': 'Yeongdodaegyo Bridge',
        'category': 'attraction',
        'zone': '影島區',
        'location': '부산광역시 영도구大桥洞',
        'lat': 35.0956,
        'lng': 129.0356,
        'ticket': '免費',
        'stay_duration': '45分鐘',
        'priority': 2,
        'tags': ['釜山', '影島', '開合橋', '每日開橋'],
        'description': '韓國唯一開合式大橋，每日下午2點開橋秀，橋面75度升起，橋上有9隻彩繪海鷗展翅。連接南浦洞與影島，富有歷史意義。',
        'sources': ['https://today.line.me/tw/v3/article/GgrNZYR'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=영도대교',
            'blog_article': 'https://today.line.me/tw/v3/article/GgrNZYR',
        }
    },
    {
        'id': 'busan-arte-museum',
        'region_code': 'busan',
        'station_id': 'busan_029',
        'name': '釜山ARTE MUSEUM',
        'name_en': 'ARTE MUSEUM Busan',
        'category': 'attraction',
        'zone': '影島區',
        'location': '부산광역시 영도구 해양로247번길 29',
        'lat': 35.0911,
        'lng': 129.0422,
        'ticket': '成人22000韓元（使用VBP可免費）',
        'stay_duration': '1.5-2小時',
        'priority': 2,
        'tags': ['釜山', '影島', '數位藝術', '沉浸式展覽'],
        'description': '全球最大規模沉浸式數位藝術展，2024年7月開幕，由國際知名設計團隊 d\'strict 打造，以CIRCLE為主題，結合光影、聲音、氣味。',
        'sources': ['https://www.arte-museum.com/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=해양로247번길+29+arte+museum',
            'blog_article': 'https://alinalife.tw/arte-museum-busan',
        }
    },
    {
        'id': 'white-yeoul-village',
        'region_code': 'busan',
        'station_id': 'busan_029',
        'name': '白淺灘文化村',
        'name_en': 'White Yeoul Cultural Village',
        'category': 'attraction',
        'zone': '影島區',
        'location': '부산광역시 영도구 흰여울길',
        'lat': 35.0892,
        'lng': 129.0392,
        'ticket': '免費',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['釜山', '影島', '壁畫', '文創', '海岸步道'],
        'description': '影島超人氣景點，昔日的海女村，現在處處是壁畫、裝置藝術與可愛咖啡廳，藍色海岸散步路景色優美。',
        'sources': ['https://lillian.tw/hynyeoul-munhwa-maul'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=흰여울문화마을+영도',
            'blog_article': 'https://lillian.tw/hynyeoul-munhwa-maul',
        }
    },
    {
        'id': 'thrill-on-the-mug',
        'region_code': 'busan',
        'station_id': 'busan_029',
        'name': 'Thrill On The Mug 海景咖啡廳',
        'name_en': 'Thrill On The Mug',
        'category': 'attraction',
        'zone': '影島區',
        'location': '부산 영도구 해양힐링로 55',
        'lat': 35.0883,
        'lng': 129.0444,
        'ticket': '免費（餐飲自費）',
        'stay_duration': '1小時',
        'priority': 3,
        'tags': ['釜山', '影島', '海景咖啡', '太宗台'],
        'description': '影島超人氣海景咖啡廳，大面落地窗搭配階梯式座位，每個座位都能看見海，4樓為太宗台高空滑索。',
        'sources': ['https://whereamber.com/thrill-on-the-mug'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=해양힐링로+55+Thrill+On+The+Mug',
            'blog_article': 'https://whereamber.com/thrill-on-the-mug',
        }
    },
    # ---- FUKUOKA ----
    {
        'id': 'riverwalk-kitakyushu',
        'region_code': 'fukuoka',
        'station_id': 'fukuoka_043',
        'name': '北九州 RIVERWALK',
        'name_en': 'RIVERWALK Kitakyushu',
        'category': 'attraction',
        'zone': '北九州市',
        'location': '北九州市小倉北区室町',
        'lat': 33.8836,
        'lng': 130.8775,
        'ticket': '免費（各店鋪消費）',
        'stay_duration': '1.5小時',
        'priority': 3,
        'tags': ['福岡', '北九州', '河畔', '購物'],
        'description': '北九州知名複合型河畔購物商場，位於小倉繁華區，結合購物、餐飲與河岸景觀。',
        'sources': ['https://www.riverwalk.co.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=RIVERWALK+北九州',
            'blog_article': 'https://www.crossroadfukuoka.jp/tw/spot/13223',
        }
    },
    {
        'id': 'kushida-shrine-fukuoka',
        'region_code': 'fukuoka',
        'station_id': 'fukuoka_003',
        'name': '櫛田神社',
        'name_en': 'Kushida Shrine',
        'category': 'shrine',
        'zone': '博多',
        'location': '福岡市博多區上川端町',
        'lat': 33.6067,
        'lng': 130.4181,
        'ticket': '免費',
        'stay_duration': '45分鐘',
        'priority': 2,
        'tags': ['福岡', '博多', '神社', '祇園山笠'],
        'description': '博多總鎮守，博多祇園山笠的所在地，神社內常年展示巨大裝飾山轎，歷史悠久，是感受博多文化的好去處。',
        'sources': ['https://www.kushidajinja.com/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=櫛田神社+福岡',
            'blog_article': 'https://matcha-jp.com/tw/3528',
        }
    },
    {
        'id': 'hakata- Port Museum',
        'region_code': 'fukuoka',
        'station_id': 'fukuoka_002',
        'name': '博多港歷史公園',
        'name_en': 'Hakata Port Historical Park',
        'category': 'attraction',
        'zone': '博多',
        'location': '福岡市博多區築港口',
        'lat': 33.5981,
        'lng': 130.4067,
        'ticket': '免費',
        'stay_duration': '1小時',
        'priority': 3,
        'tags': ['福岡', '博多', '港口', '歷史'],
        'description': '博多港周邊的歷史公園，可以遠眺海景，結合海洋歷史展示，是福岡市民日常休憩的場所。',
        'sources': ['https://www.crossroadfukuoka.jp/tw/spot/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=博多港+歴史公園',
        }
    },
    {
        'id': 'dazaifu-tenmangu',
        'region_code': 'fukuoka',
        'station_id': 'fukuoka_047',
        'name': '太宰府天滿宮',
        'name_en': 'Dazaifu Tenmangu',
        'category': 'shrine',
        'zone': '太宰府',
        'location': '太宰府市宰府4-7-1',
        'lat': 33.5134,
        'lng': 130.5186,
        'ticket': '免費',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['福岡', '太宰府', '神社', '學問之神', '賞櫻'],
        'description': '供奉學問之神菅原道真，福岡最具代表性的神社之一，參道兩側有眾多商店，梅枝餅是必吃美食。',
        'sources': ['https://www.dazaifutenmangu.com/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=太宰府天滿宮',
            'blog_article': 'https://matcha-jp.com/tw/3528',
        }
    },
    # ---- TOKYO ----
    {
        'id': 'coredo-muromachi-2',
        'region_code': 'tokyo',
        'station_id': 'tokyo_047',
        'name': 'COREDO室町2',
        'name_en': 'COREDO Muromachi 2',
        'category': 'attraction',
        'zone': '日本橋',
        'location': '東京都中央区日本橋室町2-3-1',
        'lat': 35.6835,
        'lng': 139.7734,
        'ticket': '免費（各店鋪消費）',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['東京', '日本橋', '商場', '美食'],
        'description': '日本橋超人氣商場，2025年新開幕，結合美食與生活，有多間人氣餐廳進駐，包括金子半之助新品牌、和牛漢堡排蛋包飯等。',
        'sources': ['https://mitsui-shopping-park.com/urban/muromachi/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=COREDO室町2+日本橋',
            'blog_article': 'https://japanzerolag.com/?p=22377',
        }
    },
    {
        'id': 'fukutoku-shrine',
        'region_code': 'tokyo',
        'station_id': 'tokyo_047',
        'name': '福德神社',
        'name_en': 'Fukutoku Shrine',
        'category': 'shrine',
        'zone': '日本橋',
        'location': '東京都中央区日本橋室町2-4-14',
        'lat': 35.6831,
        'lng': 139.7737,
        'ticket': '免費',
        'stay_duration': '30分鐘',
        'priority': 3,
        'tags': ['東京', '日本橋', '神社', '金運', '樂透'],
        'description': '東京知名金運神社，據說是江戶時代樂透發祥地之一，被稱為「東京錢洗弁天」，參拜者可洗錢招財。',
        'sources': ['https://mebuki.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=福德神社+日本橋',
            'blog_article': 'https://tw.wamazing.com/media/article/a-233',
        }
    },
    {
        'id': 'koami-shrine',
        'region_code': 'tokyo',
        'station_id': 'tokyo_047',
        'name': '小網神社',
        'name_en': 'Koami Shrine',
        'category': 'shrine',
        'zone': '人形町',
        'location': '東京都中央区日本橋小網町16-23',
        'lat': 35.6828,
        'lng': 139.7806,
        'ticket': '免費',
        'stay_duration': '30分鐘',
        'priority': 3,
        'tags': ['東京', '人形町', '神社', '強運除厄'],
        'description': '隱身巷弄的人形町神社，祭祀弁天神，以「東京錢洗弁天」聞名，二戰期間參拜者奇蹟生還，因此被認為可除厄強運。',
        'sources': ['https://www.koamijinja.or.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=小網神社',
            'blog_article': 'https://tw.wamazing.com/media/article/a-233',
        }
    },
    {
        'id': 'suitengu',
        'region_code': 'tokyo',
        'station_id': 'tokyo_047',
        'name': '水天宮',
        'name_en': 'Suitengu',
        'category': 'shrine',
        'zone': '日本橋',
        'location': '東京都中央区日本橋蛎殻町2-4-1',
        'lat': 35.6820,
        'lng': 139.7791,
        'ticket': '免費',
        'stay_duration': '30分鐘',
        'priority': 3,
        'tags': ['東京', '日本橋', '神社', '安產', '求子'],
        'description': '以祈求順產、保佑嬰幼兒健康聞名的神社，著名的「子寶犬」雕像，周圍有代表12干支的圓球。',
        'sources': ['https://www.suitengu.or.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=水天宮+日本橋',
            'blog_article': 'https://tw.wamazing.com/media/article/a-233',
        }
    },
    # ---- OKINAWA ----
    {
        'id': 'junglia-okinawa',
        'region_code': 'okinawa',
        'station_id': 'okinawa_station_041',
        'name': 'JUNGLIA OKINAWA',
        'name_en': 'JUNGLIA OKINAWA',
        'category': 'attraction',
        'zone': '本部町',
        'location': '沖縄県国頭郡今帰仁村字呉我山553番地1',
        'lat': 26.7242,
        'lng': 127.9914,
        'ticket': '需購票（大人2800日元）',
        'stay_duration': '3-4小時',
        'priority': 2,
        'tags': ['沖繩', '北部', '主題樂園', '2025新開幕'],
        'description': '2025年7月25日開幕的北部全新主題樂園，以叢林為主題，擁有世界最大級無邊際溫泉、JUNGLIA TREE地標、及多間特色餐廳。',
        'sources': ['https://junglia.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=JUNGLIA+OKINAWA',
            'blog_article': 'https://www.japaholic.com/tw/article/detail/941288',
        }
    },
    {
        'id': 'nakijin-castle-sakura',
        'region_code': 'okinawa',
        'station_id': 'okinawa_station_042',
        'name': '今歸仁城跡',
        'name_en': 'Nakijin Castle',
        'category': 'attraction',
        'zone': '北部',
        'location': '沖縄県国頭郡今帰仁村字今泊510',
        'lat': 26.6958,
        'lng': 127.9708,
        'ticket': '大人400日元',
        'stay_duration': '1.5小時',
        'priority': 2,
        'tags': ['沖繩', '北部', '世界遺產', '賞櫻', '城堡'],
        'description': '琉球王國古城之一，2019年燒毀後重建，2025年1月獲指定為世界文化遺產。春季是熱門賞櫻景點，每年1月下旬至2月初舉辦今歸仁城櫻花祭。',
        'sources': ['https://www.vill.nakijin.okinawa.jp/'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=今帰仁城跡',
            'blog_article': 'https://furikake.okinawa/new-article/okinawa-winter-activity',
        }
    },
    {
        'id': 'naha-kokusui-dori',
        'region_code': 'okinawa',
        'station_id': 'okinawa_station_042',
        'name': '那霸國際通',
        'name_en': 'Kokusai Street, Naha',
        'category': 'attraction',
        'zone': '那霸',
        'location': '那霸市國際通',
        'lat': 26.2148,
        'lng': 127.6858,
        'ticket': '免費',
        'stay_duration': '2-3小時',
        'priority': 2,
        'tags': ['沖繩', '那霸', '購物', '美食', '国際通り'],
        'description': '那霸最熱鬧的購物美食大街，全長約1.6公里，匯集各式土產店、餐廳、伴手禮店，是體驗沖繩活力的必訪之地。',
        'sources': ['https://okinawa.letsgojp.com/archives/657147'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=那霸+国際通り',
            'blog_article': 'https://okinawa.letsgojp.com/archives/657147',
        }
    },
    {
        'id': 'sunrise-beach-okinawa',
        'region_code': 'okinawa',
        'station_id': 'okinawa_station_041',
        'name': '古宇利大橋',
        'name_en': 'Kouri Ohashi Bridge',
        'category': 'attraction',
        'zone': '北部',
        'location': ' Okinawa Prefecture, 国頭郡今帰仁村',
        'lat': 26.7039,
        'lng': 127.9825,
        'ticket': '免費',
        'stay_duration': '45分鐘',
        'priority': 2,
        'tags': ['沖繩', '北部', '古宇利島', '橋', '海景'],
        'description': '連接古宇利島與本島的免費通行大橋，全長1960公尺，兩側海景壯闊，是超人氣兜風打卡景點。',
        'sources': ['https://www.japaholic.com/tw/article/detail/941288'],
        'details': {
            'google_maps': 'https://maps.google.com/?q=古宇利大橋',
        }
    },
]

def main():
    conn = get_conn()
    existing = existing_names(conn)
    existing_ids = get_existing_ids(conn)
    existing_src = existing_sources(conn)

    added = 0
    skipped = 0
    errors = []

    for attr in NEW_ATTRACTIONS:
        name_lower = attr['name'].lower()

        # Skip if name already exists
        if name_lower in existing:
            print(f'  SKIP (name exists): {attr["name"]}')
            skipped += 1
            continue

        # Check sources for duplicates
        attr_sources = attr.get('sources', [])
        dup_source = False
        for src in attr_sources:
            if src.lower() in existing_src:
                print(f'  SKIP (URL exists): {attr["name"]} [{src}]')
                dup_source = True
                break
        if dup_source:
            skipped += 1
            continue

        # Generate unique ID
        base_id = attr['id']
        if base_id in existing_ids:
            base_id = slugify(attr['name'])
        attr_id = make_id(base_id, attr['name'], existing_ids)
        attr['id'] = attr_id
        existing_ids.add(attr_id)

        try:
            insert_attraction(conn, attr)
            conn.commit()
            print(f'  INSERT: {attr["name"]} ({attr["region_code"]}, station={attr.get("station_id")})')
            added += 1
        except Exception as e:
            errors.append((attr['name'], str(e)))
            print(f'  ERROR [{attr["name"]}]: {e}')

    conn.close()

    print(f'\n=== RESULT ===')
    print(f'Added: {added}')
    print(f'Skipped (duplicates): {skipped}')
    print(f'Errors: {len(errors)}')
    if errors:
        for name, err in errors:
            print(f'  - {name}: {err}')
    print(f'Total: {added} new attractions inserted.')

if __name__ == '__main__':
    main()
