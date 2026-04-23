from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import ProjectForm
from keyboards.menus import (
    project_category_keyboard, service_layer_keyboard, services_keyboard, 
    service_info_keyboard, post_service_choice_keyboard,
    budget_keyboard, tenure_keyboard, confirm_keyboard, main_menu, SERVICES
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
        "🏢 *Partner with Kraven*\n\n"
        "Ready to get your project in front of the right people?\n\n"
        "Kraven runs *mass awareness campaigns*, *sustainable distribution*, "
        "*content clipping*, *trend amplification*, and more — built specifically "
        "for projects that want *real traction*, not just impressions.\n\n"
        f"{_p(1)} Let's start with the basics. What's your *project name*?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.project_name)
async def proj_step1(message: Message, state: FSMContext):
    await state.update_data(project_name=message.text.strip())
    await state.set_state(ProjectForm.website_url)
    await message.answer(
        f"🏢 {_p(2)}\n\nDrop your *project website URL*.",
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
        f"🏢 {_p(3)}\n\nYour *X (Twitter) account*?\n_(e.g. @KravenHQ)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.x_account)
async def proj_step3(message: Message, state: FSMContext):
    await state.update_data(x_account=message.text.strip())
    await state.set_state(ProjectForm.tg_discord)
    await message.answer(
        f"🏢 {_p(4)}\n\nYour *Telegram and/or Discord* community link(s).\n_(Separate multiple with a comma)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.tg_discord)
async def proj_step4(message: Message, state: FSMContext):
    await state.update_data(tg_discord=message.text.strip())
    await state.set_state(ProjectForm.contact_name)
    await message.answer(
        f"🏢 {_p(5)}\n\nWho's the *main point of contact* on your team?",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.contact_name)
async def proj_step5(message: Message, state: FSMContext):
    await state.update_data(contact_name=message.text.strip())
    await state.set_state(ProjectForm.contact_email)
    await message.answer(
        f"🏢 {_p(6)}\n\nBest *email address* to reach them?",
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
        f"🏢 {_p(7)}\n\nWhat category best describes your project?",
        parse_mode="Markdown",
        reply_markup=project_category_keyboard()
    )


@router.callback_query(ProjectForm.project_category, F.data.startswith("pcat:"))
async def proj_step7(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split(":", 1)[1]
    await state.update_data(project_category=cat, services_selected=set(), current_layer=None)
    await state.set_state(ProjectForm.services)
    await callback.message.edit_text(
        f"🏢 {_p(8)}\n\n"
        "*What service are you looking for?*\n\n"
        "Kraven offers specialized solutions across two main infrastructure layers. "
        "Select a layer to view specific services, then hit *Done* when finished.",
        parse_mode="Markdown",
        reply_markup=service_layer_keyboard()
    )


@router.callback_query(ProjectForm.services, F.data.startswith("layer:"))
async def proj_services_layer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("services_selected", set())
    
    if callback.data == "layer:back":
        await state.update_data(current_layer=None)
        await callback.message.edit_text(
            f"🏢 {_p(8)}\n\n"
            "*What service are you looking for?*\n\n"
            "Select a layer to view specific services, then hit *Done* when finished.",
            parse_mode="Markdown",
            reply_markup=service_layer_keyboard()
        )
        return

    layer = callback.data.split(":", 1)[1]
    if layer == "stay":
        layer = data.get("current_layer", "dist")
    else:
        await state.update_data(current_layer=layer)
    
    layer_name = "📡 Distribution Infra Layer" if layer == "dist" else "🛠 Supportive Infra Layer"
    await callback.message.edit_text(
        f"🏢 {_p(8)}\n\n"
        f"*{layer_name}*\n\n"
        "Tap a service to learn more and select it.",
        parse_mode="Markdown",
        reply_markup=services_keyboard(layer, selected)
    )


@router.callback_query(ProjectForm.services, F.data.startswith("info:"))
async def proj_service_info(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split(":", 1)[1]
    service_data = SERVICES.get(service_id, {})
    
    data = await state.get_data()
    selected = data.get("services_selected", set())
    is_selected = service_id in selected
    
    text = (
        f"*{service_data.get('label', 'Service Info')}*\n\n"
        f"{service_data.get('desc', 'No description available.')}"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=service_info_keyboard(service_id, is_selected)
    )


@router.callback_query(ProjectForm.services, F.data.startswith("svc:"))
async def proj_services_toggle(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected: set = data.get("services_selected", set())
    current_layer = data.get("current_layer", "dist")

    if callback.data == "svc:done":
        if not selected:
            await callback.answer("⚠️ Pick at least one service.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🔥 *Excellent choice.*\n\n"
            "How would you like to proceed? You can fill out our briefing form "
            "right now, or book a direct strategy call with our team.",
            parse_mode="Markdown",
            reply_markup=post_service_choice_keyboard()
        )
        return

    service_id = callback.data.split(":", 1)[1]
    if service_id in selected:
        selected.discard(service_id)
        await callback.answer("❌ Service removed.")
    else:
        selected.add(service_id)
        await callback.answer("✅ Service selected.")
    
    await state.update_data(services_selected=selected)
    
    # After toggling, go back to the list
    layer_name = "📡 Distribution Infra Layer" if current_layer == "dist" else "🛠 Supportive Infra Layer"
    await callback.message.edit_text(
        f"🏢 {_p(8)}\n\n"
        f"*{layer_name}*\n\n"
        "Tap a service to learn more and select it.",
        parse_mode="Markdown",
        reply_markup=services_keyboard(current_layer, selected)
    )


@router.callback_query(ProjectForm.services, F.data.startswith("choice:"))
async def proj_post_service_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split(":", 1)[1]
    
    if choice == "call":
        await callback.message.edit_text(
            "📅 *Book a Strategy Call*\n\n"
            "Ready to talk shop? Book a 15-minute intro call with our team to "
            "discuss your project and how we can help you scale.\n\n"
            "🔗 [Book your call here](https://calendly.com/kraven-hq)\n\n"
            "Once you've booked, you can also complete the form to give us more "
            "context beforehand!",
            parse_mode="Markdown",
            reply_markup=post_service_choice_keyboard()
        )
        return

    # choice == "form" -> proceed to budget
    data = await state.get_data()
    selected = data.get("services_selected", set())
    labels = [SERVICES[s]["label"] for s in selected if s in SERVICES]
    await state.update_data(services_display="\n  • ".join(labels))
    
    await state.set_state(ProjectForm.budget_range)
    await callback.message.edit_text(
        f"✅ *{len(selected)} service(s) locked in.*\n\n"
        f"🏢 {_p(9)}\n\nWhat's your *budget range* for this campaign?",
        parse_mode="Markdown",
        reply_markup=budget_keyboard()
    )


@router.callback_query(ProjectForm.budget_range, F.data.startswith("budget:"))
async def proj_budget(callback: CallbackQuery, state: FSMContext):
    budget = callback.data.split(":", 1)[1]
    await state.update_data(budget_range=budget)
    await state.set_state(ProjectForm.project_tenure)
    await callback.message.edit_text(
        f"🏢 {_p(10)}\n\nHow long do you want to run this campaign?",
        parse_mode="Markdown",
        reply_markup=tenure_keyboard()
    )


@router.callback_query(ProjectForm.project_tenure, F.data.startswith("tenure:"))
async def proj_tenure(callback: CallbackQuery, state: FSMContext):
    tenure = callback.data.split(":", 1)[1]
    await state.update_data(project_tenure=tenure)
    await state.set_state(ProjectForm.traction_desc)
    await callback.message.edit_text(
        f"🏢 {_p(11)}\n\n"
        "Last one — tell us about your *current traction and where you're headed*.\n\n"
        "_(Think: users, TVL, community size, recent milestones, growth targets. "
        "The more context you give us, the better we can execute.)_",
        parse_mode="Markdown"
    )


@router.message(ProjectForm.traction_desc)
async def proj_traction(message: Message, state: FSMContext):
    if len(message.text.strip()) < 20:
        await message.answer("❌ Give us a bit more to work with — a few sentences at least.")
        return
    await state.update_data(traction_desc=message.text.strip())
    data = await state.get_data()
    await state.set_state(ProjectForm.confirm)

    services_display = data.get("services_display", "None")
    summary = (
        "📋 *Review your project brief:*\n\n"
        f"🏢 Project: {data['project_name']}\n"
        f"🌐 Website: {data['website_url']}\n"
        f"🐦 X: {data['x_account']}\n"
        f"💬 TG/Discord: {data['tg_discord']}\n"
        f"👤 Contact: {data['contact_name']}\n"
        f"📧 Email: {data['contact_email']}\n"
        f"📂 Category: {data['project_category']}\n\n"
        f"🛠 *Services:*\n  • {services_display}\n\n"
        f"💰 Budget: {data['budget_range']}\n"
        f"📅 Duration: {data['project_tenure']}\n\n"
        f"📈 *Traction:*\n_{data['traction_desc']}_\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ready? Our team reviews every brief personally and we'll be in touch within 48 hours. 🚀"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_keyboard())


@router.callback_query(ProjectForm.confirm, F.data.startswith("confirm:"))
async def proj_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm:no":
        await state.clear()
        await callback.message.edit_text("🗑 Brief cancelled.", reply_markup=main_menu())
        return

    data = await state.get_data()
    selected_set: set = data.get("services_selected", set())
    data["services_selected"] = ", ".join(selected_set)
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username or "N/A"
    data.pop("services_display", None)

    await insert_project(data)
    await state.clear()

    await callback.message.edit_text(
        "🔥 *Brief submitted.*\n\n"
        "You'll hear from our team within 48 hours to align on scope, "
        "strategy, and next steps.\n\n"
        "_Let's build something that actually moves the market._",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
