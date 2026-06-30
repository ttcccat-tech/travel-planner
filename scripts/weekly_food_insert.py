#!/usr/bin/env python3
import sqlite3, json

conn = sqlite3.connect('/var/repo/travel-planner/backend/travel.db')
cur = conn.cursor()

# Clear wrongly-inserted meals (with station IDs as region_code)
cur.execute("DELETE FROM meals")
conn.commit()
print("Cleared meals table")

def fix_region(station_id):
    if station_id.startswith('seoul'): return 'seoul'
    elif station_id.startswith('busan'): return 'busan'
    elif station_id.startswith('fukuoka'): return 'fukuoka'
    elif station_id.startswith('osaka'): return 'osaka'
    elif station_id.startswith('tokyo'): return 'tokyo'
    elif station_id.startswith('okinawa'): return 'okinawa'
    return station_id

def do_insert(meal):
    region_code = fix_region(meal["station"])
    sources = json.dumps([meal["url"]])
    details = json.dumps({"blog_article": meal["url"], "google_maps": "", "youtube": ""})
    tags_j = json.dumps(meal.get("tags", []))
    try:
        cur.execute("""
            INSERT INTO meals
              (id, region_code, station_id, name, name_en, category, sub_category,
               zone, location, ticket, stay_duration, need_reservation, cash_only,
               priority, tags, description, sources, nearby_stations, details)
            VALUES (?,?,?,?,?,'meal',?,?,?,?,?,0,0,?,?,?,?,json('[]'),?)
        """, (meal["id"], region_code, meal["station"], meal["name"], meal["name_en"],
              meal["sub_cat"], meal["zone"], meal["location"], meal["ticket"], meal["stay"],
              meal["priority"], tags_j, meal["desc"], sources, details))
        return True
    except Exception as e:
        print(f"  SKIP {meal['name']}: {e}")
        return False

all_data = [
    {"id":"sm_001","station":"seoul_001","name":"FOCAL POINT","name_en":"FOCAL POINT","sub_cat":"咖啡","zone":"龍山","location":"387 Cheongpa-ro, Yongsan-gu, Seoul","ticket":"免費參觀","stay":"1小時","desc":"米其林認證休閒餐廳，3層樓空間，以精緻鹹甜派聞名，設有免費美式咖啡優惠。","tags":["咖啡","甜點","派"],"priority":3,"url":"https://creatrip.com/zh-TW/blog/963"},
    {"id":"sm_002","station":"seoul_001","name":"湖水家","name_en":"Hosujip","sub_cat":"小吃","zone":"龍山","location":"443 Cheongpa-ro, Jung-gu, Seoul","ticket":"免費參觀","stay":"1小時","desc":"1986年開業，首爾站周邊知名本地店，以辣炒雞湯和烤肉串聞名。","tags":["辣炒雞","燒烤","在地"],"priority":3,"url":"https://creatrip.com/zh-TW/blog/963"},
    {"id":"sm_003","station":"seoul_001","name":"厚肉","name_en":"Dutum","sub_cat":"燒肉","zone":"龍山","location":"10 Jungnim-ro, Jung-gu, Seoul","ticket":"付費","stay":"1.5小時","desc":"以厚切五花肉聞名的烤肉名店，傳統韓式烤肉環境，肉質多汁。","tags":["烤肉","五花肉","高級"],"priority":2,"url":"https://creatrip.com/zh-TW/blog/963"},
    {"id":"sm_004","station":"seoul_001","name":"囕盈豚","name_en":"Namyoungdon","sub_cat":"燒肉","zone":"龍山","location":"17 Hangang-daero 80-gil, Yongsan-gu, Seoul","ticket":"付費","stay":"1.5小時","desc":"韓國三大烤肉名店之一，永遠排隊，炭火烤肉香氣四溢。","tags":["烤肉","炭火","排隊名店"],"priority":2,"url":"https://creatrip.com/zh-TW/blog/963"},
    {"id":"sm_005","station":"seoul_001","name":"國民會館","name_en":"Gukminhoegwan","sub_cat":"燒肉","zone":"龍山","location":"209-2 Mallijae-ro, Jung-gu, Seoul","ticket":"付費","stay":"1.5小時","desc":"以冷凍薄切五花肉聞名的復古烤肉店，是韓劇拍攝地。","tags":["烤肉","五花肉","打卡"],"priority":3,"url":"https://creatrip.com/zh-TW/blog/963"},
    {"id":"sm_006","station":"seoul_004","name":"申美京辣炒雞","name_en":"Shinmigyeong","sub_cat":"小吃","zone":"麻浦","location":"首爾麻浦區延南洞","ticket":"免費參觀","stay":"1小時","desc":"弘大知名辣炒雞排店，份量足、口味辣而香。","tags":["辣炒雞","小吃","弘大"],"priority":3,"url":"https://bobbytravel.tw/hongdae/"},
    {"id":"sm_007","station":"seoul_004","name":"FUHAHA 奶油麵包","name_en":"FUHAHA","sub_cat":"咖啡","zone":"麻浦","location":"首爾麻浦區弘大","ticket":"免費參觀","stay":"30分鐘","desc":"弘大超人氣奶油麵包店，外酥內軟，奶油香甜而不膩。","tags":["咖啡","甜點","麵包"],"priority":3,"url":"https://tisshuang.com/blog/post/hongdaefoods"},
    {"id":"sm_008","station":"seoul_004","name":"延南洞墨西哥炸雞","name_en":"Yeonnam Mexican Chicken","sub_cat":"小吃","zone":"麻浦","location":"首爾麻浦區延南洞","ticket":"免費參觀","stay":"1小時","desc":"弘大延南洞創意墨西哥炸雞，結合美式與韓式口味。","tags":["炸雞","創意","延南洞"],"priority":3,"url":"https://bobbytravel.tw/hongdae/"},
    {"id":"sm_009","station":"seoul_004","name":"一片里脊","name_en":"Ilpyeon","sub_cat":"燒肉","zone":"麻浦","location":"首爾麻浦區弘大","ticket":"付費","stay":"1.5小時","desc":"弘大烤肉店，以特選里肌肉片稱名，肉質軟嫩。","tags":["烤肉","里肌肉","弘大"],"priority":3,"url":"https://feitravel.tw/hongdae-best-food-guide/"},
    {"id":"sm_010","station":"seoul_004","name":"橋村炸雞 弘大總店","name_en":"Kyochon Hongdae","sub_cat":"小吃","zone":"麻浦","location":"首爾麻浦區弘大","ticket":"付費","stay":"1小時","desc":"韓國代表性炸雞品牌，弘大總店人氣最旺，蜂蜜炸雞經典必吃。","tags":["炸雞","蜂蜜","連鎖"],"priority":3,"url":"https://bobbytravel.tw/hongdae/"},
    {"id":"bm_001","station":"busan_001","name":"釜田市場奶奶大飯店","name_en":"Busanje","sub_cat":"小吃","zone":"中央區","location":"釜山中區釜田洞","ticket":"免費參觀","stay":"1小時","desc":"釜山站附近傳統市場美食，價格實惠，在地人情味浓厚。","tags":["小吃","市場","中央區"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"bm_002","station":"busan_035","name":"西面辣炒年糕","name_en":"Seomyeon Tteokbokki","sub_cat":"小吃","zone":"西面","location":"釜山西面區","ticket":"免費參觀","stay":"30分鐘","desc":"西面站附近辣炒年糕小吃攤，辣甜口味正宗當地小吃。","tags":["辣炒年糕","小吃","西面"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"bm_003","station":"busan_018","name":"德川站隱藏版美食","name_en":"Deokcheon Hidden","sub_cat":"餐廳","zone":"北區","location":"釜山北區德川站周邊","ticket":"付費","stay":"1小時","desc":"德川站周邊隱藏版在地餐廳，適合深度探索釜山的旅人。","tags":["在地","隱藏","北區"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"fm_001","station":"fukuoka_001","name":"博多一幸舍 總本店","name_en":"Hakata Issho","sub_cat":"拉麵","zone":"博多","location":"福岡縣福岡市博多區車站前","ticket":"約800-1000日圓","stay":"1小時","desc":"博多豚骨拉麵名店，濃郁豚骨湯頭配細麵，是博多拉麵代表。","tags":["拉麵","豚骨","博多"],"priority":2,"url":"https://kyushu.letsgojp.com/archives/340790/"},
    {"id":"fm_002","station":"fukuoka_001","name":"元祖博多達摩 DEITOS店","name_en":"Genzo Hakata Daruma","sub_cat":"小吃","zone":"博多","location":"福岡縣福岡市博多區博多站","ticket":"約500日圓","stay":"30分鐘","desc":"博多站人氣小吃，以明太子料理聞名，是福岡必吃美食之一。","tags":["明太子","小吃","博多"],"priority":3,"url":"https://kyushu.letsgojp.com/archives/340790/"},
    {"id":"fm_003","station":"fukuoka_001","name":"牛腸鍋 道后","name_en":"Motsunabe Dohgo","sub_cat":"餐廳","zone":"博多","location":"福岡縣福岡市博多區","ticket":"約1500-2000日圓","stay":"1.5小時","desc":"福岡特色牛腸鍋，以牛小腸和高麗菜、蒜頭燉煮，冬季進補首選。","tags":["牛腸鍋","火鍋","博多"],"priority":3,"url":"https://vivianexplore.tw/fukuoka-travel/"},
    {"id":"fm_004","station":"fukuoka_004","name":"力飯店","name_en":"Rikihanten","sub_cat":"燒肉","zone":"天神","location":"福岡縣福岡市中央區天神","ticket":"約3000-5000日圓","stay":"1.5小時","desc":"米其林推薦燒肉店，專注瘦肉口感，選用國產牛及羊肉。","tags":["燒肉","米其林","天神"],"priority":2,"url":"https://omakaseje.com/zh-tw/articles/ub230860"},
    {"id":"fm_005","station":"fukuoka_004","name":"COWSI 燒肉","name_en":"Yakiniku COWSI","sub_cat":"燒肉","zone":"天神","location":"福岡縣福岡市中央區天神","ticket":"約2000-4000日圓","stay":"1.5小時","desc":"使用九州A5和牛與1-2個月熟成長達人的頂級燒肉店。","tags":["燒肉","A5和牛","天神"],"priority":2,"url":"https://omakaseje.com/zh-tw/articles/ub230860"},
    {"id":"fm_006","station":"fukuoka_041","name":"小倉燒肉","name_en":"Kokura Yakiniku","sub_cat":"燒肉","zone":"小倉","location":"福岡縣北九州市小倉區小倉站周邊","ticket":"約2000-3000日圓","stay":"1.5小時","desc":"小倉站周邊燒肉名店，份量實在，適合小倉觀光客。","tags":["燒肉","小倉"],"priority":3,"url":"https://omakaseje.com/zh-tw/articles/ub230860"},
    {"id":"om_001","station":"osaka_station_001","name":"Udon Kisuke 烏龍麵","name_en":"Udon Kisuke","sub_cat":"麵食","zone":"梅田","location":"大阪縣大阪市北區","ticket":"約800-1200日圓","stay":"1小時","desc":"米其林指南認證手打烏龍麵名店，釜玉烏龍麵是招牌，必排隊1小時。","tags":["烏龍麵","米其林","排隊"],"priority":2,"url":"https://gowithmarkhazyl.com/osaka-food-guide/"},
    {"id":"om_002","station":"osaka_station_001","name":"Moritaya 壽喜燒","name_en":"Moritaya","sub_cat":"燒肉","zone":"梅田","location":"大阪縣大阪市北區","ticket":"約3000-5000日圓","stay":"1.5小時","desc":"百年歷史和牛專賣店，嚴選A4-A5等級近江牛、黑毛和牛。","tags":["壽喜燒","和牛","百年老店"],"priority":2,"url":"https://gowithmarkhazyl.com/osaka-food-guide/"},
    {"id":"om_003","station":"osaka_station_001","name":"大阪王將 梅田","name_en":"Osaka Ohsho Umeda","sub_cat":"小吃","zone":"梅田","location":"大阪縣大阪市北區","ticket":"約600-1000日圓","stay":"45分鐘","desc":"大阪知名中華料理連鎖，煎餃和天津飯是招牌。","tags":["煎餃","中華","連鎖"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"om_004","station":"osaka_station_014","name":"蟹善","name_en":"Kani Zen","sub_cat":"餐廳","zone":"難波","location":"大阪縣大阪市中央區道頓堀","ticket":"約5000-10000日圓","stay":"1.5小時","desc":"螃蟹料理專賣店，嚴選北海道及日本各地松葉蟹、毛蟹。","tags":["螃蟹","海鮮","高級"],"priority":2,"url":"https://gowithmarkhazyl.com/osaka-food-guide/"},
    {"id":"om_005","station":"osaka_station_014","name":"達摩串炸 道頓堀店","name_en":"Daruma Kushikatsu","sub_cat":"小吃","zone":"難波","location":"大阪縣大阪市中央區道頓堀1-6-8","ticket":"約300-600日圓","stay":"45分鐘","desc":"大阪100年老字號串炸名店，秘製醬汁是最大特色。","tags":["串炸","大阪燒","百年老店"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"om_006","station":"osaka_station_014","name":"PABLO 半熟起司蛋糕","name_en":"PABLO","sub_cat":"甜點","zone":"難波","location":"大阪縣大阪市中央區道頓堀","ticket":"約800日圓","stay":"30分鐘","desc":"大阪知名半熟起司蛋糕，外酥內軟，薄脆外皮是特徵。","tags":["甜點","起司蛋糕","排隊"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"om_007","station":"osaka_station_003","name":"通天閣食堂","name_en":"Tsutenkaku Shokudo","sub_cat":"小吃","zone":"天王寺","location":"大阪縣大阪市浪速區惠美須町","ticket":"約500-1000日圓","stay":"1小時","desc":"通天閣周邊平價美食，串燒和御好燒是代表。","tags":["小吃","大阪燒","通天閣"],"priority":3,"url":"https://bobbytravel.tw/osaka-food/"},
    {"id":"om_008","station":"osaka_station_014","name":"咲藏燒肉","name_en":"Sakugura","sub_cat":"燒肉","zone":"難波","location":"大阪縣大阪市中央區","ticket":"約3000-5000日圓","stay":"1.5小時","desc":"心齋橋超人氣燒肉店，與排隊名店齊名，適合肉食愛好者。","tags":["燒肉","心齋橋"],"priority":3,"url":"https://gowithmarkhazyl.com/osaka-food-guide/"},
    {"id":"tm_001","station":"tokyo_001","name":"六厘舍沾麵","name_en":"Rokurinsha","sub_cat":"拉麵","zone":"丸之內","location":"東京站一番街拉麵街","ticket":"約900-1200日圓","stay":"1小時","desc":"東京站人氣沾麵店，粗麵條配濃郁魚介豚骨湯是招牌。","tags":["拉麵","沾麵","東京站"],"priority":2,"url":"https://bobbytravel.tw/tokyo-station/"},
    {"id":"tm_002","station":"tokyo_001","name":"斑鳩拉麵","name_en":"Kamogata","sub_cat":"拉麵","zone":"丸之內","location":"東京站一番街","ticket":"約900-1200日圓","stay":"1小時","desc":"以魚介豚骨湯聞名的拉麵店，湯頭濃郁不油膩。","tags":["拉麵","魚介","東京站"],"priority":2,"url":"https://bobbytravel.tw/tokyo-station/"},
    {"id":"tm_003","station":"tokyo_001","name":"矢場豬排","name_en":"Yabaten","sub_cat":"豬排","zone":"丸之內","location":"東京站一番街","ticket":"約1000-1500日圓","stay":"1小時","desc":"名古屋知名豬排飯連鎖，外酥內嫩，醬汁是最大特色。","tags":["豬排","名古屋","東京站"],"priority":3,"url":"https://bobbytravel.tw/tokyo-station/"},
    {"id":"tm_004","station":"tokyo_002","name":"新宿燒肉","name_en":"Shinjuku Yakiniku","sub_cat":"燒肉","zone":"新宿","location":"東京新宿區","ticket":"約3000-5000日圓","stay":"1.5小時","desc":"新宿知名燒肉店，和牛品質佳，適合肉食愛好者。","tags":["燒肉","和牛","新宿"],"priority":2,"url":"https://tokyo.letsgojp.com/archives/601864/"},
    {"id":"tm_005","station":"tokyo_002","name":"思い出食堂 新宿","name_en":"Omoide Shokudo","sub_cat":"小吃","zone":"新宿","location":"東京新宿區","ticket":"約500-800日圓","stay":"45分鐘","desc":"新宿伊勢丹附近平價小吃，份量足、價格實惠。","tags":["小吃","平價","新宿"],"priority":3,"url":"https://tokyo.letsgojp.com/archives/601864/"},
    {"id":"tm_006","station":"tokyo_004","name":"麵屋 Hulu-lu","name_en":"Menya Hulu-lu","sub_cat":"拉麵","zone":"池袋","location":"東京池袋西口","ticket":"約800-1200日圓","stay":"1小時","desc":"池袋隱藏版拉麵店，顛覆傳統拉麵印象，湯頭濃郁。","tags":["拉麵","隱藏","池袋"],"priority":3,"url":"https://www.japaholic.com/tw/article/detail/522679"},
    {"id":"tm_007","station":"tokyo_004","name":"叙叙苑 池袋","name_en":"Jojohongu","sub_cat":"燒肉","zone":"池袋","location":"東京池袋","ticket":"約3000-6000日圓","stay":"1.5小時","desc":"東京知名燒肉連鎖，午餐時段超值，適合情侶和家庭。","tags":["燒肉","連鎖","池袋"],"priority":2,"url":"https://tokyo.letsgojp.com/archives/601864/"},
    {"id":"om_ia001","station":"okinawa_station_001","name":"暖暮拉麵 牧志店","name_en":"Danbo Makishi","sub_cat":"拉麵","zone":"那霸","location":"那霸市牧志2-16-10","ticket":"約700-900日圓","stay":"1小時","desc":"曾擊敗一蘭的九州拉麵冠軍，九州豚骨拉麵代表，國際通附近。","tags":["拉麵","九州","冠軍"],"priority":2,"url":"https://bobbytravel.tw/kokusai-street/"},
    {"id":"om_ia002","station":"okinawa_station_001","name":"琉家拉麵","name_en":"Ryukariya","sub_cat":"拉麵","zone":"那霸","location":"那霸市松尾1-6-8","ticket":"約680-850日圓","stay":"1小時","desc":"招牌琉焦蒜豬骨拉麵黑湯頭，蒜香濃郁、麵體Q彈，在地人氣高。","tags":["拉麵","蒜香","那霸"],"priority":3,"url":"https://bobbytravel.tw/kokusai-street/"},
    {"id":"om_ia003","station":"okinawa_station_003","name":"琉球的牛 國際通店","name_en":"Ryukyu no Ushi","sub_cat":"燒肉","zone":"那霸","location":"那霸市牧志3-2-3 Hachimine Crystal 3F","ticket":"約4000-6000日圓","stay":"1.5小時","desc":"網友激推燒肉名店，選用不輸名牌的無名沖繩牛，價格實惠。","tags":["燒肉","A5和牛","國際通"],"priority":2,"url":"https://gowithmarkhazyl.com/okinawa-food-guide/"},
    {"id":"om_ia004","station":"okinawa_station_002","name":"Blue Seal 冰淇淋 牧志","name_en":"Blue Seal Makishi","sub_cat":"甜點","zone":"那霸","location":"那霸市牧志1-2-32","ticket":"約400-600日圓","stay":"30分鐘","desc":"沖繩冰淇淋王者，30種以上口味，鹽金楚糕口味是經典。","tags":["冰淇淋","甜點","必吃"],"priority":3,"url":"https://bobbytravel.tw/kokusai-street/"},
    {"id":"om_ia005","station":"okinawa_station_003","name":"豬肉蛋飯糰 本店","name_en":"Pork Tamago Onigiri","sub_cat":"小吃","zone":"那霸","location":"那霸市松尾2-8-35","ticket":"約300-500日圓","stay":"30分鐘","desc":"超人氣飯糰專賣店，早上排隊人潮多，建議下午前往。","tags":["飯糰","小吃","牧志"],"priority":3,"url":"https://bobbytravel.tw/kokusai-street/"},
    {"id":"om_ia006","station":"okinawa_station_002","name":"第一牧志公設市場","name_en":"Makishi Public Market","sub_cat":"小吃","zone":"那霸","location":"那霸市松尾2-10-1","ticket":"約1000-2000日圓","stay":"1小時","desc":"「沖繩人的廚房」，1樓選購海鮮，2樓代客烹調。","tags":["海鮮","市場","體驗"],"priority":3,"url":"https://bobbytravel.tw/kokusai-street/"},
    {"id":"om_ia007","station":"okinawa_station_001","name":"古宇利蝦蝦飯","name_en":"Kouri Shrimp","sub_cat":"小吃","zone":"北部","location":"沖繩縣國頭郡古宇利島","ticket":"約800-1000日圓","stay":"1小時","desc":"古宇利島超人氣小吃，蒜香奶油蝦飽滿大隻，配飯超下飯。","tags":["海鮮","古宇利","打卡"],"priority":2,"url":"https://gowithmarkhazyl.com/okinawa-food-guide/"},
    {"id":"om_ia008","station":"okinawa_station_046","name":"幸福鬆餅 瀨長島","name_en":"A Happy Pancake","sub_cat":"甜點","zone":"南部","location":"沖繩縣豐見城市瀨長島","ticket":"約800-1200日圓","stay":"1小時","desc":"世界最軟鬆餅，使用北海道生乳及紐西蘭蜂蜜，IG熱門打卡。","tags":["甜點","鬆餅","海景"],"priority":3,"url":"https://gowithmarkhazyl.com/okinawa-food-guide/"},
    {"id":"om_ia009","station":"okinawa_station_025","name":"浜屋沖繩麵","name_en":"Hamaya Soba","sub_cat":"麵食","zone":"中部","location":"沖繩縣中頭郡北谷町","ticket":"約700-1000日圓","stay":"1小時","desc":"35年歷史沖繩麵老店，湯頭清爽，豬軟骨入口即化。","tags":["沖繩麵","老店","北谷"],"priority":3,"url":"https://gowithmarkhazyl.com/okinawa-food-guide/"},
]

added = 0
for meal in all_data:
    if do_insert(meal):
        added += 1

conn.commit()

cur.execute("SELECT COUNT(*) FROM meals")
print(f"Total meals: {cur.fetchone()[0]}")

region_counts = {}
for region in ['seoul','busan','fukuoka','osaka','tokyo','okinawa']:
    cur.execute("SELECT COUNT(*) FROM meals WHERE region_code = ?", (region,))
    n = cur.fetchone()[0]
    region_counts[region] = n
    print(f"  {region}: {n}")

conn.close()
print(f"Total added: {added}")
