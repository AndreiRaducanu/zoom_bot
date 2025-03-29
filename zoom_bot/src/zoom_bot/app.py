import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Ensure logs print to console
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 


class ZoomBot:
    def __init__(self, meeting_id, password, username, cooldown=1):
        self.meeting_id = meeting_id
        self.password = password
        self.username = username
        self.cooldown = cooldown

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")  # mandatory
        self.chrome_options.add_argument("--no-sandbox") # mandatory
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        

        logger.info("Initiliazing chrome driver..")
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            logger.info("Chrome driver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def safe_find_element(self, by, value, timeout=5):
        """Finds an element and returns it, or None if not found."""
        logger.info(f"Finding element by {str(by)}={value}..")
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except (NoSuchElementException, TimeoutException):
            return None
    
    def safe_find_elements(self, by, value, timeout=5):
        logger.info(f"Finding all elements by {str(by)}={value}..")
        """Finds elements and returns them, or an empty list if not found."""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            return []
    
    def list_all_span_text(self):
        spans = self.safe_find_elements(By.TAG_NAME, "span")
        for span in spans:
            print(span.text)

    def safe_click(self, by, value):
        """Finds an element and clicks it if present."""
        element = self.safe_find_element(by, value)
        if element:
            logger.info(f"Clicking element found by {str(by)}={value}..")
            element.click()
            time.sleep(self.cooldown)  # Avoid accidental rate limiting
            return True
        return False

    def safe_send_keys(self, by, value, keys):
        """Finds an element and sends keys if present."""
        element = self.safe_find_element(by, value)
        if element:
            logger.info(f"Sending input {keys} to element found by {str(by)}={value}..")
            element.clear()
            element.send_keys(keys)
            return True
        return False

    def _check_valid_page(self):
        logger.info("Checking if page loaded properly..")
        return not self.safe_find_element(By.CLASS_NAME, 'error-message')

    def join_meeting(self):
        logger.info(f"Joining Zoom Meeting {self.meeting_id} as {self.username}..")
        self.driver.get(f"https://zoom.us/wc/join/{self.meeting_id}")
        time.sleep(1)  # Allow page to load

        logger.info("Removing cookie pop-ups..")
        self.safe_click(By.ID, "onetrust-reject-all-handler")

        self._check_valid_page()

        # Accept terms if present
        logger.info("Accepting terms and conditions..")
        self.safe_click(By.ID, "wc_agree1")

        # Continue without mic/camera
        logger.info("Skip pass mic & camera..")
        self.safe_click(By.CLASS_NAME, "continue-without-mic-camera")
        self.safe_click(By.CLASS_NAME, "continue-without-mic-camera")  # Might need a second click

        # Enter meeting credentials
        self.safe_send_keys(By.ID, "input-for-pwd", self.password)
        self.safe_send_keys(By.ID, "input-for-name", self.username)

        # Click join button
        self.safe_click(By.CSS_SELECTOR, "button.preview-join-button")

        # Check for errors
        if self.safe_find_element(By.ID, "error-for-pwd"):
            raise ValueError("Wrong password")
        if self.safe_find_element(By.ID, "error-for-name"):
            raise ValueError("Name too long")
        logger.info("Successfully joined the meeting..")

        while True:
            time.sleep(3)
            if self.is_time_to_disconnect():
                logger.info("Time to disconnect..")
                break

    def close(self):
        """Closes the browser session."""
        print("Closing Zoom bot...")
        self.driver.quit()

    def __del__(self):
        """Ensure the WebDriver quits when the instance is deleted."""
        self.close()
    
    def get_number_of_participants(self) -> int:
        parent_element = self.safe_find_element(By.CLASS_NAME, 'footer-button__number-counter')
        children_element = parent_element.find_elements(By.XPATH, '*')
        try:
            return int(children_element[0].get_attribute('textContent'))
        except Exception as e:
            print(f"Unable to get number of participats {e}")
    
    def is_time_to_disconnect(self):
        try:
            return(self.get_number_of_participants() <= 4)
        except Exception as e:
            logger.info(f"Unable to determine if it's time to disconnect {e}..")


# === Example Usage ===
if __name__ == "__main__":
    meeting_id = os.environ.get("ZOOM_MEETING_ID")
    meeintg_password = os.environ.get("ZOOM_MEETING_PASSWORD")
    username = os.environ.get("ZOOM_USERNAME")
    bot = ZoomBot(meeting_id=meeting_id, password=meeintg_password, username=username, cooldown=1, headless=False)
    try:
        bot.join_meeting()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.close()
