from pymongo import MongoClient

from Hinatahyuga.modules.sql import nobita, client 


class Nightmode:
    def __init__(self, chat_id):
        self.chat_id = chat_id


def add_nightmode(chat_id: str):
    nightmoddy = Nightmode(str(chat_id))
    nobita.insert_one(nightmoddy.__dict__)


def rmnightmode(chat_id: str):
    nobita.delete_one({'chat_id': str(chat_id)})


def get_all_chat_id():
    return list(nobita.find({}, {'_id': 0, 'chat_id': 1}))


def is_nightmode_indb(chat_id: str):
    result = nobita.find_one({'chat_id': str(chat_id)})
    return str(result['chat_id']) if result else None
