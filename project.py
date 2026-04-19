from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import ProjectForm
from keyboards.menus import (
    project_category_keyboard, services_keyboard, budget_keyboard,
    tenure_keyboard, confirm_keyboard, main_menu, SERVICES
)
from database.db import insert_project
from utils import is_valid_email, is_valid_url

router = Router()
TOTAL_STEPS = 11


def _p(step): return f"_(Step {step} of {TOTAL_STEPS})_"


@router.callback_query(F.data == "cat:project")
async def cat_project(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProjectForm.project_name)
    await callback.message.edit_text(
        "🏢 *Project Application*\n\n"
        "Let's get your project set up with Kraven's services.\n\n"
        f"{_p(1)} What is your *project name*?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.project_name)
async def proj_step1(message: Message, state: FSMContext):
    await state.update_data(project_name=message.text.strip())
    await state.set_state(ProjectForm.website_url)
    await message.answer(
        f"🏢 *Project Application* {_p(2)}\n\nWhat is your *project website URL*?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.website_url)
async def proj_step2(message: Message, state: FSMContext):
    if not is_valid_url(message.text):
        await message.answer("❌ Please send a valid URL starting with https://")
        return
    await state.update_data(website_url=message.text.strip())
    await state.set_state(ProjectForm.x_account)
    await message.answer(
        f"🏢 *Project Application* {_p(3)}\n\nWhat is your *X (Twitter) account*?\n_(e.g. @KravenHQ)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.x_account)
async def proj_step3(message: Message, state: FSMContext):
    await state.update_data(x_account=message.text.strip())
    await state.set_state(ProjectForm.tg_discord)
    await message.answer(
        f"🏢 *Project Application* {_p(4)}\n\nProvide your *Telegram / Discord community link(s)*.\n_(Separate multiple with a comma)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.tg_discord)
async def proj_step4(message: Message, state: FSMContext):
    await state.update_data(tg_discord=message.text.strip())
    await state.set_state(ProjectForm.contact_name)
    await message.answer(
        f"🏢 *Project Application* {_p(5)}\n\nWhat is the *primary contact person's full name*?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.contact_name)
async def proj_step5(message: Message, state: FSMContext):
    await state.update_data(contact_name=message.text.strip())
    await state.set_state(ProjectForm.contact_email)
    await message.answer(
        f"🏢 *Project Application* {_p(6)}\n\nWhat is the *contact email address*?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.contact_email)
async def proj_step6(message: Message, state: FSMContext):
    if not is_valid_email(message.text):
        await message.answer("❌ Please enter a valid email address.")
        return
    await state.update_data(contact_email=message.text.strip().lower())
    await state.set_state(ProjectForm.project_category)
    await message.answer(
        f"🏢 *Project Application* {_p(7)}\n\nSelect your *project category*:",
        parse_mode="Markdown",
        reply_markup=project_category_keyboard()
    )


@router.callback_query(ProjectForm.project_category, F.data.startswith("pcat:"))
async def proj_step7(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split(":", 1)[1]
    await state.update_data(project_category=cat, services_selected=set())
    await state.set_state(ProjectForm.services)
    await callback.message.edit_text(
        f"✅ Category: *{cat}*\n\n"
        f"🏢 *Project Application* {_p(8)}\n\n"
        "Select *all services* you're interested in.\n"
        "Tap each to toggle, then tap *Done* when finished.\n\n"
        "📡 *Distribution Infrastructure Layer*\n"
        "• Mass Awareness, Sustainable Dist., Clipping, Krending, Ultimatum\n\n"
        "🛠 *Supportive Infrastructure Layer*\n"
        "• Website Dev, X Social Traction",
        parse_mode="Markdown",
        reply_markup=services_keyboard(set())
    )


@router.callback_query(ProjectForm.services, F.data.startswith("svc:"))
async def proj_services_toggle(callback: CallbackQuery, state: FSMContext):
    if callback.data == "svc:done":
        data = await state.get_data()
        selected = data.get("services_selected", set())
        if not selected:
            await callback.answer("⚠️ Please select at least one service.", show_alert=True)
            return
        # Convert set to readable string for storage
        labels = [SERVICES[s] for s in selected if s in SERVICES]
        await state.update_data(services_display="\n  • ".join(labels))
        await state.set_state(ProjectForm.budget_range)
        await callback.message.edit_text(
            f"✅ *{len(selected)} service(s) selected.*\n\n"
            f"🏢 *Project Application* {_p(9)}\n\n"
            "What is your *estimated budget range*?",
            parse_mode="Markdown",
            reply_markup=budget_keyboard()
        )
        return

    data = await state.get_data()
    selected: set = data.get("services_selected", set())

    if callback.data in selected:
        selected.discard(callback.data)
    else:
        selected.add(callback.data)

    await state.update_data(services_selected=selected)
    await callback.message.edit_reply_markup(reply_markup=services_keyboard(selected))
    await callback.answer()


@router.callback_query(ProjectForm.budget_range, F.data.startswith("budget:"))
async def proj_budget(callback: CallbackQuery, state: FSMContext):
    budget = callback.data.split(":", 1)[1]
    await state.update_data(budget_range=budget)
    await state.set_state(ProjectForm.project_tenure)
    await callback.message.edit_text(
        f"✅ Budget: *{budget}*\n\n"
        f"🏢 *Project Application* {_p(10)}\n\n"
        "What is your *estimated project tenure*?",
        parse_mode="Markdown",
        reply_markup=tenure_keyboard()
    )


@router.callback_query(ProjectForm.project_tenure, F.data.startswith("tenure:"))
async def proj_tenure(callback: CallbackQuery, state: FSMContext):
    tenure = callback.data.split(":", 1)[1]
    await state.update_data(project_tenure=tenure)
    await state.set_state(ProjectForm.traction_desc)
    await callback.message.edit_text(
        f"✅ Tenure: *{tenure}*\n\n"
        f"🏢 *Project Application* {_p(11)}\n\n"
        "Briefly describe your *product's current traction* and *future expectations*.\n"
        "_(TVL, users, milestones, growth targets, etc.)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.traction_desc)
async def proj_traction(message: Message, state: FSMContext):
    if len(message.text.strip()) < 20:
        await message.answer("❌ Please provide more detail — at least a few sentences.")
        return
    await state.update_data(traction_desc=message.text.strip())
    data = await state.get_data()
    await state.set_state(ProjectForm.confirm)

    services_display = data.get("services_display", "None")
    summary = (
        "📋 *Review Your Project Application*\n\n"
        f"🏢 Project: {data['project_name']}\n"
        f"🌐 Website: {data['website_url']}\n"
        f"🐦 X: {data['x_account']}\n"
        f"💬 TG/Discord: {data['tg_discord']}\n"
        f"👤 Contact: {data['contact_name']}\n"
        f"📧 Email: {data['contact_email']}\n"
        f"📂 Category: {data['project_category']}\n\n"
        f"🛠 *Services Requested:*\n  • {services_display}\n\n"
        f"💰 Budget: {data['budget_range']}\n"
        f"📅 Tenure: {data['project_tenure']}\n\n"
        f"📈 *Traction:*\n_{data['traction_desc']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\nReady to submit?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(ProjectForm.confirm, F.data.startswith("confirm:"))
async def proj_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Application cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    selected_set: set = data.get("services_selected", set())
    data["services_selected"] = ", ".join(selected_set)  # serialise for DB
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    data.pop("services_display", None)

    await insert_project(data)
    await state.clear()

    await callback.message.edit_text(
        "🎉 *Project Application Submitted!*\n\n"
        "Thank you! Our team will review your submission and reach out to your contact email within 48 hours.\n\n"
        "_We appreciate you choosing Kraven as your growth partner._",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
