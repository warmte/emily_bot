import telebot
import dbworker
import config

bot = telebot.TeleBot(config.token)


class Button(config.Enum):
    B_HELLO = 'Привет, Ванда'
    B_YES = 'Да'
    B_NO = 'Нет'
    B_TO_MAIN_MENU = 'В главное меню'

    B_MENU_MOOD = 'Отметить настроение'
    B_MENU_ABOUT = 'Обо мне'
    B_MENU_STAT = 'Статистика'
    B_MENU_SETTINGS = 'Настройки'

    B_SETTINGS_TIME_ZONE = 'Изменить часовой пояс'
    B_SETTINGS_NOTIFICATIONS_CHANGE = 'Изменить время напоминаний'
    B_SETTINGS_NOTIFICATION_REMOVE = 'Отменить напоминания'


hello = telebot.types.ReplyKeyboardMarkup(True, True)
hello.row(Button.B_HELLO)

yes_or_no = telebot.types.ReplyKeyboardMarkup(True, True)
yes_or_no.row(Button.B_YES, Button.B_NO)

to_main_menu = telebot.types.ReplyKeyboardMarkup(True, True)
to_main_menu.row(Button.B_TO_MAIN_MENU)

main_menu = telebot.types.ReplyKeyboardMarkup(True, True)
main_menu.row(Button.B_MENU_MOOD, Button.B_MENU_ABOUT)
main_menu.row(Button.B_MENU_STAT, Button.B_MENU_SETTINGS)

settings = telebot.types.ReplyKeyboardMarkup(True, True)
settings.row(Button.B_SETTINGS_TIME_ZONE)
settings.row(Button.B_SETTINGS_NOTIFICATIONS_CHANGE)
settings.row(Button.B_SETTINGS_NOTIFICATION_REMOVE)
settings.row(Button.B_TO_MAIN_MENU)

M_WELCOME_MESSAGE = 'Привет! Меня зовут Ванда и я помогу тебе следить за своим настроением.'
M_WELCOME_NOTIFICATIONS = 'Ты хочешь получать напоминания? Я буду писать тебе ежедневно в выбранное время, ' \
                          'чтобы помочь не забыть отметить своё настроение.'

M_NOTIFICATIONS_TIME_QUESTION = 'Отлично! Скажи, пожалуйста, во сколько ты хочешь получать напоминание? '
M_NOTIFICATIONS_TIME_FORMAT = 'Напиши время в формате \"h:mm или hh:mm\", как, например, 7:00 или 14:00.'
M_NOTIFICATIONS_DONE = 'Спасибо, напоминания будут приходить ежедневно в '
M_NOTIFICATIONS_REMOVE = 'Ты хочешь отменить напоминания? Я больше не буду ежедневно тебе писать, ' \
                         'но ты всё ещё будешь иметь возможность отметить своё настроение из главного меню.'
M_NOTIFICATIONS_CANCELLED = 'Ежедневные напоминания отменены'
M_NOTIFICATIONS_NOT_CANCELLED = 'Ежедневные напоминания не были отменены'

M_MAIN_MENU = 'Добро пожаловать в главное меню.'
M_SETTINGS = 'Здесь ты можешь настроить свой часовой пояс и напоминания.'


def call_notifications(message):
    bot.send_message(message.chat.id, 'Хорошо! Укажи свой часовой пояс, пожалуйста, в формате UTC+_. '
                                      'Например, в Москве или Санкт-Петербурге время UTC+3')
    dbworker.set_state(message.chat.id, config.State.SET_TIME_ZONE.value)


def call_notifications_exit(message):
    bot.send_message(message.chat.id,
                     'Хорошо! Ты всегда можешь настроить напоминания в пункте "Настройки" главного меню. \n\n ',
                     reply_markup=main_menu)
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)


def call_set_time_zone_fail(message):
    bot.send_message(message.chat.id,
                     'Что-то пошло не так! Пожалуйста, проверь, что отправленное тобой время имеет '
                     'формат \"UTC+_\". Узнать свой часовой пояс можно, например, '
                     'на сайте time.is',
                     reply_markup=to_main_menu)


def call_set_time_zone_ask_time(hours, minutes):
    return 'Сейчас у тебя ' + hours + ':' + minutes + ', так?'


def call_set_notifications_time(message):
    dbworker.set_state(message.chat.id, config.State.SET_NOTIFICATIONS.value)
    bot.send_message(message.chat.id,
                     M_NOTIFICATIONS_TIME_QUESTION + M_NOTIFICATIONS_TIME_FORMAT)
