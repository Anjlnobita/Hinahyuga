import threading

from Hinatahyuga import nobita, client 


INSERTION_LOCK = threading.RLock()


class RSS:
    def __init__(self, chat_id, feed_link, old_entry_link):
        self.chat_id = chat_id
        self.feed_link = feed_link
        self.old_entry_link = old_entry_link

    def __repr__(self):
        return "<RSS for chatID {} at feed_link {} with old_entry_link {}>".format(
            self.chat_id, self.feed_link, self.old_entry_link
        )


def check_url_availability(tg_chat_id, tg_feed_link):
    try:
        return list(nobita.find({"feed_link": tg_feed_link, "chat_id": tg_chat_id}))
    finally:
        client.close()


def add_url(tg_chat_id, tg_feed_link, tg_old_entry_link):
    with INSERTION_LOCK:
        action = RSS(tg_chat_id, tg_feed_link, tg_old_entry_link)
        nobita.insert_one(action.__dict__)


def remove_url(tg_chat_id, tg_feed_link):
    with INSERTION_LOCK:
        nobita.delete_many({"chat_id": tg_chat_id, "feed_link": tg_feed_link})


def get_urls(tg_chat_id):
    try:
        return list(nobita.find({"chat_id": tg_chat_id}))
    finally:
        client.close()


def get_all():
    try:
        return list(nobita.find())
    finally:
        client.close()


def update_url(row_id, new_entry_links):
    with INSERTION_LOCK:
        nobita.update_one(
            {"_id": row_id},
            {"$set": {"old_entry_link": new_entry_links[0]}}
        )
