#!/usr/bin/env python3
"""
Phase 2 補連結腳本
attractions.json 讀取 → details{} 寫入 blog_article / google_maps / youtube
"""
import json, os

BASE = "/var/repo/travel-planner/data"

# ── 工具 ────────────────────────────────────────────────
def gmaps(name, zone):
    q = f"{name}+{zone}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def yt(query):
    q = query.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={q}"

def blog(url):
    return [url] if url else []

# ── 各地區連結資料庫（id → {blog, youtube, gmaps}）───
# 格式：每區獨立的 dict，id 為 key
REGION_DB = {

    "tokyo": {

"tokyo_disney": {"blog": ["https://www.tokyodisneyresort.jp/tc/index.html"], "yt": "東京迪士尼度假區", "gmaps": "https://www.google.com/maps/place/Tokyo+Disney+Resort"},
"tokyo_skytree": {"blog": ["https://zh-hant.tokyo-skytree.jp/"], "yt": "東京晴空塔", "gmaps": "https://www.google.com/maps/place/Tokyo+Skytree"},
"tokyo_tower": {"blog": ["https://www.gotokyo.org/tw/spot/34/index.html"], "yt": "東京鐵塔", "gmaps": "https://www.google.com/maps/place/Tokyo+Tower"},
"teamlab_borderless": {"blog": ["https://www.teamlab.art/zh-hant/e/tokyo/"], "yt": "teamLab Borderless 東京", "gmaps": "https://www.google.com/maps/place/teamLab+Borderless+Azabudai+Hills"},
"shibuya_crossing": {"blog": ["https://www.gotokyo.org/tw/spot/73/index.html"], "yt": "澀谷十字路口", "gmaps": "https://www.google.com/maps/place/Shibuya+Scramble+Crossing"},
"shibuya_sky": {"blog": ["https://www.shibuyasky.jp/tc.html"], "yt": "澀谷Sky", "gmaps": "https://www.google.com/maps/place/Shibuya+Sky"},
"akihabara": {"blog": ["https://www.gotokyo.org/tw/spot/100/index.html"], "yt": "秋葉原", "gmaps": "https://www.google.com/maps/place/秋葉原"},
"ueno_zoo": {"blog": ["https://www.gotokyo.org/tw/spot/41/index.html"], "yt": "上野動物園", "gmaps": "https://www.google.com/maps/place/Ueno+Zoo"},
"meiji_shrine": {"blog": ["https://www.gotokyo.org/tw/spot/21/index.html"], "yt": "明治神宮", "gmaps": "https://www.google.com/maps/place/Meiji+Jingu"},
"sensoji": {"blog": ["https://www.gotokyo.org/tw/spot/33/index.html"], "yt": "淺草寺", "gmaps": "https://www.google.com/maps/place/Senso-ji"},
"tokyo_station": {"blog": ["https://www.gotokyo.org/tw/spot/31/index.html"], "yt": "東京車站", "gmaps": "https://www.google.com/maps/place/Tokyo+Station"},
"ginza": {"blog": ["https://www.gotokyo.org/tw/spot/54/index.html"], "yt": "銀座", "gmaps": "https://www.google.com/maps/place/銀座"},
"shinjuku_gyoen": {"blog": ["https://www.gotokyo.org/tw/spot/40/index.html"], "yt": "新宿御苑", "gmaps": "https://www.google.com/maps/place/Shinjuku+Gyoen"},
"ghibli_museum": {"blog": ["https://www.ghibli-museum.jp/"], "yt": "三鷹之森吉卜力美術館", "gmaps": "https://www.google.com/maps/place/三鷹之森吉卜力美術館"},
"nezu_shrine": {"blog": ["https://www.gotokyo.org/tw/spot/23/index.html"], "yt": "根津神社", "gmaps": "https://www.google.com/maps/place/Nezu+Shrine"},
"harajuku": {"blog": ["https://www.gotokyo.org/tw/spot/56/index.html"], "yt": "原宿竹下通", "gmaps": "https://www.google.com/maps/place/原宿"},
"daiba": {"blog": ["https://www.gotokyo.org/tw/spot/83/index.html"], "yt": "台場海濱公園", "gmaps": "https://www.google.com/maps/place/台場海濱公園"},
"asakusa": {"blog": ["https://www.gotokyo.org/tw/spot/33/index.html"], "yt": "淺草仲見世通", "gmaps": "https://www.google.com/maps/place/仲見世通"},
"ikebukuro_sunshine": {"blog": ["https://www.sunshinecity.co.jp/"], "yt": "池袋陽光城", "gmaps": "https://www.google.com/maps/place/Sunshine+City"},
"tsukiji_outer": {"blog": ["https://www.gotokyo.org/tw/spot/36/index.html"], "yt": "築地場外市場", "gmaps": "https://www.google.com/maps/place/築地場外市場"},
"omotesando": {"blog": ["https://www.gotokyo.org/tw/spot/57/index.html"], "yt": "表參道", "gmaps": "https://www.google.com/maps/place/表參道"},
"roppongi": {"blog": ["https://www.gotokyo.org/tw/spot/78/index.html"], "yt": "六本木之丘", "gmaps": "https://www.google.com/maps/place/Roppongi+Hills"},
"ueno_ameyoko": {"blog": ["https://www.gotokyo.org/tw/spot/43/index.html"], "yt": "上野阿美橫丁", "gmaps": "https://www.google.com/maps/place/阿美橫丁"},
"nihonbashi": {"blog": ["https://www.nihonbashi-tokyo.jp/"], "yt": "日本橋", "gmaps": "https://www.google.com/maps/place/日本橋"},
"nakameguro": {"blog": ["https://www.gotokyo.org/tw/spot/50/index.html"], "yt": "中目黑賞櫻", "gmaps": "https://www.google.com/maps/place/中目黑"},
"yanaka": {"blog": ["https://www.gotokyo.org/tw/spot/48/index.html"], "yt": "谷中銀杏", "gmaps": "https://www.google.com/maps/place/谷中銀杏並木"},
"shimokitazawa": {"blog": ["https://www.gotokyo.org/tw/spot/51/index.html"], "yt": "下北澤", "gmaps": "https://www.google.com/maps/place/下北澤"},
"koenji": {"blog": ["https://www.gotokyo.org/tw/spot/52/index.html"], "yt": "高圓寺", "gmaps": "https://www.google.com/maps/place/高圓寺"},
"kichijoji": {"blog": ["https://www.gotokyo.org/tw/spot/46/index.html"], "yt": "吉祥寺井之頭公園", "gmaps": "https://www.google.com/maps/place/吉祥寺"},
"daikanyama": {"blog": ["https://www.gotokyo.org/tw/spot/49/index.html"], "yt": "代官山", "gmaps": "https://www.google.com/maps/place/代官山"},
"kagurazaka": {"blog": ["https://www.gotokyo.org/tw/spot/45/index.html"], "yt": "神楽坂", "gmaps": "https://www.google.com/maps/place/神楽坂"},
"tomigaya": {"blog": ["https://www.gotokyo.org/tw/spot/58/index.html"], "yt": "富谷原宿咖啡", "gmaps": "https://www.google.com/maps/place/富谷原宿"},
"zoshigaya": {"blog": ["https://www.gotokyo.org/tw/spot/47/index.html"], "yt": "雜司谷", "gmaps": "https://www.google.com/maps/place/雑司が谷"},
"nishiogikubo": {"blog": ["https://www.gotokyo.org/tw/spot/53/index.html"], "yt": "西荻窪", "gmaps": "https://www.google.com/maps/place/西荻窪"},
"ogikubo": {"blog": ["https://www.gotokyo.org/tw/spot/44/index.html"], "yt": "荻窪拉麵", "gmaps": "https://www.google.com/maps/place/荻窪"},
"tsukiji_sushi": {"blog": ["https://www.gotokyo.org/tw/spot/36/index.html"], "yt": "壽司大", "gmaps": "https://www.google.com/maps/place/壽司大"},
"ginza_sushi": {"blog": ["https://www.gotokyo.org/tw/spot/55/index.html"], "yt": "美登利寿司", "gmaps": "https://www.google.com/maps/place/銀座美登利"},
"shinjuku_izakaya": {"blog": ["https://www.gotokyo.org/tw/spot/37/index.html"], "yt": "新宿居酒屋", "gmaps": "https://www.google.com/maps/place/思い出橫丁"},
"harajuku_crepes": {"blog": ["https://www.gotokyo.org/tw/spot/56/index.html"], "yt": "原宿可麗餅", "gmaps": "https://www.google.com/maps/place/原宿可麗餅"},
"akihabara_maid": {"blog": ["https://www.gotokyo.org/tw/spot/100/index.html"], "yt": "秋葉原女僕咖啡", "gmaps": "https://www.google.com/maps/place/秋葉原"},
"ueno_yakitori": {"blog": ["https://www.gotokyo.org/tw/spot/43/index.html"], "yt": "上野燒鳥", "gmaps": "https://www.google.com/maps/place/上野不忍口"},
"shibuya_italian": {"blog": ["https://www.gotokyo.org/tw/spot/73/index.html"], "yt": "澀谷異國料理", "gmaps": "https://www.google.com/maps/place/澀谷"},
"tokyo_station_keireki": {"blog": ["https://www.gotokyo.org/tw/spot/31/index.html"], "yt": "東京車站一番街", "gmaps": "https://www.google.com/maps/place/東京駅一番街"},
"asakusa_wagyu": {"blog": ["https://www.gotokyo.org/tw/spot/33/index.html"], "yt": "淺草燒肉", "gmaps": "https://www.google.com/maps/place/淺草燒肉"},
"asakusa_kaminarimon": {"blog": ["https://www.gotokyo.org/tw/spot/33/index.html"], "yt": "淺草寺雷門", "gmaps": "https://www.google.com/maps/place/淺草寺"},
"meiji_jingu": {"blog": ["https://www.gotokyo.org/tw/spot/21/index.html"], "yt": "明治神宮", "gmaps": "https://www.google.com/maps/place/明治神宮"},
"nezu_jinja": {"blog": ["https://www.gotokyo.org/tw/spot/23/index.html"], "yt": "根津神社", "gmaps": "https://www.google.com/maps/place/根津神社"},
"kanda_jinja": {"blog": ["https://www.gotokyo.org/tw/spot/24/index.html"], "yt": "神田神社", "gmaps": "https://www.google.com/maps/place/神田神社"},
"yasukuni": {"blog": ["https://www.gotokyo.org/tw/spot/26/index.html"], "yt": "靖國神社", "gmaps": "https://www.google.com/maps/place/靖國神社"},
"zoujii": {"blog": ["https://www.gotokyo.org/tw/spot/32/index.html"], "yt": "增上寺", "gmaps": "https://www.google.com/maps/place/増上寺"},
"akihabara_kunitsu": {"blog": ["https://www.gotokyo.org/tw/spot/100/index.html"], "yt": "秋葉原神社", "gmaps": "https://www.google.com/maps/place/秋葉原"},
"st_maryia": {"blog": ["https://www.gotokyo.org/tw/spot/42/index.html"], "yt": "聖瑪利亞大教堂", "gmaps": "https://www.google.com/maps/place/聖瑪利亞大教堂"},

    },  # tokyo

    "fukuoka": {

"fukuoka_tower": {"blog": ["https://www.fukuokatower.co.jp/"], "yt": "福岡塔", "gmaps": "https://www.google.com/maps/place/福岡塔"},
"dazaifu": {"blog": ["https://www.dazaifutenmangu.com/"], "yt": "太宰府天滿宮", "gmaps": "https://www.google.com/maps/place/太宰府天滿宮"},
"ohori_park": {"blog": ["https://www.moyam.jp/ohori/"], "yt": "大濠公園", "gmaps": "https://www.google.com/maps/place/大濠公園"},
"kushida_ramen": {"blog": ["https://yamato.gr.jp/"], "yt": "博多拉麵", "gmaps": "https://www.google.com/maps/place/博多站+拉麵"},
"momochi_seaside": {"blog": ["https://www.fukuoka-dome.com/"], "yt": "福岡巨蛋百道海濱", "gmaps": "https://www.google.com/maps/place/福岡PayPay巨蛋"},
"hirokazu": {"blog": ["https://itoshima.info/"], "yt": "糸島半島", "gmaps": "https://www.google.com/maps/place/糸島半島"},
"karatsu_castle": {"blog": ["https://www.city.karatsu.lg.jp/kanko/spot/1004682_10481.html"], "yt": "唐津城", "gmaps": "https://www.google.com/maps/place/唐津城"},
"saga_balloon": {"blog": ["https://www.saga-bs.jp/"], "yt": "佐賀熱氣球", "gmaps": "https://www.google.com/maps/place/佐賀縣"},
"kokura_castle": {"blog": ["https://www.kokura-castle.jp/"], "yt": "小倉城", "gmaps": "https://www.google.com/maps/place/小倉城"},
"mojiko": {"blog": ["https://www.mojiko.com/"], "yt": "門司港懷舊街", "gmaps": "https://www.google.com/maps/place/門司港"},
"nakagawa_canal": {"blog": ["https://www.amagi-railway.com/"], "yt": "甘木鐵道咖啡街", "gmaps": "https://www.google.com/maps/place/甘木鐵道"},
"hakata_donton": {"blog": ["https://www.yokanavi.com/"], "yt": "博多運河城", "gmaps": "https://www.google.com/maps/place/博多運河城"},
"ramen_yamato": {"blog": ["https://yamato.gr.jp/"], "yt": "久留米拉麵", "gmaps": "https://www.google.com/maps/place/久留米+拉麵"},
"chikugo_yudofu": {"blog": ["https://www.ukiha-tofu.jp/"], "yt": "浮羽湯豆腐", "gmaps": "https://www.google.com/maps/place/浮羽市"},
"karatsu_seafood": {"blog": ["https://www.karatsu-bussan.com/"], "yt": "唐津海鮮", "gmaps": "https://www.google.com/maps/place/唐津+海鮮"},
"kashima_jinja": {"blog": ["https://www.hakozaki.com/"], "yt": "筥崎宮", "gmaps": "https://www.google.com/maps/place/筥崎宮"},
"kokura_gokoku": {"blog": ["https://kokura.tenjin.info/"], "yt": "小倉天滿宮", "gmaps": "https://www.google.com/maps/place/小倉天滿宮"},
"dazu_tenjin": {"blog": ["https://www.dazaifutenmangu.com/"], "yt": "太宰府天滿宮學業", "gmaps": "https://www.google.com/maps/place/太宰府天滿宮"},

    },  # fukuoka

    "seoul": {

"gwangjang": {"blog": ["https://gwangjang.com/"], "yt": "廣藏市場", "gmaps": "https://www.google.com/maps/place/廣藏市場"},
"myeongdong": {"blog": ["https://www.mcd.or.kr/"], "yt": "明洞購物", "gmaps": "https://www.google.com/maps/place/明洞"},
"namsan": {"blog": ["https://www.nseoultower.com/"], "yt": "N首爾塔", "gmaps": "https://www.google.com/maps/place/N+Seoul+Tower"},
"gyeongbok": {"blog": ["https://www.royalpalace.go.kr/"], "yt": "景福宮", "gmaps": "https://www.google.com/maps/place/Gyeongbokgung+Palace"},
"insadong": {"blog": ["https://insainfo.kr/"], "yt": "仁寺洞", "gmaps": "https://www.google.com/maps/place/仁寺洞"},
"cheonggyecheon": {"blog": ["https://www.sisul.or.kr/"], "yt": "清溪川", "gmaps": "https://www.google.com/maps/place/Cheonggyecheon"},
"hongdae": {"blog": ["https://www.seoul.go.kr/"], "yt": "弘大街頭表演", "gmaps": "https://www.google.com/maps/place/弘大"},
"garosu": {"blog": ["https://www.garosu.com/"], "yt": "窟山路", "gmaps": "https://www.google.com/maps/place/窟山路"},
"coex": {"blog": ["https://www.coexcenter.com/"], "yt": "COEX MALL", "gmaps": "https://www.google.com/maps/place/COEX+MALL"},
"lotte_world": {"blog": ["https://www.lotteworld.com/"], "yt": "樂天世界", "gmaps": "https://www.google.com/maps/place/Lotte+World"},
"seoul_forest": {"blog": ["https://www.seoulforest.co.kr/"], "yt": "首爾森林公園", "gmaps": "https://www.google.com/maps/place/首爾林"},
"trickeye": {"blog": ["https://www.trickeye.com/seoul/"], "yt": "首爾3D奇幻美術館", "gmaps": "https://www.google.com/maps/place/3D+幻視美術館"},
"nami": {"blog": ["https://www.namisum.com/"], "yt": "南怡島", "gmaps": "https://www.google.com/maps/place/Nami+Island"},
"petit_france": {"blog": ["https://www.petitefrance.go.kr/"], "yt": "小法國村", "gmaps": "https://www.google.com/maps/place/Petit+France"},
"nami_nem_nemo": {"blog": ["https://www.railbike.co.kr/"], "yt": "江村鐵道自行車", "gmaps": "https://www.google.com/maps/place/江村+Rail+Bike"},
"dongdaemun": {"blog": ["https://ddp.or.kr/"], "yt": "東大门設計廣場", "gmaps": "https://www.google.com/maps/place/Dongdaemun+Design+Plaza"},
"seoul_station": {"blog": ["https://www.lotteria.com/"], "yt": "首爾站南大門", "gmaps": "https://www.google.com/maps/place/首爾站"},
"seongsu": {"blog": ["https://www.seongsu.com/"], "yt": "聖水洞咖啡街", "gmaps": "https://www.google.com/maps/place/聖水洞"},
"mangwon": {"blog": ["https://www.mangwon.com/"], "yt": "延南洞咖啡街", "gmaps": "https://www.google.com/maps/place/延南洞"},
"gamcheon": {"blog": ["https://www.gamcheon.or.kr/"], "yt": "甘川洞文化村", "gmaps": "https://www.google.com/maps/place/甘川洞文化村"},
"hanok": {"blog": ["https://hanok.seoul.go.kr/"], "yt": "北村韓屋村", "gmaps": "https://www.google.com/maps/place/Bukchon+Hanok+Village"},
"yong山": {"blog": ["https://www.yongsan.go.kr/"], "yt": "龍山三角地", "gmaps": "https://www.google.com/maps/place/龍山三角地"},
"gwangjang_bibim": {"blog": ["https://gwangjang.com/"], "yt": "廣藏市場綠豆煎餅", "gmaps": "https://www.google.com/maps/place/廣藏市場"},
"myeongdong_kbok": {"blog": ["https://www.mcd.or.kr/"], "yt": "明洞烤雞肉串", "gmaps": "https://www.google.com/maps/place/明洞"},
"hongdae_beer": {"blog": ["https://www.seoul.go.kr/"], "yt": "弘大啤酒街", "gmaps": "https://www.google.com/maps/place/弘大"},
"gangnam_cake": {"blog": ["https://www.seoul.go.kr/"], "yt": "江南網紅咖啡", "gmaps": "https://www.google.com/maps/place/江南+首爾"},
"insadong_tea": {"blog": ["https://insainfo.kr/"], "yt": "仁寺洞傳統茶屋", "gmaps": "https://www.google.com/maps/place/仁寺洞"},
"jokbal": {"blog": ["https://www.jokbal.com/"], "yt": "孔陵一隻雞", "gmaps": "https://www.google.com/maps/place/孔陵一隻雞"},
"jogyesa": {"blog": ["https://www.jogyesa.kr/"], "yt": "曹溪寺", "gmaps": "https://www.google.com/maps/place/Jogyesa+Temple"},
"bongeunsa": {"blog": ["https://www.bongeunsa.org/"], "yt": "奉恩寺", "gmaps": "https://www.google.com/maps/place/Bongeunsa+Temple"},
"namsan_catholic": {"blog": ["https://www.catholic.or.kr/"], "yt": "南山天主教花園", "gmaps": "https://www.google.com/maps/place/南山+首爾"},
"icheon_energy": {"blog": ["https://www.gimpo.go.kr/"], "yt": "軍浦能量神殿", "gmaps": "https://www.google.com/maps/place/軍浦"},

    },  # seoul

    "busan": {

"haeundae": {"blog": ["https://www.visitbusan.net/"], "yt": "海雲台海水浴場", "gmaps": "https://www.google.com/maps/place/Haeundae+Beach"},
"gamcheon_culture": {"blog": ["https://www.gamcheon.or.kr/"], "yt": "甘川洞文化村", "gmaps": "https://www.google.com/maps/place/甘川洞文化村"},
"jagalchi": {"blog": ["https://www.jagalchi.co.kr/"], "yt": "札嘎其水產市場", "gmaps": "https://www.google.com/maps/place/札嘎其市場"},
"gwangandae": {"blog": ["https://www.visitbusan.net/"], "yt": "廣安里海水浴場", "gmaps": "https://www.google.com/maps/place/Gwangalli+Beach"},
"biyong": {"blog": ["https://www.visitbusan.net/"], "yt": "太宗台", "gmaps": "https://www.google.com/maps/place/Taejongdae"},
"apec_house": {"blog": ["https://www.visitbusan.net/"], "yt": "APEC世峰樓", "gmaps": "https://www.google.com/maps/place/APEC+Nurimaru+House"},
"songdo": {"blog": ["https://www.visitbusan.net/"], "yt": "松島海水浴場", "gmaps": "https://www.google.com/maps/place/Songdo+Beach"},
"busan_tower": {"blog": ["https://www.visitbusan.net/"], "yt": "釜山塔龍頭山", "gmaps": "https://www.google.com/maps/place/Yongdusan+Park"},
"dadaepo": {"blog": ["https://www.visitbusan.net/"], "yt": "多大浦夕陽噴泉", "gmaps": "https://www.google.com/maps/place/Dadaepo"},
"gukje": {"blog": ["https://www.gukje.com/"], "yt": "國債市場", "gmaps": "https://www.google.com/maps/place/國債市場"},
"gamcheon_maze": {"blog": ["https://www.gamcheon.or.kr/"], "yt": "甘川洞小王子迷宮", "gmaps": "https://www.google.com/maps/place/甘川洞文化村"},
"gwangalli_everyday": {"blog": ["https://www.visitbusan.net/"], "yt": "廣安里海景咖啡", "gmaps": "https://www.google.com/maps/place/廣安里海邊"},
"nampo_underground": {"blog": ["https://www.visitbusan.net/"], "yt": "南浦洞地下街", "gmaps": "https://www.google.com/maps/place/南浦洞地下街"},
"ulsan_market": {"blog": ["https://www.ulsan.go.kr/"], "yt": "蔚山張氏市場", "gmaps": "https://www.google.com/maps/place/蔚山張氏市場"},
"jagalchi_sashimi": {"blog": ["https://www.jagalchi.co.kr/"], "yt": "札嘎其生魚片", "gmaps": "https://www.google.com/maps/place/札嘎其市場"},
"haeundae_crab": {"blog": ["https://www.visitbusan.net/"], "yt": "海雲台螃蟹火鍋", "gmaps": "https://www.google.com/maps/place/海雲台+螃蟹"},
"dongnae_pajeon": {"blog": ["https://www.visitbusan.net/"], "yt": "東萊蔥煎餅", "gmaps": "https://www.google.com/maps/place/東萊區"},
"gwangalli_dessert": {"blog": ["https://www.visitbusan.net/"], "yt": "廣安里甜點", "gmaps": "https://www.google.com/maps/place/廣安里"},
"yonggung": {"blog": ["https://www.yonggungsa.net/"], "yt": "龍宮寺", "gmaps": "https://www.google.com/maps/place/Yonggunsa+Temple"},
"beomeosa": {"blog": ["https://www.beomeosa.kr/"], "yt": "梵魚寺", "gmaps": "https://www.google.com/maps/place/Beomeosa"},
"jangseong": {"blog": ["https://www.jangseong.go.kr/"], "yt": "張氏市場神社", "gmaps": "https://www.google.com/maps/place/張氏市場"},

    },  # busan

    "okinawa": {

"churaumi": {"blog": ["https://churaumi.okinawa/"], "yt": "美之海水族館", "gmaps": "https://www.google.com/maps/place/美之海水族館"},
"shurijo": {"blog": ["https://oki-park.jp/shuraku/0/"], "yt": "首里城", "gmaps": "https://www.google.com/maps/place/Shurijo+Castle"},
"american_village": {"blog": ["https://american-village.okinawa/"], "yt": "美國村沖繩", "gmaps": "https://www.google.com/maps/place/American+Village"},
"zampa": {"blog": ["https://www.visitokinawa.jp/"], "yt": "殘波岬", "gmaps": "https://www.google.com/maps/place/残波岬"},
"manzamo": {"blog": ["https://www.visitokinawa.jp/"], "yt": "萬座毛", "gmaps": "https://www.google.com/maps/place/万座毛"},
"kokusai": {"blog": ["https://www.kokusaidori.com/"], "yt": "國際通", "gmaps": "https://www.google.com/maps/place/国際通り"},
"ryukyu_mura": {"blog": ["https://www.ryukyu-mura.com/"], "yt": "琉球村", "gmaps": "https://www.google.com/maps/place/琉球村"},
"bise": {"blog": ["https://www.visitokinawa.jp/"], "yt": "備瀨一線路", "gmaps": "https://www.google.com/maps/place/備瀨+福木"},
"senagajima": {"blog": ["https://senagashima.okinawa/"], "yt": "瀨長島", "gmaps": "https://www.google.com/maps/place/瀬長島"},
"katsuracha": {"blog": ["https://www.visitokinawa.jp/"], "yt": "勝連城跡", "gmaps": "https://www.google.com/maps/place/Katsuracha+Castle"},
"chatan_bar": {"blog": ["https://www.visitokinawa.jp/"], "yt": "北谷美式酒吧", "gmaps": "https://www.google.com/maps/place/北谷アメリカ村"},
"awase_cafe": {"blog": ["https://www.visitokinawa.jp/"], "yt": "泡瀨海岸咖啡", "gmaps": "https://www.google.com/maps/place/泡瀨"},
"gyokusendo": {"blog": ["https://www.gyokusendo.co.jp/"], "yt": "玉泉洞", "gmaps": "https://www.google.com/maps/place/玉泉洞"},
"okinawa_soba": {"blog": ["https://www.visitokinawa.jp/"], "yt": "沖繩麵", "gmaps": "https://www.google.com/maps/place/沖繩麵"},
"taco_rice": {"blog": ["https://www.visitokinawa.jp/"], "yt": "塔可飯", "gmaps": "https://www.google.com/maps/place/北谷+塔可飯"},
"goya_champuru": {"blog": ["https://www.visitokinawa.jp/"], "yt": "苦瓜什錦", "gmaps": "https://www.google.com/maps/place/苦瓜+什錦"},
"awamori": {"blog": ["https://www.okinawa.or.jp/awamori/"], "yt": "泡盛", "gmaps": "https://www.google.com/maps/place/首里+泡盛"},
"naminoue": {"blog": ["https://naminouegu.or.jp/"], "yt": "波上宮", "gmaps": "https://www.google.com/maps/place/波上宮"},
"sefa": {"blog": ["https://www.pref.okinawa.jp/"], "yt": "齋場御嶽", "gmaps": "https://www.google.com/maps/place/斎場御嶽"},
"katsuracha_shrine": {"blog": ["https://www.visitokinawa.jp/"], "yt": "勝連城神社", "gmaps": "https://www.google.com/maps/place/勝連城"},

    },  # okinawa

}  # REGION_DB

# ── 主程式 ────────────────────────────────────────────────
def patch(region):
    path = f"{BASE}/{region}/attractions.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    db = REGION_DB.get(region, {})
    hits = fallbacks = 0

    for att in data["attractions"]:
        if "details" not in att:
            att["details"] = {}
        links = db.get(att["id"])
        if links:
            att["details"]["blog_article"] = links.get("blog", [])
            att["details"]["google_maps"] = links.get("gmaps", gmaps(att["name"], att["zone"]))
            att["details"]["youtube"] = [yt(links["yt"])] if links.get("yt") else []
            hits += 1
        else:
            att["details"]["blog_article"] = []
            att["details"]["google_maps"] = gmaps(att["name"], att["zone"])
            att["details"]["youtube"] = []
            fallbacks += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return hits, fallbacks

if __name__ == "__main__":
    total_h = total_f = 0
    for region in ["osaka", "tokyo", "fukuoka", "seoul", "busan", "okinawa"]:
        h, f = patch(region)
        print(f"OK {region}: {h} 精確連結 | {f} fallback gmaps")
        total_h += h
        total_f += f
    print(f"\n共補 {total_h} 筆，fallback {total_f} 筆")
