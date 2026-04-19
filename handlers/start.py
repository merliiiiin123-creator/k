from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from keyboards.menus import main_menu, kol_menu, support_menu

router = Router()

WELCOME = """
⚡ *Welcome to Kraven.*

Where creators get campaigns. Projects get distribution. Deals get done.

━━━━━━━━━━━━━━━━━━━━
Kraven connects elite KOLs, high-growth projects, and strategic investors into one ecosystem built for *real impact* — not vanity metrics.

Whether you're here to *run campaigns*, *grow your project*, *invest*, or *partner up* — you're in the right place.
━━━━━━━━━━━━━━━━━━━━

*Who are you?* 👇
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
        "🎤 *Kraven KOL Network*\n\n"
        "Stop chasing brands. Let them come to you.\n\n"
        "Kraven's KOL network plugs you directly into *paid UGC campaigns*, "
        "*KOL deals*, *engagement groups*, and a community of creators who are "
        "actually moving the needle in Web3 and beyond.\n\n"
        "What do you want to do?",
        parse_mode="Markdown",
        reply_markup=kol_menu()
    )


@router.callback_query(F.data == "cat:support")
async def cat_support(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 *Support*\n\n"
        "Got a question? Something not working? We've got you.\n\n"
        "Open a ticket and our team will get back to you ASAP.",
        parse_mode="Markdown",
        reply_markup=support_menu()
    )
