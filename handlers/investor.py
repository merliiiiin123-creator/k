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
        "💰 *Investor Application*\n\n"
        "We're glad you're considering investing in Kraven. "
        "Let's learn more about your goals.\n\n"
        f"{_p(1)} What is your *primary motivation* for considering an investment in Kraven?\n\n"
        "_(Please describe in a few sentences — e.g. long-term value, ecosystem alignment, strategic partnership, etc.)_",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.motivation)
async def inv_step1(message: Message, state: FSMContext):
    if len(message.text.strip()) < 10:
        await message.answer("❌ Please provide a more detailed response.")
        return
    await state.update_data(motivation=message.text.strip())
    await state.set_state(InvestorForm.investment_scope)
    await message.answer(
        f"💰 *Investor Application* {_p(2)}\n\n"
        "Are you interested in participating in *fundraising rounds for projects* within the Kraven ecosystem, "
        "or solely in *Kraven itself*?",
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
        f"✅ Scope: *{scope}*\n\n"
        f"💰 *Investor Application* {_p(3)}\n\n"
        "What is your *full name*?",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.full_name)
async def inv_step3(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(InvestorForm.email)
    await message.answer(
        f"💰 *Investor Application* {_p(4)}\n\nWhat is your *contact email address*?",
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
        f"💰 *Investor Application* {_p(5)}\n\nWhat is your *country of residence*?",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.country)
async def inv_step5(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await state.set_state(InvestorForm.invest_experience)
    await message.answer(
        f"💰 *Investor Application* {_p(6)}\n\n"
        "Describe your *investment experience*.\n"
        "_(e.g. years in crypto investing, notable portfolios, prior rounds participated in)_",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.invest_experience)
async def inv_step6(message: Message, state: FSMContext):
    await state.update_data(invest_experience=message.text.strip())
    await state.set_state(InvestorForm.invest_size)
    await message.answer(
        f"💰 *Investor Application* {_p(7)}\n\nWhat is your *preferred investment size / range*?",
        parse_mode="Markdown",
        reply_markup=invest_size_keyboard()
    )


@router.callback_query(InvestorForm.invest_size, F.data.startswith("isize:"))
async def inv_step7(callback: CallbackQuery, state: FSMContext):
    size = callback.data.split(":", 1)[1]
    await state.update_data(invest_size=size)
    await state.set_state(InvestorForm.specific_questions)
    await callback.message.edit_text(
        f"✅ Investment Range: *{size}*\n\n"
        f"💰 *Investor Application* {_p(8)}\n\n"
        "Do you have any *specific questions or areas of interest* regarding Kraven's financials or roadmap?\n\n"
        "_(Type 'None' if not applicable)_",
        parse_mode="Markdown"
    )


@router.message(InvestorForm.specific_questions)
async def inv_step8(message: Message, state: FSMContext):
    await state.update_data(specific_questions=message.text.strip())
    data = await state.get_data()
    await state.set_state(InvestorForm.confirm)

    summary = (
        "📋 *Review Your Investor Application*\n\n"
        f"👤 Name: {data['full_name']}\n"
        f"📧 Email: {data['email']}\n"
        f"🌍 Country: {data['country']}\n"
        f"🎯 Scope: {data['investment_scope']}\n"
        f"💰 Preferred Size: {data['invest_size']}\n\n"
        f"💡 *Motivation:*\n_{data['motivation']}_\n\n"
        f"📊 *Experience:*\n_{data['invest_experience']}_\n\n"
        f"❓ *Specific Questions:*\n_{data['specific_questions']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\nReady to submit?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(InvestorForm.confirm, F.data.startswith("confirm:"))
async def inv_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Application cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    await insert_investor(data)
    await state.clear()

    await callback.message.edit_text(
        "🎉 *Investor Application Submitted!*\n\n"
        "Thank you for your interest in Kraven. A member of our team will be in touch with you at your provided email address.\n\n"
        "_We look forward to exploring this opportunity together._",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
