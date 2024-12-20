import threading
from Hinatahyuga.modules.sql import nobita, client
from DazaiRobot.modules.helper_funcs.msg_types import Types



CUST_FILT_LOCK = threading.RLock()
BUTTON_LOCK = threading.RLock()
CHAT_FILTERS = {}

class CustomFilters:
    def __init__(self, chat_id, keyword, reply, is_sticker=False, is_document=False,
                 is_image=False, is_audio=False, is_voice=False, is_video=False,
                 has_buttons=False, reply_text=None, file_type=1, file_id=None):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.reply = reply
        self.is_sticker = is_sticker
        self.is_document = is_document
        self.is_image = is_image
        self.is_audio = is_audio
        self.is_voice = is_voice
        self.is_video = is_video
        self.has_buttons = has_buttons
        self.reply_text = reply_text
        self.file_type = file_type
        self.file_id = file_id

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "keyword": self.keyword,
            "reply": self.reply,
            "is_sticker": self.is_sticker,
            "is_document": self.is_document,
            "is_image": self.is_image,
            "is_audio": self.is_audio,
            "is_voice": self.is_voice,
            "is_video": self.is_video,
            "has_buttons": self.has_buttons,
            "reply_text": self.reply_text,
            "file_type": self.file_type,
            "file_id": self.file_id
        }

class Buttons:
    def __init__(self, chat_id, keyword, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.name = name
        self.url = url
        self.same_line = same_line

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "keyword": self.keyword,
            "name": self.name,
            "url": self.url,
            "same_line": self.same_line
        }

def get_all_filters():
    return list(nobita.custom_filters.find())

def add_filter(chat_id, keyword, reply, is_sticker=False, is_document=False,
               is_image=False, is_audio=False, is_voice=False, is_video=False,
               buttons=None):
    global CHAT_FILTERS

    if buttons is None:
        buttons = []

    with CUST_FILT_LOCK:
        prev = nobita.custom_filters.find_one({"chat_id": str(chat_id), "keyword": keyword})
        if prev:
            nobita.custom_filters.delete_one({"chat_id": str(chat_id), "keyword": keyword})

        filt = CustomFilters(chat_id, keyword, reply, is_sticker, is_document,
                             is_image, is_audio, is_voice, is_video, bool(buttons))
        nobita.custom_filters.insert_one(filt.to_dict())

        if keyword not in CHAT_FILTERS.get(str(chat_id), []):
            CHAT_FILTERS[str(chat_id)] = sorted(
                CHAT_FILTERS.get(str(chat_id), []) + [keyword],
                key=lambda x: (-len(x), x),
            )

    for b_name, url, same_line in buttons:
        add_note_button_to_db(chat_id, keyword, b_name, url, same_line)

def remove_filter(chat_id, keyword):
    global CHAT_FILTERS
    with CUST_FILT_LOCK:
        filt = nobita.custom_filters.find_one({"chat_id": str(chat_id), "keyword": keyword})
        if filt:
            if keyword in CHAT_FILTERS.get(str(chat_id), []):
                CHAT_FILTERS.get(str(chat_id), []).remove(keyword)

            nobita.custom_filters.delete_one({"chat_id": str(chat_id), "keyword": keyword})
            return True
        return False

def get_chat_filters(chat_id):
    return list(nobita.custom_filters.find({"chat_id": str(chat_id)}))

def add_note_button_to_db(chat_id, keyword, b_name, url, same_line):
    with BUTTON_LOCK:
        button = Buttons(chat_id, keyword, b_name, url, same_line)
        nobita.buttons.insert_one(button.to_dict())

def get_buttons(chat_id, keyword):
    return list(nobita.buttons.find({"chat_id": str(chat_id), "keyword": keyword}))

def num_filters():
    return nobita.custom_filters.count_documents({})

def num_chats():
    return nobita.custom_filters.distinct("chat_id")

def __load_chat_filters():
    global CHAT_FILTERS
    chats = nobita.custom_filters.distinct("chat_id")
    for chat_id in chats:
        CHAT_FILTERS[chat_id] = []

    all_filters = nobita.custom_filters.find()
    for x in all_filters:
        CHAT_FILTERS[x['chat_id']].append(x['keyword'])

    CHAT_FILTERS = {
        x: sorted(set(y), key=lambda i: (-len(i), i))
        for x, y in CHAT_FILTERS.items()
    }

__load_chat_filters()
