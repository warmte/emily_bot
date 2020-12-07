import dbworker
import config
from aiogram import types


class Button(config.Enum):
    B_HELLO = 'Привет'
    B_HELLO_VANDA = 'Привет, Ванда'
    B_YES = 'Да'
    B_NO = 'Нет'
    B_TO_MAIN_MENU = 'В главное меню'
    B_BACK = '<< Назад'

    B_MENU_EMOTIONS = 'Отметить настроение'
    B_MENU_ABOUT = 'Обо мне'
    B_MENU_STAT = 'Статистика'
    B_MENU_SETTINGS = 'Настройки'

    B_SETTINGS_TIME_ZONE = 'Изменить часовой пояс'
    B_SETTINGS_NOTIFICATIONS_CHANGE = 'Изменить время напоминаний'
    B_SETTINGS_NOTIFICATION_REMOVE = 'Отменить напоминания'

    E_ANGER = 'Гнев'
    E_FEAR = 'Страх'
    E_SADNESS = 'Печаль'
    E_JOY = 'Радость'


hello = types.ReplyKeyboardMarkup(resize_keyboard=True)
hello.row(Button.B_HELLO_VANDA.value)

yes_or_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
yes_or_no.row(Button.B_YES.value, Button.B_NO.value)

to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
to_main_menu.row(Button.B_TO_MAIN_MENU.value)

back_or_to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_or_to_main_menu.row(Button.B_BACK.value, Button.B_TO_MAIN_MENU.value)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(Button.B_MENU_EMOTIONS.value, Button.B_MENU_ABOUT.value)
main_menu.row(Button.B_MENU_STAT.value, Button.B_MENU_SETTINGS.value)

settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
settings.row(Button.B_SETTINGS_TIME_ZONE.value)
settings.row(Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value)
settings.row(Button.B_SETTINGS_NOTIFICATION_REMOVE.value)
settings.row(Button.B_TO_MAIN_MENU.value)

emotions_groups = types.ReplyKeyboardMarkup(resize_keyboard=True)
emotions_groups.row(Button.E_ANGER.value, Button.E_FEAR.value)
emotions_groups.row(Button.E_SADNESS.value, Button.E_JOY.value)
emotions_groups.row(Button.B_TO_MAIN_MENU.value)

M_NL = '\n\n'
M_WS = ' '
M_COLON = ':'


async def move_to_state(message, state, markup, answer):
    await message.answer(answer, reply_markup=markup)
    dbworker.set_state(message.chat.id, state.value)


def get_hour(hours, delta, sign):
    return (24 + hours + delta * (1 if sign == '+' else -1)) % 24


def get_minutes(minutes):
    return '0' + str(minutes) if minutes < 10 else str(minutes)
