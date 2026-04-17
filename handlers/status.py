from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import get_application
from keyboards.menus import main_menu

router = Router()

STATUS_EMOJI = {
    "pending":  "⏳",
    "approved": "✅",
    "rejected": "❌",
}


@router.callback_query(F.data == "status")
async def check_status(callback: CallbackQuery):
    app = await get_application(callback.from_user.id)

    if not app:
        await callback.message.edit_text(
            "📭 You haven't submitted an application yet.\n\n"
            "Tap <b>Apply to Join Kraven</b> to get started!",
            reply_markup=main_menu()
        )
        return

    status = app["status"]
    emoji = STATUS_EMOJI.get(status, "❓")

    text = (
        f"<b>Application Status</b>\n\n"
        f"{emoji} <b>Status:</b> {status.capitalize()}\n"
        f"📅 <b>Submitted:</b> {app['submitted_at'][:16]}\n"
    )

    if app["reviewed_at"]:
        text += f"🔍 <b>Reviewed:</b> {app['reviewed_at'][:16]}\n"

    if status == "rejected" and app["admin_note"]:
        text += f"\n📝 <b>Admin Note:</b>\n<i>{app['admin_note']}</i>\n"

    if status == "approved":
        text += "\n🎉 Congratulations! You're now a Kraven Creator."

    await callback.message.edit_text(text, reply_markup=main_menu())


@router.callback_query(F.data == "get_id")
async def get_user_id(callback: CallbackQuery):
    user = callback.from_user
    text = (
        "🪪 <b>Your Telegram Info</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>Name:</b> {user.full_name}\n"
        f"🔖 <b>Username:</b> @{user.username or 'N/A'}"
    )
    await callback.message.edit_text(text, reply_markup=main_menu())
