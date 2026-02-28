
import requests
from bs4 import BeautifulSoup
import logging
import concurrent.futures
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv("conf.env")

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ZODIAC_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

def fetch_horoscope(sign: str, day: int = 0):
    """
    Fetches the horoscope for the given zodiac sign.
    day: 0 for Today, 1 for Tomorrow.
    """
    sign = sign.lower()
    # URL structure: ?day=0 (today), ?day=1 (tomorrow)
    url = f"https://astrology.com.au/horoscopes/daily-horoscopes/{sign}?day={day}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        text = ""
        date = ""
        
        # Extract Date
        # Based on analysis, date is in <h3 class="center" style="text-align: center;">14 January 2026</h3>
        date_elem = soup.select_one('h3.center')
        if date_elem:
            date = date_elem.get_text(strip=True)

        # Strategy 1: Primary Target (Full Text)
        full_text_div = soup.select_one('div.daily-horoscope-text')
        if full_text_div:
            text = full_text_div.get_text(separator=' ', strip=True)
            # Extra cleanup
            text = " ".join(text.split())
        else:
            # Strategy 2: Fallback Target (Sidebar Summary)
            sidebar_div = soup.select_one(f'div#day_{sign} p')
            if sidebar_div:
                text = sidebar_div.get_text(separator="\n", strip=True)
                # If we are falling back, it might not be specific to "tomorrow" if the sidebar doesn't update dynamically via JS query param,
                # but this is the best effort given the structure.
        
        if not text:
            logger.warning(f"Could not retrieve text for {sign} on day {day}. Text div missing or empty.")
            return {"sign": sign, "text": "Could not retrieve text.", "date": "Unknown", "count": 0}

        count = len(text)
        logger.info(f"Successfully scraped {sign} (Day {day}, length: {count})")
        return {"sign": sign, "text": text, "date": date, "count": count}


    except Exception as e:
        logger.error(f"Error fetching {sign} (Day {day}): {e}")
        return {"sign": sign, "text": "Error fetching data.", "count": 0}



def _scrape_offset(day: int):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_sign = {executor.submit(fetch_horoscope, sign, day): sign for sign in ZODIAC_SIGNS}
        for future in concurrent.futures.as_completed(future_to_sign):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logger.error(f"Generated an exception: {exc}")
    results.sort(key=lambda x: ZODIAC_SIGNS.index(x['sign']))
    return results

def get_horoscopes_by_date(target_date: str, language: str = "english", fallback_offset: int = None):
    """
    Fetches horoscopes exactly by the target date string.
    If not in DB, it scrapes using the optionally provided fallback_offset and caches it.
    """
    import db
    
    # 1. Check DB Cache explicitly for this date and language
    cached_data = db.get_horoscopes(target_date, language=language)
    if cached_data:
        logger.info(f"Returning CACHED data for {target_date} ({language}).")
        return cached_data

    logger.info(f"No {language} cache found for {target_date}. Need to fetch/translate...")
    
    # If asking for Telugu, we can check if English is cached first to save scraping time
    if language == "telugu":
        english_data = db.get_horoscopes(target_date, language="english")
        if english_data:
            from translator import translate_to_telugu
            logger.info("Translating existing English DB cache to Telugu...")
            telugu_results = []
            for res in english_data:
                telugu_res = res.copy()
                telugu_res['text'] = translate_to_telugu(res['text'])
                telugu_results.append(telugu_res)
            db.save_horoscopes(target_date, telugu_results, language="telugu")
            return telugu_results
            
    # 2. Not in Cache - Fetch From Website ONLY if we have an offset
    if fallback_offset is not None:
        logger.info(f"Scraping source website offset {fallback_offset} for expected date {target_date}...")
        results = _scrape_offset(fallback_offset)
        
        if results and len(results) == 12:
            fetched_date = results[0].get('date', target_date)
            
            # Save English baseline to DB 
            logger.info(f"Saving scraped English data for {fetched_date} into DB.")
            db.save_horoscopes(fetched_date, results, language="english")
            db.cleanup_old_horoscopes(1, language="english")
            
            if language == "telugu":
                from translator import translate_to_telugu
                logger.info("Translating freshly scraped data to Telugu...")
                telugu_results = []
                for res in results:
                    telugu_res = res.copy()
                    telugu_res['text'] = translate_to_telugu(res['text'])
                    telugu_results.append(telugu_res)
                db.save_horoscopes(fetched_date, telugu_results, language="telugu")
                db.cleanup_old_horoscopes(1, language="telugu")
                return telugu_results
            
            return results
        else:
            logger.warning("Scrape failed to return 12 signs.")
            
    return None

if __name__ == "__main__":
    # Test run for Today
    print("Fetching Today's Horoscopes...")
    daily_results = get_horoscopes_by_date("28 February 2026", fallback_offset=0)
    if daily_results:
        for res in daily_results[:2]: 
            print(f"--- {res['sign'].upper()} ---")
            print(res['text'])
            print(f"Count: {res['count']}\n")
