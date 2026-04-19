from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_IDS   # ← fixed
from states.forms import AdminNote
from keyboards.menus import admin_main_menu, admin_review_keyboard, close_ticket_keyboard
from database.db import (
    get_pending_kols, update_kol_status,
    get_pending_projects, update_project_status,
    get_pending_investors, update_investor_status,
    get_pending_partners, update_partner_status,
    get_open_tickets, close_ticket,
)

router = Router()

APP_CONFIG = {
    "kol": {
        "get_pending": get_pending_kols,
        "update_status": update_kol_status,
        "label": "KOL",
        "emoji": "🎤",
        "format": lambda a: (
            f"🎤 *KOL Application*\n\n"
            f"👤 {a['full_name']} (@{a['username']})\n"
            f"🆔 `{a['user_id']}`\n"
            f"📧 {a['email']}\n"
            f"🐦 X: {a['x_handle']}\n"
            f"💬 TG: {a['telegram_handle']} | Discord: {a['discord_handle']}\n"
            f"🎯 Niche: {a['niche']}\n"
            f"👥 Audience: {a['audience_size']}\n"
            f"📊 Engagement: {a['engagement_metrics']}\n"
            f"🏆 Past Collabs: {a['past_collabs']}\n"
            f"🕒 {a['submitted_at'][:16]}"
        ),
    },
    "project": {
        "get_pending": get_pending_projects,
        "update_status": update_project_status,
        "label": "Project",
        "emoji": "🏢",
        "format": lambda a: (
            f"🏢 *Project Application*\n\n"
            f"🏷 {a['project_name']} (@{a['username']})\n"
            f"🆔 `{a['user_id']}`\n"
            f"🌐 {a['website_url']}\n"
            f"🐦 X: {a['x_account']}\n"
            f"💬 TG/Discord: {a['tg_discord']}\n"
            f"👤 Contact: {a['contact_name']} | 📧 {a['contact_email']}\n"
            f"📂 Category: {a['project_category']}\n"
            f"🛠 Services: {a['services_selected']}\n"
            f"💰 Budget: {a['budget_range']} | 📅 Tenure: {a['project_tenure']}\n\n"
            f"📈 Traction:\n_{a['traction_desc']}_\n"
            f"🕒 {a['submitted_at'][:16]}"
        ),
    },
    "investor": {
        "get_pending": get_pending_investors,
        "update_status": update_investor_status,
        "label": "Investor",
        "emoji": "💰",
        "format": lambda a: (
            f"💰 *Investor Application*\n\n"
            f"👤 {a['full_name']} (@{a['username']})\n"
            f"🆔 `{a['user_id']}`\n"
            f"📧 {a['email']} | 🌍 {a['country']}\n"
            f"🎯 Scope: {a['investment_scope']}\n"
            f"💵 Size: {a['invest_size']}\n\n"
            f"💡 Motivation:\n_{a['motivation']}_\n\n"
            f"📊 Experience:\n_{a['invest_experience']}_\n\n"
            f"❓ Questions:\n_{a['specific_questions']}_\n"
            f"🕒 {a['submitted_at'][:16]}"
        ),
    },
    "partner": {
        "get_pending": get_pending_partners,
        "update_status": update_partner_status,
        "label": "Partner",
        "emoji": "🤝",
        "format": lambda a: (
            f"🤝 *Partner Application*\n\n"
            f"🏢 {a['company_name']} (@{a['username']})\n"
            f"🆔 `{a['user_id']}`\n"
            f"👤 {a['contact_person']} | 📧 {a['contact_email']}\n"
            f"🌐 {a['website']}\n"
            f"🌱 Ecosystem Interest: {a['ecosystem_interest']}\n\n"
            f"📝 Terms:\n_{a['partnership_terms']}_\n\n"
            f"🛠 Services:\n_{a['services_overview']}_\n\n"
            f"✉️ Cover Letter:\n_{a['cover_letter']}_\n"
            f"🕒 {a['submitted_at'][:16]}"
        ),
    },
}


def is_admin(uid): return uid in ADMIN_IDS


# ─── Admin Entry ───────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🛠 *Kraven Admin Panel*\n\nSelect a queue to manage:",
        parse_mode="Markdown",
        reply_markup=admin_main_menu()
    )


# ─── List Applications ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:list:"))
async def admin_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    queue = callback.data.split(":")[-1]

    if queue == "tickets":
        tickets = await get_open_tickets()
        if not tickets:
            await callback.message.edit_text("✅ No open tickets.", reply_markup=admin_main_menu())
            return
        await callback.message.edit_text(f"🎫 *{len(tickets)} Open Ticket(s)*", parse_mode="Markdown")
        for t in tickets:
            text = (
                f"🎫 *Ticket #{t['id']}*\n\n"
                f"👤 @{t['username']} (`{t['user_id']}`)\n"
                f"📧 {t['email']}\n"
                f"🕒 {t['created_at'][:16]}\n\n"
                f"📝 {t['description']}"
            )
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=close_ticket_keyboard(t['id']))
        return

    cfg = APP_CONFIG.get(queue)
    if not cfg:
        return

    apps = await cfg["get_pending"]()
    if not apps:
        await callback.message.edit_text(
            f"✅ No pending {cfg['label']} applications.",
            reply_markup=admin_main_menu()
        )
        return

    await callback.message.edit_text(
        f"{cfg['emoji']} *{len(apps)} Pending {cfg['label']} Application(s)*",
        parse_mode="Markdown"
    )
    for app in apps:
        await callback.message.answer(
            cfg["format"](app),
            parse_mode="Markdown",
            reply_markup=admin_review_keyboard(queue, app["user_id"])
        )


# ─── Approve ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:approve:"))
async def admin_approve(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return
    _, _, app_type, user_id_str = callback.data.split(":")
    user_id = int(user_id_str)
    cfg = APP_CONFIG[app_type]

    await cfg["update_status"](user_id, "approved")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ {cfg['label']} application for `{user_id}` approved.", parse_mode="Markdown")

    approval_msgs = {
        "kol":      "🎉 *Congratulations!* You've been approved as a *Kraven KOL*!\n\nOur team will be in touch with your onboarding details shortly.",
        "project":  "🎉 *Great news!* Your project application has been *approved by Kraven*!\n\nExpect an email from our team within 24 hours to discuss next steps.",
        "investor": "🎉 *Welcome!* Your investor application has been *approved*.\n\nA Kraven representative will reach out to you via email to schedule a call.",
        "partner":  "🎉 *Exciting news!* Your ecosystem partner application has been *approved by Kraven*!\n\nWe'll follow up via email to begin the partnership process.",
    }
    try:
        await bot.send_message(user_id, approval_msgs[app_type], parse_mode="Markdown")
    except Exception:
        await callback.message.answer(f"⚠️ Could not DM user `{user_id}`.", parse_mode="Markdown")


# ─── Reject ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:reject:"))
async def admin_reject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    _, _, app_type, user_id_str = callback.data.split(":")
    await state.update_data(target_user_id=int(user_id_str), app_type=app_type)
    await state.set_state(AdminNote.waiting)
    await callback.message.answer(
        "✏️ Enter a *rejection note* for the applicant _(or /skip for no note)_:",
        parse_mode="Markdown"
    )


@router.message(AdminNote.waiting)
async def admin_reject_note(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    user_id = data["target_user_id"]
    app_type = data["app_type"]
    note = "" if message.text == "/skip" else message.text.strip()
    cfg = APP_CONFIG[app_type]

    await cfg["update_status"](user_id, "rejected", note)
    await state.clear()
    await message.answer(f"❌ {cfg['label']} application for `{user_id}` rejected.", parse_mode="Markdown")

    rejection_msg = (
        f"❌ *Your {cfg['label']} application was not approved at this time.*\n\n"
        + (f"📝 *Reason:* {note}\n\n" if note else "")
        + "You're welcome to reapply in the future. If you have questions, please open a support ticket."
    )
    try:
        await bot.send_message(user_id, rejection_msg, parse_mode="Markdown")
    except Exception:
        await message.answer(f"⚠️ Could not DM user `{user_id}`.", parse_mode="Markdown")


# ─── Close Ticket ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:close_ticket:"))
async def admin_close_ticket(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    ticket_id = int(callback.data.split(":")[-1])
    await close_ticket(ticket_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Ticket #{ticket_id} closed.")
