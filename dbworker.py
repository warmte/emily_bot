from vedis import Vedis
import config


def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return config.State.START.value


def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            # TODO: do something
            return False


def get_current_emotion_state(user_id):
    with Vedis(config.db_records) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return config.State.START.value


def set_emotion_state(user_id, value):
    with Vedis(config.db_records) as db:
        try:
            db[user_id] = value
            return True
        except:
            # TODO: do something
            return False
