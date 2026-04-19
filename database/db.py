import aiosqlite
from config import DB_PATH


# ─── Init ──────────────────────────────────────────────────────────────────────

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS kol_applications (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id             INTEGER UNIQUE NOT NULL,
                username            TEXT,
                full_name           TEXT,
                email               TEXT,
                x_handle            TEXT,
                telegram_handle     TEXT,
                discord_handle      TEXT,
                niche               TEXT,
                audience_size       TEXT,
                engagement_metrics  TEXT,
                past_collabs        TEXT,
                status              TEXT DEFAULT 'pending',
                admin_note          TEXT,
                submitted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at         TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS project_applications (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id             INTEGER NOT NULL,
                username            TEXT,
                project_name        TEXT,
                website_url         TEXT,
                x_account           TEXT,
                tg_discord          TEXT,
                contact_name        TEXT,
                contact_email       TEXT,
                project_category    TEXT,
                services_selected   TEXT,
                budget_range        TEXT,
                project_tenure      TEXT,
                traction_desc       TEXT,
                status              TEXT DEFAULT 'pending',
                admin_note          TEXT,
                submitted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at         TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS investor_applications (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id             INTEGER NOT NULL,
                username            TEXT,
                full_name           TEXT,
                email               TEXT,
                country             TEXT,
                motivation          TEXT,
                investment_scope    TEXT,
                invest_experience   TEXT,
                invest_size         TEXT,
                specific_questions  TEXT,
                status              TEXT DEFAULT 'pending',
                admin_note          TEXT,
                submitted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at         TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS partner_applications (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id             INTEGER NOT NULL,
                username            TEXT,
                company_name        TEXT,
                contact_person      TEXT,
                contact_email       TEXT,
                website             TEXT,
                services_overview   TEXT,
                partnership_terms   TEXT,
                ecosystem_interest  TEXT,
                cover_letter        TEXT,
                status              TEXT DEFAULT 'pending',
                admin_note          TEXT,
                submitted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at         TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS support_tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                email       TEXT,
                priority    TEXT DEFAULT 'General',
                description TEXT NOT NULL,
                status      TEXT DEFAULT 'open',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()


# ─── Helpers ───────────────────────────────────────────────────────────────────

async def _upsert(table: str, conflict_col: str, data: dict):
    cols = ", ".join(data.keys())
    placeholders = ", ".join(f":{k}" for k in data.keys())
    updates = ", ".join(f"{k}=excluded.{k}" for k in data.keys() if k != conflict_col)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT({conflict_col}) DO UPDATE SET {updates}, "
            f"status='pending', admin_note=NULL, submitted_at=CURRENT_TIMESTAMP",
            data
        )
        await db.commit()


async def _insert(table: str, data: dict) -> int:
    cols = ", ".join(data.keys())
    placeholders = ", ".join(f":{k}" for k in data.keys())
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", data
        )
        await db.commit()
        return cur.lastrowid


async def _get_one(table: str, user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"SELECT * FROM {table} WHERE user_id = ? ORDER BY submitted_at DESC LIMIT 1",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def _get_pending(table: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"SELECT * FROM {table} WHERE status='pending' ORDER BY submitted_at"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def _update_status(table: str, user_id: int, status: str, note: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE {table} SET status=?, admin_note=?, reviewed_at=CURRENT_TIMESTAMP "
            f"WHERE user_id=?",
            (status, note, user_id)
        )
        await db.commit()


# ─── KOL ───────────────────────────────────────────────────────────────────────

async def upsert_kol(data: dict): await _upsert("kol_applications", "user_id", data)
async def get_kol(user_id: int): return await _get_one("kol_applications", user_id)
async def get_pending_kols(): return await _get_pending("kol_applications")
async def update_kol_status(uid, status, note=""): await _update_status("kol_applications", uid, status, note)


# ─── Project ───────────────────────────────────────────────────────────────────

async def insert_project(data: dict) -> int: return await _insert("project_applications", data)
async def get_project(user_id: int): return await _get_one("project_applications", user_id)
async def get_pending_projects(): return await _get_pending("project_applications")
async def update_project_status(uid, status, note=""): await _update_status("project_applications", uid, status, note)


# ─── Investor ──────────────────────────────────────────────────────────────────

async def insert_investor(data: dict) -> int: return await _insert("investor_applications", data)
async def get_investor(user_id: int): return await _get_one("investor_applications", user_id)
async def get_pending_investors(): return await _get_pending("investor_applications")
async def update_investor_status(uid, status, note=""): await _update_status("investor_applications", uid, status, note)


# ─── Partner ───────────────────────────────────────────────────────────────────

async def insert_partner(data: dict) -> int: return await _insert("partner_applications", data)
async def get_partner(user_id: int): return await _get_one("partner_applications", user_id)
async def get_pending_partners(): return await _get_pending("partner_applications")
async def update_partner_status(uid, status, note=""): await _update_status("partner_applications", uid, status, note)


# ─── Tickets ───────────────────────────────────────────────────────────────────

async def create_ticket(user_id: int, username: str, email: str, description: str) -> int:
    return await _insert("support_tickets", {
        "user_id": user_id, "username": username,
        "email": email, "description": description
    })


async def get_open_tickets() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM support_tickets WHERE status='open' ORDER BY created_at"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE support_tickets SET status='closed' WHERE id=?", (ticket_id,))
        await db.commit()
