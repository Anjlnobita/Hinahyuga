import threading
from Hinatahyuga.modules.sql import nobita, client


CLEANER_CHAT_SETTINGS = threading.RLock()
CLEANER_CHAT_LOCK = threading.RLock()
CLEANER_GLOBAL_LOCK = threading.RLock()

CLEANER_CHATS = {}
GLOBAL_IGNORE_COMMANDS = set()


def set_cleanbt(chat_id, is_enable):
    with CLEANER_CHAT_SETTINGS:
        nobita.cleaner_bluetext_chat_setting.delete_one({'chat_id': str(chat_id)})
        newcurr = {'chat_id': str(chat_id), 'is_enable': is_enable}
        nobita.cleaner_bluetext_chat_setting.insert_one(newcurr)


def chat_ignore_command(chat_id, ignore):
    ignore = ignore.lower()
    with CLEANER_CHAT_LOCK:
        ignored = nobita.cleaner_bluetext_chat_ignore_commands.find_one({'chat_id': str(chat_id), 'command': ignore})

        if not ignored:
            if str(chat_id) not in CLEANER_CHATS:
                CLEANER_CHATS.setdefault(
                    str(chat_id),
                    {"setting": False, "commands": set()},
                )

            CLEANER_CHATS[str(chat_id)]["commands"].add(ignore)

            ignored = {'chat_id': str(chat_id), 'command': ignore}
            nobita.cleaner_bluetext_chat_ignore_commands.insert_one(ignored)
            return True
        return False


def chat_unignore_command(chat_id, unignore):
    unignore = unignore.lower()
    with CLEANER_CHAT_LOCK:
        unignored = nobita.cleaner_bluetext_chat_ignore_commands.find_one({'chat_id': str(chat_id), 'command': unignore})

        if unignored:
            if str(chat_id) not in CLEANER_CHATS:
                CLEANER_CHATS.setdefault(
                    str(chat_id),
                    {"setting": False, "commands": set()},
                )
            if unignore in CLEANER_CHATS.get(str(chat_id)).get("commands"):
                CLEANER_CHATS[str(chat_id)]["commands"].remove(unignore)

            nobita.cleaner_bluetext_chat_ignore_commands.delete_one({'chat_id': str(chat_id), 'command': unignore})
            return True

        return False


def global_ignore_command(command):
    command = command.lower()
    with CLEANER_GLOBAL_LOCK:
        ignored = nobita.cleaner_bluetext_global_ignore_commands.find_one({'command': str(command)})

        if not ignored:
            GLOBAL_IGNORE_COMMANDS.add(command)

            ignored = {'command': str(command)}
            nobita.cleaner_bluetext_global_ignore_commands.insert_one(ignored)
            return True

        return False


def global_unignore_command(command):
    command = command.lower()
    with CLEANER_GLOBAL_LOCK:
        unignored = nobita.cleaner_bluetext_global_ignore_commands.find_one({'command': str(command)})

        if unignored:
            if command in GLOBAL_IGNORE_COMMANDS:
                GLOBAL_IGNORE_COMMANDS.remove(command)

            nobita.cleaner_bluetext_global_ignore_commands.delete_one({'command': str(command)})
            return True

        return False


def is_command_ignored(chat_id, command):
    if command.lower() in GLOBAL_IGNORE_COMMANDS:
        return True

    if str(chat_id) in CLEANER_CHATS:
        if command.lower() in CLEANER_CHATS.get(str(chat_id)).get("commands"):
            return True

    return False


def is_enabled(chat_id):
    try:
        resultcurr = nobita.cleaner_bluetext_chat_setting.find_one({'chat_id': str(chat_id)})
        if resultcurr:
            return resultcurr['is_enable']
        return False  # default
    finally:
        pass


def get_all_ignored(chat_id):
    if str(chat_id) in CLEANER_CHATS:
        LOCAL_IGNORE_COMMANDS = CLEANER_CHATS.get(str(chat_id)).get("commands")
    else:
        LOCAL_IGNORE_COMMANDS = set()

    return GLOBAL_IGNORE_COMMANDS, LOCAL_IGNORE_COMMANDS


def __load_cleaner_list():
    global GLOBAL_IGNORE_COMMANDS
    global CLEANER_CHATS

    GLOBAL_IGNORE_COMMANDS = {x['command'] for x in nobita.cleaner_bluetext_global_ignore_commands.find()}

    for x in nobita.cleaner_bluetext_chat_setting.find():
        CLEANER_CHATS.setdefault(x['chat_id'], {"setting": False, "commands": set()})
        CLEANER_CHATS[x['chat_id']]["setting"] = x['is_enable']

    for x in nobita.cleaner_bluetext_chat_ignore_commands.find():
        CLEANER_CHATS.setdefault(x['chat_id'], {"setting": False, "commands": set()})
        CLEANER_CHATS[x['chat_id']]["commands"].add(x['command'])


__load_cleaner_list()
