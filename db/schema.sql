-- === Core tables ===
CREATE TABLE IF NOT EXISTS garmin_daily (
  date TEXT PRIMARY KEY,          -- 'YYYY-MM-DD'
  steps INTEGER,
  calories INTEGER,
  distance_km REAL,
  sleep_hours REAL,
  hrv_ms REAL,
  rhr_bpm REAL,
  stress REAL,
  training_load REAL,
  vo2max REAL,
  readiness REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calories_daily (
  date TEXT PRIMARY KEY,
  calories INTEGER NOT NULL,
  source TEXT DEFAULT 'nutrition-mcp',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weight_daily (
  date TEXT PRIMARY KEY,
  weight_kg REAL,
  bodyfat_pct REAL,
  source TEXT DEFAULT 'samsung-or-manual',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Events for notifications & audit
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,             -- garmin_sync|nutrition_sync|recommendation|error
  message TEXT,
  payload TEXT,
  delivered INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
