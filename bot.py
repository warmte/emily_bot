import data
import config
import dbworker
from datetime import datetime, timezone

from data import bot
from data import Button


# ------------------------------------
#               INTRO
# ------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    dbworker.set_state(message.chat.id, config.State.START.value)
    if message.from_user.username == 'warmte':  # TODO: remove when available for everybody
        bot.send_message(message.chat.id, data.M_WELCOME_MESSAGE, reply_markup=data.hello)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.START.value,
                     content_types=['text'])
def send_text(message):
    dbworker.set_state(message.chat.id, config.State.WELCOME_PAGE.value)
    if message.text.lower() == Button.B_HELLO.value.lower():
        bot.send_message(message.chat.id, data.M_WELCOME_NOTIFICATIONS, reply_markup=data.yes_or_no)


# NOTIFICATIONS

@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.WELCOME_PAGE.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_NO.value.lower():
        data.call_notifications_exit(message)
    elif message.text.lower() == Button.B_YES.value.lower():
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
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        data.call_notifications_exit(message)
    else:
        data.call_set_time_zone_fail(message)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_NO.value.lower():
        data.call_set_time_zone_fail(message)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        data.call_notifications_exit(message)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_NOTIFICATIONS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        data.call_notifications_exit(message)
        return

    try:
        hours, minutes = message.text.lower().split(':')
    except:
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=data.to_main_menu)
        return

    if hours.isdigit() and minutes.isdigit() and 0 <= int(hours) < 24 and 0 <= int(minutes) < 60:
        # TODO: add notifications to db
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        bot.send_message(message.chat.id,
                         data.M_NOTIFICATIONS_DONE + hours + ':' + minutes + data.M_SEP + data.M_MAIN_MENU,
                         reply_markup=data.main_menu)
    else:
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=data.to_main_menu)


# ------------------------------------
#             MAIN MENU
# ------------------------------------


@bot.message_handler(
    commands=['menu'], content_types=['text'])
def send_text(message):
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
    bot.send_message(message.chat.id, data.M_MAIN_MENU)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.MAIN_MENU.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_MENU_MOOD.value.lower():
        dbworker.set_state(message.chat.id, config.State.SET_MOOD.value)
        bot.send_message(message.chat.id, data.M_MOOD_START, reply_markup=data.mood_groups)
    elif message.text.lower() == Button.B_MENU_ABOUT.value.lower():
        bot.send_message(message.chat.id, data.M_ABOUT, reply_markup=data.main_menu)
    elif message.text.lower() == Button.B_MENU_SETTINGS.value.lower():
        dbworker.set_state(message.chat.id, config.State.SETTINGS.value)
        bot.send_message(message.chat.id, data.M_SETTINGS, reply_markup=data.settings)
    elif message.text.lower() == Button.B_MENU_STAT.value.lower():
        e = True
        # TODO create stat panel


# SETTINGS


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SETTINGS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_SETTINGS_TIME_ZONE.value.lower():
        data.call_notifications(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value.lower():
        data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATION_REMOVE.value.lower():
        dbworker.set_state(message.chat.id, config.State.REMOVE_NOTIFICATIONS.value)
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_REMOVE, reply_markup=data.main_menu)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        bot.send_message(message.chat.id, data.M_MAIN_MENU, reply_markup=data.main_menu)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.REMOVE_NOTIFICATIONS.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_CANCELLED, reply_markup=data.main_menu)
        # TODO remove notifications from db
    elif message.text.lower() == Button.B_NO.value.lower():
        bot.send_message(message.chat.id, data.M_NOTIFICATIONS_NOT_CANCELLED, reply_markup=data.main_menu)


# MOOD

@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_MOOD.value,
    content_types=['text'])
def send_text(message):
    group = message.text.lower()
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        data.call_mood_exit(message)
    elif group.lower() == Button.E_ANGER.value.lower():
        data.get_emotions_by_group(message, data.mood_anger)
    elif group.lower() == Button.E_FEAR.value.lower():
        data.get_emotions_by_group(message, data.mood_fear)
    elif group.lower() == Button.E_SADNESS.value.lower():
        data.get_emotions_by_group(message, data.mood_sadness)
    elif group.lower() == Button.E_JOY.value.lower():
        data.get_emotions_by_group(message, data.mood_joy)
    else:
        bot.send_message(message.chat.id, data.M_MOOD_UNKNOWN_GROUP)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION.value,
    content_types=['text'])
def send_text(message):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        data.call_mood_exit(message)
    elif message.text.lower() == Button.B_BACK.value.lower():
        dbworker.set_state(message.chat.id, config.State.SET_MOOD.value)
        bot.send_message(message.chat.id, data.M_MOOD_START, reply_markup=data.mood_groups)
    elif len(message.text) >= 2:
        emotion = message.text[0].upper() + message.text[1:].lower()
        if emotion in data.mood_anger or emotion in data.mood_fear or emotion in data.mood_sadness or emotion in data.mood_joy:
            dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
            bot.send_message(message.chat.id, data.M_MOOD_EMOTION_GOT, reply_markup=data.main_menu)
        else:
            bot.send_message(message.chat.id, data.M_MOOD_UNKNOWN_EMOTION)
    else:
        bot.send_message(message.chat.id, data.M_MOOD_UNKNOWN_EMOTION)


bot.polling()
