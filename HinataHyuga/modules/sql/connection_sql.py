import threading
import time
from typing import Union

from Hinatahyuga.modules.sql import nobita, client 




CHAT_ACCESS_LOCK = threading.RLock()
CONNECTION_INSERTION_LOCK = threading.RLock()
CONNECTION_HISTORY_LOCK = threading.RLock()

HISTORY_CONNECT = {}


class ChatAccessConnectionSettings:
    def __init__(self, chat_id, allow_connect_to_chat):
        self.chat_id = str(chat_id)
        self.allow_connect_to_chat = bool(allow_connect_to_chat)

    def save(self):
        nobita.update_one(
            {'chat_id': self.chat_id},
            {'$set': self.__dict__},
            upsert=True
        )

    @staticmethod
    def get(chat_id):
        return nobita.find_one({'chat_id': str(chat_id)})


class Connection:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = str(chat_id)

    def save(self):
        nobita.update_one(
            {'user_id': self.user_id},
            {'$set': self.__dict__},
            upsert=True
        )

    @staticmethod
    def get(user_id):
        return nobita.find_one({'user_id': user_id})


class ConnectionHistory:
    def __init__(self, user_id, chat_id, chat_name, conn_time):
        self.user_id = user_id
        self.chat_id = str(chat_id)
        self.chat_name = str(chat_name)
        self.conn_time = int(conn_time)

    def save(self):
        nobita.update_one(
            {'user_id': self.user_id, 'chat_id': self.chat_id},
            {'$set': self.__dict__},
            upsert=True
        )

    @staticmethod
    def get(user_id, chat_id):
        return nobita.find_one({'user_id': user_id, 'chat_id': str(chat_id)})


def allow_connect_to_chat(chat_id: Union[str, int]) -> bool:
    chat_setting = ChatAccessConnectionSettings.get(chat_id)
    if chat_setting:
        return chat_setting['allow_connect_to_chat']
    return False


def set_allow_connect_to_chat(chat_id: Union[int, str], setting: bool):
    with CHAT_ACCESS_LOCK:
        chat_setting = ChatAccessConnectionSettings.get(chat_id)
        if not chat_setting:
            chat_setting = ChatAccessConnectionSettings(chat_id, setting)
        chat_setting.allow_connect_to_chat = setting
        chat_setting.save()


def connect(user_id, chat_id):
    with CONNECTION_INSERTION_LOCK:
        prev = Connection.get(user_id)
        if prev:
            nobita.delete_one({'user_id': user_id})
        connect_to_chat = Connection(user_id, chat_id)
        connect_to_chat.save()
        return True


def get_connected_chat(user_id):
    return Connection.get(user_id)


def curr_connection(chat_id):
    return Connection.get(chat_id)


def disconnect(user_id):
    with CONNECTION_INSERTION_LOCK:
        disconnect = Connection.get(user_id)
        if disconnect:
            nobita.delete_one({'user_id': user_id})
            return True
        return False


def add_history_conn(user_id, chat_id, chat_name):
    global HISTORY_CONNECT
    with CONNECTION_HISTORY_LOCK:
        conn_time = int(time.time())
        if HISTORY_CONNECT.get(int(user_id)):
            counting = nobita.count_documents({'user_id': user_id})
            getchat_id = {}
            for x in HISTORY_CONNECT[int(user_id)]:
                getchat_id[HISTORY_CONNECT[int(user_id)][x]["chat_id"]] = x
            if chat_id in getchat_id:
                todeltime = getchat_id[str(chat_id)]
                delold = ConnectionHistory.get(user_id, chat_id)
                if delold:
                    nobita.delete_one({'user_id': user_id, 'chat_id': chat_id})
                    HISTORY_CONNECT[int(user_id)].pop(todeltime)
            elif counting >= 5:
                todel = list(HISTORY_CONNECT[int(user_id)])
                todel.reverse()
                todel = todel[4:]
                for x in todel:
                    chat_old = HISTORY_CONNECT[int(user_id)][x]["chat_id"]
                    delold = ConnectionHistory.get(user_id, chat_old)
                    if delold:
                        nobita.delete_one({'user_id': user_id, 'chat_id': chat_old})
                        HISTORY_CONNECT[int(user_id)].pop(x)
        else:
            HISTORY_CONNECT[int(user_id)] = {}
        delold = ConnectionHistory.get(user_id, chat_id)
        if delold:
            nobita.delete_one({'user_id': user_id, 'chat_id': chat_id})
        history = ConnectionHistory(user_id, chat_id, chat_name, conn_time)
        history.save()
        HISTORY_CONNECT[int(user_id)][conn_time] = {
            "chat_name": chat_name,
            "chat_id": str(chat_id),
        }


def get_history_conn(user_id):
    if not HISTORY_CONNECT.get(int(user_id)):
        HISTORY_CONNECT[int(user_id)] = {}
    return HISTORY_CONNECT[int(user_id)]


def clear_history_conn(user_id):
    global HISTORY_CONNECT
    todel = list(HISTORY_CONNECT[int(user_id)])
    for x in todel:
        chat_old = HISTORY_CONNECT[int(user_id)][x]["chat_id"]
        delold = ConnectionHistory.get(user_id, chat_old)
        if delold:
            nobita.delete_one({'user_id': user_id, 'chat_id': chat_old})
            HISTORY_CONNECT[int(user_id)].pop(x)
    return True


def __load_user_history():
    global HISTORY_CONNECT
    qall = nobita.find()
    HISTORY_CONNECT = {}
    for x in qall:
        check = HISTORY_CONNECT.get(x['user_id'])
        if check is None:
            HISTORY_CONNECT[x['user_id']] = {}
        HISTORY_CONNECT[x['user_id']][x['conn_time']] = {
            "chat_name": x['chat_name'],
            "chat_id": x['chat_id'],
        }


__load_user_history()
