from bot import bot, datetime, mysqldb, data, send_report
import asyncio
import time
import aioschedule as schedule


async def send_ntfs():
    cur_time = datetime.datetime.utcnow().time()
    ntime = datetime.time(cur_time.hour, cur_time.minute, 0)
    ids = mysqldb.get_ntfs_list(ntime)
    if ids is not None:
        for chat_id in ids:
            await bot.send_message(chat_id['chat_key'], data['ntf'])
    await asyncio.sleep(0.1)


async def send_monthly_report():
    time_now = datetime.datetime.utcnow()
    if time_now.day == 1:
        ids = mysqldb.get_users_list()
        if ids is not None:
            for chat_id in ids:
                tz = mysqldb.get_timezone(chat_id['chat_key'])
                border_time = time_now - datetime.timedelta(days=1)
                border = datetime.datetime(border_time.year, border_time.month, 1)
                records = mysqldb.get_records(chat_id['chat_key'], border)
                if records is not None and len(records) > 0:
                    await send_report(chat_id['chat_key'], (border + datetime.timedelta(hours=tz)).date(),
                                          (time_now + datetime.timedelta(hours=tz)).date(), records, tz)
                    await bot.send_message(chat_id['chat_key'], data['m_report'])
    await asyncio.sleep(0.1)


schedule.every().minute.do(send_ntfs)
schedule.every().day.at("12:00").do(send_monthly_report)

loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(schedule.run_pending())
    time.sleep(0.1)
