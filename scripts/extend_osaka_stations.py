#!/usr/bin/env python3
"""
extend_osaka_stations.py
只新增缺失的車站到 data/osaka/stations.json（按名稱去重，保留現有ID）
"""
import json, time, urllib.request, urllib.parse, sys, os
from pathlib import Path

REPO = Path("/var/repo/travel-planner")
STATIONS_PATH = REPO / "data" / "osaka" / "stations.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# ── Osaka STATION_LISTS（與 generate_stations.py 同步）────────────────────────────
STATION_LISTS_OSAKA = [
    # JR 西日本（保留原有）
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
    # ── 以下為新增車站（需要補 lat/lng）────────────────────────────
    # JR 環狀線延伸
    {"name": "蘆原橋", "name_en": "Ashiharacho Station", "company": "JR", "line": ["JR大阪環狀線"], "zone": "蘆原橋"},
    {"name": "今宮", "name_en": "Imamiya Station", "company": "JR", "line": ["JR大阪環狀線"], "zone": "今宮"},
    {"name": "玉造", "name_en": "Tamatsukuri Station", "company": "JR", "line": ["JR大阪環狀線"], "zone": "玉造"},
    {"name": "森之宮", "name_en": " Morinomiya Station", "company": "JR", "line": ["JR大阪環狀線", "JR中央線"], "zone": "森之宮"},
    {"name": "大阪城北詰", "name_en": "Osakajokitazume Station", "company": "JR", "line": ["JR東西線"], "zone": "大阪城"},
    {"name": "天滿", "name_en": "Temma Station", "company": "JR", "line": ["JR大阪環狀線", "JR東西線"], "zone": "天滿"},
    {"name": "福岛", "name_en": "Fukushima Station Osaka", "company": "JR", "line": ["JR大阪環狀線", "JR東西線"], "zone": "福岛"},
    {"name": "野田（JR）", "name_en": "Noda Station Osaka", "company": "JR", "line": ["JR大阪環狀線"], "zone": "野田"},
    # JR 片町線 / JR東西線
    {"name": "大阪天滿宮", "name_en": "Osaka-Temmangu Station", "company": "JR", "line": ["JR東西線"], "zone": "天滿"},
    {"name": "新大阪（JR東西線）", "name_en": "Shin-Osaka Station JR", "company": "JR", "line": ["JR東西線"], "zone": "新大阪"},
    {"name": "大阪", "name_en": "Osaka Station", "company": "JR", "line": ["JR東西線"], "zone": "梅田"},
    # JR大和路線
    {"name": "小路", "name_en": "Shoji Station", "company": "JR", "line": ["JR大和路線"], "zone": "小路"},
    {"name": "JR難波（升陽）", "name_en": "JR Namba Station", "company": "JR", "line": ["JR大和路線"], "zone": "難波"},
    # 地下鐵 御堂筋線（追加）
    {"name": "新大阪（地下鐵）", "name_en": "Shin-Osaka Station Metro", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "新大阪"},
    {"name": "西中島南方", "name_en": "Nishinakajima-Minamigata Station", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "新大阪"},
    {"name": "中津", "name_en": "Nakatsu Station Osaka", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "梅田"},
    {"name": "狸小路", "name_en": "Tanukibashi Station", "company": "地下鐵", "line": ["地下鐵御堂筋線"], "zone": "狸"},
    # 地下鐵 谷町線（追加）
    {"name": "南森町", "name_en": "Minamimorimachi Station", "company": "地下鐵", "line": ["地下鐵谷町線"], "zone": "天滿"},
    {"name": "長柄橋", "name_en": "Nagarekawa Station", "company": "地下鐵", "line": ["地下鐵谷町線"], "zone": "天滿橋"},
    {"name": "四天王寺前/夕陽丘", "name_en": "Shitennoji-mae Station", "company": "地下鐵", "line": ["地下鐵谷町線"], "zone": "天王寺"},
    {"name": "鶴見綠地", "name_en": "Tsurumiryokuchi Station", "company": "地下鐵", "line": ["地下鐵鶴見綠地線"], "zone": "鶴見綠地"},
    {"name": "門真南", "name_en": "Kadomasouth Station", "company": "地下鐵", "line": ["地下鐵鶴見綠地線"], "zone": "門真"},
    # 地下鐵 中央線（追加）
    {"name": "深江橋", "name_en": "Fukaebashi Station", "company": "地下鐵", "line": ["地下鐵中央線"], "zone": "深江橋"},
    {"name": "高津", "name_en": "Takatsu Station Osaka", "company": "地下鐵", "line": ["地下鐵中央線"], "zone": "高津"},
    {"name": "長田", "name_en": "Nagata Station Osaka", "company": "地下鐵", "line": ["地下鐵中央線"], "zone": "長田"},
    # 地下鐵 四橋線（追加）
    {"name": "北加賀屋", "name_en": "Kita-Kagaya Station", "company": "地下鐵", "line": ["地下鐵四橋線"], "zone": "北加賀屋"},
    {"name": "住之江公園", "name_en": "Suminoekoen Station", "company": "地下鐵", "line": ["地下鐵四橋線"], "zone": "住之江"},
    # 地下鐵 堺筋線（追加）
    {"name": "北濱（堺筋）", "name_en": "Kitahama Station", "company": "地下鐵", "line": ["地下鐵堺筋線"], "zone": "北濱"},
    {"name": "淀橋", "name_en": "Yodobashi Station", "company": "地下鐵", "line": ["地下鐵堺筋線"], "zone": "梅田"},
    # 地下鐵 千日前線（追加）
    {"name": "蘆原橋（地下鐵）", "name_en": "Ashiharacho Station Metro", "company": "地下鐵", "line": ["地下鐵千日前線"], "zone": "蘆原橋"},
    {"name": "今里（地下鐵）", "name_en": "Imazato Station", "company": "地下鐵", "line": ["地下鐵千日前線"], "zone": "今里"},
    # 地下鐵 長堀鶴見綠地線（追加）
    {"name": "鶴見綠地（地下鐵）", "name_en": "Tsurumiryokuchi Station Metro", "company": "地下鐵", "line": ["地下鐵長堀鶴見綠地線"], "zone": "鶴見綠地"},
    {"name": "今里（長堀鶴見）", "name_en": "Imazato-Sangiin Station", "company": "地下鐵", "line": ["地下鐵長堀鶴見綠地線"], "zone": "今里"},
    # 大阪單軌
    {"name": "大阪單軌 千里", "name_en": "Senri Station Osaka Monorail", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "千里"},
    {"name": "大阪單軌 萬博紀念公園", "name_en": "Banpaku-Kinen-Koen Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "萬博"},
    {"name": "大阪單軌 EXPOCITY", "name_en": "EXPOCITY Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "萬博"},
    {"name": "南茨木", "name_en": "Minami-Ibaraki Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "茨木"},
    {"name": "澤良宜", "name_en": "Sawara Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "茨木"},
    {"name": "大阪單軌 攝津", "name_en": "Setsu Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "攝津"},
    {"name": "南攝津", "name_en": "Minami-Setsu Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "攝津"},
    {"name": "柴原阪大", "name_en": "Shiharaniosaka-mae Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "千里"},
    {"name": "豐川", "name_en": "Toyokawa Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "千里"},
    {"name": "彩都西", "name_en": "Saitosai Station", "company": "大阪單軌", "line": ["大阪單軌線"], "zone": "彩都"},
    # 京阪電車
    {"name": "淀屋橋（京阪）", "name_en": "Yodoyabashi Station Keihan", "company": "京阪", "line": ["京阪本線"], "zone": "淀屋橋"},
    {"name": "北濱（京阪）", "name_en": "Kitahama Station Keihan", "company": "京阪", "line": ["京阪本線"], "zone": "北濱"},
    {"name": "天滿橋（京阪）", "name_en": "Temmabashi Station Keihan", "company": "京阪", "line": ["京阪本線"], "zone": "天滿橋"},
    {"name": "京橋（京阪）", "name_en": "Keihan Kyobashi Station", "company": "京阪", "line": ["京阪本線"], "zone": "京橋"},
    {"name": "枚方町", "name_en": "Hirakata-cho Station", "company": "京阪", "line": ["京阪本線"], "zone": "枚方"},
    {"name": "樟葉", "name_en": "Kamohaya Station", "company": "京阪", "line": ["京阪本線"], "zone": "樟葉"},
    {"name": "石津", "name_en": "Ishida Station", "company": "京阪", "line": ["京阪巾下田線"], "zone": "石津"},
    # 阪神電車（追加）
    {"name": "野田（阪神）", "name_en": "Noda Station Hanshin", "company": "阪神", "line": ["阪神難波線"], "zone": "野田"},
    {"name": "杭濑", "name_en": "Kosei Station", "company": "阪神", "line": ["阪神難波線"], "zone": "大正"},
    {"name": "大物", "name_en": "Daio Station", "company": "阪神", "line": ["阪神難波線"], "zone": "大物"},
    {"name": "尼崎（阪神）", "name_en": "Amagasaki Station Hanshin", "company": "阪神", "line": ["阪神本線"], "zone": "尼崎"},
    # 近鐵（追加）
    {"name": "鶴橋（近鐵）", "name_en": "Tsuruhashi Station Kintetsu", "company": "近鐵", "line": ["近鐵奈良線", "近鐵大阪線"], "zone": "鶴橋"},
    {"name": "上本町（近鐵）", "name_en": "Uehommachi Station Kintetsu", "company": "近鐵", "line": ["近鐵大阪線"], "zone": "上本町"},
    {"name": "布施", "name_en": "Fuse Station", "company": "近鐵", "line": ["近鐵大阪線"], "zone": "布施"},
    {"name": "河内松原", "name_en": "Kawachi-Matsubara Station", "company": "近鐵", "line": ["近鐵南大阪線"], "zone": "松原"},
    {"name": "藤井寺", "name_en": "Fujidera Station", "company": "近鐵", "line": ["近鐵南大阪線"], "zone": "藤井寺"},
    {"name": "古市", "name_en": "Furuichi Station", "company": "近鐵", "line": ["近鐵南大阪線"], "zone": "古市"},
    # 南海電鐵（追加）
    {"name": "岸里", "name_en": "Kishiki Station", "company": "南海", "line": ["南海高野線"], "zone": "岸里"},
    {"name": "初芝", "name_en": "Hatsushiba Station", "company": "南海", "line": ["南海高野線"], "zone": "初芝"},
    {"name": "千代田", "name_en": "Chiyoda Station", "company": "南海", "line": ["南海高野線"], "zone": "千代田"},
    {"name": "北野田", "name_en": "Kita-No-Den Station", "company": "南海", "line": ["南海高野線"], "zone": "北野田"},
    {"name": "泉ヶ丘", "name_en": "Izumigaoka Station", "company": "南海", "line": ["南海高野線"], "zone": "泉北"},
    {"name": "泉北高速 和泉中央", "name_en": "Izumi-Chuo Station", "company": "泉北", "line": ["泉北高速鐵道線"], "zone": "和泉"},
    {"name": "临空城", "name_en": "Rinku-Toyokawa Station", "company": "南海", "line": ["南海空港線"], "zone": "臨空城"},
    {"name": "關西機場（南海）", "name_en": "Kansai Airport Station", "company": "南海", "line": ["南海空港線"], "zone": "關西機場"},
    # JR 追加
    {"name": "關西機場（JR）", "name_en": "Kansai Airport Station JR", "company": "JR", "line": ["JR關西機場線"], "zone": "關西機場"},
    {"name": "日根野", "name_en": "Hineno Station", "company": "JR", "line": ["JR關西機場線"], "zone": "日根野"},
    {"name": "佐野", "name_en": "Sano Station Osaka", "company": "JR", "line": ["JR阪和線"], "zone": "佐野"},
    {"name": "LR 堺市", "name_en": "Sakai-Shoji Station", "company": "JR", "line": ["JR阪和線"], "zone": "堺"},
    {"name": "LR 鳳", "name_en": "Otori Station", "company": "JR", "line": ["JR阪和線"], "zone": "鳳"},
    {"name": "三国丘（JR）", "name_en": "Mikunigaoka Station", "company": "JR", "line": ["JR阪和線"], "zone": "堺"},
    {"name": "LR 津久野", "name_en": "Tsurugaguchi Station", "company": "JR", "line": ["JR阪和線"], "zone": "津久野"},
    {"name": "和泉府中", "name_en": "Izumi-Fuchu Station", "company": "JR", "line": ["JR阪和線"], "zone": "和泉"},
    {"name": "LR 紀泉", "name_en": "Kisen Station", "company": "JR", "line": ["JR阪和線"], "zone": "紀泉"},
    {"name": "東貝塚", "name_en": "Higashi-Kaizuka Station", "company": "JR", "line": ["JR阪和線"], "zone": "貝塚"},
    {"name": "和泉砂川", "name_en": "Izumi-Sunagawa Station", "company": "JR", "line": ["JR阪和線"], "zone": "砂川"},
    {"name": "LR 走高", "name_en": "Takashio Station", "company": "JR", "line": ["JR阪和線"], "zone": "走高"},
    {"name": "LR 熊取", "name_en": "Kumatori Station", "company": "JR", "line": ["JR阪和線"], "zone": "熊取"},
    {"name": "日根野（JR加古川）", "name_en": "Hineno Station", "company": "JR", "line": ["JR加古川線"], "zone": "加古川"},
    # 能勢電鐵
    {"name": "川西能勢口", "name_en": "Kawanishi-Noseguchi Station", "company": "能勢", "line": ["能勢電鐵"], "zone": "川西"},
    {"name": "山下（能勢）", "name_en": "Yamashita Station Nosatsu", "company": "能勢", "line": ["能勢電鐵"], "zone": "山下"},
    {"name": "塚口（能勢）", "name_en": "Tsukaguchi Station Nosatsu", "company": "能勢", "line": ["能勢電鐵"], "zone": "塚口"},
    # 會員制的私鐵
    {"name": "JR東西線 加島", "name_en": "Kashima Station", "company": "JR", "line": ["JR東西線"], "zone": "加島"},
    {"name": "野田（JR東西線）", "name_en": "Noda Station JR West", "company": "JR", "line": ["JR東西線"], "zone": "野田"},
]

# Nominatim 查詢函式
def geocode(station, region="Osaka"):
    name_en = station.get("name_en") or station["name"]
    query = f"{name_en}, {region}, Japan"
    params = {"q": query, "format": "json", "limit": "1", "addressdetails": "0"}
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "TravelPlannerBot/1.0 (educational project)", "Accept": "application/json"}
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

# ── 主程式 ─────────────────────────────────────────────────────────────────────
existing_data = json.load(open(STATIONS_PATH))
existing_stations = existing_data["stations"]
existing_names = {s["name"] for s in existing_stations}
existing_ids   = {s["id"] for s in existing_stations}
print(f"現有車站：{len(existing_stations)} 個")

new_stations = []
for station in STATION_LISTS_OSAKA:
    name = station["name"]
    if name in existing_names:
        print(f"  [skip] {name}（已存在）")
        continue
    print(f"  [new] {name}... ", end="", flush=True)
    lat, lng = geocode(station, "Osaka")
    time.sleep(0.8)
    if lat:
        print(f"✅ ({lat:.4f}, {lng:.4f})")
    else:
        print("⚠️ 無座標")

    # 自動產生 ID
    idx = len(existing_stations) + len(new_stations) + 1
    sid = f"osaka_station_{idx:03d}"
    while sid in existing_ids:
        idx += 1
        sid = f"osaka_station_{idx:03d}"

    entry = {
        "id": sid,
        "name": name,
        "name_en": station.get("name_en", name),
        "company": station["company"],
        "line": station["line"],
        "zone": station["zone"],
        "lat": lat,
        "lng": lng,
        "radius_m": 800,
        "active": True,
    }
    new_stations.append(entry)

print(f"\n新增 {len(new_stations)} 個車站")

# 合併
existing_stations.extend(new_stations)
existing_data["stations"] = existing_stations
existing_data["updated"] = "2026-06-29"

with open(STATIONS_PATH, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)
os.chmod(STATIONS_PATH, 0o644)
print(f"寫入完成：共 {len(existing_stations)} 個車站 → {STATIONS_PATH}")
