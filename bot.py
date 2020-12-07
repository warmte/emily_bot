#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types

import util
import json
import config
import dbworker
from datetime import datetime
from util import Button

bot = Bot(token=config.token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
data = json.load(open('data.json', 'r', encoding="utf-8"))


# ------------------------------------
#               INTRO
# ------------------------------------

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    if message.from_user.username == 'warmte':  # TODO: remove when available for everybody
        await util.move_to_state(message, config.State.WELCOME_PAGE, util.hello, data['about'][0])


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.WELCOME_PAGE.value,
    content_types=['text'])
async def send_text(message):
    if util.Button.B_HELLO.value in message.text:
        answer = ''
        for i in range(2, 6):
            answer += data['about'][i]
        await message.answer(answer)
        await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['about'][7])


# NOTIFICATIONS

async def handle_back_buttons(message, back_state, back_markup):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['exit'])
        return True
    elif message.text.lower() == Button.B_BACK.value.lower():
        await util.move_to_state(message, back_state, back_markup, data['back'])
        return True
    return False


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.SETTINGS, util.settings):
        return

    time = message.text.lower().replace(' ', '')

    if len(time) >= 5 and time[0:3] == 'utc' and (time[3] == '+' or time[3] == '-') and time[4:].isdigit() and 0 <= int(
            time[4:]) < 24:
        current_time = int(time[4:])
        answer = data['timezone']['check_time_st'] + str(
            util.get_hour(datetime.utcnow().hour, current_time, time[3])) + util.M_COLON + util.get_minutes(
            datetime.utcnow().minute) + data['timezone']['check_time_end']
        await util.move_to_state(message, config.State.SET_TIME_ZONE_SUCCESS, util.yes_or_no, answer)
    else:
        await message.answer(data['timezone']['fail'], reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings, data['timezone']['ready'])
    elif message.text.lower() == Button.B_NO.value.lower():
        await util.move_to_state(message, config.State.SET_TIME_ZONE, util.back_or_to_main_menu,
                                 data['timezone']['fail'])
    elif message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['exit'])


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_NOTIFICATIONS.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.SETTINGS, util.settings):
        return

    try:
        hours, minutes = message.text.lower().replace(' ', '').split(':')
    except:
        await message.answer(data['ntfs_time']['format'], reply_markup=util.back_or_to_main_menu)
        return

    if hours.isdigit() and minutes.isdigit() and 0 <= int(hours) < 24 and 0 <= int(minutes) < 60:
        # TODO: add notifications to db
        answer = data['ntfs_time']['ready'] + hours + util.M_COLON + minutes
        await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, answer)
    else:
        await message.answer(data['ntfs_time']['format'], reply_markup=util.back_or_to_main_menu)


# ------------------------------------
#             MAIN MENU
# ------------------------------------


@dp.message_handler(commands=['menu'], content_types=['text'])
async def send_text(message):
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
    await message.answer(data['menu'])


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.MAIN_MENU.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_MENU_EMOTIONS.value.lower():
        await util.move_to_state(message, config.State.SET_EMOTIONS, util.emotions_groups,
                                 data['emotions']['info'] + util.M_NL + data['emotions']['pick_group'])
    elif message.text.lower() == Button.B_MENU_ABOUT.value.lower():
        answer = data['about'][1]
        for i in range(3, 7):
            answer += data['about'][i]
        await message.answer(answer, reply_markup=util.main_menu)
    elif message.text.lower() == Button.B_MENU_SETTINGS.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings, data['settings']['info'])
    elif message.text.lower() == Button.B_MENU_STAT.value.lower():
        e = True
        # TODO create stat panel


# SETTINGS


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SETTINGS.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.SETTINGS, util.settings):
        return

    if message.text.lower() == Button.B_SETTINGS_TIME_ZONE.value.lower():
        await util.move_to_state(message, config.State.SET_TIME_ZONE, util.back_or_to_main_menu,
                                 data['timezone']['set'])
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value.lower():
        await util.move_to_state(message, config.State.SET_NOTIFICATIONS, util.back_or_to_main_menu,
                                 data['ntfs_time']['format'])
    elif message.text.lower() == Button.B_SETTINGS_NOTIFICATION_REMOVE.value.lower():
        await util.move_to_state(message, config.State.REMOVE_NOTIFICATIONS, util.yes_or_no,
                                 data['ntfs_time']['remove'])


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.REMOVE_NOTIFICATIONS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings,
                                 data['ntfs_time']['remove_done'])
        # TODO remove notifications from db
    elif message.text.lower() == Button.B_NO.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings,
                                 data['ntfs_time']['remove_cancelled'])


# EMOTIONS

async def set_emotions_list(message, emotions_list, state):
    dbworker.set_state(message.chat.id, state)
    await message.answer(data['emotions']['pick_emotion'] + util.M_NL)
    await message.answer(''.join(str('·  ' + e + '\n') for e in emotions_list), reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTIONS.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.MAIN_MENU, util.main_menu):
        return

    group = message.text.lower()
    if group.lower() == Button.E_ANGER.value.lower():
        await set_emotions_list(message, data['emotions']['anger'], config.State.SET_EMOTION_ANGER.value)
    elif group.lower() == Button.E_FEAR.value.lower():
        await set_emotions_list(message, data['emotions']['fear'], config.State.SET_EMOTION_FEAR.value)
    elif group.lower() == Button.E_SADNESS.value.lower():
        await set_emotions_list(message, data['emotions']['sadness'], config.State.SET_EMOTION_SADNESS.value)
    elif group.lower() == Button.E_JOY.value.lower():
        await set_emotions_list(message, data['emotions']['joy'], config.State.SET_EMOTION_JOY.value)
    else:
        await message.answer(data['emotions']['unknown_group'], reply_markup=util.emotions_groups)


async def handle_emotion(message, group):
    if await handle_back_buttons(message, config.State.SET_EMOTIONS, util.emotions_groups):
        return

    if len(message.text) >= 2:
        emotion = message.text[0].upper() + message.text[1:].lower()
        if emotion in data['emotions'][group]:
            # TODO add emotion to db
            await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['emotions']['ready'])
        else:
            await message.answer(data['emotions']['unknown_emotion'], reply_markup=util.back_or_to_main_menu)
    else:
        await message.answer(data['emotions']['unknown_emotion'], reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION_ANGER.value,
    content_types=['text'])
async def send_text(message):
    await handle_emotion(message, 'anger')


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION_FEAR.value,
    content_types=['text'])
async def send_text(message):
    await handle_emotion(message, 'fear')


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION_SADNESS.value,
    content_types=['text'])
async def send_text(message):
    await handle_emotion(message, 'sadness')


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION_JOY.value,
    content_types=['text'])
async def send_text(message):
    await handle_emotion(message, 'joy')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
