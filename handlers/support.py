from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, FAQ_URL
from states.forms import SupportForm
from keyboards.menus import support_menu, main_menu, close_ticket_keyboard
from database.db import create_ticket
from utils import is_valid_email

router = Router()


@router.callback_query(F.data == "support:faq")
async def support_faq(callback: CallbackQuery):
    await callback.message.edit_text(
        f"📚 *Kraven Help Center*\n\n"
        f"Find answers to the most common questions here:\n"
        f"👉 {FAQ_URL}\n\n"
        "Still stuck? Open a ticket and we'll sort it out.",
        parse_mode="Markdown",
        reply_markup=support_menu()
    )


@router.callback_query(F.data == "support:ticket")
async def support_ticket_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportForm.email)
    await callback.message.edit_text(
        "🎫 *Open a Ticket*\n\n"
        "Step 1 of 2 — What's the best *email address* to reach you?\n\n"
        "_(We'll follow up there once we've looked into it)_",
        parse_mode="Markdown"
    )


@router.message(SupportForm.email)
async def support_step1(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("❌ Please enter a valid email address.")
        return
    await state.update_data(email=message.text.strip().lower())
    await state.set_state(SupportForm.description)
    await message.answer(
        "🎫 *Open a Ticket*\n\n"
        "Step 2 of 2 — What's going on?\n\n"
        "Describe your issue in as much detail as you can. "
        "The more context you give, the faster we can help.",
        parse_mode="Markdown"
    )


@router.message(SupportForm.description)
async def support_step2(message: Message, state: FSMContext, bot: Bot):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Please describe the issue in a bit more detail.")
        return

    data = await state.get_data()
    user = message.from_user

    ticket_id = await create_ticket(
        user_id=user.id,
        username=user.username or "N/A",
        email=data["email"],
        description=message.text.strip()
    )
    await state.clear()

    admin_text = (
        f"🎫 *New Ticket #{ticket_id}*\n\n"
        f"👤 {user.full_name} (@{user.username or 'N/A'})\n"
        f"🆔 `{user.id}`\n"
        f"📧 {data['email']}\n\n"
        f"📝 {message.text.strip()}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, admin_text,
                parse_mode="Markdown",
                reply_markup=close_ticket_keyboard(ticket_id)
            )
        except Exception:
            pass

    await message.answer(
        f"✅ *Ticket #{ticket_id} is open.*\n\n"
        "Our team will get back to you via email. We typically respond within a few hours.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
