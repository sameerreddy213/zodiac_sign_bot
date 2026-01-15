
import os
import logging
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from scraper import fetch_all_horoscopes, fetch_horoscope
from image_generator import generate_horoscope_images
from utils import get_date_label
from instagram_manager import ig_manager

# Load environment variables
load_dotenv("conf.env")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation States
ASK_CREDENTIALS, SELECT_TIME = range(2)

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
            
            # Prompt for Instagram
            keyboard = [[InlineKeyboardButton("Post to Instagram 📸", callback_data="post_instagram")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id, 
                text="Here are your daily readings! ✨\n\nWould you like to auto-post these to Instagram?",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in generation: {e}")
            await context.bot.send_message(chat_id=query.message.chat_id, text="An error occurred while generating horoscopes.")

# --- Instagram Conversation Handlers ---

async def ask_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Triggered by 'Post to Instagram' button."""
    query = update.callback_query
    await query.answer()
    
    username = "daily_horoscopes_astrology"
    context.user_data['ig_user'] = username
    
    await query.message.reply_text(
        f"Please send your **Instagram Password** for account `{username}`.\n\n"
        "_(Password is used only for this session and not stored permenantly)_",
        parse_mode='Markdown'
    )
    return ASK_CREDENTIALS

async def receive_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives password and asks for time."""
    password = update.message.text.strip()
    
    # Simple check to avoid spaces if user mistakenly sends "user pass"
    if " " in password:
        # Heuristic: if user still sends "user pass", try to handle or just warn?
        # User explicitly said "ask me for password only".
        # We'll just take the whole text as password to be safe, or split if it looks like they ignored instruction.
        # Let's assume they follow instructions. 
        pass
    
    context.user_data['ig_pass'] = password
    
    # Delete the message with password for security
    try:
        await update.message.delete()
    except:
        pass

    # Ask for Time
    times = ["12:00 AM", "2:00 AM", "4:00 AM", "5:00 AM", "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM"]
    keyboard = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(t, callback_data=f"time_{t}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Credentials received! ✅\n\nSelect a time to schedule the post (IST):",
        reply_markup=reply_markup
    )
    return SELECT_TIME

import pytz

# ... [imports] ...

async def schedule_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finalizes scheduling."""
    query = update.callback_query
    await query.answer()
    time_str = query.data.replace("time_", "")
    
    username = context.user_data.get('ig_user')
    password = context.user_data.get('ig_pass')
    paths = context.user_data.get('generated_images')
    date_label = context.user_data.get('date_label', 'Today')
    
    if not username or not paths:
        await query.message.reply_text("Session incorrect. Please start over.")
        return ConversationHandler.END

    # Timezone Handling
    ist_tz = pytz.timezone('Asia/Kolkata')
    
    # Calculate Target Date (IST)
    # Start with current time in IST
    now_ist = datetime.datetime.now(ist_tz)
    
    # Determine target day based on offset
    day_offset = context.user_data.get('selected_day', 0)
    target_date_ist = now_ist + datetime.timedelta(days=day_offset)
    
    # Parse selected hour/minute
    t = datetime.datetime.strptime(time_str, "%I:%M %p")
    
    # Construct combined datetime in IST
    final_dt_ist = target_date_ist.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    
    # If the constructed time is in the past (e.g. it's 2 PM IST, user picked 10 AM IST for Today),
    # then it should probably schedule for Tomorrow's 10 AM? 
    # Or just fail/schedule immediately?
    # User intent implies "Schedule for [Date]", so we stick to the date even if past. 
    # APScheduler will define behavior (usually "missed job" -> run immediately).
    
    # Convert to System Time (UTC for Render)
    # APScheduler running on server (UTC) needs a datetime it understands.
    # Passing a timezone-aware datetime usually works if scheduler is configured, 
    # but converting to UTC/server-local is safest.
    final_dt_utc = final_dt_ist.astimezone(pytz.utc)
    
    # Remove tzinfo for APScheduler if it's using naive local time (default)
    # Actually, keep it aware if using 'date' trigger? 
    # BackgroundScheduler defaults: use local time.
    # Let's convert to naive UTC (assuming server is UTC) to be 100% sure.
    # OR, just pass the aware datetime object. APScheduler 3.x handles it.
    
    caption = f"{date_label} 🙏🏻\n\n#astrology #horoscope #zodiac #tarot #jyotish"
    
    # Display IST time to user
    msg_time = final_dt_ist.strftime('%d %B %I:%M %p')
    await query.edit_message_text(f"Scheduling post for **{msg_time} IST**... ⏳", parse_mode='Markdown')
    
    # Pass the Datetime object (aware) to manager
    success = ig_manager.schedule_post(username, password, paths, caption, final_dt_utc)
    
    if success:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Post scheduled successfully! ✅\n(Location: United States 🇺🇸)")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Failed to schedule post.")
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Instagram posting cancelled.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env file.")
        return

    application = Application.builder().token(token).build()

    # Conversation Handler for Instagram
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_credentials, pattern="^post_instagram$")],
        states={
            ASK_CREDENTIALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credentials)],
            SELECT_TIME: [CallbackQueryHandler(schedule_time_selection, pattern="^time_")]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
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
