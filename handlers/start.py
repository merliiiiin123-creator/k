from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from keyboards.menus import main_menu, kol_menu, support_menu

router = Router()

WELCOME = """
👋 *Welcome to Kraven Bot!*

I'm here to guide you through Kraven's engagement opportunities — whether you're a creator, a project, an investor, or a potential partner.

━━━━━━━━━━━━━━━━━━━━
*What would you like to do today?*
━━━━━━━━━━━━━━━━━━━━

Select a category below 👇
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME, parse_mode="Markdown", reply_markup=main_menu())


@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME, parse_mode="Markdown", reply_markup=main_menu())


# ─── Category routers ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "cat:kol")
async def cat_kol(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎤 *Key Opinion Leader (KOL)*\n\n"
        "Join Kraven's creator network and gain access to exclusive campaigns, "
        "networking events, and brand deals.\n\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=kol_menu()
    )


@router.callback_query(F.data == "cat:support")
async def cat_support(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 *General Inquiry / Support*\n\n"
        "Need help or have a question? We've got you covered.",
        parse_mode="Markdown",
        reply_markup=support_menu()
    )


# cat:project, cat:investor, cat:partner are handled directly in their
# respective handler files via their own routers.
