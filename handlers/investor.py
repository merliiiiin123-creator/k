from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import InvestorForm
from keyboards.menus import investment_scope_keyboard, invest_size_keyboard, confirm_keyboard, main_menu
from database.db import insert_investor
from utils import is_valid_email

router = Router()
TOTAL_STEPS = 8


def _p(step): return f"_(Step {step} of {TOTAL_STEPS})_"


@router.callback_query(F.data == "cat:investor")
async def cat_investor(callback: CallbackQuery, state: FSMContext):
    await state.set_state(InvestorForm.motivation)
    await callback.message.edit_text(
        "💰 *Invest in Kraven*\n\n"
        "Kraven is building the distribution layer for the next wave of Web3 growth — "
        "connecting projects, creators, and capital in one ecosystem.\n\n"
        "If you're looking to back something with *real infrastructure* and a "
        "growing network of KOLs and projects, let's talk.\n\n"
        f"{_p(1)} What's drawing you to Kraven? Tell us about your *investment thesis*.",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.motivation)
async def inv_step1(message: Message, state: FSMContext):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Give us a bit more context.")
        return
    await state.update_data(motivation=message.text.strip())
    await state.set_state(InvestorForm.investment_scope)
    await message.answer(
        f"💰 {_p(2)}\n\nAre you looking to invest in *Kraven directly*, "
        "in *projects within the Kraven ecosystem*, or *both*?",
        parse_mode="Markdown",
        reply_markup=investment_scope_keyboard()
    )


@router.callback_query(InvestorForm.investment_scope, F.data.startswith("scope:"))
async def inv_step2(callback: CallbackQuery, state: FSMContext):
    scope_map = {
        "scope:kraven_only":    "Kraven itself only",
        "scope:ecosystem_only": "Ecosystem projects only",
        "scope:both":           "Both Kraven & ecosystem projects",
    }
    scope = scope_map.get(callback.data, callback.data)
    await state.update_data(investment_scope=scope)
    await state.set_state(InvestorForm.full_name)
    await callback.message.edit_text(
        f"💰 {_p(3)}\n\nYour *full name*?",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.full_name)
async def inv_step3(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(InvestorForm.email)
    await message.answer(
        f"💰 {_p(4)}\n\nBest *email address* to reach you?",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.email)
async def inv_step4(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("❌ Please enter a valid email address.")
        return
    await state.update_data(email=message.text.strip().lower())
    await state.set_state(InvestorForm.country)
    await message.answer(
        f"💰 {_p(5)}\n\n*Country of residence*?",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.country)
async def inv_step5(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await state.set_state(InvestorForm.invest_experience)
    await message.answer(
        f"💰 {_p(6)}\n\nTell us about your *investment background*.\n"
        "_(Rounds you've participated in, notable portfolio projects, years active, etc.)_",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.invest_experience)
async def inv_step6(message: Message, state: FSMContext):
    await state.update_data(invest_experience=message.text.strip())
    await state.set_state(InvestorForm.invest_size)
    await message.answer(
        f"💰 {_p(7)}\n\nWhat's your *typical investment size*?",
        parse_mode="Markdown",
        reply_markup=invest_size_keyboard()
    )


@router.callback_query(InvestorForm.invest_size, F.data.startswith("isize:"))
async def inv_step7(callback: CallbackQuery, state: FSMContext):
    size = callback.data.split(":", 1)[1]
    await state.update_data(invest_size=size)
    await state.set_state(InvestorForm.specific_questions)
    await callback.message.edit_text(
        f"💰 {_p(8)}\n\n"
        "Anything specific you want to know about *Kraven's financials, roadmap, or tokenomics* "
        "before we connect?\n\n_(Type 'None' if you're good for now)_",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.specific_questions)
async def inv_step8(message: Message, state: FSMContext):
    await state.update_data(specific_questions=message.text.strip())
    data = await state.get_data()
    await state.set_state(InvestorForm.confirm)

    summary = (
        "📋 *Your investor profile:*\n\n"
        f"👤 Name: {data['full_name']}\n"
        f"📧 Email: {data['email']}\n"
        f"🌍 Country: {data['country']}\n"
        f"🎯 Scope: {data['investment_scope']}\n"
        f"💰 Ticket Size: {data['invest_size']}\n\n"
        f"💡 *Thesis:*\n_{data['motivation']}_\n\n"
        f"📊 *Background:*\n_{data['invest_experience']}_\n\n"
        f"❓ *Questions:*\n_{data['specific_questions']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Submit and we'll be in touch to set up a call. 🤝"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(InvestorForm.confirm, F.data.startswith("confirm:"))
async def inv_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Submission cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    await insert_investor(data)
    await state.clear()

    await callback.message.edit_text(
        "✅ *We've got your details.*\n\n"
        "A member of the Kraven team will reach out to your email to schedule a conversation.\n\n"
        "_We're building something worth backing — and we appreciate the interest._",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
