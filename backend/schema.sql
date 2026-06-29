-- Travel Planner SQLite Schema
-- Region → Station → Attraction/Meal/Outlet (一對多)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS regions (
    code        TEXT PRIMARY KEY,   -- 'seoul', 'osaka', 'tokyo'...
    name        TEXT NOT NULL,
    name_en     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stations (
    id          TEXT PRIMARY KEY,   -- 'seoul_001', 'osaka_001'...
    region_code TEXT NOT NULL,
    name        TEXT NOT NULL,
    name_en     TEXT,
    company     TEXT,               -- 'MRT', 'JR', 'KTX'...
    lines       TEXT,               -- JSON array: ["1號線","2號線"]
    zone        TEXT,               -- 所屬區域：龍山/江南/弘大...
    lat         REAL,
    lng         REAL,
    radius_m    INTEGER DEFAULT 600,
    active      INTEGER DEFAULT 1,  -- 0=停用, 1=啟用
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES regions(code)
);

CREATE TABLE IF NOT EXISTS attractions (
    id              TEXT PRIMARY KEY,   -- UUID or short-id: 'gwangjang'
    region_code     TEXT NOT NULL,
    station_id      TEXT,                -- 主要車站（最近/地鐵優先）
    name            TEXT NOT NULL,
    name_en         TEXT,
    category        TEXT NOT NULL,       -- 'attraction' / 'meal' / 'shrine' / 'hotel' / 'hidden_gem'
    sub_category    TEXT,
    zone            TEXT,                -- 所屬分區
    location        TEXT,                -- 地址/描述
    lat             REAL,
    lng             REAL,
    ticket          TEXT,                -- 免費/付費/約XXX
    stay_duration   TEXT,                -- '1.5小時', '2小時'
    need_reservation INTEGER DEFAULT 0,
    cash_only       INTEGER DEFAULT 0,
    priority        INTEGER DEFAULT 3,   -- 1=必去 3=普通 5=閒逛
    tags            TEXT,                 -- JSON array: ["市場","美食","明洞"]
    description      TEXT,
    sources         TEXT,                 -- JSON array: URL list
    nearby_stations TEXT,                -- JSON array: 附近車站ID
    details         TEXT,                -- JSON object: {blog_article, google_maps, youtube}
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES regions(code),
    FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS meals (
    -- Meal 從 attractions 分離出來，但共享同一個 ID 空間
    -- 若 meal 有独立数据，可单独建表；此处与 attractions 表合并，通过 category 区分
    id              TEXT PRIMARY KEY,
    region_code     TEXT NOT NULL,
    station_id      TEXT,
    name            TEXT NOT NULL,
    name_en         TEXT,
    category        TEXT NOT NULL DEFAULT 'meal',  -- 固定為 meal
    sub_category    TEXT,               -- '小吃' / '餐廳' / '咖啡'
    zone            TEXT,
    location        TEXT,
    lat             REAL,
    lng             REAL,
    ticket          TEXT,
    stay_duration   TEXT,
    need_reservation INTEGER DEFAULT 0,
    cash_only       INTEGER DEFAULT 0,
    priority        INTEGER DEFAULT 3,
    tags            TEXT,
    description     TEXT,
    sources         TEXT,
    nearby_stations TEXT,
    details         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES regions(code),
    FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS outlets (
    id              TEXT PRIMARY KEY,
    region_code     TEXT NOT NULL,
    station_id      TEXT,
    name            TEXT NOT NULL,
    name_en         TEXT,
    category        TEXT NOT NULL DEFAULT 'outlet',  -- outlet / shopping / convenience
    zone            TEXT,
    location        TEXT,
    lat             REAL,
    lng             REAL,
    ticket          TEXT,
    stay_duration   TEXT,
    priority        INTEGER DEFAULT 3,
    tags            TEXT,
    description     TEXT,
    sources         TEXT,
    nearby_stations TEXT,
    details         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES regions(code),
    FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS itineraries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    region_code     TEXT NOT NULL,
    day_key         TEXT NOT NULL,      -- 'day1', 'day2', ... or '1','2'
    name            TEXT,
    suitable_for    TEXT,               -- '商務/轉機客', '家庭', '情侶'
    layout          TEXT,               -- '單區精華', '多區漫遊'
    days_json       TEXT NOT NULL,      -- 完整 JSON array（含所有天數的 activities）
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES regions(code)
);

-- 查詢：某車站的所有景點
-- CREATE INDEX IF NOT EXISTS idx_attractions_station ON attractions(station_id);
-- CREATE INDEX IF NOT EXISTS idx_attractions_zone   ON attractions(zone);
-- CREATE INDEX IF NOT EXISTS idx_stations_region    ON stations(region_code);
