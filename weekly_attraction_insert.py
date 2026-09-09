#!/usr/bin/env python3
"""Weekly attraction update 2026-09-09"""
import sqlite3, json

DB = "/var/repo/travel-planner/backend/travel.db"

# New attractions (pre-verified: names don't exist in DB)
NEW_ATTRACTIONS = [
    # ── SEOUL ──────────────────────────────────────────────────────────
    {
        "id": "seoul_attr_201", "region": "seoul", "station": "seoul_024",
        "name": "雲峴宮", "name_en": "Unhyeongung Palace",
        "category": "attraction", "zone": "鍾路",
        "location": "首爾特別市鍾路區三一大路464",
        "ticket": "免費（傳統表演另計）", "stay_duration": "1.5小時",
        "tags": json.dumps(["歷史", "宮殿", "韓劇拍攝地", "傳統表演"]),
        "description": "朝鮮時代興宣大院君的居住地，保存鬼面瓦當、洋館彩色玻璃窗等特色建築。每週日下午2點有傳統歌舞弓箭表演。《鬼怪》等知名韓劇拍攝地。",
        "sources": json.dumps(["https://koreanetour.com/seoul/?idx=177"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/雲峴宮", "blog_article": "https://rosaroundtheworld.com/insa-dong", "youtube": ""}),
    },
    {
        "id": "seoul_attr_202", "region": "seoul", "station": "seoul_024",
        "name": "耕仁美術館", "name_en": "Geumhorang Art Museum",
        "category": "attraction", "zone": "仁寺洞",
        "location": "首爾特別市鍾路區仁寺洞12街21",
        "ticket": "免費參觀（傳統茶及導覽另計）", "stay_duration": "1.5小時",
        "tags": json.dumps(["美術", "韓屋", "庭園", "茶院", "傳統工藝"]),
        "description": "傳統韓屋改建的美術館，中央為綠意盎然的庭園。展出傳統與現代藝術，室外展示場、室內展廳、御劍堂（韓中日刀具常設展）。年長者可報名參加傳統茶體驗。春秋季舉辦露天音樂會。",
        "sources": json.dumps(["https://gogolvyouqu.com/seoul-insadong-attractions"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/耕仁美術館", "blog_article": "https://gogolvyouqu.com/seoul-insadong-attractions", "youtube": ""}),
    },
    {
        "id": "seoul_attr_203", "region": "seoul", "station": "seoul_024",
        "name": "魚羅淵篆刻館", "name_en": "Eorayeon Seal Carving Workshop",
        "category": "hidden_gem", "zone": "仁寺洞",
        "location": "首爾特別市鍾路區仁寺洞街34 2樓",
        "ticket": "₩20,000（基礎班，含材料）", "stay_duration": "1.5小時",
        "tags": json.dumps(["篆刻", "工房", "體驗", "仁寺洞", "文創"]),
        "description": "老師傅根據生辰推薦韓文吉語，黑檀木在刻刀下翻飛成「福」「壽」紋樣。進階版可選用天然瑪瑙石。現場報名體驗。",
        "sources": json.dumps(["https://traveltokoreanow.com/insadong-cave-seoul"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/魚羅淵篆刻館", "blog_article": "https://traveltokoreanow.com/insadong-cave-seoul", "youtube": ""}),
    },
    {
        "id": "seoul_attr_204", "region": "seoul", "station": "seoul_024",
        "name": "仁寺洞宣傳館", "name_en": "Insadong Hanbok Experience Hall",
        "category": "hidden_gem", "zone": "仁寺洞",
        "location": "首爾特別市鍾路區仁寺洞11街19",
        "ticket": "₩30,000/2小時（韓服體驗）", "stay_duration": "2小時",
        "tags": json.dumps(["韓服", "體驗", "拍攝", "傳統", "文化"]),
        "description": "提供新羅時代宮廷款韓服租賃，配飾含金線繡雲肩與玉飾禁步。館內10+實景攝影點。開放時間09:30-18:30，韓服體驗10:00-17:30。",
        "sources": json.dumps(["https://traveltokoreanow.com/insadong-cave-seoul"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/仁寺洞宣傳館", "blog_article": "https://traveltokoreanow.com/insadong-cave-seoul", "youtube": ""}),
    },
    {
        "id": "seoul_attr_205", "region": "seoul", "station": "seoul_026",
        "name": "布帳馬車街", "name_en": "Pojangmacha Street (钟路3街)",
        "category": "hidden_gem", "zone": "鐘路",
        "location": "首爾特別市鍾路區鐘路3街站4號出口",
        "ticket": "免費參觀（餐飲自費）", "stay_duration": "1小時",
        "tags": json.dumps(["路邊攤", "美食", "夜市", "鐘路", "在地"]),
        "description": "鍾路3街站4號出口出來的布帳馬車（路邊帳篷小吃）聚集地，凌晨兩點仍座無虛席。推荐「鍾路嫂子」攤位辣炒年糕，₩3,000血腸湯鍋、₩5,000海鮮蔥餅。體驗道地首爾夜宵文化。",
        "sources": json.dumps(["https://traveltokoreanow.com/insadong-cave-seoul"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/布帳馬車街", "blog_article": "https://traveltokoreanow.com/insadong-cave-seoul", "youtube": ""}),
    },
    # ── BUSAN ─────────────────────────────────────────────────────────
    {
        "id": "busan_attr_050", "region": "busan", "station": "busan_027",
        "name": "札嘎其市場", "name_en": "Jagalchi Market",
        "category": "attraction", "zone": "南浦洞",
        "location": "釜山廣域市中区자갈치해안로 52",
        "ticket": "免費參觀（餐飲自費）", "stay_duration": "1.5小時",
        "tags": json.dumps(["海鮮", "市場", "南浦洞", "魚市場", "觀光"]),
        "description": "韓國最大規模水產市場之一，位於南浦洞海邊。不僅有珍稀魚種，海鮮加工廠及餐廳林立。一樓為水產攤，二樓為代客料理餐廳。可品嚐活生生的章魚、海鞘等道地海味。",
        "sources": json.dumps(["https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/札嘎其市場", "blog_article": "https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5", "youtube": ""}),
    },
    {
        "id": "busan_attr_051", "region": "busan", "station": "busan_029",
        "name": "バウノバ白山站", "name_en": "Baunova Baekseong Station",
        "category": "hidden_gem", "zone": "中央洞",
        "location": "釜山廣域市中区백산길 9",
        "ticket": "免費參觀（低消）", "stay_duration": "45分鐘",
        "tags": json.dumps(["咖啡", "老屋", "文青", "歷史建築"]),
        "description": "由南浦洞僅存的日治時期韓屋改建的星巴克概念店，2024年翻新後重新開幕。保留了原始韓屋的木造結構與庭院，室內環境幽靜，是感受老建築歲月痕跡的好去處。",
        "sources": json.dumps(["https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/バウノバ白山", "blog_article": "https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5", "youtube": ""}),
    },
    {
        "id": "busan_attr_052", "region": "busan", "station": "busan_042",
        "name": "海雲台午後海岸", "name_en": "Haeundae Beach Afternoon",
        "category": "hidden_gem", "zone": "海雲台",
        "location": "釜山廣域市海雲台区海雲台海邊路264",
        "ticket": "免費", "stay_duration": "1小時",
        "tags": json.dumps(["海灘", "海雲台", "下午", "海岸", "網美"]),
        "description": "海雲台海水浴場午後時段（14:00-17:00）陽光角度最佳，配合防波堤形成的獨特陰影線條，成為超人氣網美打卡時段。沙灘旁的BL Story咖啡廳提供二樓觀景座位。",
        "sources": json.dumps(["https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/海雲台BLStory", "blog_article": "https://www.kkday.com/ko/blog/23131/aisa-korea-busan-nampo-dong-best-spots-5", "youtube": ""}),
    },
    # ── FUKUOKA ────────────────────────────────────────────────────────
    {
        "id": "fukuoka_attr_110", "region": "fukuoka", "station": "fukuoka_004",
        "name": "福岡市赤煉瓦文化館", "name_en": "Fukuoka Red Brick Cultural Hall",
        "category": "hidden_gem", "zone": "天神",
        "location": "福岡縣福岡市中央區天神2-14-8",
        "ticket": "免費參觀", "stay_duration": "45分鐘",
        "tags": json.dumps(["洋風建築", "明治", "天神", "歷史", "文化"]),
        "description": "建於1932年的煉瓦造建築，原為日本生命保險九州分公司。現為文化設施，展示福岡的近代化歷程。紅磚外牆與精緻的室內裝潢重現1920-30年代氛圍，是天神地區推薦的隱藏版歷史建築。",
        "sources": json.dumps(["https://www.crossroadfukuoka.jp/tw/spot/12309"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/福岡市赤煉瓦文化館", "blog_article": "https://www.crossroadfukuoka.jp/tw/spot/12309", "youtube": ""}),
    },
    {
        "id": "fukuoka_attr_111", "region": "fukuoka", "station": "fukuoka_004",
        "name": "ACROS福岡 台階花園", "name_en": "ACROS Fukuoka Step Garden",
        "category": "hidden_gem", "zone": "天神",
        "location": "福岡縣福岡市中央區天神1-1-1",
        "ticket": "免費參觀", "stay_duration": "30分鐘",
        "tags": json.dumps(["都市綠洲", "天神", "免費", "建築", "自然"]),
        "description": "15層的台階式空中花園覆蓋建築外牆，種植大量植物與花卉。穿著西裝的上班族可在此午休放鬆。從天神地下街直通天神站的途中可順路參觀。",
        "sources": json.dumps(["https://www.crossroadfukuoka.jp/tw/spot/12309"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/ACROS福岡", "blog_article": "https://www.crossroadfukuoka.jp/tw/spot/12309", "youtube": ""}),
    },
    # ── OSAKA ──────────────────────────────────────────────────────────
    {
        "id": "osaka_attr_220", "region": "osaka", "station": "osaka_station_076",
        "name": "淀屋橋門塔", "name_en": "Yodayabashi Gate Tower",
        "category": "hidden_gem", "zone": "淀屋橋",
        "location": "大阪府大阪市北區中之島（淀屋橋站附近）",
        "ticket": "免費外觀（頂樓展望收費）", "stay_duration": "30分鐘",
        "tags": json.dumps(["2026新開幕", "淀屋橋", "近代建築", "水岸", "夜景"]),
        "description": "2026年夏季開幕的河畔新地標，頂樓設展望空間，可眺望堂島川水岸風光與中之島近代建築群。周邊保留大量1920-30年代的復興洋風建築群。是目前大阪最受關注的新散步路線。",
        "sources": json.dumps(["https://japantravel.navitime.com/zh-tw/area/jp/guide/NTJjtg2510079-zh-tw"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/淀屋橋門塔", "blog_article": "https://japantravel.navitime.com/zh-tw/area/jp/guide/NTJjtg2510079-zh-tw", "youtube": ""}),
    },
    # ── TOKYO ──────────────────────────────────────────────────────────
    {
        "id": "tokyo_attr_130", "region": "tokyo", "station": "tokyo_059",
        "name": "中目黑川沿岸", "name_en": "Nakameguro River Banks",
        "category": "attraction", "zone": "中目黑",
        "location": "東京都目黑區中目黑（各車站步行可達）",
        "ticket": "免費", "stay_duration": "1小時",
        "tags": json.dumps(["賞櫻", "河岸", "中目黑", "散步", "夜遊"]),
        "description": "目黑川沿岸約3.8公里的散步道，兩側種植約800棵櫻花樹，是東京首屈一指的賞櫻名點。夜櫻時分兩岸店家也會點燈，倒映水面的粉色燈光被譽為東京最美的賞櫻體驗之一。沿途有不少質感咖啡廳可小憩。",
        "sources": json.dumps(["https://travel.line.me/article/T1golaa9rp"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/中目黑川", "blog_article": "https://travel.line.me/article/T1golaa9rp", "youtube": ""}),
    },
    {
        "id": "tokyo_attr_131", "region": "tokyo", "station": "tokyo_089",
        "name": "下北澤一番街", "name_en": "Shimokitazawa Ichiban-gai (Shotengai)",
        "category": "hidden_gem", "zone": "下北澤",
        "location": "東京都世田谷區下北澤（小田急線下北澤站南口）",
        "ticket": "免費逛街", "stay_duration": "1.5小時",
        "tags": json.dumps(["古著", "街頭", "下北澤", "年輕文化", "小巷"]),
        "description": "從下北澤站南口出來即為一番街，短短200公尺的拱廊街道聚集了40間以上的古著店、二手唱片行與小酒吧。是東京次文化的重要地標，與附近的北澤小鎮與下北澤本通形成完整逛街區域。",
        "sources": json.dumps(["https://www.lucenashopping.com/?p=eonewcbpcwbxv9s_gkind14523974"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/下北澤一番街", "blog_article": "https://www.lucenashopping.com/?p=eonewcbpcwbxv9s_gkind14523974", "youtube": ""}),
    },
    # ── OKINAWA ────────────────────────────────────────────────────────
    {
        "id": "okinawa_attr_090", "region": "okinawa", "station": "okinawa_station_007",
        "name": "浮島通商店", "name_en": "Ukishima-dori Shopping Street",
        "category": "hidden_gem", "zone": "那霸",
        "location": "沖繩縣那霸市美榮橋站步行5分鐘",
        "ticket": "免費逛街", "stay_duration": "45分鐘",
        "tags": json.dumps(["小巷", "選物店", "咖啡", "那霸", "在地", "文青"]),
        "description": "被在地人稱為「裏國際通」的隱藏小巷，與國際通的觀光客氣氛截然不同。兩側約有20間獨立咖啡廳、選物店與手作雜貨小店舖，遊客稀少、氣氛悠閒。",
        "sources": json.dumps(["https://ayaca.tw/naha-attractions"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/浮島通", "blog_article": "https://ayaca.tw/naha-attractions", "youtube": ""}),
    },
    {
        "id": "okinawa_attr_091", "region": "okinawa", "station": "okinawa_station_008",
        "name": "福州園", "name_en": "Fuku-shu-en (Fujian Garden)",
        "category": "attraction", "zone": "那霸",
        "location": "沖繩縣那霸市久茂地2-29-1（縣廳前站步行7分鐘）",
        "ticket": "¥200", "stay_duration": "45分鐘",
        "tags": json.dumps(["中國風庭園", "免費WiFi", "縣廳前", "世界遺產關聯", "安靜"]),
        "description": "仿照中國福州風格建造的回遊式庭園，1992年為紀念那霸市與福州締結友好城市10週年而建。佔地約1.7公頃，庭園內有小橋、流水與傳統建築。與周邊的現代化國際通相比，彷彿置身另一個世界。",
        "sources": json.dumps(["https://ayaca.tw/naha-attractions"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/福州園", "blog_article": "https://ayaca.tw/naha-attractions", "youtube": ""}),
    },
    {
        "id": "okinawa_attr_092", "region": "okinawa", "station": "okinawa_station_009",
        "name": "市場本通", "name_en": "Ichiba-hondori (Market Main Street)",
        "category": "hidden_gem", "zone": "那霸",
        "location": "沖繩縣那霸市松尾2（牧志站步行6分鐘）",
        "ticket": "免費逛街（餐飲自費）", "stay_duration": "45分鐘",
        "tags": json.dumps(["市場", "那霸", "在地的", "生活", "小店"]),
        "description": "從國際通通往第一牧志公設市場的主要通道，是僅見於那霸的拱廊式狹窄商街。兩側林立著生活用品、傳統食材與服飾小店，保有濃厚的市場氛圍與生活感。極少外國觀光客涉足。",
        "sources": json.dumps(["https://ayaca.tw/naha-attractions"]),
        "details": json.dumps({"google_maps": "https://maps.app.goo.gl/市場本通", "blog_article": "https://ayaca.tw/naha-attractions", "youtube": ""}),
    },
]


def get_next_id(cur, region):
    """Generate next sequential ID for a region."""
    cur.execute("SELECT id FROM attractions WHERE region_code = ? ORDER BY id DESC LIMIT 1", (region,))
    row = cur.fetchone()
    if not row:
        return f"{region}_attr_001"
    last_id = row[0]
    # Try to extract numeric suffix
    import re
    m = re.search(r'(\d+)$', last_id)
    if m:
        num = int(m.group(1)) + 1
        prefix = last_id[:m.start()]
        return f"{prefix}{num:03d}"
    return f"{last_id}_new"


def insert_attractions():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    added = 0
    skipped = 0
    errors = []

    for a in NEW_ATTRACTIONS:
        # Check duplicate by name (case-insensitive) within region
        cur.execute(
            "SELECT 1 FROM attractions WHERE region_code=? AND LOWER(name)=LOWER(?)",
            (a["region"], a["name"])
        )
        if cur.fetchone():
            skipped += 1
            print(f"  SKIP (name exists): {a['region']}/{a['name']}")
            continue

        # Generate new ID (avoid conflict)
        new_id = a["id"]
        cur.execute("SELECT 1 FROM attractions WHERE id=?", (new_id,))
        if cur.fetchone():
            new_id = get_next_id(cur, a["region"])

        try:
            cur.execute("""
                INSERT INTO attractions (
                    id, region_code, station_id, name, name_en, category,
                    zone, location, ticket, stay_duration, tags,
                    description, sources, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_id, a["region"], a["station"], a["name"], a.get("name_en"),
                a["category"], a["zone"], a.get("location"), a.get("ticket"),
                a.get("stay_duration"), a.get("tags"), a.get("description"),
                a.get("sources"), a.get("details")
            ))
            added += 1
            print(f"  ADDED: {a['region']}/{a['name']} ({new_id})")
        except Exception as e:
            errors.append(f"[{a['name']}]: {e}")
            print(f"  ERROR [{a['name']}]: {e}")

    conn.commit()
    conn.close()
    return added, skipped, errors


if __name__ == "__main__":
    print("Starting weekly attraction insert...")
    added, skipped, errors = insert_attractions()
    print(f"\nResult: Added={added}, Skipped={skipped}, Errors={len(errors)}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
