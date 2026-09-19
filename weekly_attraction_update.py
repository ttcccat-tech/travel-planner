#!/usr/bin/env python3
"""
Weekly Attraction Update Script
Inserts new hidden gem / local attractions into SQLite for 6 regions.
"""

import sqlite3, json, hashlib, re
from datetime import datetime

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

def get_station_id(region_code: str, station_name_hint: str) -> str:
    """Find best matching station_id for a given station name hint."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM stations WHERE region_code=? AND name LIKE ? LIMIT 1",
        (region_code, f"%{station_name_hint}%")
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def attraction_exists(name: str, region_code: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM attractions WHERE name=? AND region_code=? LIMIT 1",
        (name, region_code)
    )
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def short_id(name: str) -> str:
    """Generate a short ID from the name."""
    # Remove non-alphanumeric, take first 8 chars, lowercase
    clean = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', name)
    return clean[:12].lower()

def insert_attraction(
    region_code: str,
    station_id: str,
    name: str,
    name_en: str,
    category: str,
    sub_category: str,
    zone: str,
    location: str,
    description: str,
    ticket: str,
    stay_duration: str,
    priority: int,
    tags: list,
    sources: list,
    details: dict,
    nearby_stations: list,
):
    """Insert an attraction if it doesn't already exist."""
    if attraction_exists(name, region_code):
        print(f"  SKIP (exists): {name}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    att_id = short_id(name)
    # Handle duplicate IDs by appending counter
    counter = 1
    original_id = att_id
    while True:
        cur.execute("SELECT 1 FROM attractions WHERE id=?", (att_id,))
        if not cur.fetchone():
            break
        att_id = f"{original_id}_{counter}"
        counter += 1

    details_json = json.dumps(details, ensure_ascii=False)
    tags_json = json.dumps(tags, ensure_ascii=False)
    sources_json = json.dumps(sources, ensure_ascii=False)
    nearby_stations_json = json.dumps(nearby_stations, ensure_ascii=False)

    cur.execute("""
        INSERT INTO attractions (
            id, region_code, station_id, name, name_en, category, sub_category,
            zone, location, lat, lng, ticket, stay_duration,
            need_reservation, cash_only, priority, tags, description,
            sources, nearby_stations, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        att_id, region_code, station_id, name, name_en, category, sub_category,
        zone, location, None, None, ticket, stay_duration,
        0, 0, priority,
        tags_json, description,
        sources_json, nearby_stations_json, details_json
    ))
    conn.commit()
    conn.close()
    print(f"  INSERTED [{att_id}]: {name} (station={station_id})")
    return True


def main():
    new_count = 0
    stations_used = set()

    print("=" * 60)
    print("TOKYO attractions")
    print("=" * 60)

    tokyo_data = [
        # name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby_stations, station_hint
        ("MIKAN下北", "MIKAN Shimokitazawa", "complex", "下北澤", "東京都世田谷区北沢2-1054-12",
         "2024年開幕的複合商業設施，聚集古著店、多國籍餐飲、工作空間，位於下北澤站高架下，分A~E五個街區。",
         "免費（店鋪消費）", "1-2小時", 3,
         ["文青", "古著", "咖啡", "複合設施"],
         ["https://mikan-shimokita.jp/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/MIKAN%E4%B8%8B%E5%8C%97", "youtube": ""},
         [],
         "下北澤"),
        ("reload 下北澤", "reload", "complex", "下北澤", "東京都世田谷区北沢3-19-20",
         "位於下北線路街的複合設施，約20間風格小店聚集，白色2層樓建築一字排開，概念是「看得見店主臉孔的個性小店街」。",
         "免費", "1-1.5小時", 3,
         ["文青", "小店", "散步"],
         ["https://reload.jp/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/reload", "youtube": ""},
         [],
         "下北澤"),
        ("下北線路街 空地", "Shimokitazawa Rojiara", "open_space", "下北澤", "東京都世田谷区北沢2-33-12附近",
         "以「自由遊樂場」為概念的開放空間，常有市集、餐車、快閃活動，設有草地區、活動區及常設的「空地咖啡」。",
         "免費", "30分-1小時", 4,
         ["市集", "免費", "散步"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B8%8B%E5%8C%97%E7%B7%9A%E8%B7%AF%E8%A1%97", "youtube": ""},
         [],
         "下北澤"),
        ("北澤八幡神社", "Kitazawa Hachimangu", "shrine", "下北澤", "東京都世田谷区北沢3-9-1",
         "隱身在下北澤街區一角的神社，境內清幽、人潮相對少，從熱鬧商店街步行過來瞬間轉換成安靜氛圍，適合想暫時避開喧鬧的旅客。",
         "免費", "30分鐘", 4,
         ["神社", "免費", "在地"],
         ["https://www.jinja.jp/kitazawa-hachiman/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E5%8C%97%E6%B2%B3%E5%85%AB%E5%B9%B3%E7%A5%9E%E7%A4%BE", "youtube": ""},
         [],
         "下北澤"),
        ("馬事公苑", "Bajishikoen (Horse Riding Ground)", "park", "下北澤", "東京都世田谷区上用賀2-1-1",
         "讓人與馬匹交流的場所，平日有觸摸體驗區及馬匹走秀、迷你馬賽馬等活動，苑內以梅花、櫻花聞名，距離下北澤站較遠但可安排順遊。",
         "免費", "1-2小時", 3,
         ["公園", "馬匹", "自然"],
         ["https://www.jra.go.jp/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E9%A6%AC%E4%BA%8B%E5%85%AC%E8%8B%91", "youtube": ""},
         [],
         "下北澤"),
    ]

    for row in tokyo_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("tokyo", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "tokyo", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print("OSAKA attractions")
    print("=" * 60)

    osaka_data = [
        ("木津市場", "Kozo Market (Kiyo Market)", "market", "難波", "大阪市浪速区敷津東2-2-8",
         "擁有300年以上歷史的老市場，比黑門市場更在地的傳統市場，清晨五點開始營業，在地人經常前往採買海鮮、蔬菜。",
         "免費（消費另計）", "1-2小時", 3,
         ["市場", "海鮮", "在地"],
         ["https://www.kichi1208.com/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E6%9C%A8%E6%B4%81%E5%B8%82%E5%A0%B4", "youtube": ""},
         [],
         "難波"),
        ("大阪生活今昔館", "Osaka Museum of Housing and Living", "museum", "天神橋筋", "大阪市北区天神橋6-4-20",
         "日本首座以大阪「居住和生活」為主題的博物館，室內重現江戶時代大阪街道，燈光定時切換日夜，付費可穿和服體驗。",
         "大人600円", "1-1.5小時", 3,
         ["博物館", "江戶", "文化"],
         ["https://www.osaka-chikumugu.com/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E5%A4%A7%E9%98%AA%E7%94%9F%E6%B4%8B%E4%BB%8A%E9%A4%A8", "youtube": ""},
         [],
         "天神橋筋六丁目"),
        ("中崎町", "Nakazaki-cho", "area", "大阪", "大阪市北区中崎町",
         "保留昭和老長屋改建的咖啡廳與雜貨店的深度散步區，是大阪年輕人喜愛的隱蔽街區，巷弄氣氛悠閒。",
         "免費", "1.5-2小時", 4,
         ["老街", "咖啡", "散步"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B8%AD%E5%B4%96%E5%8C%BD", "youtube": ""},
         [],
         "大阪"),
        ("中之島美術館", "Nakanoshima Museum of Art", "museum", "大阪", "大阪市北区中之島4-3-1",
         "2022年開幕的美術館，收藏日本近代美術作品，建築由遠藤克彦設計，是大阪新文化地標。",
         "依展覽", "1-2小時", 3,
         ["美術館", "近代美術"],
         ["https://www.nakanoshima museum.jp/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B8%AD%E4%B9%8B%E5%B3%B6%E7%BE%8E%E8%A1%93%E9%A4%A8", "youtube": ""},
         [],
         "淀屋橋"),
    ]

    for row in osaka_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("osaka", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "osaka", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print("SEOUL attractions")
    print("=" * 60)

    seoul_data = [
        ("乙支路小巷", "Euljiro Alley", "area", "乙支路", "首爾特別市中區乙支路3街一帶",
         "越迷路越有趣的魅力空間，列為城市整備型重建區。印刷廠與文青空間共生，巷弄中隱藏許多沒有招牌的神秘小店如「小心頭部」。",
         "免費", "1-2小時", 4,
         ["小巷", "文青", "在地"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B9%99%E6%94%AF%E8%B7%AF%E5%B0%8F%E5%B8%98", "youtube": ""},
         [],
         "乙支路3街"),
        ("世運商街", "Saeunmall / Sejun Shopping Area", "shopping_street", "乙支路", "首爾特別市中區清溪川路5街附近",
         "1970年代曾因韓國首座商住兩用建築而繁榮一時的電子產業地標，透過空中步行橋重新與大林商街連結，成為新的文化活動空間。",
         "免費", "1小時", 3,
         ["商店街", "電子", "懷舊"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B8%96%E9%81%8B%E5%95%86%E8%A1%97", "youtube": ""},
         [],
         "乙支路3街"),
        ("Vacance Coffee", "Vacance Coffee", "cafe", "乙支路", "首爾特別市中區乙支路入口站 羅真大廈9樓",
         "隱身在1960年代老建築9樓的純白咖啡廳，擁有落地窗可俯瞰首爾繁華辦公大樓，招牌Vacance Latte漸層咖啡以藍柑橘糖漿聞名。",
         "飲料1000-2000韓元", "30分-1小時", 4,
         ["咖啡", "景觀", "隱蔽"],
         ["https://www.instagram.com/vacance.coffee/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/Vacance+Coffee", "youtube": ""},
         [],
         "乙支路入口"),
        ("聖水洞", "Seongsu-dong", "area", "聖水", "首爾市城東區聖水洞",
         "被譽為「首爾的布魯克林」，改建倉庫成為的咖啡廳與概念商店聚集，街頭攝影天堂，工業風與時尚藝術結合。",
         "免費", "2-3小時", 3,
         ["文青", "咖啡", "工業風"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E8%81%96%E6%B0%B4%E6%B4%9E", "youtube": ""},
         [],
         "聖水"),
    ]

    for row in seoul_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("seoul", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "seoul", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print("FUKUOKA attractions")
    print("=" * 60)

    fukuoka_data = [
        ("TOTO博物館", "TOTO Museum", "museum", "小倉", "北九州市小倉北区中島2-1-1",
         "為慶祝TOTO創立100周年於2015年開幕，展出馬桶與陶瓷器的發展歷史，是相當受歡迎的免費景點，離小倉城不遠。",
         "免費", "1-1.5小時", 3,
         ["博物館", "免費", "知識"],
         ["https://www.toto.jp/museum/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/TOTO%E5%8D%9A%E7%89%A9%E9%A4%A8", "youtube": ""},
         [],
         "小倉"),
        ("北九州市漫畫博物館", "Kitakyushu Manga Museum", "museum", "小倉", "北九州市小倉北区米町1-1-1 Aruaru City 5F",
         "以漫畫為主題的專門博物館，常設展介紹漫畫歷史，漫畫圖書室可閱讀大量漫畫，適合動漫愛好者。",
         "大人800円", "1.5-2小時", 3,
         ["博物館", "漫畫", "動漫"],
         ["https://www.kitakyushu-manga.jp/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E5%8C%97%E4%B9%8D%E5%B7%9E%E5%B8%82%E6%BC%AB%E7%94%BB%E5%8D%9A%E7%89%A9%E9%A4%A8", "youtube": ""},
         [],
         "小倉"),
        ("久留米杜鵑公園", "Kurume Azalea Park", "park", "久留米", "久留米市山rof南側",
         "以久留米杜鵑聞名，約100個品種、61,000株杜鵑花競相盛開，同時也是適合健行的自然公園。久留米市是世界知名久留米杜鵑的發源地。",
         "免費", "1.5-2小時", 3,
         ["公園", "杜鵑", "自然"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E4%B9%99%E3%81%97%E3%83%A1%E6%9D%BE%E5%8D%97%E8%8A%B1%E5%9C%92", "youtube": ""},
         [],
         "久留米"),
    ]

    for row in fukuoka_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("fukuoka", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "fukuoka", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print("BUSAN attractions")
    print("=" * 60)

    busan_data = [
        ("白淺灘文化村", "Huinnyeoul Culture Village", "cultural_village", "影島", "釜山廣域市影島區影島洞",
         "曾為低收入戶與戰爭避難者聚落，2011年起推行都市再生計畫，注入藝術元素打造成藝術村。擁有峭壁山城地形與無敵海景，步道縱橫14條胡同巷弄。",
         "免費", "2-3小時", 3,
         ["藝術村", "海岸", "在地"],
         ["https://www.huinneoul.com/"],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E7%99%BD%E6%B5%85%E7%81%91%E6%96%87%E5%8C%96%E6%9D%91", "youtube": ""},
         [],
         "南浦"),
        ("BIFF廣場", "BIFF Square (Busan Int'l Film Festival Plaza)", "plaza", "南浦洞", "釜山廣域市中区光復路一帶",
         "釜山國際電影節的主要場地，廣場上有眾多電影人的手印和銅像，平時是旅客與在地人的休閒去處，周圍有許多餐廳和街頭小吃攤。",
         "免費", "30分-1小時", 3,
         ["電影", "廣場", "小吃"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/BIFF%E5%BB%A3%E5%A0%B4", "youtube": ""},
         [],
         "札嘎其"),
        ("富平罐頭市場", "Bupyeong (Jagalchi) Canned Food Market", "market", "南浦洞", "釜山廣域市中区南浦洞",
         "比札嘎其市場更在地的傳統市場，晚間變身為繁華夜市，有各式小吃攤、當季水果（草莓），是體驗釜山庶民生活的好去處。",
         "免費（小吃消費）", "1小時", 4,
         ["市場", "小吃", "夜市"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E5%AF%8C%E5%B9%B3%E7%BD%90%E9%A0%AD%E5%B8%82%E5%A0%B4", "youtube": ""},
         [],
         "札嘎其"),
    ]

    for row in busan_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("busan", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "busan", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print("OKINAWA attractions")
    print("=" * 60)

    okinawa_data = [
        ("知念岬公園", "Chinen Misaki Park", "park", "知念", "沖繩縣南城市知念久手堅",
         "三面被太平洋環繞的絕美海岬，可遠眺琉球聖地久高島與一望無際的海平面，是沖繩南部觀海的絕佳地點。",
         "免費", "30分-1小時", 3,
         ["海岬", "海景", "免費"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E7%9F%A5%E5%BF%B5%E5%B2%9A%E5%85%AC%E5%9C%92", "youtube": ""},
         [],
         "知念"),
        ("泊港漁市場", "Tominato Fish Market", "market", "那霸", "沖繩縣那霸市港町2-3-1",
         "那霸重要的鮮魚市場，每日鮪魚漁獲量可達50公噸，沒有冷凍過非常新鮮。24間店鋪供應生魚片、壽司、海鮮丼等，CP值極高。",
         "免費（海鮮消費）", "1-1.5小時", 3,
         ["市場", "海鮮", "在地名物"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E6%B3%8A%E6%B8%AF%E9%87%9C%E5%B8%82%E5%A0%B4", "youtube": ""},
         [],
         "縣廳前"),
        ("玉城城跡", "Tamagusuku Castle Ruins", "castle_ruins", "南城", "沖繩縣南城市玉城136",
         "海拔180公尺的古城跡，相傳由創造琉球群島的創世女神Amamikiyo建造，曾是琉球王室Amamikiyo朝聖之旅的一站，可俯瞰久高島。",
         "免費", "1-1.5小時", 3,
         ["城跡", "世界遺產", "歷史"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E7%8E%89%E5%9F%8E%E5%9F%8E%E8%B7%A1", "youtube": ""},
         [],
         "南城"),
        ("平和通商店街", "Heiwadori Shopping Street", "shopping_street", "那霸", "沖繩縣那霸市松尾",
         "與第一牧志公設市場相連的拱廊商店街，匯聚在地餐廳、藥妝、超市，氣氛比國際通更為悠閒，保有濃厚的在地生活感。",
         "免費", "1小時", 4,
         ["商店街", "購物", "美食"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E5%B9%B3%E5%92%8C%E9%80%9A%E5%95%86%E5%BA%97%E8%A1%97", "youtube": ""},
         [],
         "牧志"),
        ("福州園", "Fukuishien Garden", "garden", "那霸", "沖繩縣那霸市泉崎1-29-3",
         "模仿中國福州風格建造的迴遊式庭園，1992年為紀念那霸與福州結為友好城市而建，環境清幽，是那霸市區內的寧靜角落。",
         "免費", "30分鐘", 4,
         ["庭園", "免費", "中國風"],
         [],
         {"blog_article": "", "google_maps": "https://www.google.com/maps/place/%E7%A6%8F%E5%B7%9E%E5%9C%92", "youtube": ""},
         [],
         "旭橋"),
    ]

    for row in okinawa_data:
        (name, name_en, sub_cat, zone, location, desc, ticket, stay, priority, tags, sources, details, nearby, station_hint) = row
        sid = get_station_id("okinawa", station_hint)
        if not sid:
            print(f"  SKIP (no station match): {name}")
            continue
        ok = insert_attraction(
            "okinawa", sid, name, name_en, "hidden_gem", sub_cat, zone, location,
            desc, ticket, stay, priority, tags, sources, details, nearby
        )
        if ok:
            new_count += 1
            stations_used.add(sid)

    print()
    print("=" * 60)
    print(f"SUMMARY: {new_count} new attractions inserted from {len(stations_used)} stations")
    print(f"Stations used: {sorted(stations_used)}")
    print("=" * 60)

    # Final count per region
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print()
    print("Attractions per region after update:")
    cur.execute("SELECT region_code, COUNT(*) FROM attractions GROUP BY region_code ORDER BY region_code")
    for (r, c) in cur.fetchall():
        print(f"  {r}: {c}")
    conn.close()

if __name__ == "__main__":
    main()
