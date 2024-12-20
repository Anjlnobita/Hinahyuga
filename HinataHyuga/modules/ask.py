from Hinatahyuga import dispatcher 
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from transformers import pipeline

# Initialize the AI model pipeline
ai_pipeline = pipeline('text-generation', model='gpt-3')



def ask(update: Update, context: CallbackContext) -> None:
    """Generate a response to the user's query using the AI model."""
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Please provide a query after the /ask command.')
        return

    # Generate a response using the AI model
    response = ai_pipeline(query, max_length=512, num_return_sequences=1)[0]['generated_text']
    
    # Ensure the response does not exceed Telegram's character limit
    if len(response) > 4096:
        response = response[:4093] + '...'

    update.message.reply_text(response)

   
    dispatcher.add_handler(CommandHandler("ask", ask))