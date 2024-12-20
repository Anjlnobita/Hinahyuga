import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
import os
from Hinatahyuga import dispatcher, logger


# Load the NSFW detection model
model = load_model("nsfw_model.h5")

def is_nsfw(file_path):
    img = image.load_img(file_path, target_size=(224, 224))  # Adjust size as needed by your model
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Create batch axis

    # Normalize the image array
    img_array /= 255.0

    # Predict using the model
    predictions = model.predict(img_array)
    nsfw_score = predictions[0][1]  # Assuming the model outputs [safe_score, nsfw_score]

    return nsfw_score > 0.6

def nsfw_check(update: Update, context: CallbackContext) -> None:
    # Check if the message has photo, video, or sticker
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        file_id = update.message.video.file_id
    elif update.message.sticker:
        file_id = update.message.sticker.file_id
    else:
        return

    # Download the file
    new_file = context.bot.get_file(file_id)
    file_path = f"{file_id}.jpg"
    new_file.download(file_path)

    # Check if the content is NSFW
    if is_nsfw(file_path):
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        update.message.reply_text("NSFW content detected and deleted.")

    # Clean up downloaded file
    os.remove(file_path)

    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video | Filters.sticker, nsfw_check))