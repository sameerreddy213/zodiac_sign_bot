
import os
import logging
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scraper import fetch_horoscope, get_horoscopes_by_date

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "conf.env")
load_dotenv(env_path)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches dates from website and shows dates, falling back to MongoDB if down."""
    await update.message.reply_text("Welcome to the Horoscope Bot! 🌟\nFetching available dates...")
    
    date_offsets = {}
    website_up = False
    
    offsets = [-1, 0, 1]
    
    # 1. Check if website is up and get dates
    for offset in offsets:
         try:
             data = fetch_horoscope("aries", offset)
             date_str = data.get('date')
             if date_str and date_str != "Unknown":
                 date_offsets[date_str] = offset
                 website_up = True
         except:
             pass

    context.user_data['date_offsets'] = date_offsets
    keyboard = []
    
    if website_up:
        # Show real website dates
        for d_str in date_offsets.keys():
            # Pass prefix "date_" followed by the exact date string
            keyboard.append([InlineKeyboardButton(d_str, callback_data=f"date_{d_str}")])
    else:
        # 2. Fallback to DB
        from db import get_available_dates
        db_dates = get_available_dates("english")
        for d_str in db_dates:
            keyboard.append([InlineKeyboardButton(f"{d_str} (Cached)", callback_data=f"date_{d_str}")])
            
    if not keyboard:
        await update.message.reply_text("Sorry, no horoscopes are currently available.")
        return
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a date to view horoscopes for all signs:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Date and Template selection."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. Date Selected -> Show Template Options
    if data.startswith("date_"):
        target_date = data.split("_", 1)[1]
        context.user_data['selected_date'] = target_date
        
        keyboard = [
            [InlineKeyboardButton("Template 1 (Standard)", callback_data="template_1")],
            [InlineKeyboardButton("Template 2 (White/Black)", callback_data="template_2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"Selected Date: **{target_date}**.\nNow please select a design template:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    # 2. Template Selected -> Show Language Options
    if data.startswith("template_"):
        template_id = data.split("_")[1]
        context.user_data['selected_template'] = template_id
        
        keyboard = [
            [InlineKeyboardButton("English", callback_data="lang_english")],
            [InlineKeyboardButton("Telugu (తెలుగు)", callback_data="lang_telugu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"Selected Template: **{template_id}**.\nNow please select a language:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    # 3. Language Selected -> Generate Images
    if data.startswith("lang_"):
        language = data.split("_")[1]
        template_id = context.user_data.get('selected_template', '1')
        target_date = context.user_data.get('selected_date')
        
        fallback_offset = context.user_data.get('date_offsets', {}).get(target_date)
        
        from image_generator import generate_horoscope_images
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_assets_dir = os.path.join(os.path.dirname(base_dir), "assets")
        assets_dir = os.getenv("ASSETS_DIR", default_assets_dir)
        
        await query.edit_message_text(text=f"Generating **{target_date}** horoscopes in **{language.title()}**... Please wait 📸", parse_mode='Markdown')
        
        try:
            # Check DB or Fetch website via target_date
            # Offload synchronous Playwright hooks AND blocking translates
            import asyncio
            horoscopes = await asyncio.to_thread(
                get_horoscopes_by_date, target_date, language, fallback_offset
            )
            
            if not horoscopes:
                await query.message.reply_text("Sorry, failed to fetch horoscopes for that date.")
                return
            
            context.user_data['date_label'] = target_date

            # Generate Images 
            image_paths = await asyncio.to_thread(
                generate_horoscope_images,
                horoscopes, 
                target_date, 
                template_id=template_id, 
                language=language, 
                assets_dir=assets_dir
            )
            
            context.user_data['generated_images'] = image_paths
            
            # Send Album
            media_group = [InputMediaPhoto(open(path, 'rb')) for path in image_paths]
            await context.bot.send_media_group(chat_id=query.message.chat_id, media=media_group)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id, 
                text="Here are your daily readings! ✨"
            )

        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            logger.error(f"Error in generation: {e}\n{err_msg}")
            with open("error.log", "w", encoding="utf-8") as f:
                f.write(err_msg)
            await context.bot.send_message(chat_id=query.message.chat_id, text="An error occurred while generating horoscopes.")

def main() -> None:
    """Run the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env file.")
        return

    import pytz
    
    # Disable PTB's job queue fully to stop the conflict with Python 3.13 zoneinfo defaults
    application = Application.builder().token(token).job_queue(None).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler)) # General buttons

    # Start the daily prefetch scheduler
    try:
        from scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

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
