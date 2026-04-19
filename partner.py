from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import PartnerForm
from keyboards.menus import ecosystem_interest_keyboard, confirm_keyboard, main_menu
from database.db import insert_partner
from utils import is_valid_email, is_valid_url

router = Router()
TOTAL_STEPS = 8


def _p(step): return f"_(Step {step} of {TOTAL_STEPS})_"


@router.callback_query(F.data == "cat:partner")
async def cat_partner(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PartnerForm.partnership_terms)
    await callback.message.edit_text(
        "🤝 *Ecosystem Partner Application*\n\n"
        "We're always looking to grow with aligned partners.\n\n"
        f"{_p(1)} Are you open to a partnership with Kraven under *specific terms*?\n\n"
        "If yes, please *briefly describe your proposed terms or expectations*.\n"
        "_(Type 'Open to discuss' if you'd prefer a conversation first)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.partnership_terms)
async def partner_step1(message: Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("❌ Please provide a valid response.")
        return
    await state.update_data(partnership_terms=message.text.strip())
    await state.set_state(PartnerForm.ecosystem_interest)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(2)}\n\n"
        "Are you also interested in *partnering with projects within the Kraven ecosystem* "
        "that align with your niche?",
        parse_mode="Markdown",
        reply_markup=ecosystem_interest_keyboard()
    )


@router.callback_query(PartnerForm.ecosystem_interest, F.data.startswith("eco:"))
async def partner_step2(callback: CallbackQuery, state: FSMContext):
    interest = "Yes" if callback.data == "eco:yes" else "No"
    await state.update_data(ecosystem_interest=interest)
    await state.set_state(PartnerForm.company_name)
    await callback.message.edit_text(
        f"✅ Ecosystem Interest: *{interest}*\n\n"
        f"🤝 *Ecosystem Partner Application* {_p(3)}\n\n"
        "What is your *company / organization name*?",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.company_name)
async def partner_step3(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text.strip())
    await state.set_state(PartnerForm.contact_person)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(4)}\n\nWho is the *primary contact person*?",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.contact_person)
async def partner_step4(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text.strip())
    await state.set_state(PartnerForm.contact_email)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(5)}\n\nWhat is the *contact email address*?",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.contact_email)
async def partner_step5(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("❌ Please enter a valid email address.")
        return
    await state.update_data(contact_email=message.text.strip().lower())
    await state.set_state(PartnerForm.website)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(6)}\n\n"
        "What is your *website or portfolio URL*?\n_(Type 'N/A' if not applicable)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.website)
async def partner_step6(message: Message, state: FSMContext):
    url = message.text.strip()
    if url.upper() != "N/A" and not is_valid_url(url):
        await message.answer("❌ Please enter a valid URL (https://...) or type 'N/A'.")
        return
    await state.update_data(website=url)
    await state.set_state(PartnerForm.services_overview)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(7)}\n\n"
        "Provide a *brief overview of your services or products*.\n"
        "_(2–4 sentences is ideal)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.services_overview)
async def partner_step7(message: Message, state: FSMContext):
    if len(message.text.strip()) < 20:
        await message.answer("❌ Please provide more detail.")
        return
    await state.update_data(services_overview=message.text.strip())
    await state.set_state(PartnerForm.cover_letter)
    await message.answer(
        f"🤝 *Ecosystem Partner Application* {_p(8)}\n\n"
        "Finally, please write a *cover letter or brief proposal*.\n\n"
        "This should outline:\n"
        "• Why you want to partner with Kraven\n"
        "• The value you bring to the ecosystem\n"
        "• Any specific collaboration ideas\n\n"
        "_(A short paragraph is fine — quality over quantity!)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.cover_letter)
async def partner_step8(message: Message, state: FSMContext):
    if len(message.text.strip()) < 30:
        await message.answer("❌ Please write a more detailed proposal.")
        return
    await state.update_data(cover_letter=message.text.strip())
    data = await state.get_data()
    await state.set_state(PartnerForm.confirm)

    summary = (
        "📋 *Review Your Partner Application*\n\n"
        f"🏢 Company: {data['company_name']}\n"
        f"👤 Contact: {data['contact_person']}\n"
        f"📧 Email: {data['contact_email']}\n"
        f"🌐 Website: {data['website']}\n"
        f"🌱 Ecosystem Interest: {data['ecosystem_interest']}\n\n"
        f"📝 *Proposed Terms:*\n_{data['partnership_terms']}_\n\n"
        f"🛠 *Services Overview:*\n_{data['services_overview']}_\n\n"
        f"✉️ *Cover Letter:*\n_{data['cover_letter']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\nReady to submit?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(PartnerForm.confirm, F.data.startswith("confirm:"))
async def partner_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Application cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    await insert_partner(data)
    await state.clear()

    await callback.message.edit_text(
        "🎉 *Partnership Application Submitted!*\n\n"
        "Thank you for your interest in partnering with Kraven. "
        "We'll review your proposal and reach out via email within 72 hours.\n\n"
        "_We're excited about the possibilities ahead!_",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
