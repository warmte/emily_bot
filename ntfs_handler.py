from bot import bot, datetime, mysqldb, data
import asyncio
import time
import aioschedule as schedule

DELTA = datetime.timedelta(minutes=1)


async def send_ntfs():
    cur_time = datetime.datetime.utcnow().time()
    ntime = datetime.time(cur_time.hour, cur_time.minute, 0)
    ids = mysqldb.get_ntfs_list(ntime)
    if ids is not None:
        for chat_id in ids:
            await bot.send_message(chat_id['chat_key'], data['ntf'])
    await asyncio.sleep(0.1)


schedule.every().minute.do(send_ntfs)

loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(schedule.run_pending())
    time.sleep(0.1)
