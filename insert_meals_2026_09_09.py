#!/usr/bin/env python3
"""Weekly station food update - 2026-09-09"""
import sqlite3, json, uuid

DB = "/var/repo/travel-planner/backend/travel.db"

# (region_code, station_id, zone, name, sub_category, url)
FOODS = [
  # ── SEOUL (5 stations) ──
  ("seoul","seoul_016","明洞","Myth Jokbal 三星豬腳 24H","小吃","https://www.bigfang.tw/blog/post/samseong-jokbal"),
  ("seoul","seoul_004","弘大","弘大入口站 特色咖啡街甜點","咖啡甜點","https://feitravel.tw"),
  ("seoul","seoul_067","江南","江南站 韓屋村24H 豬肉湯飯","小吃","https://feitravel.tw"),
  ("seoul","seoul_002","龍山","龍山站 E-Mart Hyper 美食街","小吃","https://feitravel.tw"),
  ("seoul","seoul_014","乙支路","乙支路4街站 辦公大樓美食","小吃","https://feitravel.tw"),

  # ── BUSAN (5 stations) ──
  ("busan","busan_035","西面","西面站 釜山烤豬肉名店","小吃","https://feitravel.tw/p-5068753684"),
  ("busan","busan_035","西面","味贊王鹽烤肉 西面本店","烤肉","https://www.bigfang.tw/blog/post/busan-seomyeon-delicioius"),
  ("busan","busan_028","南浦","南浦站 釜山大福炸魚糕","小吃","https://feitravel.tw/p-5068333058"),
  ("busan","busan_027","札嘎其","札嘎其市場 烤貝類海鮮","小吃","https://flyfishlife.tw/busan-yunine"),
  ("busan","busan_042","海雲台","海雲台市場 元祖老奶奶湯飯","小吃","https://feitravel.tw"),

  # ── FUKUOKA (5 stations) ──
  ("fukuoka","fukuoka_001","博多","博多一双 泡系豚骨拉麵 百大","拉麵","https://omakaseje.com/zh-tw/articles/ub230860"),
  ("fukuoka","fukuoka_001","博多","Shin Shin 純情豚骨拉麵 DEITOS","拉麵","https://hedonistjun.com/hakata-ramen-shin-shin"),
  ("fukuoka","fukuoka_001","博多","資さんうどん 牛肉牛篣麵 24H","烏龍麵","https://marukoblog.tw/2018-10-18.html"),
  ("fukuoka","fukuoka_004","天神","麵屋兼虎 浓厚豚骨魚介沾麵","拉麵","https://catheadtravel.com/fukuoka-food-recommendations"),
  ("fukuoka","fukuoka_004","天神","Blue Bottle Coffee 天神警固神社","咖啡甜點","https://gogojp.tw/bluebottle-tenji"),

  # ── OSAKA (5 stations) ──
  ("osaka","osaka_station_004","難波","新宿焼肉 牛たんの檸檬 厚切牛舌","燒肉","https://www.hk01.com/%E6%97%85%E9%81%8A/60287801"),
  ("osaka","osaka_station_004","難波","うなぎの中庄 關西風鰻魚飯","日本料理","https://www.hk01.com/%E6%97%85%E9%81%8A/60287801"),
  ("osaka","osaka_station_004","難波","Kusaka Curry 歐風咖喱飯 高島屋","小吃","https://www.hk01.com/%E6%97%85%E9%81%8A/60287801"),
  ("osaka","osaka_station_013","心齋橋","KIBORI 北海文字燒×鐵板燒","居酒屋","https://omakaseje.com/zh-tw/articles/ac314547"),
  ("osaka","osaka_station_001","大阪","北極星 蛋包飯總本店","餐廳","https://omakaseje.com/zh-tw/articles/ac314547"),

  # ── TOKYO (5 stations) ──
  ("tokyo","tokyo_002","新宿","Afuri 柚子鹽拉麵 LUMINE EST","拉麵","https://www.klook.com/zh-TW/blog/shinjuku-food"),
  ("tokyo","tokyo_002","新宿","六歌仙 和牛燒肉放題","燒肉","https://www.klook.com/zh-TW/blog/shinjuku-food"),
  ("tokyo","tokyo_002","新宿","HARBS LUMINE 水果千層蛋糕","甜點","https://www.klook.com/zh-TW/blog/shinjuku-food"),
  ("tokyo","tokyo_005","上野","拉麵 鴨 to 蔥 24H 清湯鴨肉","小吃","https://tw.trip.com/blog/%E4%B8%8A%E9%87%8E%E7%BE%8E%E9%A3%9F"),
  ("tokyo","tokyo_006","淺草","大黑屋天婦羅 130年 蝦\/牡蠣","小吃","https://kanzashi-tokyoasakusa.com/tc/activity/activity-1835"),

  # ── OKINAWA (5 stations) ──
  ("okinawa","okinawa_station_008","縣廳前","縣廳前站 通堂拉麵 男人麵","小吃","https://todolist-japan.com/zh/naha-food-guide"),
  ("okinawa","okinawa_station_008","縣廳前","縣廳前站 Jack's steakhouse 88年","牛排","https://todolist-japan.com/zh/naha-food-guide"),
  ("okinawa","okinawa_station_009","牧志","牧志站 浜屋拉麵 沖繩麵 51年","小吃","https://todolist-japan.com/zh/naha-food-guide"),
  ("okinawa","okinawa_station_008","縣廳前","縣廳前站 花織咖啡 草莓蛋糕","咖啡甜點","https://todolist-japan.com/zh/naha-food-guide"),
  ("okinawa","okinawa_station_008","縣廳前","縣廳前站 豬肉蛋飯糰 限定","小吃","https://todolist-japan.com/zh/naha-food-guide"),
]

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get existing URLs
    cur.execute("SELECT sources FROM meals")
    existing = set()
    for (s,) in cur.fetchall():
        try:
            for u in json.loads(s) if s else []:
                existing.add(u)
        except Exception:
            pass

    # Verify stations exist
    cur.execute("SELECT id FROM stations")
    valid_stations = {r[0] for r in cur.fetchall()}

    inserted = skipped = 0
    errors = []

    for row in FOODS:
        region, sid, zone, name, sub_cat, url = row
        if sid not in valid_stations:
            errors.append(f"[SKIP] invalid station: {sid} ({name})")
            continue
        if url in existing:
            skipped += 1
            continue

        mid = f"meal_{region}_{uuid.uuid4().hex[:8]}"
        details = json.dumps({"blog_article": url})
        sources = json.dumps([url])

        try:
            cur.execute("""
                INSERT INTO meals (id,region_code,station_id,name,category,sub_category,zone,details,sources)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (mid, region, sid, name, 'meal', sub_cat, zone, details, sources))
            inserted += 1
            print(f"  + {name[:40]}")
        except Exception as e:
            errors.append(f"[ERR] {name}: {e}")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM meals")
    total = cur.fetchone()[0]
    conn.close()

    print(f"\n✅ Inserted: {inserted}")
    print(f"⏭ Skipped (duplicate): {skipped}")
    print(f"📊 Total meals now: {total}")
    for e in errors:
        print(e)

if __name__ == "__main__":
    main()
