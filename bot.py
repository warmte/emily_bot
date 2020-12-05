import data
import config
import dbworker
from datetime import datetime, timezone

from data import bot
from data import Button


# START

@bot.message_handler(commands=['start'])
def start_message(message):
    dbworker.set_state(message.chat.id, config.State.START.value)
    if message.from_user.username == 'warmte':  # TODO: remove when available for everybody
        bot.send_message(message.chat.id, data.M_WELCOME_MESSAGE, reply_markup=data.hello)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.START.value,
                     content_types=['text'])
def send_text(message):
    dbworker.set_state(message.chat.id, config.State.WELCOME_PAGE.value)
    if message.text.lower() == Button.B_HELLO.lower():
        bot.send_message(message.chat.id, data.M_WELCOME_NOTIFICATIONS, reply_markup=data.yes_or_no)


# NOTIFICATIONS

@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.WELCOME_PAGE.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_NO.lower():
        data.call_notifications_exit(message)
    elif message.text.lower() == Button.B_YES.lower():
        data.call_notifications(message)


def get_hour(hours, delta, sign):
    return (24 + hours + delta * (1 if sign == '+' else -1)) % 24


def get_minutes(minutes):
    return '0' + str(minutes) if minutes < 10 else str(minutes)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE.value,
    content_types=['text'])
def send_text(message):
    time = message.text.lower()

    if len(time) >= 5 and time[0:3] == 'utc' and (time[3] == '+' or time[3] == '-') and time[4:].isdigit() and 0 <= int(
            time[4:]) < 24:
        current_time = int(time[4:])
        dbworker.set_state(message.chat.id, config.State.SET_TIME_ZONE_SUCCESS.value)
        bot.send_message(message.chat.id,
                         data.call_set_time_zone_ask_time(str(get_hour(datetime.utcnow().hour, current_time, time[3])),
                                                          get_minutes(datetime.utcnow().minute)),
                         reply_markup=data.yes_or_no)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.lower():
        data.call_notifications_exit(message)
    else:
        data.call_set_time_zone_fail(message)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_YES.lower():
        data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_NO.lower():
        data.call_set_time_zone_fail(message)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.lower():
        data.call_notifications_exit(message)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_NOTIFICATIONS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_TO_MAIN_MENU.lower():
        data.call_notifications_exit(message)
        return

    try:
        hours, minutes = message.text.lower().split(':')
    except:
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=exit)
        return

    if hours.isdigit() and minutes.isdigit() and 0 <= int(hours) < 24 and 0 <= int(minutes) < 60:
        # TODO: где-то сохранить
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        bot.send_message(message.chat.id,
                         data.M_NOTIFICATIONS_DONE + hours + ':' + minutes + '.\n\n' + data.M_MAIN_MENU,
                         reply_markup=data.main_menu)
    else:
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=exit)


# MAIN MENU


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.MAIN_MENU.value,
    content_types=['text'], commands='menu')
def send_text(message):
    if message.text.lower() == Button.B_MENU_MOOD.lower():
        e = True
        # TODO
    elif message.text.lower == Button.B_MENU_ABOUT.lower():
        e = True
        # TODO
    elif message.text.lower == Button.B_MENU_SETTINGS.lower():
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        bot.send_message(message.chat.id, data.M_SETTINGS, reply_markup=data.settings)
        e = True
    elif message.text.lower == Button.B_MENU_STAT.lower():
        e = True
        # TODO


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SETTINGS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_SETTINGS_TIME_ZONE.lower():
        data.call_notifications(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATIONS_CHANGE:
        data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATION_REMOVE:
        dbworker.set_state(message.chat.id, config.State.REMOVE_NOTIFICATIONS.value)
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_REMOVE, reply_markup=data.main_menu)
    elif message.text.lower() == Button.B_TO_MAIN_MENU:
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        bot.send_message(message.chat.id, data.M_MAIN_MENU, reply_markup=data.main_menu)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.REMOVE_NOTIFICATIONS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_YES.lower():
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_CANCELLED, reply_markup=data.main_menu)
        # TODO
    elif message.text.lower() == Button.B_NO.lower():
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_NOT_CANCELLED, reply_markup=data.main_menu)


bot.polling()
