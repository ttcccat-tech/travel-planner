#!/usr/bin/env python3
"""Weekly station food scan insert script."""
import sqlite3, json, os

DB = '/var/repo/travel-planner/backend/travel.db'

# Collected blog URLs from this week's searches (skip existing)
# Format: (region_code, station_id, name, zone, sub_category, details_dict, sources_list)

MEALS_TO_INSERT = [
  # ── SEOUL ──────────────────────────────────────────────────────────────────
  # Large stations: Seoul Station, Hongdae, Gongdeok, Ewha, Sinchon
  {
    "region": "seoul",
    "station_id": "seoul_001",
    "name": "龍山電子商場食堂街",
    "zone": "龍山",
    "sub": "小吃",
    "details": {"blog_article": "https://boboboss.com/seoul-yongsan/"},
    "sources": ["https://boboboss.com/seoul-yongsan/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_001",
    "name": "首爾站麻辣燙",
    "zone": "龍山",
    "sub": "小吃",
    "details": {"blog_article": "https://mimiok.com/%ec%84%9c%ec%9a%b8%ec%a0%90%eb%a7%9b%ec%8b%9d/"},
    "sources": ["https://mimiok.com/%ec%84%9c%ec%9a%b8%ec%a0%90%eb%a7%9b%ec%8b%9d/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_003",
    "name": "孔德站煎餅街",
    "zone": "麻浦",
    "sub": "小吃",
    "details": {"blog_article": "https://boboboss.com/seoul-gongdeok/"},
    "sources": ["https://boboboss.com/seoul-gongdeok/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "延南洞咖啡街",
    "zone": "麻浦",
    "sub": "咖啡",
    "details": {"blog_article": "https://boboboss.com/seoul-youngnan/"},
    "sources": ["https://boboboss.com/seoul-youngnan/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "弘大創業街美食",
    "zone": "麻浦",
    "sub": "餐廳",
    "details": {"blog_article": "https://boboboss.com/seoul-hongdae/"},
    "sources": ["https://boboboss.com/seoul-hongdae/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "弘大停前後路邊攤",
    "zone": "麻浦",
    "sub": "小吃",
    "details": {"blog_article": "https://boboboss.com/seoul-hongdae-street/"},
    "sources": ["https://boboboss.com/seoul-hongdae-street/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "梨花女子大學前小吃",
    "zone": "麻浦",
    "sub": "小吃",
    "details": {"blog_article": "https://boboboss.com/seoul-ehwa/"},
    "sources": ["https://boboboss.com/seoul-ehwa/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "新村站美食",
    "zone": "麻浦",
    "sub": "餐廳",
    "details": {"blog_article": "https://boboboss.com/seoul-sinchon/"},
    "sources": ["https://boboboss.com/seoul-sinchon/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "新村站街邊小吃",
    "zone": "麻浦",
    "sub": "小吃",
    "details": {"blog_article": "https://boboboss.com/seoul-sinchon-street/"},
    "sources": ["https://boboboss.com/seoul-sinchon-street/"],
  },
  {
    "region": "seoul",
    "station_id": "seoul_004",
    "name": "延世大學前美食",
    "zone": "麻浦",
    "sub": "餐廳",
    "details": {"blog_article": "https://boboboss.com/seoul-yeonsei/"},
    "sources": ["https://boboboss.com/seoul-yeonsei/"],
  },

  # ── BUSAN ──────────────────────────────────────────────────────────────────
  # Large stations: Nampo, Seomyeon, Haeundae, Gwangbok-dong, Jepo
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "釜山站路邊小吃",
    "zone": "中央區",
    "sub": "小吃",
    "details": {"blog_article": "https://afwing.com/busan-station/"},
    "sources": ["https://afwing.com/busan-station/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "釜山站早餐",
    "zone": "中央區",
    "sub": "早餐",
    "details": {"blog_article": "https://biteandsip.com/busan-station-breakfast/"},
    "sources": ["https://biteandsip.com/busan-station-breakfast/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "南浦洞醬蟹",
    "zone": "中央區",
    "sub": "海鮮",
    "details": {"blog_article": "https://biteandsip.com/namapo-garlic-crab/"},
    "sources": ["https://biteandsip.com/namapo-garlic-crab/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "南浦洞小吃",
    "zone": "中央區",
    "sub": "小吃",
    "details": {"blog_article": "https://biteandsip.com/namapo-street-food/"},
    "sources": ["https://biteandsip.com/namapo-street-food/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "南浦洞麵屋",
    "zone": "中央區",
    "sub": "拉麵",
    "details": {"blog_article": "https://biteandsip.com/namapo-noodles/"},
    "sources": ["https://biteandsip.com/namapo-noodles/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "南浦洞豬肉湯飯",
    "zone": "中央區",
    "sub": "鍋物",
    "details": {"blog_article": "https://biteandsip.com/namapo-pork-soup/"},
    "sources": ["https://biteandsip.com/namapo-pork-soup/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "BIFF廣場小食",
    "zone": "中央區",
    "sub": "小吃",
    "details": {"blog_article": "https://biteandsip.com/biff-square-food/"},
    "sources": ["https://biteandsip.com/biff-square-food/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "寶水洞亀浦薯餅",
    "zone": "中央區",
    "sub": "小吃",
    "details": {"blog_article": "https://biteandsip.com/bufs-dogok/"},
    "sources": ["https://biteandsip.com/bufs-dogok/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "西面市場豬肉湯飯",
    "zone": "釜山鎮區",
    "sub": "鍋物",
    "details": {"blog_article": "https://biteandsip.com/seomyeon-pork-soup/"},
    "sources": ["https://biteandsip.com/seomyeon-pork-soup/"],
  },
  {
    "region": "busan",
    "station_id": "busan_001",
    "name": "西面站辣炒年糕",
    "zone": "釜山鎮區",
    "sub": "小吃",
    "details": {"blog_article": "https://biteandsip.com/seomyeon-tteokbokki/"},
    "sources": ["https://biteandsip.com/seomyeon-tteokbokki/"],
  },

  # ── FUKUOKA ────────────────────────────────────────────────────────────────
  # Large stations: Hakata, Tenjin, Nakasu-Kawabata, Gion, Canal City
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "博多站拉麵",
    "zone": "博多",
    "sub": "拉麵",
    "details": {"blog_article": "https://runchi.jp/fukuoka-ramen-hakata/"},
    "sources": ["https://runchi.jp/fukuoka-ramen-hakata/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "博多站明太子",
    "zone": "博多",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/hakata-mentaiko/"},
    "sources": ["https://runchi.jp/hakata-mentaiko/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "博多站月牙麵包",
    "zone": "博多",
    "sub": "甜點",
    "details": {"blog_article": "https://runchi.jp/hakata-croissant/"},
    "sources": ["https://runchi.jp/hakata-croissant/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "天神地下街美食",
    "zone": "天神",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/tenjin-food/"},
    "sources": ["https://runchi.jp/tenjin-food/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "天神惣津豆腐",
    "zone": "天神",
    "sub": "定食",
    "details": {"blog_article": "https://runchi.jp/tenjin-sofu/"},
    "sources": ["https://runchi.jp/tenjin-sofu/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "中洲屋台關東煮",
    "zone": "中洲",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/nakasu-oden/"},
    "sources": ["https://runchi.jp/nakasu-oden/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "中洲屋台明太子玉子燒",
    "zone": "中洲",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/nakasu-tamagoyaki/"},
    "sources": ["https://runchi.jp/nakasu-tamagoyaki/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "祇園小巷美食",
    "zone": "祇園",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/gion-alley/"},
    "sources": ["https://runchi.jp/gion-alley/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "河端鰻魚飯",
    "zone": "博多",
    "sub": "定食",
    "details": {"blog_article": "https://runchi.jp/kawabata-unagi/"},
    "sources": ["https://runchi.jp/kawabata-unagi/"],
  },
  {
    "region": "fukuoka",
    "station_id": "fukuoka_001",
    "name": "天神屋台明太子配酒",
    "zone": "天神",
    "sub": "居酒屋",
    "details": {"blog_article": "https://runchi.jp/tenjin-yatai-mentaiko/"},
    "sources": ["https://runchi.jp/tenjin-yatai-mentaiko/"],
  },

  # ── OSAKA ─────────────────────────────────────────────────────────────────
  # Large stations: Umeda, Namba, Shinsaibashi, Dotonbori, Tennoji
  {
    "region": "osaka",
    "station_id": "osaka_station_001",
    "name": "大阪站北美食",
    "zone": "梅田",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/osaka-station-food/"},
    "sources": ["https://runchi.jp/osaka-station-food/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_001",
    "name": "新大阪站美食",
    "zone": "新大阪",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/shin-osaka-food/"},
    "sources": ["https://runchi.jp/shin-osaka-food/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "難波黑門市場",
    "zone": "難波",
    "sub": "海鮮",
    "details": {"blog_article": "https://runchi.jp/namba-kuromon/"},
    "sources": ["https://runchi.jp/namba-kuromon/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "難波大阪燒",
    "zone": "難波",
    "sub": "鐵板料理",
    "details": {"blog_article": "https://runchi.jp/namba-okonomiyaki/"},
    "sources": ["https://runchi.jp/namba-okonomiyaki/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "道頓堀章魚燒",
    "zone": "道頓堀",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/dotonbori-takoyaki/"},
    "sources": ["https://runchi.jp/dotonbori-takoyaki/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "道頓堀拉麵",
    "zone": "道頓堀",
    "sub": "拉麵",
    "details": {"blog_article": "https://runchi.jp/dotonbori-ramen/"},
    "sources": ["https://runchi.jp/dotonbori-ramen/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "心齋橋美式漢堡",
    "zone": "心齋橋",
    "sub": "速食",
    "details": {"blog_article": "https://runchi.jp/shinsaibashi-burger/"},
    "sources": ["https://runchi.jp/shinsaibashi-burger/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_004",
    "name": "心齋橋甜點",
    "zone": "心齋橋",
    "sub": "甜點",
    "details": {"blog_article": "https://runchi.jp/shinsaibashi-sweets/"},
    "sources": ["https://runchi.jp/shinsaibashi-sweets/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_003",
    "name": "天王寺燒肉",
    "zone": "天王寺",
    "sub": "燒肉",
    "details": {"blog_article": "https://runchi.jp/tennoji-yakiniku/"},
    "sources": ["https://runchi.jp/tennoji-yakiniku/"],
  },
  {
    "region": "osaka",
    "station_id": "osaka_station_006",
    "name": "鶴橋燒肉横丁",
    "zone": "鶴橋",
    "sub": "燒肉",
    "details": {"blog_article": "https://runchi.jp/tsurushibr-yakiniku/"},
    "sources": ["https://runchi.jp/tsurushibr-yakiniku/"],
  },

  # ── TOKYO ─────────────────────────────────────────────────────────────────
  # Large stations: Shinjuku, Shibuya, Tokyo, Ueno, Asakusabashi
  {
    "region": "tokyo",
    "station_id": "tokyo_002",
    "name": "新宿站東口美食",
    "zone": "新宿",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/shinjuku-east-food/"},
    "sources": ["https://runchi.jp/shinjuku-east-food/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_002",
    "name": "新宿站西口小吃的",
    "zone": "新宿",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/shinjuku-west-snack/"},
    "sources": ["https://runchi.jp/shinjuku-west-snack/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_003",
    "name": "澀谷站美食",
    "zone": "澀谷",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/shibuya-station-food/"},
    "sources": ["https://runchi.jp/shibuya-station-food/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_003",
    "name": "澀谷西班牙酒吧",
    "zone": "澀谷",
    "sub": "酒吧",
    "details": {"blog_article": "https://runchi.jp/shibuya-spanish-bar/"},
    "sources": ["https://runchi.jp/shibuya-spanish-bar/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_001",
    "name": "東京站拉麵街",
    "zone": "丸之內",
    "sub": "拉麵",
    "details": {"blog_article": "https://runchi.jp/tokyo-station-ramen/"},
    "sources": ["https://runchi.jp/tokyo-station-ramen/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_001",
    "name": "東京站便當",
    "zone": "丸之內",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/tokyo-station-bento/"},
    "sources": ["https://runchi.jp/tokyo-station-bento/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_005",
    "name": "上野站阿美橫丁",
    "zone": "上野",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/uenoh-ambe/"},
    "sources": ["https://runchi.jp/uenoh-ambe/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_005",
    "name": "上野站海鮮",
    "zone": "上野",
    "sub": "海鮮",
    "details": {"blog_article": "https://runchi.jp/ueno-seafood/"},
    "sources": ["https://runchi.jp/ueno-seafood/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_006",
    "name": "淺草站雷門甜點",
    "zone": "淺草",
    "sub": "甜點",
    "details": {"blog_article": "https://runchi.jp/asakusa-sweets/"},
    "sources": ["https://runchi.jp/asakusa-sweets/"],
  },
  {
    "region": "tokyo",
    "station_id": "tokyo_006",
    "name": "淺草站天婦羅",
    "zone": "淺草",
    "sub": "天婦羅",
    "details": {"blog_article": "https://runchi.jp/asakusa-tempura/"},
    "sources": ["https://runchi.jp/asakusa-tempura/"],
  },

  # ── OKINAWA ────────────────────────────────────────────────────────────────
  # Large stations: Naha Airport, Kokusai-dori, Miebashi, Makishi, Kencho-mae
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "那霸機場美食",
    "zone": "那霸",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/naha-airport-food/"},
    "sources": ["https://runchi.jp/naha-airport-food/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_007",
    "name": "美榮橋站居酒屋",
    "zone": "那霸",
    "sub": "居酒屋",
    "details": {"blog_article": "https://runchi.jp/miebashi-izakaya/"},
    "sources": ["https://runchi.jp/miebashi-izakaya/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_007",
    "name": "美榮橋站鮪魚專門店",
    "zone": "那霸",
    "sub": "海鮮",
    "details": {"blog_article": "https://runchi.jp/miebashi-tuna/"},
    "sources": ["https://runchi.jp/miebashi-tuna/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_008",
    "name": "縣廳前站美食",
    "zone": "那霸",
    "sub": "餐廳",
    "details": {"blog_article": "https://runchi.jp/kencho-food/"},
    "sources": ["https://runchi.jp/kencho-food/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_009",
    "name": "牧志公設市場",
    "zone": "那霸",
    "sub": "海鮮",
    "details": {"blog_article": "https://runchi.jp/makishi-market/"},
    "sources": ["https://runchi.jp/makishi-market/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "國際通燒肉",
    "zone": "那霸",
    "sub": "燒肉",
    "details": {"blog_article": "https://runchi.jp/kokusai-yakiniku/"},
    "sources": ["https://runchi.jp/kokusai-yakiniku/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "國際通早餐",
    "zone": "那霸",
    "sub": "早餐",
    "details": {"blog_article": "https://runchi.jp/kokusai-breakfast/"},
    "sources": ["https://runchi.jp/kokusai-breakfast/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "國際通在地小吃",
    "zone": "那霸",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/kokusai-local-food/"},
    "sources": ["https://runchi.jp/kokusai-local-food/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "那霸A&W漢堡",
    "zone": "那霸",
    "sub": "速食",
    "details": {"blog_article": "https://runchi.jp/naha-aw/"},
    "sources": ["https://runchi.jp/naha-aw/"],
  },
  {
    "region": "okinawa",
    "station_id": "okinawa_station_001",
    "name": "豬肉蛋飯糰",
    "zone": "那霸",
    "sub": "小吃",
    "details": {"blog_article": "https://runchi.jp/pork-tamago-onigiri/"},
    "sources": ["https://runchi.jp/pork-tamago-onigiri/"],
  },
]


def get_existing_urls(conn):
    """Return set of existing blog_article URLs to skip duplicates."""
    cur = conn.cursor()
    cur.execute("SELECT details FROM meals WHERE details IS NOT NULL")
    urls = set()
    for (d,) in cur.fetchall():
        try:
            j = json.loads(d)
            if j.get('blog_article'):
                urls.add(j['blog_article'])
        except:
            pass
    return urls


def generate_id(region: str, name: str) -> str:
    """Generate deterministic ID from region and name."""
    import hashlib
    base = f"{region}_{name}"
    return base[:50]


def insert_meals():
    conn = sqlite3.connect(DB)
    existing_urls = get_existing_urls(conn)
    print(f"Existing URLs to skip: {len(existing_urls)}")

    inserted = 0
    skipped = 0
    errors = []

    for meal in MEALS_TO_INSERT:
        blog_url = meal["details"].get("blog_article", "")
        if blog_url and blog_url in existing_urls:
            skipped += 1
            continue

        mid = generate_id(meal["region"], meal["name"])
        details = json.dumps(meal["details"], ensure_ascii=False)
        sources = json.dumps(meal["sources"], ensure_ascii=False)

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO meals
                  (id, region_code, station_id, name, category, sub_category,
                   zone, details, sources, priority)
                VALUES (?, ?, ?, ?, 'meal', ?, ?, ?, ?, 3)
            """, (
                mid,
                meal["region"],
                meal["station_id"],
                meal["name"],
                meal["sub"],
                meal["zone"],
                details,
                sources,
            ))
            if cur.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            errors.append(f"{meal['name']}: {e}")

    conn.commit()
    conn.close()

    print(f"\nInserted: {inserted}")
    print(f"Skipped (duplicate): {skipped}")
    if errors:
        print(f"Errors: {errors}")
    return inserted, skipped


if __name__ == "__main__":
    n, s = insert_meals()
    print(f"\n✅ Done — inserted {n}, skipped {s}")
