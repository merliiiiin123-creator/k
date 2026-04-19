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
        "🤝 *Ecosystem Partner*\n\n"
        "Kraven's network is growing fast — and we partner with builders, "
        "agencies, tools, and platforms that bring *real value* to the ecosystem.\n\n"
        "If you're aligned with what we're building, let's figure out how we grow together.\n\n"
        f"{_p(1)} Are you open to a partnership under *specific terms*?\n\n"
        "Tell us what you have in mind — or type *'Open to discuss'* if you'd rather talk first.",
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
        f"🤝 {_p(2)}\n\n"
        "Beyond a direct Kraven partnership — are you also open to *collaborating with projects "
        "in the Kraven ecosystem* that fit your niche?",
        parse_mode="Markdown",
        reply_markup=ecosystem_interest_keyboard()
    )


@router.callback_query(PartnerForm.ecosystem_interest, F.data.startswith("eco:"))
async def partner_step2(callback: CallbackQuery, state: FSMContext):
    interest = "Yes" if callback.data == "eco:yes" else "No"
    await state.update_data(ecosystem_interest=interest)
    await state.set_state(PartnerForm.company_name)
    await callback.message.edit_text(
        f"🤝 {_p(3)}\n\nWhat's your *company or organization name*?",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.company_name)
async def partner_step3(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text.strip())
    await state.set_state(PartnerForm.contact_person)
    await message.answer(
        f"🤝 {_p(4)}\n\nWho's the *primary contact person* on your end?",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.contact_person)
async def partner_step4(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text.strip())
    await state.set_state(PartnerForm.contact_email)
    await message.answer(
        f"🤝 {_p(5)}\n\nBest *email address* to reach them?",
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
        f"🤝 {_p(6)}\n\n*Website or portfolio URL*?\n_(Type 'N/A' if not applicable)_",
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
        f"🤝 {_p(7)}\n\n"
        "Give us a *quick overview of what you do* — your services, product, or offering.\n"
        "_(2–4 sentences is perfect)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.services_overview)
async def partner_step7(message: Message, state: FSMContext):
    if len(message.text.strip()) < 20:
        await message.answer("❌ Please give us a bit more detail.")
        return
    await state.update_data(services_overview=message.text.strip())
    await state.set_state(PartnerForm.cover_letter)
    await message.answer(
        f"🤝 {_p(8)}\n\n"
        "Last step — write us a *short pitch*.\n\n"
        "Tell us:\n"
        "• Why Kraven?\n"
        "• What you bring to the table\n"
        "• Any specific collab ideas you have in mind\n\n"
        "_(Keep it real — we read every single one)_",
        parse_mode="Markdown"
    )


@router.message(PartnerForm.cover_letter)
async def partner_step8(message: Message, state: FSMContext):
    if len(message.text.strip()) < 30:
        await message.answer("❌ Give us a bit more — this is your pitch!")
        return
    await state.update_data(cover_letter=message.text.strip())
    data = await state.get_data()
    await state.set_state(PartnerForm.confirm)

    summary = (
        "📋 *Your partnership brief:*\n\n"
        f"🏢 Company: {data['company_name']}\n"
        f"👤 Contact: {data['contact_person']}\n"
        f"📧 Email: {data['contact_email']}\n"
        f"🌐 Website: {data['website']}\n"
        f"🌱 Ecosystem Interest: {data['ecosystem_interest']}\n\n"
        f"📝 *Proposed Terms:*\n_{data['partnership_terms']}_\n\n"
        f"🛠 *What You Do:*\n_{data['services_overview']}_\n\n"
        f"✉️ *Your Pitch:*\n_{data['cover_letter']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Happy with this? We'll review and reach out within 72 hours. 🤝"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(PartnerForm.confirm, F.data.startswith("confirm:"))
async def partner_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Submission cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    await insert_partner(data)
    await state.clear()

    await callback.message.edit_text(
        "✅ *Proposal received.*\n\n"
        "We review every partnership personally. "
        "Expect a reply to your email within 72 hours.\n\n"
        "_Big things happen when the right people link up. Talk soon._",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
