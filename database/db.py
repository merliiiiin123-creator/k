import aiosqlite
from config import DB_PATH


# ─── Setup ────────────────────────────────────────────────────────────────────

async def init_db():
    """Create all tables on first run."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS applications (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER UNIQUE NOT NULL,
                username        TEXT,
                full_name       TEXT,
                platform        TEXT,
                profile_link    TEXT,
                follower_count  INTEGER,
                mutuals         INTEGER,
                account_age     REAL,
                is_verified     TEXT,
                pitch           TEXT,
                status          TEXT DEFAULT 'pending',
                admin_note      TEXT,
                submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at     TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                priority    TEXT NOT NULL,
                message     TEXT NOT NULL,
                status      TEXT DEFAULT 'open',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()


# ─── Applications ──────────────────────────────────────────────────────────────

async def upsert_application(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO applications
                (user_id, username, full_name, platform, profile_link,
                 follower_count, mutuals, account_age, is_verified, pitch)
            VALUES
                (:user_id, :username, :full_name, :platform, :profile_link,
                 :follower_count, :mutuals, :account_age, :is_verified, :pitch)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                platform=excluded.platform,
                profile_link=excluded.profile_link,
                follower_count=excluded.follower_count,
                mutuals=excluded.mutuals,
                account_age=excluded.account_age,
                is_verified=excluded.is_verified,
                pitch=excluded.pitch,
                status='pending',
                admin_note=NULL,
                submitted_at=CURRENT_TIMESTAMP
        """, data)
        await db.commit()


async def get_application(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM applications WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_pending_applications() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM applications WHERE status = 'pending' ORDER BY submitted_at"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def update_application_status(user_id: int, status: str, note: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE applications
            SET status = ?, admin_note = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (status, note, user_id))
        await db.commit()


# ─── Tickets ───────────────────────────────────────────────────────────────────

async def create_ticket(user_id: int, username: str, priority: str, message: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO tickets (user_id, username, priority, message)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, priority, message))
        await db.commit()
        return cur.lastrowid


async def get_open_tickets() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tickets WHERE status = 'open' ORDER BY created_at"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,)
        )
        await db.commit()
