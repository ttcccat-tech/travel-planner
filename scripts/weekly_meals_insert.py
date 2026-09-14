#!/usr/bin/env python3
"""Weekly station food insert script - 2026-09-14"""
import sqlite3
import json
import os

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

# Get existing URLs to avoid duplicates
def get_existing_urls(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, details FROM meals")
    existing = {}
    for row in cur.fetchall():
        meal_id, details_str = row
        if details_str:
            try:
                details = json.loads(details_str)
                url = details.get('blog_article', '')
                if url:
                    existing[url] = meal_id
            except:
                pass
    return existing

# Station ID mapping
STATION_IDS = {
    # Seoul
    'seoul-my': 'SE001', 'seoul-hk': 'SE002', 'seoul-gn': 'SE003',
    'seoul-ss': 'SE004', 'seoul-ys': 'SE005',
    # Busan
    'busan-sm': 'BS001', 'busan-np': 'BS002', 'busan-jg': 'BS003',
    'busan-hd': 'BS004', 'busan-gl': 'BS005',
    # Fukuoka
    'fukuoka-hk': 'FK001', 'fukuoka-tn': 'FK002', 'fukuoka-nk': 'FK003',
    'fukuoka-ks': 'FK004', 'fukuoka-dz': 'FK005',
    # Osaka
    'osaka-nb': 'OS001', 'osaka-um': 'OS002', 'osaka-ss': 'OS003',
    'osaka-tn': 'OS004', 'osaka-os': 'OS005',
    # Tokyo
    'tokyo-sj': 'TY001', 'tokyo-ue': 'TY002', 'tokyo-sb': 'TY003',
    'tokyo-tk': 'TY004', 'tokyo-ik': 'TY005',
    # Okinawa
    'okinawa-ch': 'OK001', 'okinawa-mk': 'OK002', 'okinawa-om': 'OK003',
    'okinawa-ak': 'OK004', 'okinawa-gr': 'OK005',
}

# Meals data: (region_code, station_key, name, name_en, sub_category, zone, description, blog_url, nearby_stations)
MEALS = [
    # ===================== SEOUL =====================
    # Myeongdong (明洞)
    ('seoul', 'seoul-my', '神仙雪濃湯明洞店', 'Shinsun Seolnongtang Myeongdong',
     'soup', '明洞', '牛骨熬煮乳白色清甜湯頭，搭配大顆蒸餃，米其林必比登推薦', 'https://www.funliday.com/posts/myungdong-seolnongtang', '424明洞站'),
    ('seoul', 'seoul-my', '明洞餃子', 'Myeongdong Kyoja',
     'noodle', '明洞', '米其林必比登推薦，手工刀削麵與蒸餃，湯頭濃郁', 'https://flyfishlife.tw/myeongdong-kyoja', '424明洞站'),
    ('seoul', 'seoul-my', 'BHC炸雞明洞店', 'BHC Chicken Myeongdong',
     'fried_chicken', '明洞', '全智賢代言，招牌香甜起司粉炸雞，24小時營業', 'https://nnyy.tw/seoul-tasty-food', '424明洞站'),
    ('seoul', 'seoul-my', '荒謬的生肉', 'Absurd Meat',
     'bbq', '明洞', '豬五花吃到飽，每人約台幣400元超高CP值', 'https://nnyy.tw/seoul-tasty-food', '424明洞站'),
    ('seoul', 'seoul-my', 'Isaac吐司明洞店', 'Isaac Toast Myeongdong',
     'breakfast', '明洞', '招牌排骨吐司，奶油吐司香脆，一個只要5000韓元', 'https://twopigsfun.com/myeongdong-food', '424明洞站'),
    ('seoul', 'seoul-my', '明洞鹹可頌麵包店', 'Fresh Bread Factory Myeongdong',
     'cafe', '明洞', '鹹可頌麵包出爐時間排隊名店，奶油香氣濃郁', 'https://twopigsfun.com/myeongdong-food', '424明洞站'),

    # Hongik (弘大)
    ('seoul', 'seoul-hk', '保承會館弘大店', 'Bosung Hoegwan Hongdae',
     'soup', '弘大', '24小時營業，馬鈴薯排骨湯與醒酒湯，宵夜首選', 'https://feitravel.tw/p-5070251291', '239弘大入口站'),
    ('seoul', 'seoul-hk', '李太祖脊骨土豆湯弘大店', 'Lee Taejo Gamjatang Hongdae',
     'soup', '弘大', '馬鈴薯排骨湯需兩人以上，醒酒湯可一人享用', 'https://feitravel.tw/p-5071141824', '239弘大入口站'),
    ('seoul', 'seoul-hk', '江南豬肉商會弘大店', 'Gangnam Pork Association Hongdae',
     'bbq', '弘大', '烤肉吃到飽，17,900韓元起七種肉類無限續', 'https://feitravel.tw/p-5071626555', '239弘大入口站'),
    ('seoul', 'seoul-hk', '一片里脊弘大店', 'Ilpyeon Daesin Hongdae',
     'bbq', '弘大', '21日低溫熟成1++韓牛，桌邊代烤服務', 'https://feitravel.tw/p-5070251291', '239弘大入口站'),
    ('seoul', 'seoul-hk', '胖胖豬頰肉弘大', 'Hongdae Tongtong Pork Cheek',
     'bbq', '弘大', '烤三層肉CP值高，烤腸與水芹菜一起烤', 'https://creatrip.com/zh-TW/blog/2351', '239弘大入口站'),
    ('seoul', 'seoul-hk', '豚壽百弘大店', 'Donsoo Baek Hongdae',
     'soup', '弘大', '24小時營業，傳統豬骨湯頭配各式配料', 'https://minako.tw/hongdae-food', '239弘大入口站'),
    ('seoul', 'seoul-hk', 'Egg Drop弘大店', 'Egg Drop Hongdae',
     'breakfast', '弘大', '蛋香濃郁份量多，蒜香培根三明治人氣', 'https://nnyy.tw/seoul-tasty-food', '239弘大入口站'),

    # Gangnam (江南)
    ('seoul', 'seoul-gn', '溫心屋', 'Onsimok',
     'soup', '江南', '牛排骨湯熬煮超過20小時，濃郁滋補', 'https://creatrip.com/zh-TW/blog/2043', '江南站'),
    ('seoul', 'seoul-gn', '全州食堂江南', 'Jeonju Sikdang Gangnam',
     'korean', '江南', '隱身CU便利商店旁地下室，CP值超高的韓食料理', 'https://creatrip.com/zh-TW/blog/2043', '江南站'),
    ('seoul', 'seoul-gn', '匠人辣炒雞江南店', 'Jangin Dakgalbi Gangnam',
     'spicy', '江南', '辣炒雞排兩人份24000韓元，加起司更美味', 'https://creatrip.com/zh-TW/blog/2043', '江南站'),
    ('seoul', 'seoul-gn', '味道人江南', 'Midoin Gangnam',
     'korean', '江南', '典雅裝潢情侶適用，擔擔麵與九菜飯桌', 'https://creatrip.com/zh-TW/blog/2043', '江南站'),
    ('seoul', 'seoul-gn', '江南真解酒', 'Gangnam Jinhaejang',
     'soup', '江南', '24小時營業，湯飯類與烤腸火鍋', 'https://creatrip.com/zh-TW/blog/2043', '江南站'),

    # Seoul Station (首爾站)
    ('seoul', 'seoul-ss', '龍山元祖馬鈴薯排骨湯', 'Yongsan Gamjatang Original',
     'soup', '首爾站', '24小時營業，辣味馬鈴薯排骨湯，經營20年老字號', 'https://www.kkday.com/zh-hk/blog/101575/seoul-station-food', '首爾站'),
    ('seoul', 'seoul-ss', '厚肉首爾站店', 'Dutum Seoul Station',
     'bbq', '首爾站', '熟成肉專門烤肉店，五花肉厚實多汁', 'https://www.kkday.com/zh-hk/blog/101575/seoul-station-food', '首爾站'),
    ('seoul', 'seoul-ss', '一隻雞刀切麵元祖家', 'Original Chicken Noodle',
     'soup', '首爾站', '白鍾元推介，一隻雞刀切麵經營三十多年', 'https://www.kkday.com/zh-hk/blog/101575/seoul-station-food', '首爾站'),
    ('seoul', 'seoul-ss', 'Ojeje炸豬扒首爾站', 'Ojeje Tonkatsu Seoul',
     'tonkatsu', '首爾站', '濟州島豬肉，炸豬扒配抹茶冷烏龍', 'https://www.kkday.com/zh-hk/blog/101575/seoul-station-food', '首爾站'),

    # Yongsan (龍山)
    ('seoul', 'seoul-ys', '陳玉華奶奶元祖一隻雞', 'Chen Yuhua One Chicken',
     'soup', '龍山', '蒜味雞湯濃郁軟嫩，最後加年糕或刀削麵', 'https://nnyy.tw/seoul-tasty-food', '龍山站'),
    ('seoul', 'seoul-ys', 'Myth豬腳小姐', 'Myth Jokbal',
     'bbq', '龍山', '經營超過30年老饕經典，蒜泥口味豬腳軟嫩', 'https://nnyy.tw/seoul-tasty-food', '龍山站'),
    ('seoul', 'seoul-ys', '橋村炸雞東廟店', 'Kyochon Chicken Dongmyo',
     'fried_chicken', '龍山', '神級炸雞，雙拼炸雞原味蒜香醬油', 'https://bobbytravel.tw/seoul-food', '東廟站'),

    # ===================== BUSAN =====================
    # Seomyeon (西面)
    ('busan', 'busan-sm', '味贊王鹽烤肉西面店', 'Matjaneul Salt Grilled Meat',
     'bbq', '西面', '3.5公分厚切五花肉，專人桌邊代烤', 'https://feitravel.tw/seoul-travel-guide-2026', '219西面站'),
    ('busan', 'busan-sm', '烤肉的男子西面店', 'Meat Grilling Man',
     'bbq', '西面', '桌邊代烤服務，點餐送螃蟹海鮮湯', 'https://feitravel.tw/seoul-travel-guide-2026', '219西面站'),
    ('busan', 'busan-sm', '水營本家豬肉湯飯西面店', 'Suengbon Pork Soup',
     'soup', '西面', '在地人也推薦的豬肉湯飯', 'https://feitravel.tw/seoul-travel-guide-2026', '219西面站'),
    ('busan', 'busan-sm', '乘槎包肉專門店', '乘槎',
     'bbq', '西面', '五花肉專門店', 'https://feitravel.tw/seoul-travel-guide-2026', '219西面站'),

    # Nampo (南浦)
    ('busan', 'busan-np', '南浦洞新昌洞咖啡', 'Nampodong Sinchangdong Coffee',
     'cafe', '南浦洞', '水蜜桃果昔、濟州芒果冰，水果甜點專賣', 'https://feitravel.tw/seoul-travel-guide-2026', '111南浦站'),
    ('busan', 'busan-np', '明星一隻雞', 'Myeongseong One Chicken',
     'soup', '南浦洞', '釜山一隻雞推薦，不辣食物長輩小孩適合', 'https://feitravel.tw/seoul-travel-guide-2026', '111南浦站'),
    ('busan', 'busan-np', 'BIFF廣場黑糖餅', 'BIFF Square Hotteok',
     'dessert', '南浦洞', '黑糖堅果煎餅，甜而不膩', 'https://feitravel.tw/seoul-travel-guide-2026', '111南浦站'),

    # Jungang (中央)
    ('busan', 'busan-jg', '富平罐頭市場炸豬排', 'Bupyeong Market Tonkatsu',
     'tonkatsu', '富平', '在地市場人氣店，超滿足沾醬炸豬排', 'https://feitravel.tw/seoul-travel-guide-2026', '中央站'),
    ('busan', 'busan-jg', '味名食堂', 'Mimyong Sikdang',
     'korean', '中央', '在地人推薦的傳統食堂', 'https://feitravel.tw/seoul-travel-guide-2026', '中央站'),

    # Haeundae (海雲台)
    ('busan', 'busan-hd', '密陽血腸豬肉湯飯海雲台店', 'Milnyang Sundae Pork Soup Haeundae',
     'soup', '海雲台', 'SJ始源也愛訪，24小時營業，濃郁湯頭', 'https://damei17.com/haeundae-food', '203海雲台站'),
    ('busan', 'busan-hd', '百年食堂海雲台店', 'Baeknyun Sikdang Haeundae',
     'bbq', '海雲台', '濟州火山岩烤五花肉，專人代烤', 'https://damei17.com/haeundae-food', '203海雲台站'),
    ('busan', 'busan-hd', '小香燉牛排骨海雲台店', 'Sochong Galbi Jjim Haeundae',
     'stew', '海雲台', '傳統韓式燉牛排骨48小時醃製，入口即化', 'https://couplehuang.com/sohyang_galbi_jjim', '203海雲台站'),
    ('busan', 'busan-hd', '秀國豬肉湯飯海雲台', 'Suguk Pork Soup Haeundae',
     'soup', '海雲台', '在地早餐推薦，豬肉湯飯不辣', 'https://feitravel.tw/seoul-travel-guide-2026', '203海雲台站'),
    ('busan', 'busan-hd', '風川灣淡水鰻魚海雲台', 'Pungcheon Eel',
     'seafood', '海雲台', '炭烤淡水鰻魚專業代烤，外酥內嫩', 'https://damei17.com/haeundae-food', '203海雲台站'),

    # Gwangalli (廣安里)
    ('busan', 'busan-gl', '青春酒館烤貝廣安店', 'Cheongchun Jokbal Gwangalli',
     'seafood', '廣安里', '海景第一排，無限供應烤貝酒場', 'https://feitravel.tw/seoul-travel-guide-2026', '廣安里站'),
    ('busan', 'busan-gl', '伍班長烤肉廣安店', 'Obanjang BBQ Gwangalli',
     'bbq', '廣安里', '炭火烤五花肉，肉質鮮嫩多汁', 'https://feitravel.tw/seoul-travel-guide-2026', '廣安里站'),

    # ===================== FUKUOKA =====================
    # Hakata (博多)
    ('fukuoka', 'fukuoka-hk', 'Shin-Shin博多拉麵', 'Shin-Shin Hakata Ramen',
     'ramen', '博多', '博多豚骨拉麵代表，純情拉麵乳白湯底', 'https://tasting-japan.com/archives/4975', 'JR博多站'),
    ('fukuoka', 'fukuoka-hk', 'Mikan and虎博多', 'MikanjIto Hakata',
     'ramen', '博多', '釜玉明太子烏龍麵，限量100碗', 'https://marukoblog.tw/2020-02-8.html', 'JR博多站'),
    ('fukuoka', 'fukuoka-hk', '博多牛腸鍋一鷹', 'HakataMotsunabe Ichitaka',
     'hotpot', '博多', '牛小腸Q彈，味噌醬油可選，最後加強棒麵', 'https://tasting-japan.com/archives/4975', 'JR博多站'),
    ('fukuoka', 'fukuoka-hk', '大山牛腸鍋博多', 'OoyamaMotsunabe Hakata',
     'hotpot', '博多', '100%牛小腸，KITTE博多9樓', 'https://tasting-japan.com/archives/4975', 'JR博多站'),
    ('fukuoka', 'fukuoka-hk', '雞皮長政博多店', 'Toripera Nagamasa Hakata',
     'yakitori', '博多', '雞皮串燒5天醃製，柚子醬爽口', 'https://tasting-japan.com/archives/4975', 'JR博多站'),

    # Tenjin (天神)
    ('fukuoka', 'fukuoka-tn', '玄界天神', 'Genkai Tenjin',
     'yakitori', '天神', '70年老字號路邊攤，天婦羅8品1000日圓', 'https://kyushu.letsgojp.com/archives/603822', '天神站'),
    ('fukuoka', 'fukuoka-tn', ' Chabakaya 九州路的麵店', 'Chabakaya',
     'noodle', '天神', '烏龍麵', 'https://kyushu.letsgojp.com/archives/603822', '天神站'),
    ('fukuoka', 'fukuoka-tn', '味藏天牛', 'Ajikuraya',
     'bbq', '天神', '自由組合配料大阪燒，20種以上選擇', 'https://kyushu.letsgojp.com/archives/603822', '天神站'),

    # Nakasu (中洲川端)
    ('fukuoka', 'fukuoka-nk', '屋台路地酒場', 'Yatai Roji Sakaba',
     'izakaya', '中洲', '屋台小酌文化，炭烤海鮮串燒', 'https://tasting-japan.com/archives/5892', '中洲川端站'),
    ('fukuoka', 'fukuoka-nk', '中洲魚河岸', 'Nakasu Uogashi',
     'sushi', '中洲', '新鮮海產代客料理', 'https://tasting-japan.com/archives/5892', '中洲川端站'),

    # Kashii (香椎)
    ('fukuoka', 'fukuoka-ks', '香椎燒鳥', 'Kashii Yakitori',
     'yakitori', '香椎', '在地串燒專門店', 'https://tasting-japan.com/archives/5892', '香椎站'),

    # Dazaifu (太宰府)
    ('fukuoka', 'fukuoka-dz', '太宰府拉麵', 'Dazaifu Ramen',
     'ramen', '太宰府', '太宰府名物拉麵', 'https://tasting-japan.com/archives/5892', '太宰府站'),

    # ===================== OSAKA =====================
    # Namba (難波)
    ('osaka', 'osaka-nb', '一蘭拉麵道頓堀店', 'Ichiran Dotonbori',
     'ramen', '難波', '豚骨拉麵一人包廂，自動販賣機點餐', 'https://suni.tw/osaka-food', '南海難波站'),
    ('osaka', 'osaka-nb', '神座拉麵道頓堀店', 'Kamukura Dotonbori',
     'ramen', '難波', '加入大量白菜的清爽湯頭，24小時', 'https://minako.tw/shinsaibashisuji-japan', '難波站'),
    ('osaka', 'osaka-nb', '福太郎大阪燒', 'Fukutarou Okonomiyaki',
     'okonomiyaki', '難波', '1945年創立，蔥燒與麻糬起司最人氣', 'https://minako.tw/shinsaibashisuji-japan', '南海難波站'),
    ('osaka', 'osaka-nb', '新世界第一牧志公設市場', 'Daiichi Makishi Market',
     'seafood', '難波', '代客料理服務，新鮮海產', 'https://we4-travel.com/naha-lucky-maximum', '牧志站'),
    ('osaka', 'osaka-nb', '牛かつもと村炸牛排', 'Ushikatsu Motomura',
     'tonkatsu', '難波', '外酥內嫩炸牛排，飯糰套餐推薦', 'https://minako.tw/shinsaibashisuji-japan', '南海難波站'),
    ('osaka', 'osaka-nb', 'MooKEN泡芙', 'MooKEN Puff',
     'dessert', '難波', '脆皮綿密卡士達醬，每日售完為止', 'https://minako.tw/shinsaibashisuji-japan', '難波站'),

    # Umeda (梅田)
    ('osaka', 'osaka-um', 'KIP Bisteak 牛排', 'KIP Bisteak',
     'steak', '梅田', '時尚牛排店', 'https://suni.tw/osaka-food', '大阪站'),
    ('osaka', 'osaka-um', '大阪王將餃子', 'Ohsho Umeda',
     'gyoza', '梅田', '天津飯與煎餃代表', 'https://suni.tw/osaka-food', '大阪站'),
    ('osaka', 'osaka-um', '北極星蛋包飯', 'Kitokitobu Omurice',
     'omrice', '梅田', '蛋包飯老字號', 'https://suni.tw/osaka-food', '大阪站'),

    # Shinsaibashi (心齋橋)
    ('osaka', 'osaka-ss', 'PAUL祕密酒館', 'Paul Shuinsen',
     'izakaya', '心齋橋', '時尚居酒屋', 'https://suni.tw/osaka-food', '心齋橋站'),
    ('osaka', 'osaka-ss', '河崎燒鳥', 'Kawazaki Yakitori',
     'yakitori', '心齋橋', '在地串燒名店', 'https://suni.tw/osaka-food', '心齋橋站'),

    # Tennoji (天王寺)
    ('osaka', 'osaka-tn', '四天王拉麵天王寺店', 'Shitenno Ramen Tennoji',
     'ramen', '天王寺', '豚骨拉麵名店', 'https://suni.tw/osaka-food', '天王寺站'),
    ('osaka', 'osaka-tn', '串かつ大叫', 'Kushikatsu Daisuke',
     'kushikatsu', '天王寺', '酥脆炸串專門店', 'https://suni.tw/osaka-food', '天王寺站'),

    # Osaka Station (大阪站)
    ('osaka', 'osaka-os', 'GRILLemon UP牛排館', 'GRILLemon UP',
     'steak', '大阪站', '時尚牛排套餐', 'https://suni.tw/osaka-food', '大阪站'),
    ('osaka', 'osaka-os', '北極星蛋包飯OS', 'Kitokitobu Omurice OS',
     'omrice', '大阪站', '經典蛋包飯', 'https://suni.tw/osaka-food', '大阪站'),

    # ===================== TOKYO =====================
    # Shinjuku (新宿)
    ('tokyo', 'tokyo-sj', '情的專業火鍋', 'Jonetsu Shinjuku',
     'hotpot', '新宿', '精品火鍋專門', 'https://tw.savorjapan.com/contents/discover-oishii-japan/10-nabe-restaurants-in-tokyo-s-major-shopping-areas-shinjuku-shibuya-and-ikebukuro', '新宿站'),
    ('tokyo', 'tokyo-sj', '海底撈火鍋新宿店', 'Haidilao Shinjuku',
     'hotpot', '新宿', '四色鍋服務周到，包廂適合聚會', 'https://tw.savorjapan.com/contents/discover-oishii-japan/10-nabe-restaurants-in-tokyo-s-major-shopping-areas-shinjuku-shibuya-and-ikebukuro', '新宿站'),

    # Ueno (上野)
    ('tokyo', 'tokyo-ue', '鰻割烹伊勢榮上野本店', 'Ueno Isei Honten',
     'unagi', '上野', '270年歷史鰻魚老店，關東風蒲燒', 'https://www.esquirehk.com/lifestyle/tokyo-ueno-best-restaurant-recommandation', 'JR上野站'),
    ('tokyo', 'tokyo-ue', '拉麵鴨to蔥', 'Ramen Kamo to Negi',
     'ramen', '上野', '清湯鴨肉拉麵，24小時營業', 'https://www.esquirehk.com/lifestyle/tokyo-ueno-best-restaurant-recommandation', 'JR上野站'),
    ('tokyo', 'tokyo-ue', 'Ponta本家炸豬排', 'Ponta Honke Tonkatsu',
     'tonkatsu', '上野', '米其林必比登，1905年炸肉排元祖', 'https://omakaseje.com/zh-tw/articles/iu662555', '上野廣小路站'),
    ('tokyo', 'tokyo-ue', '鳥惠燒鳥上野廣小路店', 'Torie Ueno Hiro Koji',
     'yakitori', '上野', '米其林必比登，黑薩摩雞與大山雞', 'https://omakaseje.com/zh-tw/articles/iu662555', '上野廣小路站'),
    ('tokyo', 'tokyo-ue', '天婦羅深川', 'Tempura Fukutaro',
     'tempura', '上野', '根津預約制天婦羅百大名店', 'https://omakaseje.com/zh-tw/articles/iu662555', '根津站'),

    # Shibuya (澀谷)
    ('tokyo', 'tokyo-sb', 'Log理dam Grill牛排館', 'Rod Rob',
     'steak', '澀谷', '時尚牛排套餐', 'https://omakaseje.com/zh-tw/articles/ne999642', '澀谷站'),
    ('tokyo', 'tokyo-sb', 'AFURI阿夫利拉麵澀谷店', 'AFURI Shibuya',
     'ramen', '澀谷', '柚子鹽拉麵清爽系', 'https://omakaseje.com/zh-tw/articles/ne999642', '澀谷站'),
    ('tokyo', 'tokyo-sb', '銀杏火化學', 'Ginkgo',
     'kaiseki', '澀谷', '時尚日本料理', 'https://omakaseje.com/zh-tw/articles/ne999642', '澀谷站'),

    # Tokyo Station (東京站)
    ('tokyo', 'tokyo-tk', '東京站一番街拉麵', 'Tokyo Station Ichiban',
     'ramen', '東京站', '車站地下街拉麵名店', 'https://omakaseje.com/zh-tw/articles/ne999642', '東京站'),
    ('tokyo', 'tokyo-tk', '東京站燒肉', 'Tokyo Station Yakiniku',
     'bbq', '東京站', '車站周邊優質燒肉', 'https://omakaseje.com/zh-tw/articles/ne999642', '東京站'),
    ('tokyo', 'tokyo-tk', '東京站壽司', 'Tokyo Station Sushi',
     'sushi', '東京站', '豐洲市場直送', 'https://omakaseje.com/zh-tw/articles/ne999642', '東京站'),

    # Ikebukuro (池袋)
    ('tokyo', 'tokyo-ik', ' 無敵家拉麵', 'Mutekiya Ramen',
     'ramen', '池袋', '豚骨叉燒拉麵，肥瘦均勻', 'https://omakaseje.com/zh-tw/articles/ne999642', '池袋站'),
    ('tokyo', 'tokyo-ik', 'Maid Fresh Parlor', 'Maid Fresh Parlor',
     'cafe', '池袋', '女僕主題咖啡', 'https://omakaseje.com/zh-tw/articles/ne999642', '池袋站'),
    ('tokyo', 'tokyo-ik', 'SPICE COURT 中華', 'Spice Court',
     'chinese', '池袋', '池袋東武百貨內', 'https://omakaseje.com/zh-tw/articles/ne999642', '池袋站'),

    # ===================== OKINAWA =====================
    # Kenchomae (縣廳前)
    ('okinawa', 'okinawa-ch', '琉球料理ふる里縣廳前', 'Ryukyu Furusato Kenchomae',
     'ryukyu', '縣廳前', 'RYUBO百貨地下街，琉球傳統料理', 'https://dorapig.com/furusato-okinawa', '縣廳前站'),
    ('okinawa', 'okinawa-ch', '傑克牛排館', 'Jack Steak House',
     'steak', '縣廳前', '昭和風正統派炸牛排', 'https://tasting-japan.com/archives/4071', '旭橋站'),
    ('okinawa', 'okinawa-ch', '琉美食堂', 'Ryumi Shokudo',
     'okinawa', '縣廳前', '沖繩家庭料理', 'https://tasting-japan.com/archives/4071', '縣廳前站'),

    # Makishi (牧志)
    ('okinawa', 'okinawa-mk', '第一牧志公設市場', 'Daiichi Makishi Public Market',
     'seafood', '牧志', '代客料理服務，海產與和牛', 'https://we4-travel.com/naha-lucky-maximum', '牧志站'),
    ('okinawa', 'okinawa-mk', 'Lucky Maximum居酒屋', 'Lucky Maximum',
     'izakaya', '牧志', '氣氛佳食物好，創意居酒屋', 'https://we4-travel.com/naha-lucky-maximum', '牧志站'),
    ('okinawa', 'okinawa-mk', '暖暮拉麵牧志店', 'Danburu Ramen',
     'ramen', '牧志', '豚骨拉麵名店', 'https://we4-travel.com/naha-lucky-maximum', '牧志站'),

    # Omoromachi (おもろま)
    ('okinawa', 'okinawa-om', 'Hohobare和牛牛排', 'Hohobare Wagyu Steak',
     'steak', 'おもろま', '米其林姊妹店，高級酥烤牛排', 'https://tasting-japan.com/archives/4071', 'おもろま站'),
    ('okinawa', 'okinawa-om', '鐵板燒澤藤', 'Teppanyaki Sawahito',
     'steak', 'おもろま', '石垣牛排經典', 'https://tasting-japan.com/archives/4071', 'おもろま站'),
    ('okinawa', 'okinawa-om', '琉食久茂地店', 'Ryushoku Kumojichi',
     'okinawa', 'おもろま', '阿古豬涮涮鍋與七輪燒肉', 'https://tasting-japan.com/archives/4071', 'おもろま站'),

    # Akamine (赤嶺)
    ('okinawa', 'okinawa-ak', '海邦丸海鮮', 'Uihomaru Seafood',
     'seafood', '赤嶺', '新鮮海產直送', 'https://tasting-japan.com/archives/4071', '赤嶺站'),
    ('okinawa', 'okinawa-ak', '北谷製麵', 'Hokuten Seimen',
     'noodle', '赤嶺', '沖繩麵專門', 'https://tasting-japan.com/archives/4071', '赤嶺站'),

    # Geruma (儀津)
    ('okinawa', 'okinawa-gr', '山原新鮮組', 'Yamaha Fresh Group',
     'seafood', '儀津', '北部海鮮推薦', 'https://tasting-japan.com/archives/4071', '儀津站'),
    ('okinawa', 'okinawa-gr', '美麗海水族館周邊美食', 'Churaumi Adjacent',
     'seafood', '儀津', '海鮮料理', 'https://tasting-japan.com/archives/4071', '儀津站'),
]

def generate_id(region_code, name):
    # Simple hash-based ID
    import hashlib
    key = f"{region_code}:{name}"
    return hashlib.md5(key.encode()).hexdigest()[:12].upper()

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    existing_urls = get_existing_urls(conn)
    print(f"Existing meals with URLs: {len(existing_urls)}")
    
    inserted = 0
    skipped = 0
    
    for (region_code, station_key, name, name_en, sub_category, zone, description, blog_url, nearby_stations) in MEALS:
        if blog_url in existing_urls:
            skipped += 1
            continue
        
        meal_id = generate_id(region_code, name)
        station_id = STATION_IDS.get(station_key, station_key)
        
        details = json.dumps({"blog_article": blog_url})
        sources = json.dumps([blog_url])
        tags = json.dumps([sub_category, region_code])
        
        try:
            cur.execute("""
                INSERT INTO meals (id, region_code, station_id, name, name_en, category, sub_category, zone, 
                                location, description, sources, details, tags, nearby_stations, priority)
                VALUES (?, ?, ?, ?, ?, 'meal', ?, ?, ?, ?, ?, ?, ?, ?, 3)
            """, (meal_id, region_code, station_id, name, name_en, sub_category, zone, zone,
                  description, sources, details, tags, nearby_stations))
            inserted += 1
        except Exception as e:
            print(f"Error inserting {name}: {e}")
    
    conn.commit()
    
    # Final count
    cur.execute("SELECT COUNT(*) FROM meals WHERE category = 'meal'")
    total = cur.fetchone()[0]
    
    print(f"\n=== Summary ===")
    print(f"Inserted: {inserted}")
    print(f"Skipped (duplicate): {skipped}")
    print(f"Total meals in DB: {total}")
    
    conn.close()

if __name__ == '__main__':
    main()
