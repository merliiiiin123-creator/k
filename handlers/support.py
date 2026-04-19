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
        f"📚 *Kraven FAQ & Help Center*\n\n"
        f"Visit our help center for answers to the most common questions:\n"
        f"👉 {FAQ_URL}\n\n"
        "If you can't find what you're looking for, open a support ticket.",
        parse_mode="Markdown",
        reply_markup=support_menu()
    )


@router.callback_query(F.data == "support:ticket")
async def support_ticket_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportForm.email)
    await callback.message.edit_text(
        "🎫 *Open a Support Ticket*\n\n"
        "Step 1 of 2: What is your *contact email address*?\n\n"
        "_(We'll use this to follow up on your ticket)_",
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
        "🎫 *Open a Support Ticket*\n\n"
        "Step 2 of 2: Please describe your *issue or question* in detail.\n\n"
        "The more context you give, the faster we can help!",
        parse_mode="Markdown"
    )


@router.message(SupportForm.description)
async def support_step2(message: Message, state: FSMContext, bot: Bot):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Please provide more detail about your issue.")
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

    # Notify admins
    admin_text = (
        f"🎫 *New Support Ticket #{ticket_id}*\n\n"
        f"👤 *From:* {user.full_name} (@{user.username or 'N/A'})\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"📧 *Email:* {data['email']}\n\n"
        f"📝 *Description:*\n{message.text.strip()}"
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
        f"✅ *Ticket #{ticket_id} Submitted!*\n\n"
        "Our support team will review your message and reach out to you via email shortly.\n\n"
        "_Thank you for reaching out to Kraven!_",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
