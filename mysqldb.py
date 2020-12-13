import config
import em_config

from config import database as db


# ------------------------------------
#             USER INFO
# ------------------------------------


def add_user(chat_id):
    try:
        db.execute('INSERT INTO `Users`(`chat_key`) VALUES (\'' + str(config.count_key(chat_id)) + '\')')
        return True
    except:
        return False


def set_info(chat_id, value, field):
    try:
        db.execute(
            'UPDATE `Users` SET `' + field + '` = \'' + str(value) + '\' WHERE chat_key = \'' + config.count_key(
                chat_id) + '\'')
        return True
    except:
        return False


def set_timezone(chat_id, value):
    set_info(chat_id, value, 'timezone')


def set_ntfs(chat_id, value):
    set_info(chat_id, value, 'ntfs')


def set_last_emotion_time(chat_id, value):
    set_info(chat_id, value, 'last_emotion')


def set_last_stat_time(chat_id, value):
    set_info(chat_id, value, 'last_stat')


def get_info(chat_id):
    try:
        db.execute('SELECT * FROM `Users` WHERE `chat_key` = \'' + config.count_key(chat_id) + '\'')
        return db.fetchall()[0]
    except:
        return None


def get_timezone(chat_id):
    info = get_info(chat_id)
    return info['timezone'] if info is not None else None


def get_ntfs(chat_id):
    info = get_info(chat_id)
    return info['ntfs'] if info is not None else None


def get_last_stat_time(chat_id):
    info = get_info(chat_id)
    return info['last_stat'] if info is not None else None


def remove_ntfs(chat_id):
    try:
        db.execute(
            'UPDATE `Users` SET `ntfs`=NULL WHERE chat_key = \'' + config.count_key(chat_id) + '\'')
        return True
    except:
        return False


# ------------------------------------
#               RECORDS
# ------------------------------------

def add_record(chat_id, emotion, note):
    # try:
        db.execute(
            'INSERT INTO `Records`(`chat_key`, `emotion`, `note`) VALUES (\'' + str(
                config.count_key(chat_id)) + '\', ' + str(em_config.get(emotion)) + ', \'' + note + '\')')
        return True
    # except:
    #     return False


def get_last_record_time(chat_id):
    # try:
        db.execute('SELECT max(`timestamp`) from `Records`')
        return db.fetchall()[0]['max(`timestamp`)']
    # except:
    #     return None


def get_records(chat_id, datetime):
    # try:
        db.execute('SELECT * FROM `Records` WHERE `timestamp`>=\'' + str(datetime) + '\' ORDER BY `timestamp` DESC')
        return db.fetchall()
    # except:
    #     return None


def delete_stat_by_chat_id(chat_id, datetime):
    try:
        db.execute('DELETE FROM `Records` WHERE `timestamp`<=\'' + str(datetime) + '\'')
        return True
    except:
        return False

