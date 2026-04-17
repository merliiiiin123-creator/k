from aiogram.fsm.state import State, StatesGroup


class RegistrationForm(StatesGroup):
    full_name      = State()
    platform       = State()
    profile_link   = State()
    follower_count = State()
    mutuals        = State()
    account_age    = State()
    is_verified    = State()
    pitch          = State()
    confirm        = State()


class SupportTicket(StatesGroup):
    priority = State()
    message  = State()


class AdminAction(StatesGroup):
    note = State()  # optional rejection note
