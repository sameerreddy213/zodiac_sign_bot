import logging
from apscheduler.schedulers.background import BackgroundScheduler
from instagrapi import Client
import os
import datetime
import time

# Configure Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.cl = Client()

    def login(self, username, password):
        """
        Attempts to login to Instagram.
        Returns True if successful, False otherwise.
        """
        try:
            self.cl.login(username, password)
            logger.info(f"Logged in as {username}")
            return True
        except Exception as e:
            logger.error(f"Failed to login: {e}")
            return False

    def upload_album(self, paths, caption, location_name="United States"):
        """
        Uploads an album (carousel) to Instagram.
        """
        try:
            logger.info(f"Uploading album with {len(paths)} images. Location: {location_name}")
            
            # 1. Resolve Location
            location = None
            if location_name:
                try:
                    locs = self.cl.location_search(location_name)
                    if locs:
                        location = locs[0]
                        logger.info(f"Found location: {location.name} ({location.pk})")
                except Exception as e:
                    logger.warning(f"Could not find location '{location_name}': {e}")

            # 2. Upload
            media = self.cl.album_upload(
                paths,
                caption=caption,
                location=location
            )
            logger.info(f"Upload successful! Media PK: {media.pk}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def schedule_post(self, username, password, paths, caption, run_date, location_name="United States"):
        """
        Schedules a post job.
        """
        logger.info(f"Scheduling post for {run_date}")
        
        # We need to wrap the job to login first (since credentials are transient)
        # Note: In a real robust app, we might persist session, but here we re-login.
        self.scheduler.add_job(
            self._execute_scheduled_post, 
            'date', 
            run_date=run_date, 
            args=[username, password, paths, caption, location_name]
        )
        return True

    def _execute_scheduled_post(self, username, password, paths, caption, location_name):
        logger.info("Executing scheduled post...")
        if self.login(username, password):
            self.upload_album(paths, caption, location_name)
        else:
            logger.error("Scheduled post failed: Could not login.")

# Global instance
ig_manager = InstagramManager()
