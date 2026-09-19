#!/usr/bin/env python3
"""Insert meals from weekly scan 2026-09-19"""
import sqlite3, json, re

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def short_id(base_name, region):
    slug = re.sub(r'[^a-zA-Z0-9]', '', base_name)[:10].lower()
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

# ── All gathered food data ─────────────────────────────────────────────────────
# Format: (station_id, station_name, zone, region, stype, foods=[(url, title)])
FOODS = [
    # SEOUL - Large
    ('seoul_042', '仁川機場1號站', '仁川機場', 'seoul', 'large', [
        ('https://fanny4lin.pixnet.net/blog/posts/12227370925', '首爾糖餅 傳統糖餅與現代冰淇淋完美結合'),
        ('https://creatrip.com/zh-TW/blog/13452', '仁川機場美食懶人包'),
        ('https://hk.trip.com/moments/detail/incheon-1385-121842996', '仁川機場最後一頓韓式料理'),
    ]),
    ('seoul_022', '光化門站', '光化門', 'seoul', 'large', [
        ('https://www.funliday.com/posts/myeongdong-food-recommendations', '首爾明洞必吃美食推薦16選'),
        ('https://www.elle.com.hk/life/seoul-gwanghwamun', '光化門站不只得景福宮 Cafe美食'),
        ('https://guide.michelin.com/us/en/seoul-capital-area/kr-seoul/restaurant/mijin', 'Mijin 美進冷蕎麥麵'),
    ]),
    ('seoul_017', '會賢站', '南大門', 'seoul', 'large', [
        ('https://athena77.com/namdaemun-mkt', '南大門市場美食懶人包 刀削麵豬腳'),
        ('https://auntie.tw/category/asia-travel/%E9%9F%93%E5%9C%8B/seoul/seoul-food/namdaemun', '南大門市場彙整'),
        ('https://loveniki0108.pixnet.net/blog/posts/10347847043', '南大門市場必吃必逛必買特輯'),
    ]),
    ('seoul_024', '安國站', '三清洞', 'seoul', 'large', [
        ('https://sansalife.tw/cafe-onion-anguk', 'Cafe Onion Anguk IG打卡韓屋咖啡廳'),
        ('https://flyfishlife.tw/seoul-artist-bakery', 'Artist Bakery 神級鹽可頌與法棍麵包'),
        ('https://creatrip.com/zh-TW/blog/11864', '北村三清洞美食攻略 11間餐廳推薦'),
        ('https://pelagcy221.pixnet.net/blog/posts/9442526645', '本粥 料多味美的粥'),
    ]),
    # SEOUL - Minor
    ('seoul_037', '上鳳站', '上鳳', 'seoul', 'minor', [
        ('https://www.siksinhot.com/theme/magazine/12953', '상봉역 맛집 TOP 5 2026'),
        ('https://lately-rabbit.tistory.com/300', '100년 설렁탕 傳承老店'),
        ('https://m.blog.naver.com/toomyung_/223814469582', '상봉역 노포맛집 순대국'),
    ]),
    ('seoul_025', '仁寺洞站', '仁寺洞', 'seoul', 'minor', [
        ('https://www.kkday.com/zh-tw/blog/28453/asia-south-korea-seoul-insadong', '仁寺洞全攻略隱藏版美食'),
        ('https://creatrip.com/zh-TW/blog/902', '仁寺洞在地美食餐廳 9間推薦'),
        ('https://yiwutrip.tw/insa-dong', '仁寺洞攻略 3家必吃'),
        ('https://creatrip.com/zh-HK/blog/963', '仁寺洞瓦罐麵疙瘩 隱藏版美食'),
    ]),

    # BUSAN - Large
    ('busan_001', '釜山站', '中央區', 'busan', 'large', [
        ('https://mountaintravel.tistory.com/357', '釜山站美食完整攻略 2026'),
        ('https://blog.naver.com/PostView.naver?blogId=pinktiny&logNo=224371290718', '釜山站美食 ShabuShabu吃到飽'),
        ('https://blog.naver.com/heronet721/223011622342', '釜山站唐人街美食 原鄉재'),
        ('https://blog.naver.com/PostView.nhn?blogId=ji_ni_2&logNo=224029018767', '釜山站有家네닭갈비'),
        ('https://blog.naver.com/PostView.nhn?blogId=travelbarista&logNo=224116669515', ' 초량 인생횟집 初量人氣餐廳'),
    ]),
    ('busan_027', '札嘎其站', '南浦區', 'busan', 'large', [
        ('https://oni77.tistory.com/entry/자갈치역고기집-자갈치숯불구이-전문점', '자갈치역 고기집 炭火烤肉專門'),
        ('https://m.blog.naver.com/byprincess/223421749219', '南浦洞高品質五花肉목살'),
        ('https://moding-story.tistory.com/entry/자갈치역-채도-아늑한-카페', '札嘎其站 設計感咖啡廳'),
        ('https://ccumi0905.tistory.com/61', '釜山水泳 現撈海鮮餐廳'),
    ]),
    ('busan_028', '南浦站', '南浦區', 'busan', 'large', [
        ('https://little-cat.tistory.com/entry/남포동-점심-맛집-베스트-10-순위-추천', '南浦洞午餐美食 Best 10'),
        ('https://naknak.app/spots/kr-busan-nampo-chungmu-kimbab-street', '南浦洞 膾舞飯街 在地美食'),
        ('https://yjtripfood.tistory.com/entry/2025-부산-숨은-맛집-추천-현지지인만-아는-진짜-로컬-맛집-3곳-총정리', '釜山隱藏版美食 在地人才知道'),
    ]),
    ('busan_029', '中央站', '南浦區', 'busan', 'large', [
        ('https://triple.guide/restaurants/98a74acd-578d-4b38-929c-3ee27ec13554', '상짱 釜山中央洞 炸豬排'),
        ('https://naknak.app/videos/Wj_7fiFawMQ', '성시경의 먹을텐데 釜山 中央駅 萬里香'),
    ]),
    ('busan_045', '廣安站', '廣安區', 'busan', 'large', [
        ('https://tour.click1-tip.com/entry/광안리-맛집-베스트10-추천-현지인-로컬-식당', '廣安里美食 Best 10 在地食堂'),
        ('https://little-cat.tistory.com/entry/광안리-파스타-맛집-베스트-10-순위-추천', '廣安里 Pasta Best 10'),
        ('https://forourtour.com/entry/광안리-맛집-추천-베스트-10', '廣安里美食推薦 午餐晚餐'),
        ('https://traveling-cat.tistory.com/entry/나만-알고싶은-광안리-맛집-추천-BEST-5', '廣安里隱藏版美食推薦'),
    ]),
    # BUSAN - Minor
    ('busan_018', '德川站', '北區', 'busan', 'minor', [
        ('https://two-chickens.tistory.com/47', '북구 덕천동 젊음의 거리 라멘 쇼오텐'),
        ('https://www.siksinhot.com/theme/magazine/16482', '덕천역 맛집 TOP 6'),
    ]),
    ('busan_019', '華明站', '北區', 'busan', 'minor', [
        ('https://blog.naver.com/PostView.nhn?blogId=sorong26&logNo=224050725984', '화명동 초밥 스시 올타미스터스시'),
    ]),

    # FUKUOKA - Large
    ('fukuoka_001', '博多站', '博多', 'fukuoka', 'large', [
        ('https://gogojp.tw/hakata-yumyum', '博多美食和牛燒肉牛腸鍋居酒屋'),
        ('https://peikie.com/hakatafood', '博多站附近美食懶人包'),
        ('https://tasting-japan.com/archives/4975', '福岡博多美食必吃10選 拉麵牛腸鍋燒肉'),
    ]),
    ('fukuoka_003', '中洲川端站', '中洲', 'fukuoka', 'large', [
        ('https://nakasu-magazine.com/nakasu-taberu/nakasu-sinya-gohan', '中洲深夜美食 TOP 20 2026'),
        ('https://ichiryu-kawabata.foodre.jp/', '元祖中洲屋台ラーメン 一番一竜'),
    ]),
    ('fukuoka_043', '久留米站', '久留米', 'fukuoka', 'large', [
        ('https://welcome-kurume.com/tw/enjoys/gourmet', '久留米美食 官方觀光指南'),
    ]),
    ('fukuoka_039', '折尾站', '八幡西區', 'fukuoka', 'large', [
        ('https://kfm.sakura.ne.jp/ekiben/40fukuoka_orikas.htm', '折尾站 かしわめし 百年鐵路便當'),
        ('https://fb80801.gorp.jp/', '串揚酒場 ぞろ芽 折尾站前'),
    ]),
    ('fukuoka_040', '黑崎站', '八幡西區', 'fukuoka', 'large', [
        ('https://i7tou.com/fukuoka-ebisuya-lunch-and-night-diner', 'エビス屋 昼夜食堂 60年昭和風'),
    ]),
    # FUKUOKA - Minor
    ('fukuoka_026', '六本鬆站', '六本鬆', 'fukuoka', 'minor', [
        ('https://matomeapi.miil.me/articles/ktnpT', '六本鬆美食3選'),
        ('https://tabelog.com/fukuoka/A4001/A400105/40004048/', '六本松 ごえん 和食'),
        ('https://hitokuchi-daruma.com/', '焼肉はひとくちめ だるま'),
    ]),
    ('fukuoka_027', '別府站', '別府', 'fukuoka', 'minor', [
        ('https://www.tabirai.net/localinfo/article/article-48260', '別府今想吃的人氣美食11選'),
        ('https://gofunit.com/%E5%A4%A7%E5%88%86%E7%BE%8E%E9%A3%9F', '大分美食 豐後牛由布院美食'),
    ]),

    # OSAKA - Large
    ('osaka_station_030', '大阪上本町', '上本町', 'osaka', 'large', [
        ('https://tabelog.com/osaka/A2701/A270205/27013475/', '蛸八 上本品嘗燒老店'),
    ]),
    ('osaka_station_007', '京橋（JR）', '京橋', 'osaka', 'large', [
        ('https://manten-honten.com/', '萬てん 京橋店 鮮魚與日本料理'),
        ('https://www.magokorokomete302.com/entry/2025/09/13/063000', '肉ト串大眾酒場 一番手'),
    ]),
    ('osaka_station_033', '今宮（JR）', '今宮', 'osaka', 'large', [
        ('https://ke45500.gorp.jp/', '串銀杏 朝日 大阪新世界店'),
    ]),
    ('osaka_station_102', '佐野（JR）', '佐野', 'osaka', 'large', [
        ('https://visitizumisanojpn.com/zh/sanpei-zushi-cn', '三平寿司 泉佐野'),
        ('https://visitizumisanojpn.com/bbq-kaisenyakidokoro', '海鮮燒處 泉佐野漁協'),
        ('https://visitizumisanojpn.com/zh/osaka-local-cuisine-sora-izumisan-cno-station-store', '空 泉佐野站店'),
    ]),
    # OSAKA - Minor
    ('osaka_station_057', '北加賀屋', '北加賀屋', 'osaka', 'minor', [
        ('https://keb8600.gorp.jp/', '北加賀屋 1樓炸雞屋'),
        ('https://tabelog.com/osaka/A2701/A270406/27144209', '資さんうどん 南津守店'),
    ]),
    ('osaka_station_076', '北濱（京阪）', '北濱', 'osaka', 'minor', [
        ('https://retty.me/area/PRE27/LCAT1/CAT350', '大阪居酒屋20選'),
    ]),

    # TOKYO - Large
    ('tokyo_005', '上野站', '上野', 'tokyo', 'large', [
        ('https://tabelog.com/tokyo/A1311/A131101/13235000/', 'もつ焼 煮込み ヤリキ 上野本店'),
    ]),
    ('tokyo_001', '東京站', '丸之內', 'tokyo', 'large', [
        ('https://tabelog.com/tokyo/A1302/A130201/13279995/', 'PARLA 東京駅店'),
        ('https://tabelog.com/tokyo/A1302/A130201/13209818/', 'BAKE CHEESE TART 格拉娜斯塔丸之內店'),
    ]),
    ('tokyo_089', '下北澤站', '下北澤', 'tokyo', 'large', [
        ('https://tabelog.com/tokyo/A1318/A131802/13059050', 'ダッカールバー 下北澤'),
        ('https://tabelog.com/tokyo/A1318/A131802/13268193', 'ネオラル 下北澤站前店'),
        ('https://tabelog.com/tokyo/A1318/A131802/13085403', 'ステーキのくいしんぼ 下北澤店'),
    ]),
    ('tokyo_065', '五反田站', '五反田', 'tokyo', 'large', [
        ('https://tabelog.com/tokyo/A1316/A131603/13026345', '寿司 魚がし日本一 五反田店'),
    ]),
    ('tokyo_035', '九段下站', '九段下', 'tokyo', 'large', [
        ('https://tabelog.com/tokyo/A1309/A130906/R3470/rstLst/SC0101', '九段下站麵包店排行榜'),
    ]),
    # TOKYO - Minor
    ('tokyo_088', '三鷹站', '三鷹', 'tokyo', 'minor', [
        ('https://tabelog.com/tokyo/A1320/A132002/13010039', '韓食苑 恭楽亭 三鷹燒肉'),
        ('https://tabelog.com/tokyo/A1320/A132002/13084890', '酒と肴 磯や 三鷹居酒屋'),
    ]),
    ('tokyo_079', '中井站', '中井', 'tokyo', 'minor', [
        ('https://tabelog.com/tokyo/A1321/A132104/13198796', '大漁丼家 新宿中井站前店'),
        ('https://tabelog.com/tokyo/A1321/A132104/13144571', '日高屋 中井站前店'),
    ]),

    # OKINAWA - Large
    ('okinawa_station_020', '石川站', '中部', 'okinawa', 'large', [
        ('https://www.otv.co.jp/okitive/article/36896', 'うるま市午餐 在地人推薦'),
        ('https://tabelog.com/okinawa/C47213/C117379/rstLst', '石川 美食指南'),
        ('https://food.0star.net/kane.html', 'かね食堂 石川在地'),
    ]),
    ('okinawa_station_021', '嘉手納站', '中部', 'okinawa', 'large', [
        ('https://feeljapan.net/okinawa/article/2021-06-24-20990', '嘉手納町午餐推薦7選'),
        ('https://www.tanoshima.jp/facilities/detail/rotary_drive_in', 'ロータリードライブイン 嘉手納'),
    ]),
    ('okinawa_station_022', '北谷站', '中部', 'okinawa', 'large', [
        ('https://tabiiro.jp/gourmet/article/americanvillage-gourmet', '美國村周邊推薦餐廳12選'),
        ('https://www.okinawaclip.com/post/chatan-recommend', '北谷美食spot 10選'),
        ('https://ripplechatan.com/', 'RIPPLE北谷 WAGYU BAR'),
    ]),
    ('okinawa_station_023', '北谷Perry站', '中部', 'okinawa', 'large', [
        ('https://tabiiro.jp/gourmet/article/americanvillage-gourmet', '美國村周邊餐廳12選'),
        ('https://okinawa-labo.com/mexico-chatan-70269', '墨西哥 沖繩塔可餅老店'),
    ]),
    ('okinawa_station_024', '勝連城跡站', '中部', 'okinawa', 'large', [
        ('https://tabelog.com/lunch/okinawa/S7/S127486/COND-0-0-0-0-0-0', '勝連城跡周邊午餐排行'),
        ('https://www.otv.co.jp/okitive/article/36896', 'うるま市午餐推薦'),
    ]),
    # OKINAWA - Minor
    ('okinawa_station_025', '讀谷站', '中部', 'okinawa', 'minor', [
        ('https://okichong.com/majun-rikka/', '讀谷村 馬juna Libca 琉球創作料理'),
        ('https://tw.trip.com/moments/theme/destination-yomitan-60947-food-993052', '讀谷村美食推薦'),
        ('https://okinawaletsgojp.com/archives/780996', '讀谷村隱藏版沖繩料理店'),
    ]),
    ('okinawa_station_026', '恩納休憩所站', '中部', 'okinawa', 'minor', [
        ('https://i7tou.com/okinawa-onna-no-eki-nakayukui-market', '恩納之驛休憩市場 美食伴手禮'),
        ('https://auntie.tw/onnason-shabushabu', '恩納村 燦別邸 鳳梨阿古豬'),
        ('https://i7tou.com/okinawa-hama-no-ie-seafood-restaurant/', '浜之家海鮮料理 奶油烤魚海膽龍蝦'),
    ]),
    ('okinawa_station_027', '萬座毛站', '中部', 'okinawa', 'minor', [
        ('https://okinawaletsgojp.com/archives/780996', '萬座毛周邊美食 島豚屋 恩納本店'),
    ]),
    ('okinawa_station_029', '泡瀨站', '中部', 'okinawa', 'minor', [
        ('https://today.line.me/tw/v3/article/PM6P0l', '泡瀨漁港 中部魚市場'),
        ('https://www.klook.com/zh-TW/blog/okinawa-food', '沖繩必吃 迴轉壽司市場美浜店'),
    ]),
]

total_inserted = 0
stations_covered = []
seen_urls = set()

for station_id, station_name, zone, region, stype, foods in FOODS:
    inserted_this = 0
    for url, title in foods:
        if not url or not title or len(title) < 3:
            continue
        if url in seen_urls:
            continue
        if meal_exists(url):
            continue
        seen_urls.add(url)

        sub_cat = get_sub_category(title)
        base = short_id(title, region)
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
        except Exception as e:
            print(f"[ERROR] {meal_id}: {e}")

    if inserted_this > 0:
        print(f"  +{inserted_this} from {station_name}")

    total_inserted += inserted_this

print(f"\n{'='*55}")
print(f"  INSERTED: {total_inserted} meals")
print(f"  Stations covered: {len(set(stations_covered))}")
print(f"{'='*55}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for r in ['seoul', 'busan', 'fukuoka', 'osaka', 'tokyo', 'okinawa']:
    cur.execute("SELECT COUNT(*) FROM meals WHERE region_code=?", (r,))
    print(f"  {r}: {cur.fetchone()[0]} meals")
conn.close()
