
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scraper import fetch_all_horoscopes

# Load environment variables
load_dotenv("conf.env")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

from utils import get_date_label
from scraper import fetch_horoscope, ZODIAC_SIGNS

import concurrent.futures
from utils import get_date_label
from scraper import fetch_horoscope, fetch_all_horoscopes, ZODIAC_SIGNS
from image_generator import generate_horoscope_images
from telegram import InputMediaPhoto

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches dates from website and shows Yesterday/Today/Tomorrow buttons."""
    await update.message.reply_text("Welcome to the Horoscope Bot! 🌟\nFetching available dates...")
    
    dates = {}
    offsets = [-1, 0, 1]
    
    def get_date_for_offset(offset):
        data = fetch_horoscope("aries", offset)
        return offset, data.get('date', 'Unknown')

    # Fetch dates sequentially to avoid DNS/Connection errors
    for offset in offsets:
         _, date_str = get_date_for_offset(offset)
         dates[offset] = date_str

    keyboard = [
        [InlineKeyboardButton(f"Yesterday ({dates.get(-1)})", callback_data="day_-1")],
        [InlineKeyboardButton(f"Today ({dates.get(0)})", callback_data="day_0")],
        [InlineKeyboardButton(f"Tomorrow ({dates.get(1)})", callback_data="day_1")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a date to view horoscopes for all signs:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses selection and either shows templates or generates images."""
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
        
        # Template Selection Keyboard
        keyboard = [
            [InlineKeyboardButton("Template 1 (Standard)", callback_data="template_1")],
            [InlineKeyboardButton("Template 2 (New)", callback_data="template_2")],
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
        day = context.user_data.get('selected_day', 0) # Default to 0 (Today) if missing
        
        day_label = "Today"
        if day == -1: day_label = "Yesterday"
        if day == 1: day_label = "Tomorrow"

        # Map template_id to actual directory
        # Use relative path from this script or an env var
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_assets_dir = os.path.dirname(base_dir)
        assets_dir = os.getenv("ASSETS_DIR", default_assets_dir)
        
        # Deprecated: Logic moved to image_generator.py, we just pass assets_dir and template_id
        
        await query.edit_message_text(text=f"Generating **{day_label}'s** horoscopes using **Template {template_id}**... Please wait 📸", parse_mode='Markdown')
        
        try:
            results = fetch_all_horoscopes(day)
            
            # Determine the date label to show on images
            date_on_image = results[0].get('date', "") 
            if not date_on_image:
                date_on_image = f"{day_label} ({get_date_label(day)})"

            # Generate Images with selected template
            image_paths = generate_horoscope_images(results, date_on_image, template_id=template_id, assets_dir=assets_dir)
            
            # Create Media Group
            media_group = [InputMediaPhoto(open(path, 'rb')) for path in image_paths]
            
            # Send Album
            await context.bot.send_media_group(chat_id=query.message.chat_id, media=media_group)
            
            # Cleanup
            for path in image_paths:
                try:
                    os.remove(path)
                except:
                    pass

            await context.bot.send_message(chat_id=query.message.chat_id, text="Here are your daily readings! ✨")

        except Exception as e:
            logger.error(f"Error in button handler: {e}")
            await context.bot.send_message(chat_id=query.message.chat_id, text="An error occurred while generating horoscopes.")

# Removed start_menu_callback as it is no longer used in this flow logic
# if needed we can re-add it.



def main() -> None:
    """Run the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env file.")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

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
