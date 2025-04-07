import os
import sys
import logging
from zoom_bot.bot import ZoomBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_bot() -> ZoomBot:
    meeting_id = os.environ.get("ZOOM_MEETING_ID")
    meeting_password = os.environ.get("ZOOM_MEETING_PASSWORD")
    username = os.environ.get("ZOOM_USERNAME")

    if not all([meeting_id, meeting_password, username]):
        logger.error("Missing one or more required environment variables..")
        sys.exit(1)

    return ZoomBot(
        meeting_id=meeting_id,
        password=meeting_password,
        username=username,
        cooldown=10
    )


def main():
    bot = setup_bot()
    try:
        bot.join_meeting()
    except Exception as e:
        logger.error(f"Bot failed: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
