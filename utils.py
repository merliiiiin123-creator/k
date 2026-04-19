import re


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email.strip()))


def is_valid_url(url: str) -> bool:
    return url.strip().startswith(("http://", "https://"))


def fmt_status(status: str) -> str:
    icons = {"pending": "⏳", "approved": "✅", "rejected": "❌"}
    return f"{icons.get(status, '❓')} {status.capitalize()}"


def back_to_menu_btn():
    from keyboards.menus import main_menu
    return main_menu()
