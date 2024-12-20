# New chat added -> setup permissions
import threading

from Hinatahyuga.modules.sql import nobita, client 





PERM_LOCK = threading.RLock()
RESTR_LOCK = threading.RLock()


class Permissions:
    def __init__(self, chat_id):
        self.chat_id = str(chat_id)  # ensure string
        self.audio = False
        self.voice = False
        self.contact = False
        self.video = False
        self.document = False
        self.photo = False
        self.sticker = False
        self.gif = False
        self.url = False
        self.bots = False
        self.forward = False
        self.game = False
        self.location = False
        self.rtl = False
        self.button = False
        self.egame = False
        self.inline = False

    def __repr__(self):
        return "<Permissions for %s>" % self.chat_id


class Restrictions:
    def __init__(self, chat_id):
        self.chat_id = str(chat_id)  # ensure string
        self.messages = False
        self.media = False
        self.other = False
        self.preview = False

    def __repr__(self):
        return "<Restrictions for %s>" % self.chat_id


def init_permissions(chat_id, reset=False):
    curr_perm = nobita.permissions.find_one({"chat_id": str(chat_id)})
    if reset and curr_perm:
        nobita.permissions.delete_one({"chat_id": str(chat_id)})
    perm = Permissions(str(chat_id))
    nobita.permissions.insert_one(perm.__dict__)
    return perm


def init_restrictions(chat_id, reset=False):
    curr_restr = nobita.restrictions.find_one({"chat_id": str(chat_id)})
    if reset and curr_restr:
        nobita.restrictions.delete_one({"chat_id": str(chat_id)})
    restr = Restrictions(str(chat_id))
    nobita.restrictions.insert_one(restr.__dict__)
    return restr


def update_lock(chat_id, lock_type, locked):
    with PERM_LOCK:
        curr_perm = nobita.permissions.find_one({"chat_id": str(chat_id)})
        if not curr_perm:
            curr_perm = init_permissions(chat_id)

        nobita.permissions.update_one(
            {"chat_id": str(chat_id)},
            {"$set": {lock_type: locked}}
        )


def update_restriction(chat_id, restr_type, locked):
    with RESTR_LOCK:
        curr_restr = nobita.restrictions.find_one({"chat_id": str(chat_id)})
        if not curr_restr:
            curr_restr = init_restrictions(chat_id)

        nobita.restrictions.update_one(
            {"chat_id": str(chat_id)},
            {"$set": {restr_type: locked}}
        )


def is_locked(chat_id, lock_type):
    curr_perm = nobita.permissions.find_one({"chat_id": str(chat_id)})
    if not curr_perm:
        return False
    return curr_perm.get(lock_type, False)


def is_restr_locked(chat_id, lock_type):
    curr_restr = nobita.restrictions.find_one({"chat_id": str(chat_id)})
    if not curr_restr:
        return False
    return curr_restr.get(lock_type, False)


def get_locks(chat_id):
    return nobita.permissions.find_one({"chat_id": str(chat_id)})


def get_restr(chat_id):
    return nobita.restrictions.find_one({"chat_id": str(chat_id)})


def migrate_chat(old_chat_id, new_chat_id):
    with PERM_LOCK:
        nobita.permissions.update_one(
            {"chat_id": str(old_chat_id)},
            {"$set": {"chat_id": str(new_chat_id)}}
        )

    with RESTR_LOCK:
        nobita.restrictions.update_one(
            {"chat_id": str(old_chat_id)},
            {"$set": {"chat_id": str(new_chat_id)}}
        )
