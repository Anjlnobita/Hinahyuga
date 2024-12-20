import threading
from Hinatahyuga.modules.sql import db, client
from Hinatahyuga import dispatcher 


INSERTION_LOCK = threading.RLock()


class Users:
    def __init__(self, user_id, username=None):
        self.user_id = user_id
        self.username = username

    def __repr__(self):
        return "<User {} ({})>".format(self.username, self.user_id)


class Chats:
    def __init__(self, chat_id, chat_name):
        self.chat_id = str(chat_id)
        self.chat_name = chat_name

    def __repr__(self):
        return "<Chat {} ({})>".format(self.chat_name, self.chat_id)


class ChatMembers:
    def __init__(self, chat, user):
        self.chat = chat
        self.user = user

    def __repr__(self):
        return "<Chat user {} ({}) in chat {} ({})>".format(
            self.user.username,
            self.user.user_id,
            self.chat.chat_name,
            self.chat.chat_id,
        )


def ensure_bot_in_db():
    with INSERTION_LOCK:
        bot = Users(dispatcher.bot.id, dispatcher.bot.username)
        nobita.users.update_one({'user_id': bot.user_id}, {'$set': bot.__dict__}, upsert=True)


def update_user(user_id, username, chat_id=None, chat_name=None):
    with INSERTION_LOCK:
        user = db.users.find_one({'user_id': user_id})
        if not user:
            user = Users(user_id, username)
            db.users.insert_one(user.__dict__)
        else:
            db.users.update_one({'user_id': user_id}, {'$set': {'username': username}})

        if not chat_id or not chat_name:
            return

        chat = db.chats.find_one({'chat_id': str(chat_id)})
        if not chat:
            chat = Chats(str(chat_id), chat_name)
            db.chats.insert_one(chat.__dict__)
        else:
            db.chats.update_one({'chat_id': str(chat_id)}, {'$set': {'chat_name': chat_name}})

        member = db.chat_members.find_one({'chat': chat.chat_id, 'user': user.user_id})
        if not member:
            chat_member = ChatMembers(chat.chat_id, user.user_id)
            db.chat_members.insert_one(chat_member.__dict__)


def get_userid_by_name(username):
    return list(db.users.find({'username': {'$regex': f'^{username}$', '$options': 'i'}}))


def get_name_by_userid(user_id):
    return db.users.find_one({'user_id': int(user_id)})


def get_chat_members(chat_id):
    return list(db.chat_members.find({'chat': str(chat_id)}))


def get_all_chats():
    return list(db.chats.find())


def get_all_users():
    return list(db.users.find())


def get_user_num_chats(user_id):
    return db.chat_members.count_documents({'user': int(user_id)})


def get_user_com_chats(user_id):
    chat_members = list(db.chat_members.find({'user': int(user_id)}))
    return [i['chat'] for i in chat_members]


def num_chats():
    return db.chats.count_documents({})


def num_users():
    return db.users.count_documents({})


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        db.chats.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': str(new_chat_id)}})
        db.chat_members.update_many({'chat': str(old_chat_id)}, {'$set': {'chat': str(new_chat_id)}})


ensure_bot_in_db()


def del_user(user_id):
    with INSERTION_LOCK:
        curr = db.users.find_one({'user_id': user_id})
        if curr:
            db.users.delete_one({'user_id': user_id})
            db.chat_members.delete_many({'user': user_id})
            return True
    return False


def rem_chat(chat_id):
    with INSERTION_LOCK:
        chat = db.chats.find_one({'chat_id': str(chat_id)})
        if chat:
            db.chats.delete_one({'chat_id': str(chat_id)})
