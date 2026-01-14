
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
            return {"sign": sign, "text": "Could not retrieve text.", "date": "Unknown", "count": 0}

        count = len(text)
        return {"sign": sign, "text": text, "date": date, "count": count}


    except Exception as e:
        logger.error(f"Error fetching {sign}: {e}")
        return {"sign": sign, "text": "Error fetching data.", "count": 0}



def fetch_all_horoscopes(day: int):
    """
    Fetches horoscopes for all 12 signs concurrently.
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Fetch raw text
        future_to_sign = {executor.submit(fetch_horoscope, sign, day): sign for sign in ZODIAC_SIGNS}
        
        for future in concurrent.futures.as_completed(future_to_sign):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                logger.error(f"Generated an exception: {exc}")

    # Now enhance text (sequentially or parallel? Parallel is faster but rate limits might apply. Let's do parallel 4 workers)
    # Actually, let's just do it in the same loop or a second pass. 
    # Let's do a second pass for enhancement to keep logic clean.
    
    # Sort results to maintain zodiac order
    results.sort(key=lambda x: ZODIAC_SIGNS.index(x['sign']))
    return results

if __name__ == "__main__":
    # Test run for Today
    print("Fetching Today's Horoscopes...")
    daily_results = fetch_all_horoscopes(0)
    for res in daily_results[:2]: # Print first 2 to check
        print(f"--- {res['sign'].upper()} ---")
        print(res['text'])
        print(f"Count: {res['count']}\n")
