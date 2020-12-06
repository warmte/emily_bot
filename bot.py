#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types

import data
import config
import dbworker
from datetime import datetime
from data import Button

bot = Bot(token=config.token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


# ------------------------------------
#               INTRO
# ------------------------------------

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    dbworker.set_state(message.chat.id, config.State.START.value)
    if message.from_user.username == 'warmte':  # TODO: remove when available for everybody
        await message.answer(data.M_WELCOME_MESSAGE, reply_markup=data.hello)


@dp.message_handler(lambda message: dbworker.get_current_state(message.chat.id) == config.State.START.value,
                    content_types=['text'])
async def send_text(message):
    dbworker.set_state(message.chat.id, config.State.WELCOME_PAGE.value)
    if message.text.lower() == Button.B_HELLO.value.lower():
        await message.answer(data.M_WELCOME_NOTIFICATIONS, reply_markup=data.yes_or_no)


# NOTIFICATIONS

@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.WELCOME_PAGE.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_NO.value.lower():
        await data.call_notifications_exit(message)
    elif message.text.lower() == Button.B_YES.value.lower():
        await data.call_notifications(message)


def get_hour(hours, delta, sign):
    return (24 + hours + delta * (1 if sign == '+' else -1)) % 24


def get_minutes(minutes):
    return '0' + str(minutes) if minutes < 10 else str(minutes)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE.value,
    content_types=['text'])
async def send_text(message):
    time = message.text.lower().replace(' ', '')

    if len(time) >= 5 and time[0:3] == 'utc' and (time[3] == '+' or time[3] == '-') and time[4:].isdigit() and 0 <= int(
            time[4:]) < 24:
        current_time = int(time[4:])
        dbworker.set_state(message.chat.id, config.State.SET_TIME_ZONE_SUCCESS.value)
        await message.answer(await data.call_set_time_zone_ask_time(
            str(get_hour(datetime.utcnow().hour, current_time, time[3])),
            get_minutes(datetime.utcnow().minute)),
                             reply_markup=data.yes_or_no)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await data.call_notifications_exit(message)
    else:
        await data.call_set_time_zone_fail(message)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_NO.value.lower():
        await data.call_set_time_zone_fail(message)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await data.call_notifications_exit(message)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_NOTIFICATIONS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await data.call_notifications_exit(message)
        return
    elif message.text.lower() == Button.B_BACK.value.lower():
        await data.call_notifications(message)
        return

    try:
        hours, minutes = message.text.lower().replace(' ', '').split(':')
    except:
        await message.answer(data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=data.back_or_to_main_menu)
        return

    if hours.isdigit() and minutes.isdigit() and 0 <= int(hours) < 24 and 0 <= int(minutes) < 60:
        # TODO: add notifications to db
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        await message.answer(data.M_NOTIFICATIONS_DONE + hours + ':' + minutes + data.M_SEP + data.M_MAIN_MENU,
                             reply_markup=data.main_menu)
    else:
        await message.answer(data.M_NOTIFICATIONS_TIME_FORMAT, reply_markup=data.back_or_to_main_menu)


# ------------------------------------
#             MAIN MENU
# ------------------------------------


@dp.message_handler(
    commands=['menu'], content_types=['text'])
async def send_text(message):
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
    await message.answer(data.M_MAIN_MENU)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.MAIN_MENU.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_MENU_MOOD.value.lower():
        dbworker.set_state(message.chat.id, config.State.SET_MOOD.value)
        await message.answer(data.M_MOOD_START, reply_markup=data.mood_groups)
    elif message.text.lower() == Button.B_MENU_ABOUT.value.lower():
        await message.answer(data.M_ABOUT, reply_markup=data.main_menu)
    elif message.text.lower() == Button.B_MENU_SETTINGS.value.lower():
        dbworker.set_state(message.chat.id, config.State.SETTINGS.value)
        await message.answer(data.M_SETTINGS, reply_markup=data.settings)
    elif message.text.lower() == Button.B_MENU_STAT.value.lower():
        e = True
        # TODO create stat panel


# SETTINGS


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SETTINGS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_SETTINGS_TIME_ZONE.value.lower():
        await data.call_notifications(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value.lower():
        await data.call_set_notifications_time(message)
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATION_REMOVE.value.lower():
        dbworker.set_state(message.chat.id, config.State.REMOVE_NOTIFICATIONS.value)
        await message.answer(data.M_NOTIFICATIONS_REMOVE, reply_markup=data.main_menu)
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
        await message.answer(data.M_MAIN_MENU, reply_markup=data.main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.REMOVE_NOTIFICATIONS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await message.answer(message.chat.id, data.M_NOTIFICATIONS_CANCELLED, reply_markup=data.main_menu)
        # TODO remove notifications from db
    elif message.text.lower() == Button.B_NO.value.lower():
        await message.answer(message.chat.id, data.M_NOTIFICATIONS_NOT_CANCELLED, reply_markup=data.main_menu)


# MOOD

@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_MOOD.value,
    content_types=['text'])
async def send_text(message):
    group = message.text.lower()
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await data.call_mood_exit(message)
    elif group.lower() == Button.E_ANGER.value.lower():
        await data.get_emotions_by_group(message, data.mood_anger)
    elif group.lower() == Button.E_FEAR.value.lower():
        await data.get_emotions_by_group(message, data.mood_fear)
    elif group.lower() == Button.E_SADNESS.value.lower():
        await data.get_emotions_by_group(message, data.mood_sadness)
    elif group.lower() == Button.E_JOY.value.lower():
        await data.get_emotions_by_group(message, data.mood_joy)
    else:
        await message.answer(message.chat.id, data.M_MOOD_UNKNOWN_GROUP, reply_markup=data.to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await data.call_mood_exit(message)
    elif message.text.lower() == Button.B_BACK.value.lower():
        dbworker.set_state(message.chat.id, config.State.SET_MOOD.value)
        await message.answer(message.chat.id, data.M_MOOD_START, reply_markup=data.mood_groups)
    elif len(message.text) >= 2:
        emotion = message.text[0].upper() + message.text[1:].lower()
        if emotion in data.mood_anger or emotion in data.mood_fear or emotion in data.mood_sadness or emotion in data.mood_joy:
            dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
            await message.answer(message.chat.id, data.M_MOOD_EMOTION_GOT, reply_markup=data.main_menu)
        else:
            await message.answer(message.chat.id, data.M_MOOD_UNKNOWN_EMOTION,
                                 reply_markup=data.back_or_to_main_menu)
    else:
        await message.answer(message.chat.id, data.M_MOOD_UNKNOWN_EMOTION, reply_markup=data.back_or_to_main_menu)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
