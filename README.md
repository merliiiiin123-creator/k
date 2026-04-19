# Kraven Bot

Telegram bot for managing KOL, Project, Investor, and Ecosystem Partner applications for Kraven.

---

## Features

| Category | Steps | Key Fields |
|---|---|---|
| 🎤 KOL | 9-step form | Name, email, socials, niche, audience, engagement, past collabs |
| 🏢 Project | 11-step form | Project info, multi-select services, budget, tenure, traction |
| 💰 Investor | 8-step form | Motivation, scope, personal info, experience, investment size |
| 🤝 Partner | 8-step form | Terms, ecosystem interest, org info, services overview, cover letter |
| 💬 Support | Ticket + FAQ | Email, description, admin DM alerts |
| 🛠 Admin Panel | `/admin` command | Approve/reject any queue, DM applicants, close tickets |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — fill in BOT_TOKEN, ADMIN_IDS, FAQ_URL

# 3. Run
python bot.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | Comma-separated Telegram user IDs of admins |
| `FAQ_URL` | URL to your FAQ / help center page |

---

## Project Structure

```
kraven_bot/
├── bot.py                    # Entry point
├── config.py                 # Env vars
├── utils.py                  # Validators & helpers
├── requirements.txt
├── .env.example
├── database/
│   └── db.py                 # All SQLite tables and queries
├── handlers/
│   ├── start.py              # /start, main menu, category routing
│   ├── kol.py                # KOL 9-step form + status + ID
│   ├── project.py            # Project 11-step form with multi-select services
│   ├── investor.py           # Investor 8-step form
│   ├── partner.py            # Partner 8-step form
│   ├── support.py            # Support tickets + FAQ redirect
│   └── admin.py              # Admin panel — all queues + ticket management
├── keyboards/
│   └── menus.py              # All InlineKeyboardMarkup layouts
└── states/
    └── forms.py              # FSM state groups for all flows
```

---

## Admin Commands

- `/admin` — Opens the admin panel (restricted to `ADMIN_IDS`)

From the admin panel you can:
- View all pending applications per category
- Approve or reject with an optional note
- Auto-DM applicants with the outcome
- View and close open support tickets

---

## Notes

- **Database:** SQLite by default. Swap to PostgreSQL by replacing `aiosqlite` with `asyncpg` — the schema is standard SQL.
- **Services multi-select:** The project form uses a toggle-based inline keyboard — users can select multiple Kraven services before proceeding.
- **Validation:** Email format and URL format are validated on every relevant step.
