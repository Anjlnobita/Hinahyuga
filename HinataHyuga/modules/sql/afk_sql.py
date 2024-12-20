import threading

from Hinatahyuga.modules.sql import nobita, client 

INSERTION_LOCK = threading.RLock()

AFK_USERS = {}


def is_afk(user_id):
    return user_id in AFK_USERS


def check_afk_status(user_id):
    return nobita.find_one({"user_id": user_id})


def set_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = nobita.find_one({"user_id": user_id})
        if not curr:
            nobita.insert_one({"user_id": user_id, "reason": reason, "is_afk": True})
        else:
            nobita.update_one({"user_id": user_id}, {"$set": {"is_afk": True}})

        AFK_USERS[user_id] = reason


def rm_afk(user_id):
    with INSERTION_LOCK:
        curr = nobita.find_one({"user_id": user_id})
        if curr:
            if user_id in AFK_USERS:  # sanity check
                del AFK_USERS[user_id]

            nobita.delete_one({"user_id": user_id})
            return True

        return False


def toggle_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = nobita.find_one({"user_id": user_id})
        if not curr:
            nobita.insert_one({"user_id": user_id, "reason": reason, "is_afk": True})
        elif curr['is_afk']:
            nobita.update_one({"user_id": user_id}, {"$set": {"is_afk": False}})
        else:
            nobita.update_one({"user_id": user_id}, {"$set": {"is_afk": True}})


def __load_afk_users():
    global AFK_USERS
    all_afk = nobita.find({"is_afk": True})
    AFK_USERS = {user['user_id']: user['reason'] for user in all_afk}


__load_afk_users()
