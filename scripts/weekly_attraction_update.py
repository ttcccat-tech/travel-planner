#!/usr/bin/env python3
"""每週旅遊景點擴充任務 - 2026-09-06"""

import sqlite3, json, re, sys, os
sys.path.insert(0, '/var/repo/travel-planner/backend')

DB_PATH = '/var/repo/travel-planner/backend/travel.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_existing_attractions(region):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT name, sources, details FROM attractions WHERE region_code='{region}'")
    rows = cur.fetchall()
    conn.close()
    existing = {}
    for r in rows:
        existing[r['name'].lower().strip()] = r
        if r['sources']:
            try:
                srcs = json.loads(r['sources'])
                for s in srcs:
                    existing[s.lower().strip()] = r
            except: pass
        if r['details']:
            try:
                d = json.loads(r['details'])
                for k, v in d.items():
                    if v and isinstance(v, str) and v.startswith('http'):
                        existing[v.lower().strip()] = r
            except: pass
    return existing

def get_stations(region):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id, name, zone FROM stations WHERE region_code='{region}' AND active=1 ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [(r['id'], r['name'], r['zone']) for r in rows]

def already_exists(existing, name, sources=None):
    name_key = name.lower().strip()
    if name_key in existing:
        return True
    if sources:
        for s in sources:
            if s.lower().strip() in existing:
                return True
    return False

def slugify(text):
    """Generate a short ID from name"""
    # Remove common prefixes/suffixes
    text = re.sub(r'^[釜山|東京|大阪|首爾|福岡|沖繩| Seoul| Busan| Osaka| Tokyo| Fukuoka| Okinawa]+\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    return text[:20].lower() if text else text.lower()

def generate_id(region, name):
    base = slugify(name)
    if not base:
        base = 'attraction'
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM attractions WHERE id LIKE '{region}_{base}%'")
    count = cur.fetchone()[0]
    conn.close()
    suffix = f"_{count+1}" if count > 0 else ""
    return f"{region}_{base}{suffix}"

def insert_attraction(data):
    conn = get_db()
    cur = conn.cursor()
    cols = ['id','region_code','station_id','name','category','zone','sources','details']
    placeholders = ','.join(['?' for _ in cols])
    values = tuple(data.get(c, '') for c in cols)
    try:
        cur.execute(f"INSERT OR IGNORE INTO attractions ({','.join(cols)}) VALUES ({placeholders})", values)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"  [ERROR] Insert failed: {e}")
        return False
    finally:
        conn.close()

def mark_added(region, name, station_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM attractions WHERE region_code='{region}' AND name=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row['id'] if row else None

if __name__ == '__main__':
    print("Starting weekly attraction update...")
    print(f"DB: {DB_PATH}")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT code, name FROM regions ORDER BY code")
    regions = [(r['code'], r['name']) for r in cur.fetchall()]
    conn.close()
    print(f"Regions: {[r[0] for r in regions]}")
    print("Done - placeholder. Real search+insert done via subprocess calls.")
