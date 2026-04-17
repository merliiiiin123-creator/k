from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_IDS, GROUP_INVITE_LINK
from states.forms import AdminAction
from keyboards.menus import admin_main_menu, admin_review_keyboard, close_ticket_keyboard, main_menu
from database.db import (
    get_pending_applications,
    update_application_status,
    get_open_tickets,
    close_ticket,
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ─── Admin Panel Entry ─────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 <b>Admin Panel</b>\n\nWhat would you like to manage?",
        reply_markup=admin_main_menu()
    )


# ─── Pending Applications ──────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:pending")
async def list_pending(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    apps = await get_pending_applications()

    if not apps:
        await callback.message.edit_text(
            "✅ No pending applications.",
            reply_markup=admin_main_menu()
        )
        return

    await callback.message.edit_text(
        f"📋 <b>{len(apps)} Pending Application(s)</b>\n\nSending each one now..."
    )

    for app in apps:
        text = (
            f"📋 <b>Application Review</b>\n\n"
            f"👤 <b>Name:</b> {app['full_name']}\n"
            f"🔖 <b>Username:</b> @{app['username']}\n"
            f"🆔 <b>User ID:</b> <code>{app['user_id']}</code>\n"
            f"📱 <b>Platform:</b> {app['platform']}\n"
            f"🔗 <b>Profile:</b> {app['profile_link']}\n"
            f"👥 <b>Followers:</b> {app['follower_count']:,}\n"
            f"🤝 <b>Mutuals:</b> {app['mutuals']}\n"
            f"📅 <b>Account Age:</b> {app['account_age']} years\n"
            f"✅ <b>Verified:</b> {app['is_verified']}\n\n"
            f"💬 <b>Pitch:</b>\n<i>{app['pitch']}</i>\n\n"
            f"🕒 <b>Submitted:</b> {app['submitted_at'][:16]}"
        )
        await callback.message.answer(
            text,
            reply_markup=admin_review_keyboard(app['user_id'])
        )


# ─── Approve ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:approve:"))
async def approve_application(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return

    user_id = int(callback.data.split(":")[2])
    await update_application_status(user_id, "approved")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Application for <code>{user_id}</code> approved.")

    try:
        msg = (
            "🎉 <b>Congratulations! You've been approved!</b>\n\n"
            "You are now an official <b>Kraven Creator</b>.\n\n"
        )
        if GROUP_INVITE_LINK:
            msg += f'👉 <a href="{GROUP_INVITE_LINK}">Join the Kraven Creators Hub</a>'

        await bot.send_message(user_id, msg)
    except Exception:
        await callback.message.answer(
            f"⚠️ Could not DM user <code>{user_id}</code>. They may have blocked the bot."
        )


# ─── Reject ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:reject:"))
async def reject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    user_id = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminAction.note)
    await callback.message.answer(
        "✏️ Enter a rejection note for the applicant <i>(or send /skip to reject without a note)</i>:"
    )


@router.message(AdminAction.note)
async def reject_with_note(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    user_id = data["target_user_id"]
    note = "" if message.text == "/skip" else message.text.strip()

    await update_application_status(user_id, "rejected", note)
    await state.clear()
    await message.answer(f"❌ Application for <code>{user_id}</code> rejected.")

    try:
        msg = "❌ <b>Your Kraven Creator application was not approved at this time.</b>\n\n"
        if note:
            msg += f"📝 <b>Reason:</b> {note}\n\n"
        msg += "You're welcome to reapply in the future."
        await bot.send_message(user_id, msg)
    except Exception:
        await message.answer(f"⚠️ Could not DM user <code>{user_id}</code>.")


# ─── Open Tickets ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:tickets")
async def list_tickets(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    tickets = await get_open_tickets()

    if not tickets:
        await callback.message.edit_text(
            "✅ No open tickets.",
            reply_markup=admin_main_menu()
        )
        return

    await callback.message.edit_text(
        f"🎫 <b>{len(tickets)} Open Ticket(s)</b>\n\nSending each one..."
    )

    for t in tickets:
        text = (
            f"🎫 <b>Ticket #{t['id']}</b>\n\n"
            f"👤 <b>From:</b> @{t['username']} (<code>{t['user_id']}</code>)\n"
            f"⚡ <b>Priority:</b> {t['priority']}\n"
            f"🕒 <b>Created:</b> {t['created_at'][:16]}\n\n"
            f"📝 <b>Message:</b>\n{t['message']}"
        )
        await callback.message.answer(
            text,
            reply_markup=close_ticket_keyboard(t['id'])
        )


@router.callback_query(F.data.startswith("admin:close_ticket:"))
async def handle_close_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    ticket_id = int(callback.data.split(":")[2])
    await close_ticket(ticket_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Ticket #{ticket_id} closed.")
