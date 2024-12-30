from telegram import Update
from PIL import Image
import os
from rembg import remove
from telegram.ext import ApplicationBuilder, Updater, ContextTypes, CallbackContext, CommandHandler, MessageHandler, filters

TOKEN = '8090814648:AAFcVrPy4NAVhVXDIcK1PIO0TcQ4KmrFADE'

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, I am a background removal bot, to start click on /start")
    
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('مرحبا! لإزالة الخلفية من صورة، يرجى إرسال الصورة لي.')

def main() -> None:
    updater = Updater("YOUR_API_KEY")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

async def process_image(photo_name: str):
    name, _ = os.path.splitext(photo_name)
    output_photo_path = f'./processed/{name}.png'
    
    with open(f'./temp/{photo_name}', 'rb') as input_file:
        input_data = input_file.read()

    output_data = remove(input_data)
    
    with open(output_photo_path, 'wb') as output_file:
        output_file.write(output_data)

    os.remove(f'./temp/{photo_name}')
    
    return output_photo_path

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if filters.PHOTO.check_update(update):
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f"{unique_file_id}.jpg"
    elif update.message.document and update.message.document.mime_type.startswith('image/'):
        file_id = update.message.document.file_id
        _, f_ext = os.path.splitext(update.message.document.file_name) 
        unique_file_id = update.message.document.file_unique_id
        photo_name = f'{unique_file_id}.{f_ext}'

    # Download the image
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f'./temp/{photo_name}')
    
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='We are processing your photo. Please wait...')
    
    try:
        # Process the image and send back
        processed_image = await process_image(photo_name)
        await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_image)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists('./temp'):
        os.makedirs('./temp')
    if not os.path.exists('./processed'):
        os.makedirs('./processed')

    application = ApplicationBuilder().token(TOKEN).build()

    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.ALL, handle_message)

    # Register handlers
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)

    # Start the bot
    application.run_polling()