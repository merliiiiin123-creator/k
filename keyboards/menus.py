from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ─── Main Menu ─────────────────────────────────────────────────────────────────

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Apply to Join Kraven", callback_data="apply")],
        [InlineKeyboardButton(text="🔍 Check Application Status", callback_data="status")],
        [InlineKeyboardButton(text="🎫 Open Support Ticket", callback_data="support")],
        [InlineKeyboardButton(text="🪪 Get My ID", callback_data="get_id")],
    ])


# ─── Registration ──────────────────────────────────────────────────────────────

def platform_keyboard() -> InlineKeyboardMarkup:
    platforms = ["Twitter/X", "Instagram", "TikTok", "YouTube", "LinkedIn", "Other"]
    buttons = [[InlineKeyboardButton(text=p, callback_data=f"platform:{p}")] for p in platforms]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def verified_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="verified:Yes"),
            InlineKeyboardButton(text="❌ No", callback_data="verified:No"),
        ]
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Submit Application", callback_data="confirm:yes"),
            InlineKeyboardButton(text="🗑 Cancel", callback_data="confirm:no"),
        ]
    ])


# ─── Support ───────────────────────────────────────────────────────────────────

def priority_keyboard() -> InlineKeyboardMarkup:
    levels = [
        ("🟢 Low", "priority:Low"),
        ("🟡 Medium", "priority:Medium"),
        ("🔴 High", "priority:High"),
        ("🚨 Urgent", "priority:Urgent"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=d)] for t, d in levels
    ])


# ─── Admin ─────────────────────────────────────────────────────────────────────

def admin_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"admin:approve:{user_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"admin:reject:{user_id}"),
        ]
    ])


def admin_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Pending Applications", callback_data="admin:pending")],
        [InlineKeyboardButton(text="🎫 Open Tickets", callback_data="admin:tickets")],
    ])


def close_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Close Ticket", callback_data=f"admin:close_ticket:{ticket_id}")]
    ])
