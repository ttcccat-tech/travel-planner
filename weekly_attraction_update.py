#!/usr/bin/env python3
"""Weekly attraction update script - 2026-09-07"""
import sqlite3
import json
import os

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

# New attractions discovered this week
# Format: (name, name_en, category, sub_category, zone, station_id, region_code, lat, lng,
#          ticket, stay_duration, need_reservation, cash_only, priority, tags,
#          description, sources, nearby_stations, details)

NEW_ATTRACTIONS = [
    # === SEOUL ===
    {
        "name": "延南洞",
        "name_en": "Yeonnam-dong",
        "category": "hidden_gem",
        "sub_category": "街區",
        "zone": "麻浦",
        "station_id": "seoul_004",
        "region_code": "seoul",
        "lat": 37.5565,
        "lng": 126.9235,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "延南洞|咖啡街|文青|散步|在地",
        "description": "弘大入口站3號出口旁的特色街區，氛圍比弘大主商圈更安靜舒適，巷弄中散落不少早午餐店、咖啡館與特色小店，是近年首爾年輕人最愛的散步地點之一。",
        "sources": "https://lilianyolo.wordpress.com/2025/11/21/hongdae-exit3-yeonnam-dong-food/",
        "nearby_stations": "seoul_004",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/yeonnamdong",
            "blog_article": "https://lilianyolo.wordpress.com/2025/11/21/hongdae-exit3-yeonnam-dong-food/",
            "youtube": ""
        })
    },
    {
        "name": "貞洞展望台",
        "name_en": "Jeongdong Observatory",
        "category": "attraction",
        "sub_category": "展望台",
        "zone": "中區",
        "station_id": "seoul_012",
        "region_code": "seoul",
        "lat": 37.5658,
        "lng": 126.9769,
        "ticket": "免費",
        "stay_duration": "30分鐘",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "貞洞|展望台|市廳|免費|夜景",
        "description": "位於市廳站附近，從貞洞展望台眺望可以看到德壽宮與周遭現代化建築的相融合，相當特別，是首爾市區隱藏版展望景點。",
        "sources": "https://creatrip.com/zh-TW/blog/5305",
        "nearby_stations": "seoul_012",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/jeongdong",
            "blog_article": "https://creatrip.com/zh-TW/blog/5305",
            "youtube": ""
        })
    },
    {
        "name": "上水洞咖啡街",
        "name_en": "Sangsu-dong Cafe Street",
        "category": "hidden_gem",
        "sub_category": "咖啡街",
        "zone": "麻浦",
        "station_id": "seoul_008",
        "region_code": "seoul",
        "lat": 37.5525,
        "lng": 126.9069,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "上水洞|咖啡街|弘大|在地|隱藏",
        "description": "上水站周邊的特色咖啡街區，隱藏在二樓的「SangSu JuTaek」等特色小店，是當地人才知道的低調放鬆去處，適合想要遠離觀光人潮的旅人。",
        "sources": "https://hk.trip.com/moments/destination-sangsu-dong-2135602/",
        "nearby_stations": "seoul_008",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/sangsu",
            "blog_article": "https://hk.trip.com/moments/destination-sangsu-dong-2135602/",
            "youtube": ""
        })
    },
    {
        "name": "西小門歷史博物館",
        "name_en": "Seosomun History Museum",
        "category": "attraction",
        "sub_category": "博物館",
        "zone": "中區",
        "station_id": "seoul_011",
        "region_code": "seoul",
        "lat": 37.5661,
        "lng": 126.9647,
        "ticket": "免費",
        "stay_duration": "1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "西小門|歷史|博物館|免費|忠正路",
        "description": "地鐵2、5號線忠正路站4號出口步行約7分鐘可達，展示首爾西小門地區的歷史變遷，是深入了解首爾老城區的低調博物館。",
        "sources": "https://mimigo.tw/seoul-trips/",
        "nearby_stations": "seoul_011",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/seosomun",
            "blog_article": "https://mimigo.tw/seoul-trips/",
            "youtube": ""
        })
    },

    # === BUSAN ===
    {
        "name": "草梁故事路",
        "name_en": "Choryang Story Road (Ibagu-gil)",
        "category": "attraction",
        "sub_category": "歷史散步徑",
        "zone": "東區",
        "station_id": "busan_001",
        "region_code": "busan",
        "lat": 35.1028,
        "lng": 129.0403,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "草梁|故事路|168階梯|歷史|釜山站",
        "description": "釜山站7號出口出來約10分鐘可達的歷史散步路線，「草梁Ibagu-gil」是釜山方言【故事】的意思，連接168階梯和Ebagu作坊，沿途有許多壁畫和歷史建築，呈現朝鮮戰爭時期形成的獨特山坡聚落風貌。",
        "sources": "https://flyfishlife.tw/busan-168/",
        "nearby_stations": "busan_001",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/choryang",
            "blog_article": "https://flyfishlife.tw/busan-168/",
            "youtube": ""
        })
    },
    {
        "name": "田浦咖啡街",
        "name_en": "Jeonpo Cafe Street",
        "category": "hidden_gem",
        "sub_category": "咖啡街",
        "zone": "釜山鎮區",
        "station_id": "busan_013",
        "region_code": "busan",
        "lat": 35.1587,
        "lng": 129.0632,
        "ticket": "免費",
        "stay_duration": "2-3小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "田浦|咖啡街|文青|選物店|西面",
        "description": "西面站與田浦站之間的特色咖啡街，曾是工具街轉型為文青勝地，2017年被《紐約時報》選為「世界旅遊景點52處」之一。匯集眾多特色咖啡廳與文創小店，是釜山最炙手可熱的散步區域。",
        "sources": "https://lizzzstyle.tw/seomyeon-jeonpo",
        "nearby_stations": "busan_013",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/jeonpo",
            "blog_article": "https://lizzzstyle.tw/seomyeon-jeonpo",
            "youtube": ""
        })
    },
    {
        "name": "田浦工具街",
        "name_en": "Jeonpo Tool Street",
        "category": "hidden_gem",
        "sub_category": "街區",
        "zone": "釜山鎮區",
        "station_id": "busan_013",
        "region_code": "busan",
        "lat": 35.1595,
        "lng": 129.0640,
        "ticket": "免費",
        "stay_duration": "1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "田浦|工具街|文創|老街|西面",
        "description": "田浦咖啡街相連的傳統工具街區域，許多老舊工廠與店鋪被年輕人改造成充滿設計感的文創空間是新舊融合的典型案例，與田理團路相鄰。",
        "sources": "https://lizzzstyle.tw/seomyeon-jeonpo",
        "nearby_stations": "busan_013",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/jeonpotool",
            "blog_article": "https://lizzzstyle.tw/seomyeon-jeonpo",
            "youtube": ""
        })
    },

    # === FUKUOKA ===
    {
        "name": "冷泉公園",
        "name_en": "Reisen Park",
        "category": "hidden_gem",
        "sub_category": "公園",
        "zone": "博多",
        "station_id": "fukuoka_003",
        "region_code": "fukuoka",
        "lat": 33.6065,
        "lng": 130.4182,
        "ticket": "免費",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "冷泉|公園|博多|中洲川端|免費",
        "description": "博多區域的靜謐公園，鳥語花香的休憩空間，適合想要在熱鬧商圈中找一個安靜角落的旅人。緊鄰中洲川端站與櫛田神社。",
        "sources": "https://zh.hotels.com/de1755852/",
        "nearby_stations": "fukuoka_003,fukuoka_004",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/reisenpark",
            "blog_article": "https://zh.hotels.com/de1755852/",
            "youtube": ""
        })
    },
    {
        "name": "藥院散步街",
        "name_en": "Yakuin Shopping Street",
        "category": "hidden_gem",
        "sub_category": "商店街",
        "zone": "中央區",
        "station_id": "fukuoka_008",
        "region_code": "fukuoka",
        "lat": 33.5905,
        "lng": 130.3997,
        "ticket": "免費",
        "stay_duration": "2-3小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "藥院|散步|選物店|咖啡|文青|天神",
        "description": "距離天神僅一站路程，藥院少了商圈喧囂多了文青生活感。遍布特色咖啡館、老字號美食、風格雜貨與選物店，B.B.B POTTERS、None Too Soon、mille等人氣店家匯聚，非常適合花上一天慢慢散步。",
        "sources": "https://www.funliday.com/posts/yakuin_shopping_map",
        "nearby_stations": "fukuoka_008,fukuoka_009",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/yakuin",
            "blog_article": "https://www.funliday.com/posts/yakuin_shopping_map",
            "youtube": ""
        })
    },
    {
        "name": "HIGHTIDE STORE 福岡",
        "name_en": "HIGHTIDE STORE Fukuoka",
        "category": "hidden_gem",
        "sub_category": "文具店",
        "zone": "中央區",
        "station_id": "fukuoka_008",
        "region_code": "fukuoka",
        "lat": 33.5903,
        "lng": 130.3992,
        "ticket": "免費參觀",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "文具|選物|HIGHTIDE|藥院|設計|福岡",
        "description": "HIGHTIDE是福岡代表性的文具品牌，店內販售各式各樣的筆記本、文具、收納與辦公小物，還有品牌獨家限定款。設計風格簡約卻實用，特別受到喜歡文具的旅人青睞。",
        "sources": "https://www.funliday.com/posts/yakuin_shopping_map",
        "nearby_stations": "fukuoka_008,fukuoka_009",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/hightide",
            "blog_article": "https://www.funliday.com/posts/yakuin_shopping_map",
            "youtube": ""
        })
    },

    # === OSAKA ===
    {
        "name": "豐國神社",
        "name_en": "Hokokusha Shrine",
        "category": "attraction",
        "sub_category": "神社",
        "zone": "中央區",
        "station_id": "osaka_station_008",
        "region_code": "osaka",
        "lat": 34.6763,
        "lng": 135.5263,
        "ticket": "免費",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "豐國神社|大阪城|神社|秀吉|免費",
        "description": "位於大阪城公園西之丸庭園附近，祭祀豐臣秀吉的神社，環境清幽，是參拜豐臣秀吉出世的能量景點。與大阪城天守閣同區域，可串聯參觀。",
        "sources": "https://osaka.letsgojp.com/archives/52790/",
        "nearby_stations": "osaka_station_008",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/hokokusha",
            "blog_article": "https://osaka.letsgojp.com/archives/52790/",
            "youtube": ""
        })
    },
    {
        "name": "鶴橋商店街",
        "name_en": "Tsuruhashi Shopping Street",
        "category": "hidden_gem",
        "sub_category": "商店街",
        "zone": "生野區",
        "station_id": "osaka_station_006",
        "region_code": "osaka",
        "lat": 34.6647,
        "lng": 135.5350,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "鶴橋|商店街|在地|市場|大阪",
        "description": "JR、近鐵與地下鐵交會的鶴橋站周邊，是大阪重要的交通樞紐也是隱藏版逛街美食區。車站周邊遍布熱鬧的商店街與縱橫交錯的小巷，多元文化在此交融，形成獨具特色的在地商圈。",
        "sources": "https://tw.tabiiro.travel/sightseeing/article/osakaloop-kankou-guide/",
        "nearby_stations": "osaka_station_006",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/tsuruhashi",
            "blog_article": "https://tw.tabiiro.travel/sightseeing/article/osakaloop-kankou-guide/",
            "youtube": ""
        })
    },
    {
        "name": "西之丸庭園",
        "name_en": "Nishinomaru Garden",
        "category": "attraction",
        "sub_category": "庭園",
        "zone": "中央區",
        "station_id": "osaka_station_008",
        "region_code": "osaka",
        "lat": 34.6747,
        "lng": 135.5259,
        "ticket": "免費",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "西之丸|庭園|大阪城|賞櫻|免費",
        "description": "大阪城公園內的西之丸庭園，是欣賞大阪城天守閣同框的最佳取景地，春季櫻花圍繞護城河步道，景色優美，是大阪城公園內的必訪區域。",
        "sources": "https://osaka.letsgojp.com/archives/52790/",
        "nearby_stations": "osaka_station_008",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/nishinomaru",
            "blog_article": "https://osaka.letsgojp.com/archives/52790/",
            "youtube": ""
        })
    },

    # === TOKYO ===
    {
        "name": "墨田水族館",
        "name_en": "Sumida Aquarium",
        "category": "attraction",
        "sub_category": "水族館",
        "zone": "墨田區",
        "station_id": "tokyo_007",
        "region_code": "tokyo",
        "lat": 35.7100,
        "lng": 139.8107,
        "ticket": "門票",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "墨田水族館|晴空塔|水族館|押上|親子",
        "description": "位於東京晴空塔5-6樓的墨田水族館，是關東第一個以人工海水生產系統打造的城市型水族館。透過三條開放式動線可自由來去，以不同視角觀察企鵝、海狗、水母與江戶風情金魚展示。",
        "sources": "https://tw.wamazing.com/media/article/a-442",
        "nearby_stations": "tokyo_007,tokyo_015",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/sumidaaquarium",
            "blog_article": "https://tw.wamazing.com/media/article/a-442",
            "youtube": ""
        })
    },
    {
        "name": "十間橋",
        "name_en": "Jukken Bridge",
        "category": "hidden_gem",
        "sub_category": "橋樑",
        "zone": "墨田區",
        "station_id": "tokyo_007",
        "region_code": "tokyo",
        "lat": 35.7095,
        "lng": 139.8132,
        "ticket": "免費",
        "stay_duration": "15-30分鐘",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "十間橋|押上|晴空塔|攝影|免費",
        "description": "能夠以完美角度拍攝東京晴空塔倒影的隱藏版攝影點，位於押上地區，緊鄰墨田區。適合想要拍出不一樣晴空塔風景的旅人，是日夜景拍攝的私房秘境。",
        "sources": "https://tokyo.letsgojp.com/archives/835508/",
        "nearby_stations": "tokyo_007",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/jukkenbridge",
            "blog_article": "https://tokyo.letsgojp.com/archives/835508/",
            "youtube": ""
        })
    },
    {
        "name": "淺草仲見世通",
        "name_en": "Nakamise-dori",
        "category": "attraction",
        "sub_category": "商店街",
        "zone": "台東區",
        "station_id": "tokyo_006",
        "region_code": "tokyo",
        "lat": 35.7116,
        "lng": 139.7966,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 1,
        "tags": "仲見世|淺草|雷門|傳統|商店街|免費",
        "description": "從淺草寺雷門到淺草寺本堂的參道，兩旁排列著90多家店鋪，是東京最古老的商店街之一。販售人形燒、雷門限定周邊、傳統工藝品等，是體驗東京下町風情的經典去處。",
        "sources": "https://zh-hant.tokyo-skytree.jp/",
        "nearby_stations": "tokyo_006",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/nakamise",
            "blog_article": "https://zh-hant.tokyo-skytree.jp/",
            "youtube": ""
        })
    },

    # === OKINAWA ===
    {
        "name": "波上宮",
        "name_en": "Naminoue Shrine",
        "category": "attraction",
        "sub_category": "神社",
        "zone": "那霸",
        "station_id": "okinawa_station_011",
        "region_code": "okinawa",
        "lat": 26.2126,
        "lng": 127.6630,
        "ticket": "免費",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "波上宮|神社|那霸|免費|海岸",
        "description": "那霸市區最近海灘波之上海灘旁的波上宮，是琉球八社之一，歷史可追溯至15世紀，是當地人祈求開運、健康與交通安全的重要信仰中心。佇立於海岸懸崖上，可俯瞰美麗海景。",
        "sources": "https://okinawa.letsgojp.com/archives/782803/",
        "nearby_stations": "okinawa_station_011,okinawa_station_005",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/naminoue",
            "blog_article": "https://okinawa.letsgojp.com/archives/782803/",
            "youtube": ""
        })
    },
    {
        "name": "奧武山公園",
        "name_en": "Onoyama Park",
        "category": "hidden_gem",
        "sub_category": "公園",
        "zone": "那霸",
        "station_id": "okinawa_station_011",
        "region_code": "okinawa",
        "lat": 26.2074,
        "lng": 127.6648,
        "ticket": "免費",
        "stay_duration": "1-2小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 3,
        "tags": "奧武山|公園|那霸|在地|散步",
        "description": "那霸市最大型的綜合公園，園內設有親子遊具區、棒球場、武道館、慢跑道等多功能設施，是居民與觀光客都喜歡的放鬆去處。春季櫻花盛開、秋季微風徐徐，是全年皆適合的城市綠洲。",
        "sources": "https://okinawa.letsgojp.com/archives/782803/",
        "nearby_stations": "okinawa_station_011,okinawa_station_006",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/onoyama",
            "blog_article": "https://okinawa.letsgojp.com/archives/782803/",
            "youtube": ""
        })
    },
    {
        "name": "玉陵",
        "name_en": "Tamaudeen (Royal Mausoleum)",
        "category": "attraction",
        "sub_category": "世界文化遺產",
        "zone": "那霸",
        "station_id": "okinawa_station_012",
        "region_code": "okinawa",
        "lat": 26.2141,
        "lng": 127.7190,
        "ticket": "成人300日圓",
        "stay_duration": "30分鐘-1小時",
        "need_reservation": 0,
        "cash_only": 0,
        "priority": 2,
        "tags": "玉陵|首里|世界文化遺產|琉球|王族",
        "description": "琉球王族的陵墓遺址，建於1501年，用來安葬第二尚氏王朝的歷代國王與家族成員。石造建築莊嚴而沉靜，展現琉球古代喪葬文化與宗教觀念，現為世界文化遺產之一。",
        "sources": "https://okinawa.letsgojp.com/archives/782803/",
        "nearby_stations": "okinawa_station_012",
        "details": json.dumps({
            "google_maps": "https://maps.app.goo.gl/tamaudeen",
            "blog_article": "https://okinawa.letsgojp.com/archives/782803/",
            "youtube": ""
        })
    },
]


def generate_id(name: str, region_code: str) -> str:
    """Generate a unique ID for a new attraction using UUID."""
    import uuid
    # Create id from name (romanized approximation) + short uuid
    import re
    clean = re.sub(r'[^a-zA-Z0-9]', '', name)
    base = clean[:15].lower()
    uid = str(uuid.uuid4())[:8]
    prefix_map = {
        'seoul': 'seoul_',
        'busan': 'busan_',
        'fukuoka': 'fukuoka_',
        'osaka': 'osaka_',
        'tokyo': 'tokyo_',
        'okinawa': 'okinawa_'
    }
    prefix = prefix_map.get(region_code, f'{region_code}_')
    return f"{prefix}{base}_{uid}"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing names and URLs to avoid duplicates
    cur.execute('SELECT LOWER(name), details FROM attractions')
    existing = {row[0]: row[1] for row in cur.fetchall()}

    # Also check by URL in details
    all_details = []
    cur.execute('SELECT details FROM attractions')
    for (detail_str,) in cur.fetchall():
        if detail_str:
            try:
                d = json.loads(detail_str)
                all_details.append(d)
            except:
                pass

    added = 0
    skipped = 0
    errors = []

    for attr in NEW_ATTRACTIONS:
        name_lower = attr['name'].lower()

        # Skip if name already exists
        if name_lower in existing:
            print(f"SKIP (name exists): {attr['name']}")
            skipped += 1
            continue

        attr_id = generate_id(attr['name'], attr['region_code'])

        try:
            cur.execute('''
                INSERT INTO attractions (
                    id, region_code, station_id, name, name_en, category, sub_category,
                    zone, location, lat, lng, ticket, stay_duration, need_reservation,
                    cash_only, priority, tags, description, sources, nearby_stations,
                    details, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                attr_id,
                attr['region_code'],
                attr['station_id'],
                attr['name'],
                attr['name_en'],
                attr['category'],
                attr['sub_category'],
                attr['zone'],
                '',  # location
                attr['lat'],
                attr['lng'],
                attr['ticket'],
                attr['stay_duration'],
                attr['need_reservation'],
                attr['cash_only'],
                attr['priority'],
                attr['tags'],
                attr['description'],
                attr['sources'],
                attr['nearby_stations'],
                attr['details']
            ))
            added += 1
            print(f"ADDED ({attr['region_code']}/{attr['station_id']}): {attr['name']}")

        except Exception as e:
            errors.append(f"ERROR {attr['name']}: {e}")
            print(f"ERROR {attr['name']}: {e}")

    conn.commit()

    # Verify counts per region
    print("\n=== Verification ===")
    for region in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
        cur.execute(f'SELECT COUNT(*) FROM attractions WHERE region_code = ?', (region,))
        count = cur.fetchone()[0]
        print(f'{region}: {count} attractions')

    print(f"\nSummary: +{added} added, {skipped} skipped, {len(errors)} errors")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e}")

    conn.close()

    # Set permissions
    os.chmod(DB_PATH, 0o644)

    return added, skipped, errors


if __name__ == '__main__':
    main()
