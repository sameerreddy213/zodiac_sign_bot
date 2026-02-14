
import os
import logging
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from scraper import fetch_all_horoscopes, fetch_horoscope
from image_generator import generate_horoscope_images
from utils import get_date_label


# Load environment variables
load_dotenv("conf.env")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches dates from website and shows Yesterday/Today/Tomorrow buttons."""
    await update.message.reply_text("Welcome to the Horoscope Bot! 🌟\nFetching available dates...")
    
    dates = {}
    offsets = [-1, 0, 1]
    
    # Simple caching or fetching
    for offset in offsets:
         try:
             data = fetch_horoscope("aries", offset)
             dates[offset] = data.get('date', 'Unknown')
         except:
             dates[offset] = "Unknown"

    keyboard = [
        [InlineKeyboardButton(f"Yesterday ({dates.get(-1)})", callback_data="day_-1")],
        [InlineKeyboardButton(f"Today ({dates.get(0)})", callback_data="day_0")],
        [InlineKeyboardButton(f"Tomorrow ({dates.get(1)})", callback_data="day_1")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a date to view horoscopes for all signs:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Day and Template selection."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. Day Selected -> Show Template Options
    if data.startswith("day_"):
        day = int(data.split("_")[1])
        context.user_data['selected_day'] = day
        
        day_label = "Today"
        if day == -1: day_label = "Yesterday"
        if day == 1: day_label = "Tomorrow"
        
        keyboard = [
            [InlineKeyboardButton("Template 1 (Standard)", callback_data="template_1")],
            [InlineKeyboardButton("Template 2 (White/Black)", callback_data="template_2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"Selected Date: **{day_label}**.\nNow please select a design template:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    # 2. Template Selected -> Generate Images
    if data.startswith("template_"):
        template_id = data.split("_")[1]
        day = context.user_data.get('selected_day', 0)
        
        day_label = "Today"
        if day == -1: day_label = "Yesterday"
        if day == 1: day_label = "Tomorrow"
        if day == 0: day_label = "Today" # Explicit check if get returns 0
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_assets_dir = os.path.dirname(base_dir)
        assets_dir = os.getenv("ASSETS_DIR", default_assets_dir)
        
        await query.edit_message_text(text=f"Generating **{day_label}'s** horoscopes using **Template {template_id}**... Please wait 📸", parse_mode='Markdown')
        
        try:
            results = fetch_all_horoscopes(day)
            
            # Determine the date label
            date_on_image = results[0].get('date', "") 
            if not date_on_image:
                date_on_image = f"{day_label} ({get_date_label(day)})"

            # Store for caption
            context.user_data['date_label'] = date_on_image

            # Generate Images
            image_paths = generate_horoscope_images(results, date_on_image, template_id=template_id, assets_dir=assets_dir)
            
            # Store paths for Instagram
            context.user_data['generated_images'] = image_paths
            
            # Send Album
            media_group = [InputMediaPhoto(open(path, 'rb')) for path in image_paths]
            await context.bot.send_media_group(chat_id=query.message.chat_id, media=media_group)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id, 
                text="Here are your daily readings! ✨"
            )

        except Exception as e:
            logger.error(f"Error in generation: {e}")
            await context.bot.send_message(chat_id=query.message.chat_id, text="An error occurred while generating horoscopes.")

# --- Instagram Conversation Handlers ---

def main() -> None:
    """Run the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env file.")
        return

    application = Application.builder().token(token).build()


    application.add_handler(CallbackQueryHandler(button_handler)) # General buttons

    # Start the keep-alive server
    try:
        from keep_alive import keep_alive
        keep_alive()
    except ImportError:
        logger.warning("keep_alive module not found, skipping.")

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
