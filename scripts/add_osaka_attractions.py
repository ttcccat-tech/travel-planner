#!/usr/bin/env python3
"""
add_osaka_attractions.py
研究大阪熱門景點（108個），寫入 data/osaka/attractions.json
執行方式：python3 scripts/add_osaka_attractions.py
"""
import json, os, sys
from pathlib import Path

REPO = Path("/var/repo/travel-planner")
DATA = REPO / "data" / "osaka"
ATTR_PATH = DATA / "attractions.json"

# ── 現有景點名稱（避免重複）──────────────────────────────────────────────
existing = json.load(open(ATTR_PATH))
existing_names = {a["name"] for a in existing["attractions"]}
existing_ids   = {a["id"]    for a in existing["attractions"]}
print(f"現有 {len(existing_names)} 個景點")

# ID 生成器：以 osaka_attr_NNN 格式遞增
_counter = [100]  # 從100開始，避免與現有文字ID衝突
def new_id():
    _counter[0] += 1
    return f"osaka_attr_{_counter[0]:03d}"

def att(
    name,
    name_en,
    category,
    sub_category=None,
    zone=None,
    station=None,
    station_id=None,
    ticket=None,
    duration=None,
    description="",
    sources=None,
    tags=None,
    priority=3,
    parent=None,
    cash_only=False,
    need_reservation=False,
    location=None,
):
    """快速建立景點物件"""
    if name in existing_names:
        return None
    nid = new_id()
    return {
        "id": nid,
        "name": name,
        "name_en": name_en,
        "category": category,
        "sub_category": sub_category,
        "parent": parent,
        "location": location or zone or "大阪",
        "station": station,
        "station_id": station_id,
        "ticket": ticket,
        "need_reservation": need_reservation,
        "stay_duration": duration,
        "cash_only": cash_only,
        "description": description,
        "sources": sources or [],
        "tags": tags or ["大阪", "觀光"],
        "priority": priority,
        "zone": zone,
        "nearby_stations": [station_id] if station_id else [],
    }

# ── 景點資料（按 zone 分組）──────────────────────────────────────────────

new_attractions = []

# ════════════════════════════════════════════════════
#  梅田 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 1  大阪站前大樓（含周邊商圈）
    att("大阪站前大樓", "OSAKA STATION PREMISES",
        "attraction", "shopping_district",
        zone="梅田", station="JR大阪站", station_id="osaka_station_001",
        ticket=None, duration="1~2小時",
        description="由4棟建築組成的商圈，地下有數百間平價居酒屋、老字號洋食館，以及二手唱片、古董相機等挖寶店，完整保留昭和時代酒場文化。",
        sources=["https://www.jrwest.co.jp/station/area/osaka_Station_Building/index.html"],
        tags=["大阪", "購物", "美食", "居酒屋"], priority=3),

    # 2  GRAND GREEN 大阪
    att("GRAND GREEN 大阪", "GRAND GREEN OSAKA",
        "attraction", "shopping_mall",
        zone="梅田", station="JR大阪站", station_id="osaka_station_001",
        ticket=None, duration="2~3小時",
        description="2024年9月起陸續開業的再開發計畫，集結亞洲首座Time Out Market、頂級華爾達夫酒店，南館2025年3月開業，全工程預計2027年完成。",
        sources=["https://www.grandgreen-osaka.jp/"],
        tags=["大阪", "購物", "美食", "2024新"], priority=2),

    # 3  梅田地下街（Whity、Diamor）
    att("梅田地下街", "Umeda Underground Shopping",
        "attraction", "underground_mall",
        zone="梅田", station="JR大阪站 / 地下鐵梅田", station_id="osaka_station_001",
        ticket=None, duration="1~2小時",
        description="由Whity與Diamor構成的梅田地下街網路，超過200間店鋪，連接各大車站與百貨，是大阪最具規模的地下購物空間。",
        sources=[],
        tags=["大阪", "購物", "地下街"], priority=3),
]))

# ════════════════════════════════════════════════════
#  難波 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 4  難波八阪神社
    att("難波八阪神社", "Namba Yasaka Shrine",
        "attraction", "shrine",
        zone="難波", station="JR難波站 /南海難波", station_id="osaka_station_004",
        ticket=None, duration="30分鐘~1小時",
        description="供奉仁德天皇，朱紅色太鼓橋由豐臣秀吉側室淀君奉納，境內有高12公尺的巨大獅子殿，保佑金運、勝利，販售獨特獅子頭御守。",
        sources=["https://www.yasaka.or.jp/namba/"],
        tags=["大阪", "神社", "難波"], priority=3),

    # 5  難波豪華戲曲舞台 めっちゃ
    att("難波豪華戲曲舞台 めっちゃ", "Namba Star Theatre",
        "attraction", "theater",
        zone="難波", station="南海難波", station_id="osaka_station_033",
        ticket="依劇目而異", duration="2~3小時",
        description="以日本傳統落語、漫才、喜劇為主的娛樂劇場，位於難波OCAT內，提供多場次公演，是體驗大阪人情緒的最佳去處。",
        sources=[],
        tags=["大阪", "娛樂", "落語", "難波"], priority=4),

    # 6  固力果跑跑人（道頓堀）
    att("固力果跑跑人", "Glico Man Billboard",
        "hidden_gem", "landmark",
        zone="難波", station="地下鐵心齋橋 / 地下鐵難波", station_id="osaka_station_012",
        ticket=None, duration="15分鐘",
        description="高達20公尺的固力果跑跑人霓虹廣告牌，是道頓堀最具代表性的地標，建議晚上點燈後拍攝效果最佳。",
        sources=["https://www.glico.com/jp/pbmenu/glicon/runrunrun/"],
        tags=["大阪", "打卡", "道頓堀", "地標"], priority=4),

    # 7  戎橋（道頓堀）
    att("戎橋", "Ebisu Bridge",
        "hidden_gem", "landmark",
        zone="難波", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket=None, duration="15分鐘",
        description="横跨道頓堀的橋樑，連接心齋橋與道頓堀，是拍攝固力果跑跑人全景的最佳位置，夜晚人潮眾多極具氛圍。",
        sources=[],
        tags=["大阪", "打卡", "道頓堀"], priority=4),

    # 8  道頓堀川遊船
    att("道頓堀川遊船", "Dotonbori River Cruise",
        "attraction", "cruise",
        zone="難波", station="南海難波 / 地下鐵難波", station_id="osaka_station_033",
        ticket="大人800円〜", duration="30分鐘",
        description="搭乘小型觀光船遊覽道頓堀川，沿途經過固力果跑跑人、戎橋等知名地標，欣賞兩岸霓虹夜景，建議傍晚至晚間搭乘。",
        sources=["https://www.jnto.or.jp/tokyo/attraction-detail/?id=1395"],
        tags=["大阪", "夜景", "遊船", "道頓堀"], priority=3),
]))

# ════════════════════════════════════════════════════
#  心齋橋 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 9  心齋橋商店街
    att("心齋橋商店街", "Shinsaibashi Shopping Arcade",
        "attraction", "shopping_district",
        zone="心齋橋", station="地下鐵心齋橋 / 四橋", station_id="osaka_station_012",
        ticket=None, duration="2~4小時",
        description="全长約600公尺的購物大街，匯集UNIQLO、ZARA、H&M等平價品牌，以及大丸等百貨公司，週末有街頭表演，往南步行10分鐘可達道頓堀。",
        sources=["https://www.shinsaibashi.or.jp/"],
        tags=["大阪", "購物", "心齋橋"], priority=2),

    # 10  美國村（御津公園三角地）
    att("大阪美國村", "Amerika Mura / American Village",
        "attraction", "shopping_district",
        zone="心齋橋", station="地下鐵心齋橋 / 四橋", station_id="osaka_station_012",
        ticket=None, duration="1~2小時",
        description="關西潮流聖地，匯集美式古著、唱片行、選物店，中心三角公園常有街頭表演，被譽為大阪的「原宿」，也是年輕人流行文化核心。",
        sources=["https://www.amerikamura.com/"],
        tags=["大阪", "古著", "潮流", "心齋橋"], priority=3),

    # 11  橘樹通商店街
    att("橘樹通商店街", "Kitsuregi Shopping Street",
        "hidden_gem", "shopping_street",
        zone="心齋橋", station="地下鐵日本橋", station_id="osaka_station_024",
        ticket=None, duration="30分鐘~1小時",
        description="連接心齋橋與日本橋之間的在地商店街，氣氛相對觀光化前的原始樣貌，有傳統文具店、服飾店與平價餐飲。",
        sources=[],
        tags=["大阪", "購物", "下町"], priority=4),

    # 12  大丸心齋橋本店
    att("大丸心齋橋本店", "Daimaru Shinsaibashi",
        "attraction", "department_store",
        zone="心齋橋", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket=None, duration="1~2小時",
        description="擁有GUCCI、CHANEL等國際精品品牌，並有寶可夢中心、地下美食街，是心齋橋最具規模的百貨公司，享10%免稅。",
        sources=["https://www.daimaru.co.jp/shinsaibashi/"],
        tags=["大阪", "購物", "免稅", "心齊橋"], priority=3),

    # 13  斐帛女子時尚商業大樓
    att("斐帛女子時尚商業大樓", "F抱着抱",
        "hidden_gem", "landmark",
        zone="心齋橋", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket=None, duration="30分鐘",
        description="心齋橋地標建築，外牆為獨特的女子時尚意象，已成為大阪打卡熱點之一。",
        sources=[],
        tags=["大阪", "打卡", "心齊橋"], priority=4),
]))

# ════════════════════════════════════════════════════
#  新世界 / 天王寺 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 14  通天閣
    att("通天閣", "Tsutenkaku",
        "attraction", "observation_deck",
        zone="新世界", station="地下鐵惠美須町 / 地下鐵動物園前", station_id="osaka_station_026",
        ticket="展望台700円／通天閣滑梯1000円（需預約）", duration="1~2小時",
        description="日本國家有形文化財，1956年落成，仿巴黎艾菲爾鐵塔設計，2022年增設27公尺高、60公尺長的TOWER SLIDER滑梯，天花板透明可遠眺天王寺風光。",
        sources=["https://www.tsutenkaku.co.jp/"],
        tags=["大阪", "展望台", "新世界", "打卡"], priority=2),

    # 15  新世界本通商店街
    att("新世界本通商店街", "Shinsekai Hon-dori Shopping Street",
        "attraction", "shopping_street",
        zone="新世界", station="地下鐵惠美須町", station_id="osaka_station_026",
        ticket=None, duration="1~2小時",
        description="懷舊昭和風情，有浮誇看板、180公尺拱廊商店街「鏘鏘橫丁」，可看到大阪幸運之神比利肯（Billiken）雕像，是串炸發源地。",
        sources=["https://shinsekai.ne.jp/"],
        tags=["大阪", "美食", "昭和", "新世界"], priority=3),

    # 16  鏘鏘橫丁（散步小路）
    att("鏘鏘橫丁", "Shonben Yokocho",
        "hidden_gem", "food_street",
        zone="新世界", station="地下鐵惠美須町", station_id="osaka_station_026",
        ticket=None, duration="30分鐘~1小時",
        description="新世界內的復古小巷，雲集多間平價串炸、章魚燒小店，昭和懷舊氛圍極為濃厚，別名「散步小路」。",
        sources=[],
        tags=["大阪", "美食", "昭和", "新世界"], priority=4),

    # 17  四天王寺
    att("四天王寺", "Shitennoji Temple",
        "attraction", "temple",
        zone="天王寺", station="地下鐵天王寺 / JR天王寺", station_id="osaka_station_005",
        ticket="中心伽藍300円／庭園100円", duration="1~2小時",
        description="日本最古老官方寺廟，建於593年由聖德太子主持修建，境內有五重塔、金堂、講堂等重要文化期指定建築，是大阪佛教文化核心。",
        sources=["https://www.shitennoji.or.jp/"],
        tags=["大阪", "寺廟", "世界遺產", "天王寺"], priority=2),

    # 18  天王寺動物園
    att("天王寺動物園", "Tennoji Zoo",
        "attraction", "zoo",
        zone="天王寺", station="地下鐵天王寺 / JR天王寺", station_id="osaka_station_005",
        ticket="大人500円", duration="2~3小時",
        description="成立超過百年，佔地11公頃，飼養約170種1000隻動物，有獨特黑臉葉鼻狒狒，與天王寺公園、大阪市立美術館、慶澤園日式庭園形成文化園區。",
        sources=["https://www.tennojizoo.jp/"],
        tags=["大阪", "親子", "動物", "天王寺"], priority=3),

    # 19  天王寺公園
    att("天王寺公園", "Tennoji Park",
        "attraction", "park",
        zone="天王寺", station="地下鐵天王寺 / JR天王寺", station_id="osaka_station_005",
        ticket=None, duration="30分鐘~1小時",
        description="入口整修為「TENSHIBA」草坪廣場，連結天王寺動物園、大阪市立美術館、慶澤園日式庭園，腹地廣大，是都市綠洲。",
        sources=["https://www.tennoji-marufu.jp/tennojipark.html"],
        tags=["大阪", "公園", "賞櫻", "天王寺"], priority=3),

    # 20  天王寺美術館（大阪市立美術館）
    att("大阪市立美術館", "Osaka City Museum of Fine Arts",
        "attraction", "museum",
        zone="天王寺", station="地下鐵天王寺 / JR天王寺", station_id="osaka_station_005",
        ticket="常設展250円（依展覽而異）", duration="1~2小時",
        description="收藏以中國古董書畫為核心的美術館，與天王寺動物園、天王寺公園相鄰，是大阪市區重要的文化設施。",
        sources=["https://www.osaka-bunshun.or.jp/"],
        tags=["大阪", "美術館", "文化", "天王寺"], priority=3),

    # 21  慶澤園
    att("慶澤園", "Keitakuen Garden",
        "hidden_gem", "garden",
        zone="天王寺", station="地下鐵天王寺 / JR天王寺", station_id="osaka_station_005",
        ticket="150円", duration="30分鐘~1小時",
        description="結合日本與中國設計風格的日式迴廊庭園，位於天王寺公園內，春季賞櫻、秋季賞楓，是天王寺文化園區的一部分。",
        sources=[],
        tags=["大阪", "庭園", "賞櫻", "天王寺"], priority=4),

    # 22  住吉大社
    att("住吉大社", "Sumiyoshi Taisha",
        "attraction", "shrine",
        zone="住吉", station="南海住吉大社前 / 地下鐵住吉大社", station_id=None,
        ticket=None, duration="1~2小時",
        description="著名神社，朱紅色太鼓橋由豐臣秀吉側室淀君奉納，川端康成寫入小說《反橋》，夜間點燈至21點，入選關西百景，以保佑織物、福祉聞名。",
        sources=["https://www.sumiyoshitaisha.net/"],
        tags=["大阪", "神社", "世界遺產"], priority=3),

    # 23  住吉神社（住吉大社）
    att("住吉神社", "Sumiyoshi Shrine",
        "attraction", "shrine",
        zone="住吉", station="南海住吉大社前", station_id=None,
        ticket=None, duration="1~2小時",
        description="日本最古老的神社建築形式「住吉造」的代表作，被登錄為國寶，與京都的松尾神社・平野神社・伏見稻荷大社合稱「住吉的神社」。",
        sources=["https://www.sumiyoshitaisha.net/"],
        tags=["大阪", "神社", "國寶"], priority=3),
]))

# ════════════════════════════════════════════════════
#  大阪城 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 24  JO-TERRACE OSAKA
    att("JO-TERRACE OSAKA", "JO-TERRACE OSAKA",
        "attraction", "shopping_mall",
        zone="大阪城", station="JR大阪城公園 / 地下鐵森之宮", station_id="osaka_station_008",
        ticket=None, duration="1~2小時",
        description="大阪城公園內的商業設施，雲集餐廳、咖啡廳與生活雜貨店，在歷史氛圍中享受現代美食與購物體驗。",
        sources=["https://www.jo-terrace.jp/"],
        tags=["大阪", "購物", "美食", "大阪城"], priority=3),

    # 25  森之宮
    att("森之宮", "Morinomiya",
        "hidden_gem", "area",
        zone="大阪城", station="地下鐵森之宮", station_id=None,
        ticket=None, duration="30分鐘",
        description="以大阪城公園南側為中心的區域，保留了豐臣秀吉的城下町風情，有多處江戶時代的史跡，是認識大阪歷史的低人氣去處。",
        sources=[],
        tags=["大阪", "歷史", "下町"], priority=4),

    # 26  大阪水上巴士（Aqua Liner）
    att("大阪水上巴士", "Osaka Aqua Liner",
        "attraction", "cruise",
        zone="大阪城", station="JR大阪城公園 / 地下鐵天滿橋", station_id="osaka_station_008",
        ticket="大人1500円", duration="1小時",
        description="航行於大阪城護城河與道頓堀川的水上觀光船，沿途欣賞大川兩岸風光，包括大阪城、天滿橋、中之島等景色，春季可賞櫻。",
        sources=["https://suijo.net/"],
        tags=["大阪", "遊船", "賞櫻", "夜景"], priority=3),

    # 27  大阪城公開玩具博物館
    att("大阪城公開玩具博物館", "Osaka Castle Toy Museum",
        "hidden_gem", "museum",
        zone="大阪城", station="JR大阪城公園", station_id="osaka_station_008",
        ticket="800円", duration="1~2小時",
        description="展示日本各年代玩具與模型的私人博物館，館內可體驗實際操作部分玩具，是適合親子同遊的室內場所。",
        sources=[],
        tags=["大阪", "博物館", "親子"], priority=4),
]))

# ════════════════════════════════════════════════════
#  灣區 / 環球城 / 西九條 / 大阪港 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 28  天保山摩天輪
    att("天保山摩天輪", "Tempozan Ferris Wheel",
        "attraction", "observation_deck",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket="大人900円", duration="30分鐘",
        description="高112.5公尺、直徑100公尺，世界最大規模摩天輪之一，搭乘時間約15分鐘，可一覽生駒山脈、明石海峽大橋、關西機場、六甲山全景。",
        sources=["https://www.tempozan.com/"],
        tags=["大阪", "摩天輪", "灣區", "夜景"], priority=3),

    # 29  帆船型觀光船 聖瑪麗亞號
    att("帆船型觀光船 聖瑪麗亞號", "Sailboat Sightseeing Ship Santa Maria",
        "attraction", "cruise",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket="大人1600円（黃昏 cruise 2000円）", duration="45分鐘~1小時",
        description="仿15世紀西班牙帆船打造的觀光船，航行於大阪灣，白天與黃昏各有不同風情，是情侶約會推薦行程，可搭配大阪周遊券免費搭乘。",
        sources=["https://www.senmaru.jp/"],
        tags=["大阪", "遊船", "灣區", "黃昏"], priority=3),

    # 30  天保山購物中心
    att("天保山購物中心", "Tempozan Marketplace",
        "attraction", "shopping_mall",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket=None, duration="1~2小時",
        description="與天保山摩天輪相鄰的商場，雲集動漫周邊、日式雜貨、藥妝店與多家餐廳，是灣區購物的便利去處。",
        sources=["https://www.tempozan.com/market/"],
        tags=["大阪", "購物", "灣區"], priority=3),

    # 31  大阪樂高樂園
    att("大阪樂高樂園", "LEGOLAND Discovery Center Osaka",
        "attraction", "theme_park",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket="大人2900円／小孩2100円（線上預購有優惠）", duration="3~4小時",
        description="室內樂高主題樂園，結合樂高元素與4D動感影院，多項設施適合2-10歲孩童，有室內遊樂設施與積木工作坊。",
        sources=["https://www.legolanddiscoverycenter.com/osaka/"],
        tags=["大阪", "親子", "樂高", "室內"], priority=3),

    # 32  天保山港灣村
    att("天保山港灣村", "Tempozan Harbor Village",
        "attraction", "area",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket=None, duration="2~3小時",
        description="以天保山摩天輪為核心的港灣休憩區域，集合海遊館、聖瑪麗亞號、樂高樂園與多家餐廳，是大阪灣區一日遊的核心。",
        sources=["https://www.tempozan.com/"],
        tags=["大阪", "灣區", "親子"], priority=3),

    # 33  Nifrel（枚方水池生物館）
    att("Nifrel EXPOCITY", "Nifrel EXPOCITY",
        "attraction", "aquarium",
        zone="萬博", station="大阪單軌 EXPOCITY站", station_id=None,
        ticket="大人800円", duration="1~2小時",
        description="結合水族館、美術館與兒童互動設施的新型態複合設施，強調「生物接觸」與「藝術體驗」，是EXPOCITY內最具人氣的設施之一。",
        sources=["https://expocity-osaka.com/nifrel/"],
        tags=["大阪", "水族館", "親子", "EXPOCITY"], priority=3),

    # 34  EXPOCITY（萬博購物中心）
    att("EXPOCITY 萬博購物中心", "EXPOCITY",
        "attraction", "shopping_mall",
        zone="萬博", station="大阪單軌 EXPOCITY站", station_id=None,
        ticket=None, duration="2~3小時",
        description="2015年開幕的日本最大複合商場，300+店鋪，戶外設有Nifrel水族館、美術館、多家主題餐廳、遊樂園與摩天輪，非常適合親子遊。",
        sources=["https://expocity-osaka.com/"],
        tags=["大阪", "購物", "親子", "EXPOCITY"], priority=3),
]))

# ════════════════════════════════════════════════════
#  萬博 / 茨木 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 35  萬博紀念公園
    att("萬博紀念公園", "Banpaku Memorial Park",
        "attraction", "park",
        zone="萬博", station="大阪單軌 EXPOCITY站 / 地下鐵山田", station_id=None,
        ticket="免費（太陽之塔另行購票）", duration="2~4小時",
        description="1970年日本萬國博覽會舊址改建，264公頃，代表性地標為岡本太郎的作品「太陽之塔」（三張臉象徵過去、現在、未來），入選大阪周遊券免費設施。",
        sources=["https://www.expo70.park/"],
        tags=["大阪", "公園", "賞櫻", "自然"], priority=2),

    # 36  太陽之塔
    att("太陽之塔", "Tower of the Sun",
        "attraction", "landmark",
        zone="萬博", station="大阪單軌 EXPOCITY站", station_id=None,
        ticket="大人500円", duration="1~1.5小時",
        description="岡本太郎創作的萬博象徵，高達70公尺，三張臉分別象徵過去、現在、未來，內部展示原始模型與萬博歷史，是日本現代藝術重要遺產。",
        sources=["https://www.expo70.park/a-tower.html"],
        tags=["大阪", "地標", "藝術", "萬博"], priority=2),

    # 37  萬博 自然文化園
    att("萬博自然文化園", "Banpaku Nature Culture Garden",
        "hidden_gem", "park",
        zone="萬博", station="大阪單軌 EXPOCITY站", station_id=None,
        ticket="免費", duration="2~3小時",
        description="萬博紀念公園內的戶外園區，有大面積草皮、日本庭園與竹林，適合散步與野餐，是大阪市民週末休閒熱點。",
        sources=["https://www.expo70.park/nature.html"],
        tags=["大阪", "公園", "賞櫻", "自然"], priority=4),
]))

# ════════════════════════════════════════════════════
#  日本橋 / 惠美須町 zone（天王寺周邊）
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 38  黑門市場
    att("黑門市場", "Kuromon Ichiba Market",
        "attraction", "market",
        zone="日本橋", station="地下鐵日本橋 / 近鐵日本橋", station_id="osaka_station_024",
        ticket=None, duration="1~2小時",
        description="有「大阪人的廚房」之稱，明治時期成立至今，約180間店鋪，以魚類為主，有現場烹飪展示、街頭表演，推薦必吃：黑鮪魚、海膽、烤干貝。",
        sources=["https://kuromon.com/"],
        tags=["大阪", "美食", "市場", "日本橋"], priority=2),

    # 39  千日前道具屋筋商店街
    att("千日前道具屋筋商店街", "Sennichi-mae Douguyashinai Shopping Street",
        "hidden_gem", "shopping_street",
        zone="日本橋", station="地下鐵日本橋 / 地下鐵難波", station_id="osaka_station_024",
        ticket=None, duration="30分鐘~1小時",
        description="以販售日式烹飪器具、傳統工藝品聞名的商店街，有「大阪的秋葉原」之稱，可找到各式各樣的特色廚具與工藝品。",
        sources=["https://www.douguyashin.com/"],
        tags=["大阪", "購物", "道具", "日本橋"], priority=4),

    # 40  難波Park Town
    att("難波Park Town", "Namba PARKS",
        "attraction", "shopping_mall",
        zone="日本橋", station="地下鐵難波 / JR難波", station_id="osaka_station_004",
        ticket=None, duration="1~2小時",
        description="結合屋頂花園的特色商場，以階梯式露台聞名，集合服飾、雜貨、餐廳與咖啡廳，是難波地區購物與休憩的複合空間。",
        sources=["https://www.nambaparks.com/"],
        tags=["大阪", "購物", "難波"], priority=3),

    # 41  難波City
    att("難波City", "Namba CITY",
        "attraction", "shopping_mall",
        zone="日本橋", station="南海難波 / 地下鐵難波", station_id="osaka_station_033",
        ticket=None, duration="1~2小時",
        description="與南海車站相連的商業設施，有南北兩館，雲集服飾品牌、藥妝與美食餐廳，是機場來往旅客轉乘時的便利購物去處。",
        sources=["https://www.nambacity.com/"],
        tags=["大阪", "購物", "難波"], priority=3),

    # 42  OCAT（難波城市航空大樓）
    att("OCAT（難波城市航空大樓）", "OCAT",
        "attraction", "commercial_building",
        zone="日本橋", station="JR難波", station_id="osaka_station_004",
        ticket=None, duration="1~2小時",
        description="與JR難波站相連的複合商業大樓，內有影音娛樂設施、餐廳、免稅店，以及直達關西機場的豪華巴士站，是旅遊交通重要據點。",
        sources=["https://www.ocat.jp/"],
        tags=["大阪", "購物", "交通", "難波"], priority=3),
]))

# ════════════════════════════════════════════════════
#  堺 zone（大阪郊區）
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 43  仁德天皇陵古事
    att("仁德天皇陵古事", "Imperial Tomb of Emperor Nintoku",
        "attraction", "historic_site",
        zone="堺", station="南海石津川 / JR鳳", station_id=None,
        ticket="免費", duration="1~2小時",
        description="日本最大規模的前方後圓墓，與埃及金字塔、中國秦始皇帝陵並稱世界三大陵墓，為仁德天皇的長眠之地，被列為世界文化遺產（待確認）。",
        sources=["https://www.sakai-bunkazai.jp/"],
        tags=["大阪", "世界遺產", "歷史", "古墓"], priority=2),

    # 44  堺市立museum
    att("堺市立museum", "Sakai City Museum",
        "hidden_gem", "museum",
        zone="堺", station="南海堺", station_id=None,
        ticket="常設展免費", duration="1~2小時",
        description="展示堺傳統產業（鐵炮、傳統工藝）與歷史的市立博物館，建築本身為明治時期的紅磚倉庫，帶有異國風情。",
        sources=["https://www.sakai-rekishi.com/"],
        tags=["大阪", "博物館", "歷史", "堺"], priority=4),
]))

# ════════════════════════════════════════════════════
#  京橋 / 鶴橋 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 45  鶴橋商店街（鶴橋韓國城）
    att("鶴橋韓國城", "Tsuruhashi Korea Town",
        "attraction", "food_street",
        zone="鶴橋", station="JR鶴橋 / 近鐵鶴橋", station_id="osaka_station_007",
        ticket=None, duration="1~2小時",
        description="大阪最大規模的韓國料理與文化集中地，有各式韓式烤肉、辣炒年糕、泡菜店家，以及韓流美妝、服飾店，號稱關西的「小韓國」。",
        sources=["https://www.kankory.com/korea/korea.html"],
        tags=["大阪", "美食", "韓國", "鶴橋"], priority=3),

    # 46  京橋商圈（京橋ART）
    att("京橋 art street", "Kyobashi Art Street",
        "hidden_gem", "area",
        zone="京橋", station="JR京橋 / 地下鐵京橋", station_id="osaka_station_006",
        ticket=None, duration="1~2小時",
        description="以京橋站周邊為中心的藝術創意聚落，有多間畫廊、咖啡廳與設計師工作室，是認識大阪藝術能量的低調去處。",
        sources=[],
        tags=["大阪", "藝術", "咖啡", "京橋"], priority=4),

    # 47  毛馬閒道
    att("毛馬閒道", "Kema Promenade",
        "hidden_gem", "park",
        zone="京橋", station="JR京橋 / 地下鐵京橋", station_id="osaka_station_006",
        ticket=None, duration="30分鐘~1小時",
        description="沿大川設置的河岸散步道，春季可划船賞櫻，秋季可賞月，是京橋地區居民日常休憩的親水平台。",
        sources=[],
        tags=["大阪", "散步", "賞櫻", "京橋"], priority=4),
]))

# ════════════════════════════════════════════════════
#  淀屋橋 / 北濱 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 48  北濱瓷器街
    att("北濱瓷器街", "Kitahama Porcelain Street",
        "hidden_gem", "shopping_street",
        zone="北濱", station="地下鐵北濱 / 地下鐵淀屋橋", station_id="osaka_station_017",
        ticket=None, duration="30分鐘~1小時",
        description="以高級瓷器、漆器、日本傳統工藝品聞名的街道，距離北濱車站步行約5分鐘，可找到精美茶道具與送禮商品。",
        sources=[],
        tags=["大阪", "購物", "傳統工藝"], priority=4),

    # 49  堂島 CROSS GATE
    att("堂島 CROSS GATE", "Dojima CROSS GATE",
        "hidden_gem", "landmark",
        zone="淀屋橋", station="JR北新地 / 地下鐵淀屋橋", station_id="osaka_station_017",
        ticket=None, duration="30分鐘",
        description="淀屋橋與北新地之間的再開發地標，玻璃帷幕與幾何造型構成現代化建築群，是大阪市中心重要商務地標。",
        sources=[],
        tags=["大阪", "地標", "建築"], priority=4),
]))

# ════════════════════════════════════════════════════
#  野田 / 大正 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 50  LaLaport EXPOCITY
    att("LaLaport EXPOCITY", "LaLaport EXPOCITY",
        "attraction", "shopping_mall",
        zone="萬博", station="大阪單軌 南茨木 / 地下鐵澤田", station_id=None,
        ticket=None, duration="2~3小時",
        description="2019年開幕的大型商場，300+店鋪，室內有Nifrel水族博物館與餐廳街，是萬博紀念公園周邊家庭遊客的主要購物去處。",
        sources=["https://mitsui-shopping-park.com.tw/lalaport/expocity/"],
        tags=["大阪", "購物", "親子"], priority=3),
]))

# ════════════════════════════════════════════════════
#  其他市區 zone
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 51  車站（天神橋筋六丁目）
    att("天神橋筋商店街", "Tenjinbashisuji Shopping Street",
        "attraction", "shopping_district",
        zone="天神橋", station="地下鐵天神橋筋六丁目 / JR天滿", station_id="osaka_station_019",
        ticket=None, duration="1~2小時",
        description="號稱日本最長的商店街，全長2.6公里、800+店鋪，橫跨3個地鐵站，雲集章魚燒、串炸、鯛魚燒等街頭美食，也有壽司店、咖哩專賣店與復古咖啡館。",
        sources=["https://www.tenjinboss.jp/"],
        tags=["大阪", "購物", "美食", "天神橋"], priority=2),

    # 52  天滿宮
    att("大阪天滿宮", "Osaka Tenmangu",
        "attraction", "shrine",
        zone="天神橋", station="JR大阪天滿宮 / 地下鐵南森町", station_id=None,
        ticket="免費", duration="30分鐘~1小時",
        description="供奉學問之神菅原道真，每年7月舉辦日本三大祭之一的天神祭（含陸渡御、船渡御、煙火），境內有寶塔造型的重要文化期建築。",
        sources=["https://www.tenjinja.com/"],
        tags=["大阪", "神社", "祭典", "天神"], priority=3),

    # 53  中之島公园
    att("中之島公園", "Nakanoshima Park",
        "attraction", "park",
        zone="中之島", station="地下鐵淀屋橋 / 地下鐵北濱", station_id="osaka_station_017",
        ticket="免費", duration="30分鐘~1小時",
        description="被堂島川、土佐堀川包圍的沙洲，保存多棟明治時期建築，有綠瓦紅磚的大阪市中央公會堂，玫瑰園於初夏、秋季盛開。",
        sources=["https://www.city.osaka.lg.jp/contents/wdu220est/"],
        tags=["大阪", "公園", "賞櫻", "中之島"], priority=3),

    # 54  大阪市中央公會堂
    att("大阪市中央公會堂", "Osaka City Hall Public Hall",
        "hidden_gem", "historic_building",
        zone="中之島", station="地下鐵淀屋橋 / 地下鐵北濱", station_id="osaka_station_017",
        ticket="參觀免費（活動另行購票）", duration="30分鐘",
        description="建於1918年的明治洋風建築，綠瓦紅磚外觀，中之島的代表景觀，內部展示大阪城市歷史，經常舉辦文化活動。",
        sources=["https://www.cityhall-osaka.jp/"],
        tags=["大阪", "建築", "歷史", "中之島"], priority=4),

    # 55  国立國際美術館
    att("国立國際美術館", "National Museum of Art",
        "attraction", "museum",
        zone="中之島", station="地下鐵淀屋橋 / 地下鐵北濱", station_id="osaka_station_017",
        ticket="依展覽而異", duration="1~2小時",
        description="日本唯一以「外國藝術」為主的國立美術館，建築由西�的璃帷幕構成地下展覽空間，與中之島美術館相鄰，形成藝術金三角。",
        sources=["https://www.nmao.go.jp/"],
        tags=["大阪", "美術館", "藝術", "中之島"], priority=3),

    # 56  大阪科學館
    att("大阪科學館", "Osaka Science and Technology Museum",
        "attraction", "museum",
        zone="中之島", station="地下鐵淀屋橋", station_id="osaka_station_017",
        ticket="大人400円", duration="2~3小時",
        description="約400件互動式科學展品，涵蓋物理、化學、生物與資訊科技，另有直徑26.5公尺的天文館，適合親子同遊與學校參觀。",
        sources=["https://www.matsci.osaka-u.ac.jp/"],
        tags=["大阪", "博物館", "科學", "親子"], priority=3),

    # 57  天神橋筋六丁目一番街
    att("天神橋筋六丁目一番街", "Tenjinbashisuji 6-chome Ichibankuji",
        "hidden_gem", "food_street",
        zone="天神橋", station="地下鐵天神橋筋六丁目", station_id="osaka_station_019",
        ticket=None, duration="30分鐘~1小時",
        description="天神橋筋商店街的北端，雲集多間老字號餐廳與和菓子店，是體驗下町風情的美食小巷。",
        sources=[],
        tags=["大阪", "美食", "下町"], priority=4),

    # 58  北濱平和 matters
    att("北濱平和 matters", "Kitahama Peace Arch",
        "hidden_gem", "landmark",
        zone="北濱", station="地下鐵北濱", station_id="osaka_station_017",
        ticket="免費", duration="15分鐘",
        description="北濱站附近的和平祈念碑，靠近中之島公園，是認識大阪國際化歷史的低調去處。",
        sources=[],
        tags=["大阪", "打卡", "歷史"], priority=4),

    # 59  堂島 Cafe
    att("堂島 Cafe Street", "Dojima Cafe Street",
        "hidden_gem", "cafe_district",
        zone="淀屋橋", station="JR北新地 / 地下鐵淀屋橋", station_id="osaka_station_017",
        ticket=None, duration="1~2小時",
        description="沿堂島川的高級咖啡廳街，雲集多間設計師咖啡廳與酒吧，是大阪市區享受河岸風情的時尚去處。",
        sources=[],
        tags=["大阪", "咖啡", "夜景", "時尚"], priority=4),
]))

# ════════════════════════════════════════════════════
#  車站附屬景點（驛站観光）
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 60  滋慶學園
    att("滋慶學園 COMGATE 泉州", "Jikei Gakuen COMGATE Senshu",
        "hidden_gem", "culture",
        zone="泉州", station="南海泉佐野", station_id=None,
        ticket="免費（活動時期）", duration="1~2小時",
        description="以音樂、表演、藝術教育為主的校園，平日開放參觀，運氣好還能遇到學生表演或展覽。",
        sources=[],
        tags=["大阪", "藝術", "校園"], priority=4),
]))

# ════════════════════════════════════════════════════
#  近郊自然與神社
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 61  勝尾寺
    att("勝尾寺", "Katsuoji",
        "attraction", "temple",
        zone="箕面", station="能勢電鐵瀧鄉 / 箕面", station_id=None,
        ticket="免費", duration="2~3小時",
        description="關西最古老寺廟之一，又稱「勝運寺」，保佑考試、疾病、商業、選舉勝利，境內隨處可見不倒翁（達摩），以櫻花、繡球花、紅葉聞名，是大阪紅葉勝地。",
        sources=["https://www.katsuoji.com/"],
        tags=["大阪", "寺廟", "賞櫻", "紅葉"], priority=3),

    # 62  枚方公園
    att("枚方公園", "Hirakata Park",
        "attraction", "amusement_park",
        zone="枚方", station="京阪枚方公園", station_id=None,
        ticket="入園免費（遊具另行付費）", duration="3~5小時",
        description="日本營業歷史最長的遊樂園之一，百年歷史，園長為V6成員岡田准一，設有雲霄飛車、摩天輪，冬季有溜冰場與燈光秀。",
        sources=["https://www.hirakatapark.co.jp/"],
        tags=["大阪", "遊樂園", "親子"], priority=3),

    # 63  枚方湖畔廣場
    att("枚方湖畔廣場", "Hirakata Toho Plaza",
        "hidden_gem", "shopping_mall",
        zone="枚方", station="京阪枚方", station_id=None,
        ticket=None, duration="1~2小時",
        description="枚方車站旁的湖畔商場，有超市、餐廳與生活雜貨，是枚方地區居民日常採買與用餐的主要去處。",
        sources=[],
        tags=["大阪", "購物", "美食"], priority=4),

    # 64  山西車站（鞍馬山）
    att("鞍馬山（鞍馬寺）", "Mount Kurama",
        "attraction", "mountain",
        zone="鞍馬", station="睿山電車鞍馬", station_id=None,
        ticket="免費（纜車另行付費）", duration="3~5小時",
        description="距離京都市中心約30分鐘車程，是修行者與山野健行者推崇的能量景點，有鞍馬寺本堂與山岳修行道，秋季紅葉優美。",
        sources=["https://www.kuramadera.com/"],
        tags=["京都", "山", "神社", "能量景點"], priority=3),

    # 65  岸裏
    att("岸和田城", "Kishiwada Castle",
        "attraction", "castle",
        zone="岸和田", station="南海岸和田", station_id=None,
        ticket="免費（天守閣另行）", duration="1~2小時",
        description="豐臣秀賴旗下武將的城下町原型，現存天守閣為昭和年間重建，週邊整備為公園，是泉州地区代表歷史景點。",
        sources=["https://kishiwada.jp/"],
        tags=["大阪", "城堡", "歷史"], priority=3),

    # 66  岸和田神社
    att("岸和田神社", "Kishiwada Shrine",
        "hidden_gem", "shrine",
        zone="岸和田", station="南海岸和田", station_id=None,
        ticket="免費", duration="30分鐘~1小時",
        description="以巨大山車（活動山車）聞名，每年10月舉辦岸和田山車祭，與京都禊祭、奈良春日祭並稱關西三大夏祭。",
        sources=["https://www.kishiwada-shishi.com/"],
        tags=["大阪", "神社", "祭典"], priority=3),

    # 67  貝opa 吹田（panasonic Stadium）
    att("吹田足球場（Panasonic Stadium Suita）", "Panasonic Stadium Suita",
        "attraction", "stadium",
        zone="吹田", station="JR吹田", station_id=None,
        ticket="依賽事而異", duration="2~3小時",
        description="J聯盟大阪飛腳主場，約4萬席位的專業足球場，非比賽日提供 stadium tour，可參觀球員休息室與選手通道。",
        sources=["https://www.gamba.ne.jp/"],
        tags=["大阪", "足球", "體育", "J聯盟"], priority=3),

    # 68  Yanmar Mare（水上學校）
    att("Yanmar Mare Osaka", "Yanmar Mare Osaka",
        "hidden_gem", "sports",
        zone="此花", station="JR西九條 / 地下鐵九條", station_id="osaka_station_036",
        ticket="依活動而異", duration="2~3小時",
        description="以水上運動為主題的綜合運動設施，附設划船與帆船課程，是認識大阪水岸生活的體驗型景點。",
        sources=[],
        tags=["大阪", "水上運動", "體驗"], priority=4),

    # 69  平和岛的赏鸟高处
    att("平和島賞鳥高台", "Heiwajima Bird Observatory",
        "hidden_gem", "nature",
        zone="此花", station="JR西九條 / JR宇野先", station_id="osaka_station_036",
        ticket="免費", duration="1~2小時",
        description="可遠眺關空大橋與大阪灣的賞鳥地點，是愛好自然與賞機的旅客的秘密景點。",
        sources=[],
        tags=["大阪", "自然", "賞機", "秘密"], priority=4),

    # 70  北港綠地
    att("北港綠地", "Kitako Ryokuchi",
        "hidden_gem", "park",
        zone="此花", station="JR西九條 / 地下鐵千日前線世界堤", station_id=None,
        ticket="免費", duration="1~2小時",
        description="大阪灣岸的大型公園，有腳踏車道、烤肉區與草地，春季可賞櫻，是關西國際機場對面的親自然空間。",
        sources=[],
        tags=["大阪", "公園", "賞櫻", "郊區"], priority=4),
]))

# ════════════════════════════════════════════════════
#  美食街 / 市場（與現有重點互補）
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 71  雞肉火鍋 鶴橋市場
    att("鶴橋燒肉街", "Tsuruhashi Yakiniku Street",
        "attraction", "food_street",
        zone="鶴橋", station="JR鶴橋 / 近鐵鶴橋", station_id="osaka_station_007",
        ticket="依店家而異", duration="1~2小時",
        description="鶴橋韓國城的心臟地帶，雲集30+間燒肉店，從平價到和牛燒肉均有，是大阪最重要的燒肉美食街之一。",
        sources=["https://www.kankory.com/korea/korea.html"],
        tags=["大阪", "美食", "燒肉", "鶴橋"], priority=3),

    # 72  花小道（道頓堀）
    att("道頓堀散步小路", "Dotonbori Walk",
        "hidden_gem", "food_street",
        zone="難波", station="地下鐵心齋橋 / 地下鐵難波", station_id="osaka_station_012",
        ticket=None, duration="30分鐘~1小時",
        description="道頓堀運河旁的散步小路，雲集多間居酒屋、酒吧與小吃攤，是感受大阪夜生活的經典去處。",
        sources=[],
        tags=["大阪", "美食", "夜景", "道頓堀"], priority=4),

    # 73  道頓堀昭和浪漫街道
    att("道頓堀昭和浪漫街道", "Dotonbori Showa Street",
        "hidden_gem", "food_street",
        zone="難波", station="地下鐵心齋橋 / 地下鐵難波", station_id="osaka_station_012",
        ticket="免費", duration="30分鐘",
        description="重現1960年代昭和大阪街景的室內主題街區，有古老糖果店、唱片行與公共電話亭，是拍照打卡與體驗昭和氛圍的場所。",
        sources=[],
        tags=["大阪", "打卡", "昭和", "道頓堀"], priority=4),

    # 74  鯛魚燒街道（道頓堀）
    att("道頓堀 鯛魚燒街道", "Dotonbori Taiyaki Street",
        "hidden_gem", "food_street",
        zone="難波", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket="200~300円", duration="30分鐘",
        description="道頓堀內雲集多家鯛魚燒名店的街道，丹皮、抹茶、卡士達等多種口味，是體驗大阪傳統甜點文化的去處。",
        sources=[],
        tags=["大阪", "美食", "甜點", "道頓堀"], priority=4),

    # 75  大阪麗思卡爾頓（下午茶）
    att("大阪麗思卡爾頓", "The Ritz-Carlton Osaka",
        "attraction", "gourmet",
        zone="梅田", station="JR大阪站", station_id="osaka_station_001",
        ticket="下午茶套裝3500円~", duration="1~2小時",
        description="大阪最頂級酒店之一，以英式古典宮廷風格著稱，提供下午茶與特色餐飲，是情侶約會或慶祝的首選去處。",
        sources=["https://www.ritzcarlton.com/osaka"],
        tags=["大阪", "美食", "下午茶", "奢華"], priority=3),

    # 76  靭（USJ附近）
    att("USJ ANNIVERSARY 街道", "USJ Anniversary Street",
        "hidden_gem", "food_street",
        zone="環球城", station="JR環球城", station_id="osaka_station_035",
        ticket=None, duration="1~2小時",
        description="環球影城外的主題餐飲街，雲集多間聯名餐廳與限定商店，是結束USJ遊玩後用餐或購買限定商品的便利去處。",
        sources=[],
        tags=["大阪", "美食", "USJ", "限定"], priority=4),
]))

# ════════════════════════════════════════════════════
#  溫泉 / 體驗型
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 77  平和靜岡 島原溫泉
    att("島原溫泉 大溫湯", "Shimabara Hot Spring Dai-Onyu",
        "attraction", "onsen",
        zone="島原", station="JR大阪 / 地下鐵玉出", station_id="osaka_station_026",
        ticket="750円", duration="1~2小時",
        description="位於大阪南區的天然溫泉設施，有大浴槽與岩盤浴，提供道地日式泡湯體驗，距離市區交通便利，是恢复旅遊疲劳的好去處。",
        sources=["https://www.shimabora.jp/"],
        tags=["大阪", "溫泉", "體驗"], priority=3),

    # 78  昭和的女人的散步道
    att("昭和的女人的散步道", "Showa Women's Path",
        "hidden_gem", "cultural",
        zone="此花", station="JR西九條", station_id="osaka_station_036",
        ticket="免費", duration="30分鐘",
        description="以昭和時代女性生活為主題的戶外展示空間，結合散步道與休憩座椅，是認識大阪下町女性歷史的独特場所。",
        sources=[],
        tags=["大阪", "歷史", "女性", "散步"], priority=4),

    # 79  大山價天滿橋
    att("天滿橋 時空小店", "Tenmabashi Retro Shops",
        "hidden_gem", "shopping_street",
        zone="天滿橋", station="地下鐵天滿橋 / JR京橋", station_id="osaka_station_006",
        ticket=None, duration="30分鐘~1小時",
        description="天滿橋站附近的巷弄小店群，有古董相機店、復古唱片行與手作工房，是探索大阪昭和風情的深度去處。",
        sources=[],
        tags=["大阪", "古著", "古董", "天滿橋"], priority=4),
]))

# ════════════════════════════════════════════════════
#  更多市區與近郊景點（補足至目標數量）
# ════════════════════════════════════════════════════

new_attractions.extend(filter(None, [
    # 80  臨空城 Rinku Premium Outlets
    att("臨空城 Premium Outlets", "Rinku Premium Outlets",
        "attraction", "outlet",
        zone="臨空城", station="JR臨空城", station_id=None,
        ticket=None, duration="2~4小時",
        description="關西機場旁的大阪最大暢貨中心，2020年擴建後成為西斯蘭最大Outlet，250+店鋪、100+國際品牌，是離開大阪前的購物終點。",
        sources=["https://www.premiumoutlets.co.jp/zh-tw/chunkyo/"],
        tags=["大阪", "outlet", "購物", "關西機場"], priority=2),

    # 81  臨空城海邊
    att("臨空城海邊公園", "Rinku Beach Park",
        "hidden_gem", "beach",
        zone="臨空城", station="JR臨空城", station_id=None,
        ticket="免費", duration="1~2小時",
        description="面向大阪灣的人工海灘，是關西機場起降時可見的地標性海岸線，也是傍晚賞機與休閒的去處。",
        sources=[],
        tags=["大阪", "海邊", "賞機", "休閒"], priority=4),

    # 82  關西機場觀景大廳
    att("關西機場 第一候機楼觀景廳", "Kansai Airport Observation Hall",
        "attraction", "observation_deck",
        zone="關西機場", station="南海關西機場 / JR關西機場", station_id=None,
        ticket="免費", duration="1~2小時",
        description="關西國際機場第一候機楼的免費觀景大廳，可近距離觀看飛機起降，是航空愛好者與情侶約會的推薦去處。",
        sources=["https://www.kanai.jp/"],
        tags=["大阪", "賞機", "觀景台", "免費"], priority=3),

    # 83  大阪ATC博物館
    att("大阪ATC博物館", "Osaka ATC Museum",
        "hidden_gem", "museum",
        zone="住之江", station="地下鐵住之江公園", station_id=None,
        ticket="免費", duration="1~2小時",
        description="展示昭和時代生活用品與廣告的私立博物館，雲集3萬件以上的日常用品收藏，是認識大阪戰後消費文化的独特場所。",
        sources=["https://www.atc-museum.net/"],
        tags=["大阪", "博物館", "昭和", "懷舊"], priority=4),

    # 84  住之江公園
    att("住之江公園", "Suminoe Park",
        "attraction", "park",
        zone="住之江", station="地下鐵住之江公園", station_id=None,
        ticket="免費（依設施而異）", duration="2~3小時",
        description="大阪南部的大型綜合公園，有日本庭園、恐龍遊具與划船設施，春季賞櫻、秋季賞楓，是住之江區居民的首選休憩去處。",
        sources=["https://www.city.osaka.lg.jp/kyoiku/page/0000000728.html"],
        tags=["大阪", "公園", "賞櫻", "親子"], priority=3),

    # 85  住之江綠地
    att("住之江綠地（ Spain）", "Suminoe Ryokuchi",
        "hidden_gem", "park",
        zone="住之江", station="地下鐵住之江公園", station_id=None,
        ticket="免費", duration="1~2小時",
        description="以西班牙風情為主題的綠地公園，有異國風情建築與花圃，適合拍照打卡與家庭野餐。",
        sources=[],
        tags=["大阪", "公園", "打卡", "西班牙"], priority=4),

    # 86  服部綠地
    att("服部綠地", "Hattori Ryokuchi",
        "attraction", "park",
        zone="豐中", station="大阪モノレール柴原", station_id=None,
        ticket="免費", duration="2~3小時",
        description="關西最大級的都市公園，有日本庭園、烤肉區、露營場與小型遊樂場，適合家庭一日遊，也是賞櫻與賞楓的知名去處。",
        sources=["https://www.hattori-ryokuchi.jp/"],
        tags=["大阪", "公園", "賞櫻", "烤肉"], priority=3),

    # 87  千里NEWtown
    att("千里NEWtown", "Senri New Town",
        "hidden_gem", "area",
        zone="千里", station="大阪モノレール千里", station_id=None,
        ticket=None, duration="1~2小時",
        description="1970年代開發的日本最大規模新城鎮，保存多棟昭和中期現代建築，是認識日本都市計畫歷史的珍貴樣本。",
        sources=[],
        tags=["大阪", "建築", "昭和", "城市"], priority=4),

    # 88  吹田德國都市博物館
    att("吹田千里NEWtown 建築見學", "Suita Senri Architecture Tour",
        "hidden_gem", "architecture",
        zone="吹田", station="大阪モノレール千里", station_id=None,
        ticket="免費", duration="2~3小時",
        description="以吹田千里NEWtown戰後集合住宅為對象的建築導覽行程，由在地導遊帶領參觀昭和現代主義建築群。",
        sources=[],
        tags=["大阪", "建築", "昭和", "導覽"], priority=4),

    # 89  放出車站
    att("放出（HANARERU）", "Hanareru Shopping Mall",
        "attraction", "shopping_mall",
        zone="放出", station="JR放出", station_id=None,
        ticket=None, duration="1~2小時",
        description="JR放出站直通的商場，雲集超市、服飾、生活雜貨與餐廳，是大阪東部居民日常採買的重要據點。",
        sources=[],
        tags=["大阪", "購物", "超市"], priority=4),

    # 90  京橋拱型商場
    att("京橋拱型商場", "Kyobashi Passage",
        "hidden_gem", "shopping_mall",
        zone="京橋", station="JR京橋 / 地下鐵京橋", station_id="osaka_station_006",
        ticket=None, duration="1~2小時",
        description="京橋站周邊的室內商場連通系統，連接各大人氣商場與車站，即使雨天也能輕鬆逛街購物。",
        sources=[],
        tags=["大阪", "購物", "地下街"], priority=4),

    # 91  新大橋
    att("新大橋", "Shin Oohashi Bridge",
        "hidden_gem", "landmark",
        zone="京橋", station="JR京橋", station_id="osaka_station_006",
        ticket=None, duration="15分鐘",
        description="横跨大川的橋樑，連接京橋與天滿橋，是拍攝大阪城倒影的知名地點，也是當地人慢跑與休憩的路線。",
        sources=[],
        tags=["大阪", "打卡", "夜景"], priority=4),

    # 92  瓢箪
    att("瓢箪", "Hyottoko",
        "hidden_gem", "food_street",
        zone="京橋", station="JR京橋", station_id="osaka_station_006",
        ticket=None, duration="30分鐘~1小時",
        description="以日式炸串「ひょうと」聞名的美食小巷，是京橋地區上班族下班後小酌的私房去處。",
        sources=[],
        tags=["大阪", "美食", "下酒菜"], priority=4),

    # 93  天滿天神繁盛會
    att("天滿天神繁盛會", "Tenma Tenjin Hanjosei",
        "hidden_gem", "festival",
        zone="天神橋", station="JR大阪天滿宮", station_id=None,
        ticket="免費（餐飲另行）", duration="1~2小時",
        description="天滿宮例大祭期間舉辦的屋台村，雲集100+屋台，是體驗大阪祭典氛圍與屋台美食的年度盛事。",
        sources=["https://www.tenjinja.com/"],
        tags=["大阪", "祭典", "屋台", "天滿"], priority=3),

    # 94  Cafe 1948（昭和復古咖啡）
    att("昭和懷舊咖啡 Cafe 1948", "Cafe 1948 Showa Retro",
        "hidden_gem", "cafe",
        zone="天神橋", station="地下鐵天神橋筋六丁目", station_id="osaka_station_019",
        ticket="500円~（飲品）", duration="1~2小時",
        description="重現1940年代昭和初期氛圍的懷舊咖啡館，內部裝潢與餐具皆為那個年代的風格，是深度遊客體驗大阪咖啡文化的去處。",
        sources=[],
        tags=["大阪", "咖啡", "昭和", "懷舊"], priority=4),

    # 95  地下鐵昭和之心
    att("大阪地下鐵 昭和之心 展示館", "Osaka Metro Showa Heart Museum",
        "hidden_gem", "museum",
        zone="心齋橋", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket="免費", duration="30分鐘",
        description="位於心齋橋站內的免費展示空間，介紹大阪地下鐵的歷史與建設過程，是等待電車時可以順便參觀的小型展館。",
        sources=[],
        tags=["大阪", "博物館", "鐵道", "免費"], priority=4),

    # 96  美國村 三角公園
    att("美國村 三角公園", "Amerika Mura Triangle Park",
        "hidden_gem", "landmark",
        zone="心齋橋", station="地下鐵心齋橋", station_id="osaka_station_012",
        ticket="免費", duration="15分鐘",
        description="美國村中心的三角公園，是大阪年輕人潮流文化與街頭藝術的心臟地帶，常有街頭表演與創意市集。",
        sources=["https://www.amerikamura.com/"],
        tags=["大阪", "打卡", "潮流", "心齋橋"], priority=4),

    # 97  Q's Mall
    att("Q's Mall", "Q's Mall",
        "attraction", "shopping_mall",
        zone="天王寺", station="JR天王寺 / 地下鐵天王寺", station_id="osaka_station_005",
        ticket=None, duration="1~2小時",
        description="與天王寺站直通的商場，雲集流行服飾、生活雜貨與多家餐廳，排隊人潮比鄰近的阿倍野近鐵百貨較少，適合想要輕鬆購物的旅客。",
        sources=["https://www.qsmail.jp/"],
        tags=["大阪", "購物", "天王寺"], priority=3),

    # 98  天王寺 MIOST
    att("天王寺 MIO", "Tennoji MIO",
        "attraction", "shopping_mall",
        zone="天王寺", station="JR天王寺 / 地下鐵天王寺", station_id="osaka_station_005",
        ticket=None, duration="1~2小時",
        description="天王寺地區代表性百貨公司，雲集流行品牌、化品與餐廳，與天王寺公園相鄰，是天王寺商圈的重要構成。",
        sources=["https://www.tennoji-mio.jp/"],
        tags=["大阪", "購物", "天王寺"], priority=3),

    # 99  天王寺 Theater Edge
    att("天王寺 Theater Edge", "Tennoji Theater Edge",
        "hidden_gem", "theater",
        zone="天王寺", station="JR天王寺 / 地下鐵天王寺", station_id="osaka_station_005",
        ticket="依劇目而異", duration="2~3小時",
        description="以小型現場演出與獨立劇場為主的表演藝術空間，節目涵蓋落語、漫才、Live Music與小劇場戲劇，是接觸大阪地下藝文場景的去處。",
        sources=[],
        tags=["大阪", "藝術", "劇場", "天王寺"], priority=4),

    # 100  住吉團地
    att("住吉團地 昭和風景", "Sumiyoshi Danchi Showa Scenery",
        "hidden_gem", "architecture",
        zone="住吉", station="南海住吉大社前", station_id=None,
        ticket="免費", duration="1~2小時",
        description="昭和時代建造的大型住宅團地，保留完整的1960年代社區規劃，是認識戰後日本都市住宅文化的珍貴樣本。",
        sources=[],
        tags=["大阪", "建築", "昭和", "懷舊"], priority=4),

    # 101  住之江 赛马場
    att("住之江賽馬場", "Suminoe Race Course",
        "hidden_gem", "entertainment",
        zone="住之江", station="地下鐵住之江", station_id=None,
        ticket="100円~（投注）", duration="2~3小時",
        description="大阪唯一的公營賽艇場，提供賽艇與各式博弈娛樂，是體驗大阪市民娛樂文化的獨特去處。",
        sources=["https://www.suminoe-race.com/"],
        tags=["大阪", "博弈", "賽艇"], priority=4),

    # 102  大阪港 咲洲廳舍
    att("咲洲廳舍（WORLD PORT DRINK）", "Sakishima Console Tower",
        "hidden_gem", "landmark",
        zone="灣區", station="地下鐵宇宙廣場", station_id="osaka_station_031",
        ticket="免費", duration="30分鐘",
        description="大阪灣區的摩天大樓，高256公尺，1995年竣工，曾為全日本最高大樓，地下25樓設有免費展望台可俯瞰灣區全景。",
        sources=[],
        tags=["大阪", "地標", "夜景", "灣區"], priority=4),

    # 103  天保山 資料館
    att("天保山 資料館", "Tempozan Museum",
        "hidden_gem", "museum",
        zone="灣區", station="地下鐵大阪港", station_id="osaka_station_030",
        ticket="免費", duration="1~2小時",
        description="展示天保山周邊水域與港灣歷史的小型博物館，雲集舊照片、船舶模型與海洋生物標本，是認識大阪港灣發展史的去處。",
        sources=[],
        tags=["大阪", "博物館", "港灣", "灣區"], priority=4),

    # 104  洲筠 & 空寺
    att("空寺（Seiku-dera）", "Sakuratei",
        "hidden_gem", "temple",
        zone="貝塚", station="水間鐵道貝塚", station_id=None,
        ticket="免費", duration="1~2小時",
        description="泉州地區以「不去就會有難」傳說聞名的古寺，周邊有竹林與自然散步道，是當地人信仰的中心。",
        sources=[],
        tags=["大阪", "寺廟", "能量景點"], priority=4),

    # 105  岸和田 花街道
    att("岸和田 花街道", "Kishiwada Flower Road",
        "hidden_gem", "area",
        zone="岸和田", station="南海岸和田", station_id=None,
        ticket=None, duration="30分鐘~1小時",
        description="岸和田城周邊的散步道，春季櫻花夾道，秋季銀杏轉黃，是認識泉州歷史城下町風情的最佳起點。",
        sources=[],
        tags=["大阪", "賞櫻", "歷史", "散步"], priority=4),

    # 106  吹田 綠地 能量 Spot
    att("吹田 綠地 能量 Spot", "Suita Green Energy Spot",
        "hidden_gem", "nature",
        zone="吹田", station="JR吹田", station_id=None,
        ticket="免費", duration="1~2小時",
        description="以吹田自然觀察之林為中心的能量景點，有多處湧泉與濕地，是認識關西平野自然生態的教本地點。",
        sources=[],
        tags=["大阪", "自然", "賞鳥", "吹田"], priority=4),

    # 107  鶴橋 誠照寺
    att("鶴橋 誠照寺", "Tsuruhashi Jōshō-ji",
        "hidden_gem", "temple",
        zone="鶴橋", station="JR鶴橋", station_id="osaka_station_007",
        ticket="免費", duration="30分鐘",
        description="鶴橋韓國城附近的佛教寺院，保留了日治時期的建築風格，是認識在日朝鮮人社區宗教生活的低調去處。",
        sources=[],
        tags=["大阪", "寺廟", "歷史", "鶴橋"], priority=4),

    # 108  港住之江 綠地 運河展示
    att("運河展示廣場", "Canal Exhibition Plaza",
        "hidden_gem", "museum",
        zone="住之江", station="地下鐵住之江", station_id=None,
        ticket="免費", duration="1~2小時",
        description="以住之江運河歷史為主題的戶外展示廣場，有舊船隻、纜車與歷史解說牌，是認識大阪水運文化的水岸去處。",
        sources=[],
        tags=["大阪", "博物館", "運河", "免費"], priority=4),
]))

# ── 合併寫入 ────────────────────────────────────────────────────────────
print(f"\n新增景點：{len(new_attractions)} 個")

existing["attractions"].extend(new_attractions)
existing["updated"] = "2026-06-29"

with open(ATTR_PATH, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

os.chmod(ATTR_PATH, 0o644)
print(f"寫入完成：{ATTR_PATH}（共 {len(existing['attractions'])} 個景點）")
