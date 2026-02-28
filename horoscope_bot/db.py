import os
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "conf.env")
load_dotenv(env_path)

logger = logging.getLogger(__name__)

# Initialize MongoDB client
MONGO_URI = os.getenv("MONGO_URI")

logger.info(f"Loaded MONGO_URI from env: {'YES' if MONGO_URI else 'NO'}")

client = None
db = None
collection = None

def init_db():
    global client, db, collection, MONGO_URI
    
    if not MONGO_URI:
        # Try loading again just in case
        env_path = os.path.join(os.path.dirname(__file__), "conf.env")
        load_dotenv(env_path)
        MONGO_URI = os.getenv("MONGO_URI")
        
    if MONGO_URI and collection is None:
        try:
            client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            db = client['horoscope_db']
            collection = db['horoscopes']
            # Send a ping to confirm a successful connection
            client.admin.command('ping')
            logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            logger.error(f"MongoDB Connection Error: {e}")
            collection = None
    elif not MONGO_URI:
        logger.warning("MONGO_URI not found in conf.env. Caching will be disabled.")
        
# init immediately
init_db()


def _get_collection(language="english"):
    """Helper to get the right collection dynamically based on language."""
    if db is None:
        return None
    
    # english -> horoscopes_en, telugu -> horoscopes_te
    suffix = 'en' if language.lower() == 'english' else 'te'
    return db[f'horoscopes_{suffix}']

def get_horoscopes(target_date: str, language: str = "english"):
    """
    Retrieve cached horoscopes for a specific date string, filtered by language.
    """
    coll = _get_collection(language)
    if coll is None:
        return None
        
    try:
        data = coll.find_one({"date": target_date})
        if data and "readings" in data:
            logger.info(f"Cache HIT for {target_date} ({language})")
            return data["readings"]
        
        logger.info(f"Cache MISS for {target_date} ({language})")
        return None
    except Exception as e:
        logger.error(f"Error reading from MongoDB: {e}")
        return None

def get_available_dates(language: str = "english"):
    """
    Returns a sorted list of unique date strings currently cached in MongoDB.
    """
    coll = _get_collection(language)
    if coll is None:
        return []
    try:
        dates = coll.distinct("date")
        # Sort them roughly by parsing if possible, or leave as strings
        return sorted(dates)
    except Exception as e:
        logger.error(f"Error fetching distinct dates from MongoDB: {e}")
        return []

def save_horoscopes(target_date: str, readings: list, language: str = "english"):
    """
    Save horoscopes to MongoDB under the correct language collection.
    """
    coll = _get_collection(language)
    logger.info(f"Attempting to save {language} horoscopes for date: {target_date}, count: {len(readings)}")
    if coll is None:
        logger.error(f"Cannot save horoscopes. DB is None.")
        return
        
    try:
        document = {
            "date": target_date,
            "readings": readings,
            "language": language,
            "created_at": datetime.utcnow()
        }
        
        coll.update_one(
            {"date": target_date},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Saved {language} horoscopes for {target_date} to MongoDB.")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}")

def cleanup_old_horoscopes(days_to_keep: int = 1, language: str = "english"):
    """
    Deletes cached horoscopes strictly older than Indian Yesterday.
    """
    coll = _get_collection(language)
    if coll is None:
        return
        
    import pytz
    from datetime import datetime, timedelta
    
    ist = pytz.timezone('Asia/Kolkata')
    today_ist = datetime.now(ist).date()
    yesterday_ist = today_ist - timedelta(days=1)
        
    try:
        # We need to process each document to parse the string date
        docs = coll.find({})
        deleted = 0
        for doc in docs:
            date_str = doc.get("date")
            if not date_str: continue
            try:
                # Website formats date as "24 February 2026"
                doc_date = datetime.strptime(date_str, "%d %B %Y").date()
                if doc_date < yesterday_ist:
                    coll.delete_one({"_id": doc["_id"]})
                    deleted += 1
            except Exception as e:
                pass
                
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old {language} horoscope records (older than IST yesterday: {yesterday_ist}).")
    except Exception as e:
        logger.error(f"Error cleaning up MongoDB: {e}")
