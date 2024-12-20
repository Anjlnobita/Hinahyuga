import threading
from typing import Union
from Hinatahyuga.modules.sql import nobita, client




CHAT_LOCK = threading.RLock()
USER_LOCK = threading.RLock()


class ReportingUserSettings:
    def __init__(self, user_id):
        self.user_id = user_id
        self.should_report = True

    def __repr__(self):
        return "<User report settings ({})>".format(self.user_id)


class ReportingChatSettings:
    def __init__(self, chat_id):
        self.chat_id = str(chat_id)
        self.should_report = True

    def __repr__(self):
        return "<Chat report settings ({})>".format(self.chat_id)


def chat_should_report(chat_id: Union[str, int]) -> bool:
    chat_setting = nobita.chat_report_settings.find_one({"chat_id": str(chat_id)})
    if chat_setting:
        return chat_setting['should_report']
    return False


def user_should_report(user_id: int) -> bool:
    user_setting = nobita.user_report_settings.find_one({"user_id": user_id})
    if user_setting:
        return user_setting['should_report']
    return True


def set_chat_setting(chat_id: Union[int, str], setting: bool):
    with CHAT_LOCK:
        chat_setting = nobita.chat_report_settings.find_one({"chat_id": str(chat_id)})
        if not chat_setting:
            chat_setting = ReportingChatSettings(chat_id)
            nobita.chat_report_settings.insert_one(chat_setting.__dict__)
        else:
            nobita.chat_report_settings.update_one(
                {"chat_id": str(chat_id)},
                {"$set": {"should_report": setting}}
            )


def set_user_setting(user_id: int, setting: bool):
    with USER_LOCK:
        user_setting = nobita.user_report_settings.find_one({"user_id": user_id})
        if not user_setting:
            user_setting = ReportingUserSettings(user_id)
            nobita.user_report_settings.insert_one(user_setting.__dict__)
        else:
            nobita.user_report_settings.update_one(
                {"user_id": user_id},
                {"$set": {"should_report": setting}}
            )


def migrate_chat(old_chat_id, new_chat_id):
    with CHAT_LOCK:
        chat_notes = nobita.chat_report_settings.find({"chat_id": str(old_chat_id)})
        for note in chat_notes:
            nobita.chat_report_settings.update_one(
                {"_id": note['_id']},
                {"$set": {"chat_id": str(new_chat_id)}}
            )
