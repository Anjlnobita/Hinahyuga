import threading

from Hinatahyuga.modules.sql import nobita, client




INSERTION_LOCK = threading.RLock()


class Rules:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.rules = ""

    def __repr__(self):
        return "<Chat {} rules: {}>".format(self.chat_id, self.rules)


def set_rules(chat_id, rules_text):
    with INSERTION_LOCK:
        rules = nobita.find_one({"chat_id": str(chat_id)})
        if not rules:
            rules = Rules(str(chat_id))
            nobita.insert_one({"chat_id": rules.chat_id, "rules": rules_text})
        else:
            nobita.update_one({"chat_id": str(chat_id)}, {"$set": {"rules": rules_text}})


def get_rules(chat_id):
    rules = nobita.find_one({"chat_id": str(chat_id)})
    ret = ""
    if rules:
        ret = rules['rules']
    return ret


def num_chats():
    return nobita.distinct("chat_id").count()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = nobita.find_one({"chat_id": str(old_chat_id)})
        if chat:
            nobita.update_one({"chat_id": str(old_chat_id)}, {"$set": {"chat_id": str(new_chat_id)}})
