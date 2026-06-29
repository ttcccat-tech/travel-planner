"""
Travel Planner — FastAPI Backend
SQLite + REST API
"""
import sqlite3, json, os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import contextmanager
from contextlib import asynccontextmanager
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "travel.db"
PORT     = int(os.getenv("API_PORT", 8001))

@asynccontextmanager
async def lifespan(app: FastAPI):
    make_db()
    yield

app = FastAPI(title="Travel Planner API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB helper ────────────────────────────────────────────────────────────────
def make_db():
    """Ensure schema exists (idempotent)."""
    with open(BASE_DIR / "schema.sql") as f:
        with get_db() as con:
            con.executescript(f.read())
            con.commit()

@contextmanager
def get_db():
    con: sqlite3.Connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()

def row2dict(row: sqlite3.Row) -> dict:
    out = dict(row)
    for k, v in out.items():
        if isinstance(v, str) and (v.startswith("[") or v.startswith("{")):
            try:
                out[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass
    return out

def rows2list(rows) -> list:
    return [row2dict(r) for r in rows]

# ── Init ─────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    make_db()

# ═══════════════════════════════════════════════════════════════════════════
# REGIONS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/regions")
def list_regions():
    with get_db() as con:
        rows = con.execute("SELECT * FROM regions ORDER BY name").fetchall()
    return rows2list(rows)

@app.get("/api/regions/{code}")
def get_region(code: str):
    with get_db() as con:
        row = con.execute("SELECT * FROM regions WHERE code=?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, f"Region '{code}' not found")
    return row2dict(row)

@app.post("/api/regions")
def create_region(payload: dict):
    code = payload.get("code","")
    name = payload.get("name","")
    name_en = payload.get("name_en","")
    if not code or not name:
        raise HTTPException(400, "code and name required")
    with get_db() as con:
        try:
            con.execute(
                "INSERT OR IGNORE INTO regions (code, name, name_en) VALUES (?,?,?)",
                (code, name, name_en)
            )
            con.commit()
        except Exception as e:
            raise HTTPException(400, str(e))
    return {"code": code, "name": name}

# ═══════════════════════════════════════════════════════════════════════════
# STATIONS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/{region}/stations")
def list_stations(region: str):
    with get_db() as con:
        rows = con.execute(
            "SELECT * FROM stations WHERE region_code=? ORDER BY id",
            (region,)
        ).fetchall()
    return rows2list(rows)

@app.get("/api/{region}/stations/{station_id}")
def get_station(region: str, station_id: str):
    with get_db() as con:
        row = con.execute(
            "SELECT * FROM stations WHERE id=? AND region_code=?",
            (station_id, region)
        ).fetchone()
    if not row:
        raise HTTPException(404, f"Station '{station_id}' not found")
    return row2dict(row)

@app.post("/api/{region}/stations")
def upsert_station(region: str, payload: dict):
    with get_db() as con:
        con.execute("""
            INSERT OR REPLACE INTO stations
              (id, region_code, name, name_en, company, lines, zone, lat, lng, radius_m, active)
            VALUES (?,?,?,?,?,?,?,?,?,?,
                COALESCE((SELECT active FROM stations WHERE id=?), 1))
        """, (
            payload["id"], region, payload.get("name",""),
            payload.get("name_en",""), payload.get("company",""),
            json.dumps(payload.get("lines",[])),
            payload.get("zone",""),
            payload.get("lat") or None,
            payload.get("lng") or None,
            payload.get("radius_m", 600),
            payload["id"]
        ))
        con.commit()
    return {"id": payload["id"], "status": "ok"}

# ═══════════════════════════════════════════════════════════════════════════
# ATTRACTIONS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/{region}/attractions")
def list_attractions(region: str, zone: str = None, category: str = None, station_id: str = None):
    with get_db() as con:
        q = "SELECT * FROM attractions WHERE region_code=?";
        params = [region]
        if zone:
            q += " AND zone=?"; params.append(zone)
        if category:
            q += " AND category=?"; params.append(category)
        if station_id:
            q += " AND station_id=?"; params.append(station_id)
        q += " ORDER BY priority ASC, name"
        rows = con.execute(q, params).fetchall()
    return rows2list(rows)

@app.get("/api/{region}/attractions/{att_id}")
def get_attraction(region: str, att_id: str):
    with get_db() as con:
        row = con.execute(
            "SELECT * FROM attractions WHERE id=? AND region_code=?",
            (att_id, region)
        ).fetchone()
    if not row:
        raise HTTPException(404, f"Attraction '{att_id}' not found")
    return row2dict(row)

@app.post("/api/{region}/attractions")
def upsert_attraction(region: str, payload: dict):
    with get_db() as con:
        con.execute("""
            INSERT OR REPLACE INTO attractions
              (id, region_code, station_id, name, name_en, category, sub_category,
               zone, location, lat, lng, ticket, stay_duration, need_reservation,
               cash_only, priority, tags, description, sources, nearby_stations, details)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            payload["id"], region,
            payload.get("station_id") or "",
            payload.get("name",""),
            payload.get("name_en",""),
            payload.get("category","attraction"),
            payload.get("sub_category",""),
            payload.get("zone",""),
            payload.get("location",""),
            payload.get("lat"), payload.get("lng"),
            payload.get("ticket",""),
            payload.get("stay_duration",""),
            int(payload.get("need_reservation", False)),
            int(payload.get("cash_only", False)),
            int(payload.get("priority", 3)),
            json.dumps(payload.get("tags",[])),
            payload.get("description",""),
            json.dumps(payload.get("sources",[])),
            json.dumps(payload.get("nearby_stations",[])),
            json.dumps(payload.get("details",{})),
        ))
        con.commit()
    return {"id": payload["id"], "status": "ok"}

@app.delete("/api/{region}/attractions/{att_id}")
def delete_attraction(region: str, att_id: str):
    with get_db() as con:
        cur = con.execute(
            "DELETE FROM attractions WHERE id=? AND region_code=? RETURNING id",
            (att_id, region)
        )
        deleted = cur.fetchone()
        con.commit()
    if not deleted:
        raise HTTPException(404, f"Attraction '{att_id}' not found")
    return {"id": att_id, "status": "deleted"}

# ═══════════════════════════════════════════════════════════════════════════
# MEALS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/{region}/meals")
def list_meals(region: str, zone: str = None, station_id: str = None):
    with get_db() as con:
        q = "SELECT * FROM meals WHERE region_code=?";
        params = [region]
        if zone:
            q += " AND zone=?"; params.append(zone)
        if station_id:
            q += " AND station_id=?"; params.append(station_id)
        q += " ORDER BY priority ASC, name"
        rows = con.execute(q, params).fetchall()
    return rows2list(rows)

@app.post("/api/{region}/meals")
def upsert_meal(region: str, payload: dict):
    with get_db() as con:
        con.execute("""
            INSERT OR REPLACE INTO meals
              (id, region_code, station_id, name, name_en, category, sub_category,
               zone, location, lat, lng, ticket, stay_duration, need_reservation,
               cash_only, priority, tags, description, sources, nearby_stations, details)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            payload["id"], region,
            payload.get("station_id") or "",
            payload.get("name",""),
            payload.get("name_en",""),
            "meal",
            payload.get("sub_category",""),
            payload.get("zone",""),
            payload.get("location",""),
            payload.get("lat") or None,
            payload.get("lng") or None,
            payload.get("ticket",""),
            payload.get("stay_duration",""),
            int(payload.get("need_reservation", False)),
            int(payload.get("cash_only", False)),
            int(payload.get("priority", 3)),
            json.dumps(payload.get("tags",[])),
            payload.get("description",""),
            json.dumps(payload.get("sources",[])),
            json.dumps(payload.get("nearby_stations",[])),
            json.dumps(payload.get("details",{})),
        ))
        con.commit()
    return {"id": payload["id"], "status": "ok"}

# ═══════════════════════════════════════════════════════════════════════════
# OUTLETS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/{region}/outlets")
def list_outlets(region: str, zone: str = None, station_id: str = None):
    with get_db() as con:
        q = "SELECT * FROM outlets WHERE region_code=?";
        params = [region]
        if zone:
            q += " AND zone=?"; params.append(zone)
        if station_id:
            q += " AND station_id=?"; params.append(station_id)
        q += " ORDER BY priority ASC, name"
        rows = con.execute(q, params).fetchall()
    return rows2list(rows)

@app.post("/api/{region}/outlets")
def upsert_outlet(region: str, payload: dict):
    with get_db() as con:
        con.execute("""
            INSERT OR REPLACE INTO outlets
              (id, region_code, station_id, name, name_en, category,
               zone, location, lat, lng, ticket, stay_duration,
               priority, tags, description, sources, nearby_stations, details)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            payload["id"], region,
            payload.get("station_id") or "",
            payload.get("name",""),
            payload.get("name_en",""),
            payload.get("category","outlet"),
            payload.get("zone",""),
            payload.get("location",""),
            payload.get("lat") or None,
            payload.get("lng") or None,
            payload.get("ticket",""),
            payload.get("stay_duration",""),
            int(payload.get("priority", 3)),
            json.dumps(payload.get("tags",[])),
            payload.get("description",""),
            json.dumps(payload.get("sources",[])),
            json.dumps(payload.get("nearby_stations",[])),
            json.dumps(payload.get("details",{})),
        ))
        con.commit()
    return {"id": payload["id"], "status": "ok"}

# ═══════════════════════════════════════════════════════════════════════════
# ITINERARIES
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/{region}/itineraries")
def list_itineraries(region: str):
    with get_db() as con:
        rows = con.execute(
            "SELECT * FROM itineraries WHERE region_code=? ORDER BY day_key",
            (region,)
        ).fetchall()
    return rows2list(rows)

@app.get("/api/{region}/itineraries/{day_key}")
def get_itinerary(region: str, day_key: str):
    with get_db() as con:
        row = con.execute(
            "SELECT * FROM itineraries WHERE region_code=? AND day_key=?",
            (region, day_key)
        ).fetchone()
    if not row:
        raise HTTPException(404, f"Itinerary '{day_key}' not found")
    return row2dict(row)

@app.post("/api/{region}/itineraries")
def upsert_itinerary(region: str, payload: dict):
    with get_db() as con:
        # days_json is the full itinerary array (may contain multiple days in one record)
        days_json = json.dumps(payload.get("days_json", payload.get("days", [])))
        con.execute("""
            INSERT OR REPLACE INTO itineraries
              (region_code, day_key, name, suitable_for, layout, days_json, updated_at)
            VALUES (?,?,?,?,?,?, CURRENT_TIMESTAMP)
        """, (
            region,
            payload.get("day_key",""),
            payload.get("name",""),
            payload.get("suitable_for",""),
            payload.get("layout",""),
            days_json,
        ))
        con.commit()
    return {"region_code": region, "day_key": payload.get("day_key"), "status": "ok"}

@app.delete("/api/{region}/itineraries/{day_key}")
def delete_itinerary(region: str, day_key: str):
    with get_db() as con:
        cur = con.execute(
            "DELETE FROM itineraries WHERE region_code=? AND day_key=? RETURNING rowid",
            (region, day_key)
        )
        deleted = cur.fetchone()
        con.commit()
    if not deleted:
        raise HTTPException(404, f"Itinerary '{day_key}' not found")
    return {"day_key": day_key, "status": "deleted"}

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/health")
def health():
    return {"status": "ok", "db": str(DB_PATH)}

# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
