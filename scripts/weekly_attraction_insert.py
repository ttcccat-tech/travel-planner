#!/usr/bin/env python3
"""
每週旅遊景點擴充任務 - 2026-09-06
新增景點：12筆（來自7個車站）
"""

import sqlite3, json, os, sys

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def slugify(text):
    import re
    text = re.sub(r'^[釜山|東京|大阪|首爾|福岡|沖繩| Seoul| Busan| Osaka| Tokyo| Fukuoka| Okinawa]+\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    return text[:20].lower() if text else text.lower()

def generate_id(region, name):
    base = slugify(name)
    if not base:
        base = 'attraction'
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM attractions WHERE id LIKE '{region}_{base}%'")
    count = cur.fetchone()[0]
    conn.close()
    suffix = f"_{count+1}" if count > 0 else ""
    return f"{region}_{base}{suffix}"

def check_exists(region, name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT name FROM attractions WHERE region_code='{region}' AND name=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row is not None

# New attractions to insert
# Format: (name, name_en, category, region, station_id, zone, description, sources_list, details_dict)
NEW_ATTRACTIONS = [
    # === TOKYO ===
    {
        "id": "tokyo_bonustrack",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "BONUS TRACK 下北澤",
        "name_en": "BONUS TRACK",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "由舊鐵道用地再生而成的新型態商店街，約14間風格小店，沒有連鎖品牌，全為獨具個性的在地店家。開放式空間與中庭可自由使用，定期舉辦市集與藝廊活動。",
        "sources": ["https://bonus-tracks.jp"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/BONUS+TRACK/@35.6605,139.6702",
            "blog_article": "https://www.funliday.com/posts/shimo-kitazawa-travel-guide",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_kitazawahachiman",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "北澤八幡神社",
        "name_en": "Kitazawa Hachimangu Shrine",
        "category": "shrine",
        "zone": "下北澤",
        "description": "隱身在下北澤街區一角，從熱鬧商店街步行過來十分順路，卻能瞬間轉換成安靜沉穩的氛圍。境內清幽、人潮相對少，適合想暫時避開喧鬧、放慢腳步的旅客。",
        "sources": ["https://tokyo.letsgojp.com/archives/67499/"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/北澤八幡神社",
            "blog_article": "https://tokyo.letsgojp.com/archives/67499/",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_senrosekigaiji",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "下北線路街 空地",
        "name_en": "Shimo-Kita Line Street / 空地",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "利用小田急線舊鐵道用地再生而成的下北線路街「空地」，以「大家共同打造的自由遊樂場」為概念，規劃為開放式戶外空間。園內設有人工草坪廣場與灰色貨櫃，並以現代手法再現帶有水泥管的懷舊空地氛圍。",
        "sources": ["https://www.gltjp.com/zh-hant/article/item/21108"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/下北線路街",
            "blog_article": "https://www.gltjp.com/zh-hant/article/item/21108",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_flamingo",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "Flamingo 下北澤店",
        "name_en": "Flamingo Shimokitazawa",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "以霓虹燈招牌為標誌的復古服飾店，主要販售自美國與歐洲採購的1960至1990年代單品。室內以古董家具與復古裝飾點綴，氛圍時尚而舒適。商品涵蓋外套、襯衫、牛仔服飾與飾品，種類齊全。",
        "sources": ["https://www.gltjp.com/zh-hant/article/item/21108"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/Flamingo+下北沢店",
            "blog_article": "https://www.gltjp.com/zh-hant/article/item/21108",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_honyasanb",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "本屋B&B 下北澤",
        "name_en": "Honya B&B Shimokitazawa",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "獨立書店與啤酒的獨特組合，熱鬧不已的氛圍中人人一手翻書一口啤酒。Book & Beer的組合在其他地方相當少見，是下北澤特有的文青風格小店。",
        "sources": ["https://www.funliday.com/posts/shimo-kitazawa-travel-guide"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/本屋B%26B",
            "blog_article": "https://www.funliday.com/posts/shimo-kitazawa-travel-guide",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_monarecords",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "mona records 下北澤",
        "name_en": "mona records Shimokitazawa",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "下北澤老字號的獨立唱片行兼咖啡廳，二樓供應日式米食定食、輕食點心、蛋糕和飲品，並販售日本獨立樂團CD與周邊，三樓則是經常舉辦各種音樂風格Live house演出的場地。",
        "sources": ["https://www.funliday.com/posts/shimo-kitazawa-travel-guide"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/mona+records",
            "blog_article": "https://www.funliday.com/posts/shimo-kitazawa-travel-guide",
            "youtube": ""
        }
    },
    {
        "id": "tokyo_shimokitasouth",
        "region": "tokyo",
        "station_id": "tokyo_089",
        "name": "下北澤南口商店街",
        "name_en": "Shimokitazawa Minami-guchi Shopping Street",
        "category": "hidden_gem",
        "zone": "下北澤",
        "description": "下北澤南口商店街與北口風貌截然不同，藝文界散步者與咖啡甜點愛好者的天堂。街道兩旁聚集可愛的雜貨店與獨具風格的古著店，同時也保留傳統食堂與深受在地居民喜愛的大眾居酒屋。白天適合購物與咖啡巡禮，夜晚則能體驗酒吧或觀賞現場音樂。",
        "sources": ["https://www.gltjp.com/zh-hant/article/item/21108"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/下北沢南口商店街",
            "blog_article": "https://www.gltjp.com/zh-hant/article/item/21108",
            "youtube": ""
        }
    },
    # === BUSAN ===
    {
        "id": "busan_bupyeong_market",
        "region": "busan",
        "station_id": "busan_027",
        "name": "富平罐頭市場",
        "name_en": "Bupyeong Kkangtong Market",
        "category": "hidden_gem",
        "zone": "南浦區",
        "description": "早年因美軍罐頭等進口商品集散地而得名，白天是傳統市場，晚上七點半中間走道會推出黃色餐車成熱鬧夜市。異國料理多、美食重複度低，可找到越南春捲、土耳其冰淇淋、日式大阪燒等。通道較窄，週末晚上人潮洶湧。",
        "sources": ["https://mimigo.tw/nampo-dong-trips"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/富平罐頭市場",
            "blog_article": "https://mimigo.tw/nampo-dong-trips",
            "youtube": ""
        }
    },
    {
        "id": "busan_yeongdo_bridge",
        "region": "busan",
        "station_id": "busan_028",
        "name": "影島大橋",
        "name_en": "Yeongdodaegyo Bridge",
        "category": "attraction",
        "zone": "南浦區",
        "description": "連接南浦洞與影島的跨港大橋，是釜山代表性的地標之一。橋身開合讓船隻通過的場景壯觀，也是許多旅客會停留拍照的熱門景點。",
        "sources": ["https://mamahuhu.blog/overseas/nampodong-trip"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/影島大橋",
            "blog_article": "https://mamahuhu.blog/overseas/nampodong-trip",
            "youtube": ""
        }
    },
    # === SEOUL ===
    {
        "id": "seoul_sangsu_dong",
        "region": "seoul",
        "station_id": "seoul_008",
        "name": "上水洞 獨立文化街區",
        "name_en": "Sangsu-dong",
        "category": "hidden_gem",
        "zone": "麻浦",
        "description": "上水緊鄰弘大，卻有著更慢、更鬆弛的節奏。沿著街巷漫步，可以遇見壁畫塗鴉、Vintage小店、獨立咖啡館、柴火料理店和Live Pub，是感受首爾獨立文化氛圍的私房去處。",
        "sources": ["https://chinese.visitseoul.net/editorspicks/2026-Sangsu-dong/CNNvlk68c"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/上水洞",
            "blog_article": "https://chinese.visitseoul.net/editorspicks/2026-Sangsu-dong/CNNvlk68c",
            "youtube": ""
        }
    },
    # === FUKUOKA ===
    {
        "id": "fukuoka_koura_taisha",
        "region": "fukuoka",
        "station_id": "fukuoka_043",
        "name": "高良大社",
        "name_en": "Koura Taisha",
        "category": "shrine",
        "zone": "久留米",
        "description": "久留米市近郊以城市景色聞名的神社，距離久留米市中心約20分鐘車程。神社腹地廣大，可俯瞰久留米市全景，是當地人私藏的賞夜景秘境，也是福岡小眾旅行地推薦景點。",
        "sources": ["https://tw.trip.com/moments/kurume-57399-attraction-3/"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/高良大社",
            "blog_article": "https://tw.trip.com/moments/kurume-57399-attraction-3/",
            "youtube": ""
        }
    },
    # === OKINAWA ===
    {
        "id": "okinawa_nakijinson",
        "region": "okinawa",
        "station_id": "okinawa_station_048",
        "name": "今帰仁城跡",
        "name_en": "Nakijinson Castle Ruins",
        "category": "attraction",
        "zone": "北部",
        "description": "今帰仁城跡於2000年被聯合國教科文組織列為世界文化遺產，是琉球王國時期壯觀的城堡遺跡。曲線石牆與城郭遺跡保存完整，高處可展望沖繩北部遼闊海景，城內御嶽與史跡交織的神聖氛圍令人印象深刻。",
        "sources": ["https://okinawa.letsgojp.com/archives/737284/"],
        "details": {
            "google_maps": "https://www.google.com/maps/place/今帰仁城跡",
            "blog_article": "https://okinawa.letsgojp.com/archives/737284/",
            "youtube": ""
        }
    },
]

def insert_attraction(data):
    conn = get_db()
    cur = conn.cursor()
    cols = ['id','region_code','station_id','name','name_en','category','zone','sources','details']
    placeholders = ','.join(['?' for _ in cols])
    sources_json = json.dumps(data.get('sources', []))
    details_json = json.dumps(data.get('details', {}), ensure_ascii=False)
    values = (
        data['id'], data['region'], data['station_id'],
        data['name'], data.get('name_en', ''),
        data['category'], data['zone'],
        sources_json, details_json
    )
    try:
        cur.execute(f"INSERT OR IGNORE INTO attractions ({','.join(cols)}) VALUES ({placeholders})", values)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"  [ERROR] Insert failed for {data['name']}: {e}")
        return False
    finally:
        conn.close()

def main():
    print("=== 每週景點擴充任務 2026-09-06 ===\n")
    
    added = []
    skipped = []
    
    for item in NEW_ATTRACTIONS:
        # Check if already exists by exact name
        if check_exists(item['region'], item['name']):
            print(f"[SKIP] {item['region']}/{item['name']} (already exists)")
            skipped.append(item['name'])
            continue
        
        success = insert_attraction(item)
        if success:
            print(f"[ADD] {item['region']}/{item['name']} (station={item['station_id']})")
            added.append(item['name'])
        else:
            print(f"[FAIL] {item['region']}/{item['name']}")
    
    print(f"\n=== Summary ===")
    print(f"新增: {len(added)} 筆")
    print(f"跳過: {len(skipped)} 筆 (已存在)")
    
    # Verify counts
    conn = get_db()
    cur = conn.cursor()
    for region in ['tokyo', 'busan', 'seoul', 'fukuoka', 'okinawa']:
        cur.execute(f"SELECT COUNT(*) FROM attractions WHERE region_code='{region}'")
        count = cur.fetchone()[0]
        print(f"  {region}: {count} attractions (after insert)")
    conn.close()
    
    return len(added), added

if __name__ == '__main__':
    count, names = main()
    print(f"\nDone: {count} new attractions added.")
