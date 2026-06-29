"""
Seoul Pilot — 遷移 JSON 資料進 SQLite
Region → Station → Attraction/Meals/Outlet/Itinerary
"""
import json, sqlite3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import DB_PATH, get_db

DATA_DIR = "/var/repo/travel-planner/data/seoul"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
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
        con.execute("INSERT OR IGNORE INTO regions (code, name, name_en) VALUES (?,?,?)",
                    ("seoul", "首爾", "Seoul"))
        print("✅ regions: seoul")

        # ── 2. Stations ─────────────────────────────────────────────
        stations_raw = data["stations"]["stations"]
        for s in stations_raw:
            con.execute("""
                INSERT OR REPLACE INTO stations
                  (id, region_code, name, name_en, company, lines, zone, lat, lng, radius_m, active)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                s["id"], "seoul",
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

        # ── 3. Attractions (非 meal) ─────────────────────────────────
        attractions_raw = data["attractions"]["attractions"]
        meal_count = 0
        att_count = 0
        outlet_count = 0

        for a in attractions_raw:
            cat = a.get("category", "attraction")
            # 依照老大定義：attraction/shrine/hotel/hidden_gem → attractions
            # meal → meals table
            table = "meals" if cat == "meal" else "attractions"
            if cat == "outlet":
                table = "outlets"

            if table == "meals":
                meal_count += 1
            elif table == "outlets":
                outlet_count += 1
            else:
                att_count += 1

            con.execute(f"""
                INSERT OR REPLACE INTO {table}
                  (id, region_code, station_id, name, name_en, category, sub_category,
                   zone, location, lat, lng, ticket, stay_duration, need_reservation,
                   cash_only, priority, tags, description, sources, nearby_stations, details)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                a.get("id",""),
                "seoul",
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
        itineraries_raw = data["itineraries"]["itineraries"]
        # itineraries 是 dict: {"1": {...day1...}, "2": {...day2...}, ...}
        for day_key, itin in itineraries_raw.items():
            days_json = itin.get("days", [])
            # days_json[0] 內含 day/type/title/activities/zones
            con.execute("""
                INSERT OR REPLACE INTO itineraries
                  (region_code, day_key, name, suitable_for, layout, days_json)
                VALUES (?,?,?,?,?,?)
            """, (
                "seoul",
                str(day_key),
                itin.get("name",""),
                itin.get("suitable_for",""),
                itin.get("layout",""),
                json.dumps(days_json, ensure_ascii=False),
            ))
        print(f"✅ itineraries: {len(itineraries_raw)} 筆（天）")

        con.commit()

    print("\n遷移完成！")

if __name__ == "__main__":
    migrate()
