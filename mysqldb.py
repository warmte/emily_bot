import config
import em_config
from config import logging

from config import database as db


# ------------------------------------
#             USER INFO
# ------------------------------------


def add_user(chat_id):
    try:
        db.execute('INSERT INTO `Users`(`chat_key`) VALUES (%s)', str(chat_id))
        return True
    except Exception as e:
        logging.error(str(chat_id) + ' ADD_USER ' + str(e))
        return False


def set_info(chat_id, value, field):
    request = 'UPDATE `Users` SET `' + field + '` = %s WHERE `chat_key` = %s'
    try:
        db.execute(request, (str(value), chat_id))
        return True
    except Exception as e:
        logging.error(str(chat_id) + ' SET_INFO ' + str(e))
        return False


def set_timezone(chat_id, value):
    return set_info(chat_id, value, 'timezone')


def set_ntfs(chat_id, value):
    return set_info(chat_id, value, 'ntfs')


def set_last_stat_time(chat_id, value):
    return set_info(chat_id, value, 'last_stat')


def get_info(chat_id):
    try:
        db.execute('SELECT * FROM `Users` WHERE `chat_key` = %s', chat_id)
        return db.fetchall()[0]
    except Exception as e:
        logging.error(str(chat_id) + ' GET_INFO ' + str(e))
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
        db.execute('UPDATE `Users` SET `ntfs`=NULL WHERE `chat_key` = %s', chat_id)
        return True
    except Exception as e:
        logging.error(str(chat_id) + ' REMOVE_NTFS ' + str(e))
        return False


def get_ntfs_list(time):
    try:
        db.execute(
            'SELECT `chat_key` from `Users` WHERE `ntfs`= %s', str(time))
        return db.fetchall()
    except Exception as e:
        logging.error(str(time) + ' GET_NTFS_LIST ' + str(e))
        return None


# ------------------------------------
#               RECORDS
# ------------------------------------

def add_record(chat_id, emotion, note):
    try:
        db.execute(
            'INSERT INTO `Records`(`chat_key`, `emotion`, `note`) VALUES (%s, %s, %s)',
            (str(chat_id), str(em_config.get(emotion)), config.encode(note)))
        return True
    except Exception as e:
        logging.error(str(chat_id) + ' ADD_RECORD ' + str(e))
        return False


def get_last_record_time(chat_id):
    try:
        db.execute('SELECT max(`timestamp`) from `Records` WHERE `chat_key` = %s', chat_id)
        return db.fetchall()[0]['max(`timestamp`)']
    except Exception as e:
        logging.error(str(chat_id) + ' GET_LAST_RECORD_TIME ' + str(e))
        return None


def get_records(chat_id, datetime):
    try:
        db.execute(
            'SELECT * FROM `Records` WHERE `chat_key` = %s AND `timestamp` >= %s ORDER BY `timestamp` DESC',
            (chat_id, str(datetime)))
        return db.fetchall()
    except Exception as e:
        logging.error(str(chat_id) + ' GET_RECORDS ' + str(e))
        return None


def delete_stat_by_chat_id(chat_id, datetime):
    try:
        db.execute('DELETE FROM `Records` WHERE `chat_key` = %s AND `timestamp`<= %s', (chat_id, str(datetime)))
        return True
    except Exception as e:
        logging.error(str(chat_id) + ' DELETE_STAT ' + str(e))
        return False
