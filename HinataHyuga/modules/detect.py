import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
from Hinatahyuga import dispatcher 

def detect_member_status(update, context):
    member = update.effective_member
    chat = update.effective_chat

    if member.status == "administrator":
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} promoted by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "kicked":
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} banned by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "restricted":
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} muted by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "member":
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} unbanned by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "left":
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} kicked by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "member" and member.is_bot:
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} warned by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif member.status == "member" and not member.is_bot:
        bot.send_message(
            chat_id=chat.id,
            text=f"{member.username} demoted by @{context.update.effective_user.username}",
            parse_mode=telegram.ParseMode.MARKDOWN
        )

    dispatcher.add_handler(MessageHandler(Filters.status_update, detect_member_status))