#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types

import util
import json
import config
import em_config
import dbworker
import mysqldb
import datetime
import tempfile
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
        mysqldb.add_user(message.chat.id)
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


async def handle_back_buttons(message, back_state, back_markup):
    if message.text.lower() == Button.B_TO_MAIN_MENU.value.lower():
        await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['exit'])
        return True
    elif message.text.lower() == Button.B_BACK.value.lower():
        await util.move_to_state(message, back_state, back_markup, data['back'])
        return True
    return False


# ------------------------------------
#             MAIN MENU
# ------------------------------------


@dp.message_handler(commands=['menu'], content_types=['text'])
async def send_text(message):
    if dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS:
        mysqldb.set_timezone(message.chat.id, util.S_TIME)
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
    await message.answer(data['menu'], reply_markup=util.main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.MAIN_MENU.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_MENU_EMOTIONS.value.lower():
        last_record_time = mysqldb.get_last_record_time(message.chat.id)
        if last_record_time is not None and (datetime.datetime.utcnow() - last_record_time) < datetime.timedelta(
                seconds=3600):
            await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['emotions']['time_limit'])
            return
        await util.move_to_state(message, config.State.SET_EMOTIONS, util.emotions_groups,
                                 data['emotions']['info'] + util.M_NL + data['emotions']['pick_group'])
    elif message.text.lower() == Button.B_MENU_ABOUT.value.lower():
        answer = data['about'][1]
        for i in range(3, 7):
            answer += data['about'][i]
        await message.answer(answer, reply_markup=util.main_menu, parse_mode='Markdown')
    elif message.text.lower() == Button.B_MENU_SETTINGS.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings, data['settings']['info'])
    elif message.text.lower() == Button.B_MENU_STAT.value.lower():
        td = datetime.timedelta(hours=mysqldb.get_timezone(message.chat.id))
        last_record_time = mysqldb.get_last_stat_time(message.chat.id)
        if last_record_time is not None and (
                (datetime.datetime.utcnow() + td).date() >= (last_record_time + td).date()):
            await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['stat']['time_limit'])
            return
        await util.move_to_state(message, config.State.GET_STAT, util.stat_menu, data['stat']['info'])


# --- SETTINGS ---


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


# --- TIMEZONE ---


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
            util.get_hour(datetime.datetime.utcnow().hour, current_time, time[3])) + util.M_COLON + util.get_zero_d(
            datetime.datetime.utcnow().minute) + data['timezone']['check_time_end']
        if mysqldb.set_timezone(message.chat.id, current_time):
            await util.move_to_state(message, config.State.SET_TIME_ZONE_SUCCESS, util.yes_or_no, answer)
        else:
            await message.answer(data['error'], reply_markup=util.back_or_to_main_menu, parse_mode='Markdown')
    else:
        await message.answer(data['timezone']['fail'], reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_TIME_ZONE_SUCCESS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings, data['timezone']['ready'])
    elif message.text.lower() == Button.B_NO.value.lower():
        mysqldb.set_timezone(message.chat.id, util.S_TIME)
        await util.move_to_state(message, config.State.SET_TIME_ZONE, util.back_or_to_main_menu,
                                 data['timezone']['fail'])


# --- NOTIFICATIONS ---

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
        s_hours = (int(hours) - mysqldb.get_timezone(message.chat.id) + 24) % 24
        if mysqldb.set_ntfs(message.chat.id, datetime.time(s_hours, int(minutes))):
            d = '0' if len(minutes) == 1 else ''
            answer = data['ntfs_time']['ready'] + hours + util.M_COLON + d + minutes
            await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, answer)
        else:
            await message.answer(data['error'], reply_markup=util.back_or_to_main_menu, parse_mode='Markdown')
    else:
        await message.answer(data['ntfs_time']['format'], reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.REMOVE_NOTIFICATIONS.value,
    content_types=['text'])
async def send_text(message):
    if message.text.lower() == Button.B_YES.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings,
                                 data['ntfs_time']['remove_done'])
        mysqldb.remove_ntfs(message.chat.id)
    elif message.text.lower() == Button.B_NO.value.lower():
        await util.move_to_state(message, config.State.SETTINGS, util.settings,
                                 data['ntfs_time']['remove_cancelled'])


# --- EMOTIONS ---

async def set_emotions_list(message, e_state):
    dbworker.set_state(message.chat.id, config.State.SET_CURRENT_EMOTION.value)
    dbworker.set_emotion_state(message.chat.id, e_state.value)
    await message.answer(data['emotions']['pick_emotion'] + util.M_NL)
    list = ''
    for i in range(0, len(data['emotions'][e_state.value])):
        list += '·  ' + data['emotions'][e_state.value][i] + ' [' + str(i + 1) + '] ' + '\n'
    await message.answer(list, reply_markup=util.back_or_to_main_menu)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTIONS.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.MAIN_MENU, util.main_menu):
        return

    group = message.text.lower()
    if group.lower() == Button.E_ANGER.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_ANGER)
    elif group.lower() == Button.E_FEAR.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_FEAR)
    elif group.lower() == Button.E_SADNESS.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_SADNESS)
    elif group.lower() == Button.E_JOY.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_JOY)
    elif group.lower() == Button.E_SHAME.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_SHAME)
    elif group.lower() == Button.E_SURPRISE.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_SURPRISE)
    elif group.lower() == Button.E_INTEREST.value.lower():
        await set_emotions_list(message, config.State.SET_EMOTION_INTEREST)
    else:
        await message.answer(data['emotions']['unknown_group'], reply_markup=util.emotions_groups)


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_CURRENT_EMOTION.value,
    content_types=['text'])
async def send_text(message):
    if await handle_back_buttons(message, config.State.SET_EMOTIONS, util.emotions_groups):
        return
    group = dbworker.get_current_emotion_state(message.chat.id)
    emotion_state = dbworker.get_current_emotion_state(message.chat.id)

    if message.text.isnumeric() and 0 < int(message.text) <= len(data['emotions'][emotion_state]):
        emotion = data['emotions'][emotion_state][int(message.text) - 1]
        dbworker.set_emotion_state(message.chat.id, em_config.get(emotion))
        await util.move_to_state(message, config.State.SET_EMOTION_NOTE, util.dont_want, data['emotions']['note'])
    elif len(message.text) >= 2:
        emotion = message.text[0].upper() + message.text[1:].lower()
        if emotion in data['emotions'][group]:
            dbworker.set_emotion_state(message.chat.id, em_config.get(emotion))
            await util.move_to_state(message, config.State.SET_EMOTION_NOTE, util.dont_want, data['emotions']['note'])
        else:
            await message.answer(data['emotions']['unknown_emotion'], reply_markup=util.back_or_to_main_menu,
                                 parse_mode='Markdown')
    else:
        await message.answer(data['emotions']['unknown_emotion'], reply_markup=util.back_or_to_main_menu,
                             parse_mode='Markdown')


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.SET_EMOTION_NOTE.value,
    content_types=['text'])
async def send_text(message):
    note = message.text
    if note == Button.B_DONT_WANT.value:
        note = ''
    if len(note) > 252:
        await message.answer(data['emotions']['note_too_big'] + str(len(note)) + data['emotions']['note_too_big_end'],
                             reply_markup=util.dont_want)
    else:
        emotion = em_config.match(int(dbworker.get_current_emotion_state(message.chat.id)))
        if mysqldb.add_record(message.chat.id, emotion, note):
            await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['emotions']['ready'])
        else:
            await util.move_to_state_md(message, config.State.MAIN_MENU, util.main_menu, data['error'])


# --- STAT ---


@dp.message_handler(
    lambda message: dbworker.get_current_state(message.chat.id) == config.State.GET_STAT.value,
    content_types=['text'])
async def send_text(message):
    time_now = datetime.datetime.utcnow()
    tz = mysqldb.get_timezone(message.chat.id)
    if message.text.lower() == Button.B_STAT_WEEK.value.lower():
        await message.answer(data['stat']['wait'])
        border_time = time_now - datetime.timedelta(days=6)
        border = datetime.datetime(border_time.year, border_time.month, border_time.day)
        await send_report(message, (border + datetime.timedelta(hours=tz)).date(),
                          (time_now + datetime.timedelta(hours=tz)).date(),
                          mysqldb.get_records(message.chat.id, border), tz)
    elif message.text.lower() == Button.B_STAT_MONTH.value.lower():
        await message.answer(data['stat']['wait'])
        border_time = datetime.datetime.utcnow()
        border = datetime.datetime(border_time.year, border_time.month, 1)
        await send_report(message, (border + datetime.timedelta(hours=tz)).date(),
                          (time_now + datetime.timedelta(hours=tz)).date(),
                          mysqldb.get_records(message.chat.id, border), tz)

    await util.move_to_state(message, config.State.MAIN_MENU, util.main_menu, data['menu'])


async def send_report(message, start_date, end_date, records, tz):
    with tempfile.TemporaryDirectory() as directory:
        filename = data['report']['name'] + util.reformat_date(start_date) + '-' + util.reformat_date(end_date) + '.pdf'
        path = directory + r'\report'
        title = data['report']['title'][0] + util.reformat_date(start_date) + data['report']['title'][
            1] + util.reformat_date(
            end_date)
        util.generate_pdf(title, data['report']['title'][2], records, tz, path, data['report']['months'])
        f = types.InputFile(path + '.pdf', filename)
        mysqldb.set_last_stat_time(message.chat.id, datetime.datetime.utcnow())
        await bot.send_document(message.chat.id, f)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
