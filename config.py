import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = [
    int(i.strip()) for i in os.getenv("ADMIN_IDS", "").split(",") if i.strip()
]
FAQ_URL: str = os.getenv("FAQ_URL", "https://kraven.io/faq")
DB_PATH: str = "kraven.db"
