
import os
import aiosqlite

DB_PATH = os.getenv("NUTRITION_DB_PATH", "/data/nutrition.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal TEXT NOT NULL,
    description TEXT,
    calories REAL NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
"""

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()

async def insert_meal(entry):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO meals(date, meal, description, calories, protein, carbs, fat) VALUES (?,?,?,?,?,?,?)",
            (entry['date'], entry['meal'], entry.get('description'), entry['calories'], entry.get('protein',0), entry.get('carbs',0), entry.get('fat',0))
        )
        await db.commit()

async def daily_summary(date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT IFNULL(SUM(calories),0), IFNULL(SUM(protein),0), IFNULL(SUM(carbs),0), IFNULL(SUM(fat),0) FROM meals WHERE date = ?", (date,)
        )
        row = await cur.fetchone()
        return {"date": date, "calories": float(row[0] or 0), "protein": float(row[1] or 0), "carbs": float(row[2] or 0), "fat": float(row[3] or 0)}

async def list_meals(date=None, start_date=None, end_date=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if date:
            cur = await db.execute(
                "SELECT date, meal, description, calories, protein, carbs, fat FROM meals WHERE date = ? ORDER BY id DESC",
                (date,)
            )
        elif start_date and end_date:
            cur = await db.execute(
                "SELECT date, meal, description, calories, protein, carbs, fat FROM meals WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC",
                (start_date, end_date)
            )
        else:
            cur = await db.execute(
                "SELECT date, meal, description, calories, protein, carbs, fat FROM meals ORDER BY date DESC, id DESC LIMIT 100"
            )
        rows = await cur.fetchall()
        return [{
            "date": r[0], "meal": r[1], "description": r[2],
            "calories": float(r[3]), "protein": float(r[4]), "carbs": float(r[5]), "fat": float(r[6])
        } for r in rows]
