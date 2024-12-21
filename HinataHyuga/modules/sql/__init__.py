# MongoDB Connection Setup

from pymongo import MongoClient
from Hinatahyuga.config import DB_URI
from Hinatahyuga import LOGGER as log

def start():
    client = MongoClient(DB_URI)
    log.info("[MongoDB] Connecting to database......")
    return client

try:
    client = start()
    nobita = client.get_default_database()
except Exception as e:
    log.exception(f"[MongoDB] Failed to connect due to {e}")
    exit()

log.info("[MongoDB] Connection successful, client started.")