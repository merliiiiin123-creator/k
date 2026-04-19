from aiogram.fsm.state import State, StatesGroup


class KOLForm(StatesGroup):
    full_name           = State()
    email               = State()
    x_handle            = State()
    telegram_handle     = State()
    discord_handle      = State()
    niche               = State()
    audience_size       = State()
    engagement_metrics  = State()
    past_collabs        = State()
    confirm             = State()


class ProjectForm(StatesGroup):
    project_name        = State()
    website_url         = State()
    x_account           = State()
    tg_discord          = State()
    contact_name        = State()
    contact_email       = State()
    project_category    = State()
    services            = State()   # multi-select handled in handler
    budget_range        = State()
    project_tenure      = State()
    traction_desc       = State()
    confirm             = State()


class InvestorForm(StatesGroup):
    motivation          = State()
    investment_scope    = State()
    full_name           = State()
    email               = State()
    country             = State()
    invest_experience   = State()
    invest_size         = State()
    specific_questions  = State()
    confirm             = State()


class PartnerForm(StatesGroup):
    partnership_terms   = State()
    ecosystem_interest  = State()
    company_name        = State()
    contact_person      = State()
    contact_email       = State()
    website             = State()
    services_overview   = State()
    cover_letter        = State()
    confirm             = State()


class SupportForm(StatesGroup):
    email               = State()
    description         = State()


class AdminNote(StatesGroup):
    waiting             = State()
