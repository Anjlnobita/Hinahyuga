import threading
from Hinatahyuga.modules.sql import nobita, client



BLACKLIST_LOCK = threading.RLock()
BLACKLIST_USERS = set()


def blacklist_user(user_id, reason=None):
    with BLACKLIST_LOCK:
        user = nobita.find_one({"user_id": str(user_id)})
        if not user:
            nobita.insert_one({"user_id": str(user_id), "reason": reason})
        else:
            nobita.update_one({"user_id": str(user_id)}, {"$set": {"reason": reason}})
        
        __load_blacklist_userid_list()


def unblacklist_user(user_id):
    with BLACKLIST_LOCK:
        user = nobita.find_one({"user_id": str(user_id)})
        if user:
            nobita.delete_one({"user_id": str(user_id)})

        __load_blacklist_userid_list()


def get_reason(user_id):
    user = nobita.find_one({"user_id": str(user_id)})
    rep = ""
    if user:
        rep = user.get("reason", "")

    return rep


def is_user_blacklisted(user_id):
    return user_id in BLACKLIST_USERS


def __load_blacklist_userid_list():
    global BLACKLIST_USERS
    try:
        BLACKLIST_USERS = {int(x['user_id']) for x in nobita.find()}
    finally:
        pass


__load_blacklist_userid_list()
