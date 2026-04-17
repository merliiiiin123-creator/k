from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.menus import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Welcome to <b>Kraven Creator Hub</b>, {message.from_user.first_name}!\n\n"
        "We vet and onboard creators for the Kraven network.\n\n"
        "Use the menu below to get started:",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Main Menu</b>\n\nWhat would you like to do?",
        reply_markup=main_menu()
    )
