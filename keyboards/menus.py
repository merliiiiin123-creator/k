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
    "svc:mass_awareness": {
        "label": "📡 Mass Awareness Campaigns",
        "desc": "Get your project in front of millions. We leverage our elite KOL network to create massive visibility and brand recognition across all major social platforms."
    },
    "svc:sustainable_dist": {
        "label": "♻️ Sustainable Distribution",
        "desc": "Long-term growth over short-term hype. We build sustainable distribution channels that keep your project relevant and growing month after month."
    },
    "svc:content_clipping": {
        "label": "✂️ Content Clipping Services",
        "desc": "Turn long-form content into viral gold. Our editors craft high-engagement short-form clips optimized for TikTok, Reels, and X to maximize your reach."
    },
    "svc:krending": {
        "label": "📈 Krending (Trend Amplification)",
        "desc": "We don't just follow trends; we create them. Use our proprietary Krending strategy to amplify your message and dominate the social conversation."
    },
    "svc:ultimatum": {
        "label": "💥 Ultimatum (High-Impact Marketing)",
        "desc": "The nuclear option for project launches or major updates. A concentrated burst of high-impact marketing designed to move the market instantly."
    },
    "svc:web_dev": {
        "label": "🌐 Website Development",
        "desc": "High-converting, performance-optimized websites built for the modern Web3 ecosystem. From landing pages to complex dApps."
    },
    "svc:x_traction": {
        "label": "🐦 X Social Traction Enhancement",
        "desc": "Dominate X (Twitter). We boost your social presence, engagement, and follower growth through strategic content and network amplification."
    },
}

DISTRIBUTION_SERVICES = [
    "svc:mass_awareness", "svc:sustainable_dist", "svc:content_clipping", 
    "svc:krending", "svc:ultimatum"
]

SUPPORTIVE_SERVICES = [
    "svc:web_dev", "svc:x_traction"
]


def service_layer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("📡 Distribution Infra Layer", "layer:dist")],
        [btn("🛠 Supportive Infra Layer",   "layer:supp")],
        [btn("✔️  Done — Confirm Selection", "svc:done")]
    ])


def services_keyboard(layer: str, selected: set) -> InlineKeyboardMarkup:
    rows = []
    service_list = DISTRIBUTION_SERVICES if layer == "dist" else SUPPORTIVE_SERVICES
    
    for data in service_list:
        service_info = SERVICES.get(data, {})
        label = service_info.get("label", data)
        tick = "✅ " if data in selected else ""
        # Use info: prefix to show info first
        rows.append([btn(f"{tick}{label}", f"info:{data}")])
    
    rows.append([btn("⬅️ Back to Layers", "layer:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def service_info_keyboard(service_id: str, is_selected: bool) -> InlineKeyboardMarkup:
    toggle_text = "❌ Unselect Service" if is_selected else "✅ Select Service"
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn(toggle_text, f"svc:{service_id}")],
        [btn("⬅️ Back to List", "layer:stay")]
    ])


def post_service_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("📝 Fill the Briefing Form", "choice:form")],
        [btn("📅 Book a Strategy Call",   "choice:call")],
        [btn("⬅️ Back to Services",      "layer:back")]
    ])


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
