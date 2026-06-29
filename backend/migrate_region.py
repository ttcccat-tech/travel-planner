"""
通用遷移腳本 — 將 JSON 資料庫化
用法：python3 migrate_region.py <region_code>
例：python3 migrate_region.py osaka
"""
import json, sqlite3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import DB_PATH, get_db

REGION = sys.argv[1] if len(sys.argv) > 1 else sys.exit("用法：python3 migrate_region.py <region_code>")
DATA_DIR = f"/var/repo/travel-planner/data/{REGION}"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"⚠️  檔案不存在，跳過：{path}")
        return None
    with open(path) as f:
        return json.load(f)

def migrate():
    data = {
        "attractions": load_json("attractions.json"),
        "stations":    load_json("stations.json"),
        "itineraries": load_json("itineraries.json"),
    }

    with get_db() as con:
        # ── 1. Region ──────────────────────────────────────────────
        names = {"seoul":"首爾","busan":"釜山","okinawa":"沖繩",
                 "fukuoka":"福岡","osaka":"大阪","tokyo":"東京"}
        names_en = {"seoul":"Seoul","busan":"Busan","okinawa":"Okinawa",
                    "fukuoka":"Fukuoka","osaka":"Osaka","tokyo":"Tokyo"}
        con.execute("INSERT OR IGNORE INTO regions (code, name, name_en) VALUES (?,?,?)",
                    (REGION, names.get(REGION, REGION), names_en.get(REGION, REGION)))
        print(f"✅ regions: {REGION}")

        # ── 2. Stations ─────────────────────────────────────────────
        stations_raw = (data["stations"] or {}).get("stations", [])
        for s in stations_raw:
            con.execute("""
                INSERT OR REPLACE INTO stations
                  (id, region_code, name, name_en, company, lines, zone, lat, lng, radius_m, active)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                s.get("id",""),
                REGION,
                s.get("name",""),
                s.get("name_en",""),
                s.get("company",""),
                json.dumps(s.get("line", [])),
                s.get("zone",""),
                s.get("lat"),
                s.get("lng"),
                s.get("radius_m", 600),
                int(s.get("active", True)),
            ))
        print(f"✅ stations: {len(stations_raw)} 筆")

        # ── 3. Attractions / Meals ──────────────────────────────────
        attractions_raw = (data["attractions"] or {}).get("attractions", [])
        att_count = meal_count = outlet_count = 0

        for a in attractions_raw:
            cat = a.get("category", "attraction")
            # category=meal → meals table, 其餘 → attractions table
            if cat == "meal":
                table = "meals"
                meal_count += 1
            elif cat == "outlet":
                table = "outlets"
                outlet_count += 1
            else:
                table = "attractions"
                att_count += 1

            con.execute(f"""
                INSERT OR REPLACE INTO {table}
                  (id, region_code, station_id, name, name_en, category, sub_category,
                   zone, location, lat, lng, ticket, stay_duration, need_reservation,
                   cash_only, priority, tags, description, sources, nearby_stations, details)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                a.get("id",""),
                REGION,
                a.get("station_id",""),
                a.get("name",""),
                a.get("name_en",""),
                cat,
                a.get("sub_category",""),
                a.get("zone",""),
                a.get("location",""),
                a.get("lat"),
                a.get("lng"),
                a.get("ticket",""),
                a.get("stay_duration",""),
                int(a.get("need_reservation", False)),
                int(a.get("cash_only", False)),
                int(a.get("priority", 3)),
                json.dumps(a.get("tags", [])),
                a.get("description",""),
                json.dumps(a.get("sources", [])),
                json.dumps(a.get("nearby_stations", [])),
                json.dumps(a.get("details", {})),
            ))
        print(f"✅ attractions: {att_count} 筆, meals: {meal_count} 筆, outlets: {outlet_count} 筆")

        # ── 4. Itineraries ───────────────────────────────────────────
        itineraries_raw = (data["itineraries"] or {}).get("itineraries", {})
        for day_key, itin in itineraries_raw.items():
            days_json = itin.get("days", [])
            con.execute("""
                INSERT OR REPLACE INTO itineraries
                  (region_code, day_key, name, suitable_for, layout, days_json)
                VALUES (?,?,?,?,?,?)
            """, (
                REGION,
                str(day_key),
                itin.get("name",""),
                itin.get("suitable_for",""),
                itin.get("layout",""),
                json.dumps(days_json, ensure_ascii=False),
            ))
        print(f"✅ itineraries: {len(itineraries_raw)} 筆（天）")

        con.commit()
        print(f"\n🎉 {REGION} 遷移完成！")

if __name__ == "__main__":
    migrate()
