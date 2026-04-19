from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data)


# ─── Main Menu ─────────────────────────────────────────────────────────────────

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🎤  Apply as a KOL",              "cat:kol")],
        [btn("🏢  Apply as a Project",           "cat:project")],
        [btn("💰  Apply as an Investor",         "cat:investor")],
        [btn("🤝  Apply as an Ecosystem Partner","cat:partner")],
        [btn("💬  General Inquiry / Support",    "cat:support")],
    ])


# ─── KOL Sub-menu ──────────────────────────────────────────────────────────────

def kol_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("📝 Apply to Join Kraven (KOL)", "kol:apply")],
        [btn("🔍 Check My Application Status", "kol:status")],
        [btn("🪪 Get My KOL ID",               "kol:id")],
        [btn("⬅️ Back",                         "menu")],
    ])


# ─── Niche keyboard ────────────────────────────────────────────────────────────

def niche_keyboard() -> InlineKeyboardMarkup:
    niches = ["Crypto/Web3", "Gaming", "Finance", "Tech", "Lifestyle", "Entertainment", "Other"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(n, f"niche:{n}")] for n in niches]
    )


# ─── Project category ──────────────────────────────────────────────────────────

def project_category_keyboard() -> InlineKeyboardMarkup:
    cats = ["DeFi", "NFT/Gaming", "Layer 1/2", "Infrastructure", "SocialFi", "AI/Data", "Other"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(c, f"pcat:{c}")] for c in cats]
    )


# ─── Services (multi-select) ───────────────────────────────────────────────────

SERVICES = {
    "svc:mass_awareness":    "📡 Mass Awareness Campaigns",
    "svc:sustainable_dist":  "♻️ Sustainable Distribution",
    "svc:content_clipping":  "✂️ Content Clipping Services",
    "svc:krending":          "📈 Krending (Trend Amplification)",
    "svc:ultimatum":         "💥 Ultimatum (High-Impact Marketing)",
    "svc:web_dev":           "🌐 Website Development",
    "svc:x_traction":        "🐦 X Social Traction Enhancement",
}


def services_keyboard(selected: set) -> InlineKeyboardMarkup:
    rows = []
    for data, label in SERVICES.items():
        tick = "✅ " if data in selected else ""
        rows.append([btn(f"{tick}{label}", data)])
    rows.append([btn("✔️  Done — Confirm Selection", "svc:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── Budget ────────────────────────────────────────────────────────────────────

def budget_keyboard() -> InlineKeyboardMarkup:
    ranges = ["< $1K", "$1K–$5K", "$5K–$20K", "$20K–$50K", "$50K+", "To Be Discussed"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(r, f"budget:{r}")] for r in ranges]
    )


# ─── Tenure ────────────────────────────────────────────────────────────────────

def tenure_keyboard() -> InlineKeyboardMarkup:
    options = ["1 month", "2–3 months", "3–6 months", "6–12 months", "12+ months", "One-time"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(o, f"tenure:{o}")] for o in options]
    )


# ─── Investment scope ──────────────────────────────────────────────────────────

def investment_scope_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🏦 Kraven itself only",            "scope:kraven_only")],
        [btn("🌐 Ecosystem projects only",        "scope:ecosystem_only")],
        [btn("🔁 Both Kraven & ecosystem projects","scope:both")],
    ])


def invest_size_keyboard() -> InlineKeyboardMarkup:
    sizes = ["< $10K", "$10K–$50K", "$50K–$250K", "$250K–$1M", "$1M+", "Prefer not to say"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(s, f"isize:{s}")] for s in sizes]
    )


# ─── Partner ───────────────────────────────────────────────────────────────────

def ecosystem_interest_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("✅ Yes, I'm open to partnering with ecosystem projects", "eco:yes")],
        [btn("❌ No, only a direct Kraven partnership",                "eco:no")],
    ])


# ─── Support ───────────────────────────────────────────────────────────────────

def support_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🎫 Open a Support Ticket", "support:ticket")],
        [btn("📚 Visit FAQ / Help Center", "support:faq")],
        [btn("⬅️ Back",                   "menu")],
    ])


# ─── Confirm ───────────────────────────────────────────────────────────────────

def confirm_keyboard(yes_data: str = "confirm:yes", no_data: str = "confirm:no") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        btn("✅ Submit", yes_data),
        btn("🗑 Cancel", no_data),
    ]])


# ─── Admin ─────────────────────────────────────────────────────────────────────

def admin_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🎤 Pending KOL Applications",     "adm:list:kol")],
        [btn("🏢 Pending Project Applications", "adm:list:project")],
        [btn("💰 Pending Investor Applications","adm:list:investor")],
        [btn("🤝 Pending Partner Applications", "adm:list:partner")],
        [btn("🎫 Open Support Tickets",         "adm:list:tickets")],
    ])


def admin_review_keyboard(app_type: str, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        btn("✅ Approve", f"adm:approve:{app_type}:{user_id}"),
        btn("❌ Reject",  f"adm:reject:{app_type}:{user_id}"),
    ]])


def close_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("✅ Close Ticket", f"adm:close_ticket:{ticket_id}")]
    ])
