#!/usr/bin/env python3
"""
generate_stations.py — 自動建立各地區的 stations.json
使用 OpenStreetMap Nominatim API 查詢車站座標

用法：
  python3 scripts/generate_stations.py --region osaka
  python3 scripts/generate_stations.py --region fukuoka
  python3 scripts/generate_stations.py --region tokyo
  python3 scripts/generate_stations.py --region kyushu
  python3 scripts/generate_stations.py --region all     # 全部執行
"""

import json
import urllib.request
import urllib.parse
import time
import argparse
import os
import sys

# ---------- 各地區車站名單（慢慢補）----------

STATION_LISTS = {
    "osaka": [
        # JR 西日本
        {"name": "大阪（ Osaka）", "name_en": "Osaka Station", "company": "JR", "line": ["JR大阪環狀線", "JR京都線", "JR神戶線"], "zone": "梅田"},
        {"name": "新大阪", "name_en": "Shin-Osaka Station", "company": "JR", "line": ["JR京都線", "JR神戶線", "東海道新幹線"], "zone": "新大阪"},
        {"name": "天王寺", "name_en": "Tennoji Station Osaka", "company": "JR", "line": ["JR大阪環狀線", "JR關西機場線", "JR和歌山線"], "zone": "天王寺"},
        {"name": "難波（JR）", "name_en": "JR Namba Station", "company": "JR", "line": ["JR大和路線"], "zone": "難波"},
        {"name": "新今宮", "name_en": "Shin-Imamiya Station", "company": "JR", "line": ["JR大阪環狀線", "JR關西機場線"], "zone": "新今宮"},
        {"name": "鶴橋", "name_en": "Tsuruhashi Station", "company": "JR", "line": ["JR大阪環狀線", "JR關西機場線"], "zone": "鶴橋"},
        {"name": "京橋", "name_en": "Kyobashi Station Osaka", "company": "JR", "line": ["JR大阪環狀線", "JR片町線"], "zone": "京橋"},
        {"name": "大阪城公園", "name_en": "Osakajokoen Station", "company": "JR", "line": ["JR大阪環狀線"], "zone": "大阪城"},
        {"name": "環球城", "name_en": "Universal-City Station Osaka", "company": "JR", "line": ["JRゆめ咲線"], "zone": "環球城"},
        {"name": "西九條", "name_en": "Nishikujo Station", "company": "JR", "line": ["JR大阪環狀線", "JRゆめ咲線"], "zone": "西九條"},
        # 地下鐵 御堂筋線
        {"name": "江坂", "name_en": "Esaka Station", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "江坂"},
        {"name": "淀屋橋", "name_en": "Yodoyabashi Station", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "淀屋橋"},
        {"name": "心齋橋", "name_en": "Shinsaibashi Station", "company": "地下鐵", "line": ["地下鐵御堂筋線", "地下鐵四橋線"], "zone": "心齋橋"},
        {"name": "難波（地下鐵）", "name_en": "Namba Station Osaka Metro", "company": "地下鐵", "line": ["地下鐵御堂筋線", "地下鐵四橋線", "地下鐵千日前線"], "zone": "難波"},
        {"name": "天王寺（地下鐵）", "name_en": "Tennoji Station Osaka Metro", "company": "地下鐵", "line": ["地下鐵御堂筋線", "地下鐵谷町線"], "zone": "天王寺"},
        # 地下鐵 四橋線
        {"name": "西大橋", "name_en": "Nishi-Ohashi Station", "company": "地下鐵", "line": ["地下鐵四橋線"], "zone": "西大橋"},
        {"name": "玉出", "name_en": "Tamedani Station", "company": "地下鐵", "line": ["地下鐵四橋線"], "zone": "玉出"},
        # 地下鐵 谷町線
        {"name": "東天滿", "name_en": "Higashi-Temma Station", "company": "地下鐵", "line": ["地下鐵谷町線"], "zone": "東天滿"},
        {"name": "天神橋筋六丁目", "name_en": "Tenjinbashi-Suji Station", "company": "地下鐵", "line": ["地下鐵谷町線"], "zone": "天神橋"},
        # 地下鐵 鶴見綠地線
        {"name": "京橋（地下鐵）", "name_en": "Kyobashi Station Osaka Metro", "company": "地下鐵", "line": ["地下鐵鶴見綠地線"], "zone": "京橋"},
        # 地下鐵 中央線
        {"name": "大阪港", "name_en": "Osakako Station", "company": "地下鐵", "line": ["地下鐵中央線"], "zone": "大阪港"},
        {"name": "宇宙廣場", "name_en": "Cosmo-Square Station", "company": "地下鐵", "line": ["地下鐵中央線"], "zone": "宇宙廣場"},
        # 地下鐵 千日前線
        {"name": "野田籐井", "name_en": "Noda-Fujita Station", "company": "地下鐵", "line": ["地下鐵千日前線"], "zone": "野田"},
        {"name": "日本橋", "name_en": "Nippombashi Station Osaka", "company": "地下鐵", "line": ["地下鐵千日前線", "地下鐵堺筋線"], "zone": "日本橋"},
        # 地下鐵 堺筋線
        {"name": "惠美須町", "name_en": "Ebisucho Station", "company": "地下鐵", "line": ["地下鐵堺筋線"], "zone": "惠美須町"},
        # 地下鐵 長堀鶴見綠地線
        {"name": "大正", "name_en": "Taisho Station Osaka", "company": "地下鐵", "line": ["地下鐵長堀鶴見綠地線"], "zone": "大正"},
        # 南海電鐵
        {"name": "難波（南海）", "name_en": "Namba Station Nankai", "company": "南海", "line": ["南海高野線", "南海空港線"], "zone": "難波"},
        {"name": "天下茶屋", "name_en": "Tengachaya Station", "company": "南海", "line": ["南海高野線", "地下鐵堺筋線"], "zone": "天下茶屋"},
        # 阪神電車
        {"name": "大阪難波（阪神）", "name_en": "Hanshin Namba Station", "company": "阪神", "line": ["阪神難波線"], "zone": "難波"},
        # 近鐵
        {"name": "大阪上本町", "name_en": "Osaka-Uehonmachi Station", "company": "近鐵", "line": ["近鐵大阪線", "近鐵奈良線"], "zone": "上本町"},
        # 泉北高速鐵道
        {"name": "中和岡", "name_en": "Chuo-Oka Station", "company": "泉北", "line": ["泉北高速鐵道線"], "zone": "泉北"},
    ],

    "fukuoka": [
        # JR 九州
        {"name": "博多", "name_en": "Hakata Station Fukuoka", "company": "JR", "line": ["JR九州新幹線", "JR鹿兒島線", "JR篠栗線"], "zone": "博多"},
        {"name": "小倉", "name_en": "Kokura Station", "company": "JR", "line": ["JR九州新幹線", "JR鹿兒島線", "JR日豐本線"], "zone": "小倉"},
        {"name": "久留米", "name_en": "Kurume Station", "company": "JR", "line": ["JR九州新幹線", "JR久大本線", "JR篠栗線"], "zone": "久留米"},
        {"name": "新鳥栖", "name_en": "Shin-Tosu Station", "company": "JR", "line": ["JR九州新幹線"], "zone": "鳥栖"},
        # 地下鐵 機場線
        {"name": "天神", "name_en": "Tenjin Station Fukuoka", "company": "地下鐵", "line": ["地下鐵機場線", "地下鐵七隈線"], "zone": "天神"},
        {"name": "博多（地下鐵）", "name_en": "Hakata Station Fukuoka Metro", "company": "地下鐵", "line": ["地下鐵機場線", "地下鐵箱崎線"], "zone": "博多"},
        {"name": "祇園（福岡）", "name_en": "Gion Station Fukuoka", "company": "地下鐵", "line": ["地下鐵機場線"], "zone": "祇園"},
        {"name": "中洲川端", "name_en": "Nakasukawabata Station", "company": "地下鐵", "line": ["地下鐵機場線", "地下鐵箱崎線"], "zone": "中洲"},
        {"name": "福岡機場", "name_en": "Fukuoka Airport Station", "company": "地下鐵", "line": ["地下鐵機場線"], "zone": "機場"},
        # 西日本鐵道
        {"name": "西鐵福岡（天神）", "name_en": "Nishitetsu Fukuoka Station", "company": "西鐵", "line": ["西鐵天神大牟田線"], "zone": "天神"},
        {"name": "西鐵小倉", "name_en": "Nishitetsu Kokura Station", "company": "西鐵", "line": ["西鐵天神大牟田線"], "zone": "小倉"},
        {"name": "柳川（西鐵）", "name_en": "Yanagawa Station", "company": "西鐵", "line": ["西鐵天神大牟田線"], "zone": "柳川"},
        # JR 鹿兒島線
        {"name": "門司港", "name_en": "Mojiko Station", "company": "JR", "line": ["JR鹿兒島線"], "zone": "門司港"},
        {"name": "折尾", "company": "JR", "line": ["JR鹿兒島線", "JR筑豐本線"], "zone": "折尾", "name_en": "Orio Station"},
        {"name": "黑崎機場", "name_en": "Kurosaki-Mae Station", "company": "JR", "line": ["JR鹿兒島線"], "zone": "黑崎"},
    ],

    "tokyo": [
        # JR 中央線 / 總武線
        {"name": "東京", "name_en": "Tokyo Station", "company": "JR", "line": ["JR中央線", "JR山手線", "JR東海道線", "JR東北線"], "zone": "東京"},
        {"name": "新宿", "name_en": "Shinjuku Station", "company": "JR", "line": ["JR中央線", "JR山手線", "JR小田急線"], "zone": "新宿"},
        {"name": "秋葉原", "name_en": "Akihabara Station", "company": "JR", "line": ["JR中央線", "JR山手線", "JR總武線"], "zone": "秋葉原"},
        {"name": "四谷", "name_en": "Yotsuya Station", "company": "JR", "line": ["JR中央線", "東京地下鐵丸之內線"], "zone": "四谷"},
        {"name": "代代木", "name_en": "Yoyogi Station", "company": "JR", "line": ["JR中央線", "JR山手線"], "zone": "代代木"},
        # JR 山手線
        {"name": "品川", "name_en": "Shinagawa Station", "company": "JR", "line": ["JR山手線", "JR京濱東北線", "JR東海道線"], "zone": "品川"},
        {"name": "上野", "name_en": "Ueno Station", "company": "JR", "line": ["JR山手線", "JR京濱東北線", "JR東北線"], "zone": "上野"},
        {"name": "池袋", "name_en": "Ikebukuro Station", "company": "JR", "line": ["JR山手線", "JR京濱東北線", "東武東上線", "西武池袋線"], "zone": "池袋"},
        {"name": "澀谷", "name_en": "Shibuya Station", "company": "JR", "line": ["JR山手線", "JR湘南新宿線", "東京地下鐵銀座線", "東京地下鐵半藏門線", "東京地下鐵副都心線", "京王井之頭線", "東鐵東横線"], "zone": "澀谷"},
        {"name": "原宿", "name_en": "Harajuku Station", "company": "JR", "line": ["JR山手線", "東京地下鐵千代田線", "東京地下鐵副都心線"], "zone": "原宿"},
        {"name": "表參道", "name_en": "Omotesando Station", "company": "JR", "line": ["東京地下鐵銀座線", "東京地下鐵半藏門線", "東京地下鐵千代田線"], "zone": "表參道"},
        {"name": "新橋", "name_en": "Shimbashi Station", "company": "JR", "line": ["JR山手線", "JR京濱東北線", "JR東海道線", "百合鷗號"], "zone": "新橋"},
        {"name": "惠比壽", "name_en": "Ebisu Station Tokyo", "company": "JR", "line": ["JR山手線"], "zone": "惠比壽"},
        {"name": "五反田", "name_en": "Gotanda Station", "company": "JR", "line": ["JR山手線", "都營淺草線"], "zone": "五反田"},
        {"name": "高田馬場", "name_en": "Takadanobaba Station", "company": "JR", "line": ["JR山手線", "東京地下鐵東西線"], "zone": "高田馬場"},
        {"name": "目白", "name_en": "Mejiro Station", "company": "JR", "line": ["JR山手線"], "zone": "目白"},
        # 都營地下鐵
        {"name": "淺草（都營）", "name_en": "Asakusa Station Tokyo", "company": "都營", "line": ["都營淺草線", "東京地下鐵銀座線", "東武晴空塔線"], "zone": "淺草"},
        {"name": "押上", "name_en": "Oshiage Station", "company": "都營", "line": ["都營淺草線", "東京地下鐵半藏門線", "東武晴空塔線"], "zone": "押上"},
        {"name": "日本橋（都營）", "name_en": "Nihonbashi Station Tokyo", "company": "都營", "line": ["都營淺草線", "東京地下鐵銀座線", "東京地下鐵東西線"], "zone": "日本橋"},
        {"name": "人形町（都營）", "name_en": "Ningyocho Station", "company": "都營", "line": ["都營淺草線", "東京地下鐵日比谷線"], "zone": "人形町"},
        {"name": "清澄白河", "name_en": "Kiyosumi-Shirakawa Station", "company": "都營", "line": ["都營大江戶線", "東京地下鐵半藏門線"], "zone": "清澄白河"},
        {"name": "兩國", "name_en": "Ryogoku Station", "company": "都營", "line": ["都營大江戶線", "JR總武線"], "zone": "兩國"},
        {"name": "藏前", "name_en": "Kuramae Station", "company": "都營", "line": ["都營淺草線", "都營大江戶線"], "zone": "藏前"},
        # 東京 Metro
        {"name": "大手町", "name_en": "Otemachi Station Tokyo", "company": "東京Metro", "line": ["東京地下鐵丸之內線", "東京地下鐵東西線", "東京地下鐵千代田線", "東京地下鐵半藏門線", "都營三田線"], "zone": "大手町"},
        {"name": "日比谷", "name_en": "Hibiya Station", "company": "東京Metro", "line": ["東京地下鐵日比谷線", "東京地下鐵千代田線", "都營三田線"], "zone": "日比谷"},
        {"name": "月島", "name_en": "Tsukishima Station", "company": "東京Metro", "line": ["東京地下鐵有樂町線", "都營大江戶線"], "zone": "月島"},
        {"name": "豐洲", "name_en": "Toyosu Station", "company": "東京Metro", "line": ["東京地下鐵有樂町線", "東京地下鐵副都心線"], "zone": "豐洲"},
        # 小田急 / 東急
        {"name": "下北澤", "name_en": "Shimokitazawa Station", "company": "小田急", "line": ["小田急小田原線", "京王井之頭線"], "zone": "下北澤"},
        {"name": "三軒茶屋", "name_en": "Sangenchaya Station", "company": "東鐵", "line": ["東鐵田園都市線"], "zone": "三軒茶屋"},
        {"name": "自由が丘", "name_en": "Jiyugaoka Station", "company": "東鐵", "line": ["東鐵東横線", "東鐵大井町線"], "zone": "自由が丘"},
        {"name": "中目黑", "name_en": "Naka-Meguro Station", "company": "東鐵", "line": ["東鐵東横線", "東京地下鐵日比谷線", "都營地下鐵三田線"], "zone": "中目黑"},
        {"name": "代官山", "name_en": "Daikanyama Station", "company": "東鐵", "line": ["東鐵東横線"], "zone": "代官山"},
        # 其他
        {"name": "芝公園", "name_en": "Shibakoen Station Tokyo", "company": "都營", "line": ["都營三田線"], "zone": "芝公園"},
    ],

    "kyushu": [
        # 熊本
        {"name": "熊本", "name_en": "Kumamoto Station", "company": "JR", "line": ["JR九州新幹線", "JR鹿兒島線", "JR豐肥本線"], "zone": "熊本"},
        {"name": "人吉", "name_en": "Hitoyoshi Station", "company": "JR", "line": ["JR豐肥本線"], "zone": "人吉"},
        {"name": "玉名", "name_en": "Tamana Station", "company": "JR", "line": ["JR鹿兒島線"], "zone": "玉名"},
        # 鹿兒島
        {"name": "鹿兒島中央", "name_en": "Kagoshima-Chuo Station", "company": "JR", "line": ["JR九州新幹線", "JR鹿兒島線", "JR日豐本線", "鹿兒島市電"], "zone": "鹿兒島"},
        {"name": "鹿兒島", "name_en": "Kagoshima Station", "company": "JR", "line": ["JR日豐本線", "鹿兒島市電"], "zone": "鹿兒島"},
        {"name": "國分", "name_en": "Kokubu Station Kagoshima", "company": "JR", "line": ["JR日豐本線"], "zone": "國分"},
        # 長崎
        {"name": "長崎", "name_en": "Nagasaki Station", "company": "JR", "line": ["JR九州新幹線", "JR長崎線"], "zone": "長崎"},
        {"name": "佐世保", "name_en": "Sasebo Station", "company": "JR", "line": ["JR大村線", "松浦鐵道西九州線"], "zone": "佐世保"},
        {"name": "諫早", "name_en": "Isahaya Station", "company": "JR", "line": ["JR長崎線", "JR大村線", "島原鐵道線"], "zone": "諫早"},
        # 宮崎
        {"name": "宮崎", "name_en": "Miyazaki Station", "company": "JR", "line": ["JR宮崎線", "JR日豐本線"], "zone": "宮崎"},
        {"name": "延岡", "name_en": "Nobeoka Station", "company": "JR", "line": ["JR日豐本線"], "zone": "延岡"},
        {"name": "都城", "name_en": "Miyakonojo Station", "company": "JR", "line": ["JR日豐本線", "JR宮崎線"], "zone": "都城"},
        # 大分 / 別府 / 湯布院
        {"name": "大分", "name_en": "Oita Station", "company": "JR", "line": ["JR九州新幹線", "JR日豐本線", "JR久大本線"], "zone": "大分"},
        {"name": "別府", "name_en": "Beppu Station", "company": "JR", "line": ["JR日豐本線"], "zone": "別府"},
        {"name": "由布院", "name_en": "Yufuin Station", "company": "JR", "line": ["JR久大本線"], "zone": "湯布院"},
        {"name": "日田", "name_en": "Hita Station", "company": "JR", "line": ["JR久大本線"], "zone": "日田"},
        # 福岡縣
        {"name": "鳥栖", "name_en": "Tosu Station", "company": "JR", "line": ["JR九州新幹線", "JR鹿兒島線"], "zone": "鳥栖"},
        # 佐賀
        {"name": "佐賀", "name_en": "Saga Station", "company": "JR", "line": ["JR長崎線", "JR唐津線"], "zone": "佐賀"},
        {"name": "唐津", "name_en": "Karatsu Station", "company": "JR", "line": ["JR唐津線", "昭和鐵道線"], "zone": "唐津"},
    ]
}

# ---------- Nominatim 查詢 ----------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_station(station, region):
    """用 Nominatim 以英文名查詢座標，回傳 (lat, lng) 或 (None, None)"""
    name_en = station.get("name_en") or station["name"]
    region_map = {"osaka": "Osaka", "fukuoka": "Fukuoka", "tokyo": "Tokyo", "kyushu": "Japan"}
    region_str = region_map.get(region, "Japan")
    query = f"{name_en}, {region_str}"
    params = {
        "q": query,
        "format": "json",
        "limit": "1",
        "addressdetails": "0"
    }
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": "TravelPlannerBot/1.0 (educational project)",
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  [ERR] {name_en}: {e}", file=sys.stderr)
    return None, None


def generate_stations(region):
    """為指定地區產生 stations.json"""
    stations = []

    print(f"\n=== Processing {region.upper()} ({len(STATION_LISTS[region])} stations) ===")

    for i, station in enumerate(STATION_LISTS[region], 1):
        name = station["name"]
        name_en = station.get("name_en", name)
        print(f"  [{i}/{len(STATION_LISTS[region])}] {name}...", end=" ", flush=True)

        lat, lng = geocode_station(station, region)
        time.sleep(0.8)  # Nominatim 限制：每秒 1 筆

        station_id = f"{region}_station_{i:03d}"
        entry = {
            "id": station_id,
            "name": name,
            "name_en": name_en,
            "company": station["company"],
            "line": station["line"],
            "zone": station["zone"],
            "lat": lat,
            "lng": lng,
            "radius_m": 800,
            "active": True
        }
        stations.append(entry)

        if lat:
            print(f"✅ ({lat:.4f}, {lng:.4f})")
        else:
            print(f"⚠️  無座標（需手動填入）")

    # 寫入 JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", region)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "stations.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"region": region, "updated": str(__import__("datetime").date.today()), "stations": stations}, f, ensure_ascii=False, indent=2)

    success = sum(1 for s in stations if s["lat"] is not None)
    print(f"\n  完成：{success}/{len(stations)} 筆有座標")
    print(f"  寫入：{out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="產生各地區 stations.json")
    parser.add_argument("--region", default="all", choices=["osaka", "fukuoka", "tokyo", "kyushu", "all"])
    args = parser.parse_args()

    regions = list(STATION_LISTS.keys()) if args.region == "all" else [args.region]
    for r in regions:
        generate_stations(r)


if __name__ == "__main__":
    main()
