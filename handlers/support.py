from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states.forms import SupportTicket
from keyboards.menus import priority_keyboard, main_menu, close_ticket_keyboard
from database.db import create_ticket

router = Router()


@router.callback_query(F.data == "support")
async def start_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportTicket.priority)
    await callback.message.edit_text(
        "🎫 <b>Open a Support Ticket</b>\n\n"
        "Select the <b>priority</b> of your issue:",
        reply_markup=priority_keyboard()
    )


@router.callback_query(SupportTicket.priority, F.data.startswith("priority:"))
async def set_priority(callback: CallbackQuery, state: FSMContext):
    priority = callback.data.split(":")[1]
    await state.update_data(priority=priority)
    await state.set_state(SupportTicket.message)
    await callback.message.edit_text(
        f"🎫 <b>Priority: {priority}</b>\n\n"
        "Describe your issue in detail. Be specific:"
    )


@router.message(SupportTicket.message)
async def submit_ticket(message: Message, state: FSMContext, bot: Bot):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Please provide more detail (at least 10 characters).")
        return

    data = await state.get_data()
    user = message.from_user

    ticket_id = await create_ticket(
        user_id=user.id,
        username=user.username or "N/A",
        priority=data["priority"],
        message=message.text.strip()
    )

    await state.clear()

    admin_text = (
        f"🎫 <b>New Support Ticket #{ticket_id}</b>\n\n"
        f"👤 <b>From:</b> {user.full_name} (@{user.username or 'N/A'})\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"⚡ <b>Priority:</b> {data['priority']}\n\n"
        f"📝 <b>Message:</b>\n{message.text.strip()}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=close_ticket_keyboard(ticket_id)
            )
        except Exception:
            pass

    await message.answer(
        f"✅ <b>Ticket #{ticket_id} submitted!</b>\n\n"
        f"Priority: <b>{data['priority']}</b>\n"
        "An admin will respond shortly.",
        reply_markup=main_menu()
    )
