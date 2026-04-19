from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import KOLForm
from keyboards.menus import kol_menu, niche_keyboard, confirm_keyboard, main_menu
from database.db import upsert_kol, get_kol
from utils import is_valid_email, fmt_status

router = Router()

TOTAL_STEPS = 9


def _progress(step: int) -> str:
    return f"_(Step {step} of {TOTAL_STEPS})_"


# ─── KOL Sub-menu ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "kol:apply")
async def kol_apply(callback: CallbackQuery, state: FSMContext):
    app = await get_kol(callback.from_user.id)
    if app and app["status"] == "approved":
        await callback.message.edit_text(
            "🔥 You're already *inside the Kraven KOL Network*.\n\n"
            "Keep an eye on your DMs — campaigns drop regularly and "
            "you'll be among the first to know.",
            parse_mode="Markdown", reply_markup=main_menu()
        )
        return
    if app and app["status"] == "pending":
        await callback.message.edit_text(
            "⏳ Your application is *under review*.\n\n"
            "Our team vets every creator personally — sit tight, "
            "we'll reach out soon. Use *Check My Status* to track progress.",
            parse_mode="Markdown", reply_markup=kol_menu()
        )
        return

    await state.set_state(KOLForm.full_name)
    await callback.message.edit_text(
        f"🎤 *KOL Application* {_progress(1)}\n\n"
        "Let's get you in. This takes less than 3 minutes.\n\n"
        "First — what's your *full name*?",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "kol:status")
async def kol_status(callback: CallbackQuery):
    app = await get_kol(callback.from_user.id)
    if not app:
        await callback.message.edit_text(
            "📭 No application on file yet.\n\n"
            "Tap *Apply to Join Kraven* to get into the network.",
            parse_mode="Markdown", reply_markup=kol_menu()
        )
        return
    text = (
        f"*Your KOL Application*\n\n"
        f"{fmt_status(app['status'])}\n"
        f"📅 Submitted: {app['submitted_at'][:16]}\n"
    )
    if app.get("reviewed_at"):
        text += f"🔍 Reviewed: {app['reviewed_at'][:16]}\n"
    if app["status"] == "rejected" and app.get("admin_note"):
        text += f"\n📝 Feedback: _{app['admin_note']}_"
    if app["status"] == "approved":
        text += "\n\n🔥 You're in. Welcome to the network."
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kol_menu())


@router.callback_query(F.data == "kol:id")
async def kol_id(callback: CallbackQuery):
    u = callback.from_user
    await callback.message.edit_text(
        f"🪪 *Your Kraven ID*\n\n"
        f"🆔 User ID: `{u.id}`\n"
        f"👤 Name: {u.full_name}\n"
        f"🔖 Username: @{u.username or 'N/A'}",
        parse_mode="Markdown", reply_markup=kol_menu()
    )


# ─── Form Steps ────────────────────────────────────────────────────────────────

@router.message(KOLForm.full_name)
async def kol_step1(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("❌ Please enter your full name.")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(KOLForm.email)
    await message.answer(
        f"🎤 *KOL Application* {_progress(2)}\n\nWhat's your *contact email*?",
        parse_mode="Markdown"
    )


@router.message(KOLForm.email)
async def kol_step2(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("❌ That doesn't look right. Please enter a valid email.")
        return
    await state.update_data(email=message.text.strip().lower())
    await state.set_state(KOLForm.x_handle)
    await message.answer(
        f"🎤 *KOL Application* {_progress(3)}\n\nYour *X (Twitter) handle*?\n_(e.g. @kraven)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.x_handle)
async def kol_step3(message: Message, state: FSMContext):
    await state.update_data(x_handle=message.text.strip())
    await state.set_state(KOLForm.telegram_handle)
    await message.answer(
        f"🎤 *KOL Application* {_progress(4)}\n\nYour *Telegram username*?\n_(Type 'N/A' if none)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.telegram_handle)
async def kol_step4(message: Message, state: FSMContext):
    await state.update_data(telegram_handle=message.text.strip())
    await state.set_state(KOLForm.discord_handle)
    await message.answer(
        f"🎤 *KOL Application* {_progress(5)}\n\nYour *Discord handle*?\n_(Type 'N/A' if none)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.discord_handle)
async def kol_step5(message: Message, state: FSMContext):
    await state.update_data(discord_handle=message.text.strip())
    await state.set_state(KOLForm.niche)
    await message.answer(
        f"🎤 *KOL Application* {_progress(6)}\n\nWhat space do you create in?",
        parse_mode="Markdown",
        reply_markup=niche_keyboard()
    )


@router.callback_query(KOLForm.niche, F.data.startswith("niche:"))
async def kol_step6(callback: CallbackQuery, state: FSMContext):
    niche = callback.data.split(":", 1)[1]
    await state.update_data(niche=niche)
    await state.set_state(KOLForm.audience_size)
    await callback.message.edit_text(
        f"🎤 *KOL Application* {_progress(7)}\n\n"
        "How big is your *total audience* across all platforms?\n"
        "_(e.g. 80K on X, 15K on YouTube — give us the full picture)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.audience_size)
async def kol_step7(message: Message, state: FSMContext):
    await state.update_data(audience_size=message.text.strip())
    await state.set_state(KOLForm.engagement_metrics)
    await message.answer(
        f"🎤 *KOL Application* {_progress(8)}\n\n"
        "Talk numbers — *engagement rate, avg views, replies, CTR*.\n"
        "_(Brands care about engagement, not just follower count)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.engagement_metrics)
async def kol_step8(message: Message, state: FSMContext):
    await state.update_data(engagement_metrics=message.text.strip())
    await state.set_state(KOLForm.past_collabs)
    await message.answer(
        f"🎤 *KOL Application* {_progress(9)}\n\n"
        "Any *past brand deals or KOL campaigns* you've run?\n"
        "_(Drop names, projects, or results. Type 'None' if this is your first)_",
        parse_mode="Markdown"
    )


@router.message(KOLForm.past_collabs)
async def kol_step9(message: Message, state: FSMContext):
    await state.update_data(past_collabs=message.text.strip())
    data = await state.get_data()
    await state.set_state(KOLForm.confirm)

    summary = (
        "📋 *Almost there — review your info:*\n\n"
        f"👤 Name: {data['full_name']}\n"
        f"📧 Email: {data['email']}\n"
        f"🐦 X: {data['x_handle']}\n"
        f"💬 Telegram: {data['telegram_handle']}\n"
        f"🎮 Discord: {data['discord_handle']}\n"
        f"🎯 Niche: {data['niche']}\n"
        f"👥 Audience: {data['audience_size']}\n"
        f"📊 Engagement: {data['engagement_metrics']}\n"
        f"🏆 Past Work: {data['past_collabs']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Everything look good? Hit *Submit* and we'll take it from here. 🚀"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(KOLForm.confirm, F.data.startswith("confirm:"))
async def kol_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Application cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    await upsert_kol(data)
    await state.clear()

    await callback.message.edit_text(
        "✅ *Application received.*\n\n"
        "Our team reviews every creator personally — no bots making decisions here.\n\n"
        "You'll hear back from us directly. In the meantime, use *Check My Status* to track where you're at. 👀",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
