import logging
import time
import threading
import schedule

logger = logging.getLogger(__name__)

def prefetch_daily_data():
    """
    Job that runs daily to pre-fetch tomorrow's and today's horoscopes 
    in both English and Telugu to populate the MongoDB cache.
    """
    logger.info("Starting daily scheduled pre-fetch job...")
    
    # We fetch for yesterday (-1), today (0) and tomorrow (1).
    days_to_fetch = [-1, 0, 1]
    
    from scraper import fetch_horoscope, get_horoscopes_by_date
    for day in days_to_fetch:
        try:
            # First map the offset to the actual website date
            check_data = fetch_horoscope("aries", day)
            date_str = check_data.get('date')
            if not date_str or date_str == "Unknown":
                logger.warning(f"⚠️ Scheduled Job: Could not determine date for offset {day}")
                continue
                
            for lang in ['english', 'telugu']:
                logger.info(f"Scheduled Job: Fetching for {date_str} (offset {day}) in language: {lang}")
                results = get_horoscopes_by_date(date_str, language=lang, fallback_offset=day)
                if results and len(results) == 12:
                    logger.info(f"✅ Scheduled Job: Successfully cached data for {date_str} ({lang})")
                else:
                    logger.warning(f"⚠️ Scheduled Job: Failed to cache complete data for {date_str} ({lang})")
        except Exception as e:
            logger.error(f"❌ Scheduled Job Error: offset {day} - {e}")

    logger.info("Daily scheduled pre-fetch job completed!")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    """
    Starts the scheduler background thread.
    """
    # Run every day at 08:00 AM server time (Assuming Server time is IST for this system setting)
    # The default system time of Windows is typically what schedule reads unless overridden
    schedule.every().day.at("08:00").do(prefetch_daily_data)
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info("Schedule thread started! Daily fetch set for 08:00.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
    while True:
        time.sleep(1)
