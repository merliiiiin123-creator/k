from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import RegistrationForm
from keyboards.menus import platform_keyboard, verified_keyboard, confirm_keyboard, main_menu
from database.db import upsert_application, get_application

router = Router()


# ─── Entry Point ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "apply")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    # Block already-approved creators from spamming
    app = await get_application(callback.from_user.id)
    if app and app["status"] == "approved":
        await callback.message.edit_text(
            "✅ You're already an approved Kraven Creator!\n\n"
            "No need to apply again.",
            reply_markup=main_menu()
        )
        return

    await state.set_state(RegistrationForm.full_name)
    await callback.message.edit_text(
        "📝 <b>Kraven Creator Application</b>\n\n"
        "<b>Step 1 of 8</b>\n\n"
        "What is your full name?"
    )


# ─── Step 1: Full Name ─────────────────────────────────────────────────────────

@router.message(RegistrationForm.full_name)
async def reg_full_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Name too short. Try again.")
        return
    await state.update_data(full_name=name)
    await state.set_state(RegistrationForm.platform)
    await message.answer(
        "<b>Step 2 of 8</b>\n\n"
        "What is your primary content platform?",
        reply_markup=platform_keyboard()
    )


# ─── Step 2: Platform ──────────────────────────────────────────────────────────

@router.callback_query(RegistrationForm.platform, F.data.startswith("platform:"))
async def reg_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.split(":")[1]
    await state.update_data(platform=platform)
    await state.set_state(RegistrationForm.profile_link)
    await callback.message.edit_text(
        f"<b>Step 3 of 8</b>\n\n"
        f"Paste your <b>{platform}</b> profile link:"
    )


# ─── Step 3: Profile Link ─────────────────────────────────────────────────────

@router.message(RegistrationForm.profile_link)
async def reg_profile_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not link.startswith("http"):
        await message.answer("❌ That doesn't look like a valid link. Start with http:// or https://")
        return
    await state.update_data(profile_link=link)
    await state.set_state(RegistrationForm.follower_count)
    await message.answer(
        "<b>Step 4 of 8</b>\n\n"
        "How many followers do you have? (numbers only, e.g. 5000)"
    )


# ─── Step 4: Follower Count ───────────────────────────────────────────────────

@router.message(RegistrationForm.follower_count)
async def reg_follower_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip().replace(",", "").replace("k", "000").replace("K", "000"))
    except ValueError:
        await message.answer("❌ Enter a number only (e.g. 5000 or 12000)")
        return
    await state.update_data(follower_count=count)
    await state.set_state(RegistrationForm.mutuals)
    await message.answer(
        "<b>Step 5 of 8</b>\n\n"
        "How many mutual connections do you have in this space? (enter a number)"
    )


# ─── Step 5: Mutuals ──────────────────────────────────────────────────────────

@router.message(RegistrationForm.mutuals)
async def reg_mutuals(message: Message, state: FSMContext):
    try:
        mutuals = int(message.text.strip().replace(",", ""))
    except ValueError:
        await message.answer("❌ Enter a number only")
        return
    await state.update_data(mutuals=mutuals)
    await state.set_state(RegistrationForm.account_age)
    await message.answer(
        "<b>Step 6 of 8</b>\n\n"
        "How old is your account in years? (e.g. 2 or 1.5)"
    )


# ─── Step 6: Account Age ──────────────────────────────────────────────────────

@router.message(RegistrationForm.account_age)
async def reg_account_age(message: Message, state: FSMContext):
    try:
        age = float(message.text.strip())
        if age < 0 or age > 30:
            raise ValueError
    except ValueError:
        await message.answer("❌ Enter a valid number (e.g. 1.5 for one and a half years)")
        return
    await state.update_data(account_age=age)
    await state.set_state(RegistrationForm.is_verified)
    await message.answer(
        "<b>Step 7 of 8</b>\n\n"
        "Is your account verified on your primary platform?",
        reply_markup=verified_keyboard()
    )


# ─── Step 7: Verified ─────────────────────────────────────────────────────────

@router.callback_query(RegistrationForm.is_verified, F.data.startswith("verified:"))
async def reg_verified(callback: CallbackQuery, state: FSMContext):
    verified = callback.data.split(":")[1]
    await state.update_data(is_verified=verified)
    await state.set_state(RegistrationForm.pitch)
    await callback.message.edit_text(
        "<b>Step 8 of 8</b>\n\n"
        "Write your <b>creator pitch</b>.\n\n"
        "Tell us who you are, what content you make, and why you should be part of Kraven. "
        "Be specific — generic answers get rejected.\n\n"
        "<i>(Minimum 50 characters)</i>"
    )


# ─── Step 8: Pitch + Confirm ─────────────────────────────────────────────────

@router.message(RegistrationForm.pitch)
async def reg_pitch(message: Message, state: FSMContext):
    pitch = message.text.strip()
    if len(pitch) < 50:
        await message.answer(
            f"❌ Pitch too short ({len(pitch)} characters). "
            "Give us more — minimum 50 characters."
        )
        return
    await state.update_data(pitch=pitch)
    data = await state.get_data()

    summary = (
        "📋 <b>Review Your Application</b>\n\n"
        f"👤 <b>Name:</b> {data['full_name']}\n"
        f"📱 <b>Platform:</b> {data['platform']}\n"
        f"🔗 <b>Profile:</b> {data['profile_link']}\n"
        f"👥 <b>Followers:</b> {data['follower_count']:,}\n"
        f"🤝 <b>Mutuals:</b> {data['mutuals']}\n"
        f"📅 <b>Account Age:</b> {data['account_age']} years\n"
        f"✅ <b>Verified:</b> {data['is_verified']}\n\n"
        f"💬 <b>Pitch:</b>\n<i>{data['pitch']}</i>\n\n"
        "———\nSubmit or cancel?"
    )
    await state.set_state(RegistrationForm.confirm)
    await message.answer(summary, reply_markup=confirm_keyboard())


# ─── Confirm: Submit ──────────────────────────────────────────────────────────

@router.callback_query(RegistrationForm.confirm, F.data == "confirm:yes")
async def reg_confirm_submit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    await upsert_application({
        "user_id": user.id,
        "username": user.username or "N/A",
        "full_name": data["full_name"],
        "platform": data["platform"],
        "profile_link": data["profile_link"],
        "follower_count": data["follower_count"],
        "mutuals": data["mutuals"],
        "account_age": data["account_age"],
        "is_verified": data["is_verified"],
        "pitch": data["pitch"],
    })
    await state.clear()
    await callback.message.edit_text(
        "✅ <b>Application submitted!</b>\n\n"
        "Our team will review it and get back to you.\n"
        "Use <b>Check Application Status</b> to track progress.",
        reply_markup=main_menu()
    )


# ─── Confirm: Cancel ──────────────────────────────────────────────────────────

@router.callback_query(RegistrationForm.confirm, F.data == "confirm:no")
async def reg_confirm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🗑 Application cancelled. You can start again anytime.",
        reply_markup=main_menu()
    )
