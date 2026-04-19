import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, kol, project, investor, partner, support, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set. Please fill in your .env file.")

    await init_db()
    logger.info("Database initialised.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register routers — order matters for FSM fallthrough
    dp.include_router(start.router)
    dp.include_router(kol.router)
    dp.include_router(project.router)
    dp.include_router(investor.router)
    dp.include_router(partner.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)

    logger.info("Kraven Bot is live 🚀")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
