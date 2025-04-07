import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import logging

logger = logging.getLogger(__name__)


class ZoomBot:
    def __init__(
        self,
        meeting_id: int,
        password: str,
        username: str,
        cooldown: int = 5
    ):
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
        # Settings for mic / video
        self.chrome_options.add_argument("--use-fake-ui-for-media-stream")  
        self.chrome_options.add_argument("--use-fake-device-for-media-stream") 
        prefs = {
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.media_stream_mic": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        

        logger.info("Initiliazing chrome driver..")
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            logger.info("Chrome driver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise RuntimeError

    def join_meeting(self):
        try:
            logger.info(f"Joining Zoom Meeting {self.meeting_id} as {self.username}..")
            self.driver.get(f"https://zoom.us/wc/join/{self.meeting_id}")
        except Exception as e:
            logger.error(
                f"Unable to joing meeting: \n{e}"
            )
            self.close()

        time.sleep(self.cooldown)

        logger.info("Removing cookie pop-ups..")
        self.safe_click(By.ID, "onetrust-reject-all-handler")

        if not self._check_valid_page():
            raise ValueError("Invalid meeting ID")
        logger.info("Valid meeting..")

        logger.info("Accepting terms and conditions..")
        self.safe_click(By.ID, "wc_agree1")

        time.sleep(self.cooldown)

        logger.info("Disabling mic and camera..")
        if not self._disable_mic_and_camera():
            raise RuntimeError("Failed to disable mic or camera..")

        self.safe_send_keys(By.ID, "input-for-pwd", self.password)
        self.safe_send_keys(By.ID, "input-for-name", self.username)

        logger.info("Joining meeting..")
        self.safe_click(By.CSS_SELECTOR, "button.preview-join-button")

        if self.safe_find_element(By.ID, "error-for-pwd"):
            raise ValueError("Wrong password")
        if self.safe_find_element(By.ID, "error-for-name"):
            raise ValueError("Name too long")
        logger.info("Successfully joined the meeting..")

        self.check_and_disconnect()

    def check_and_disconnect(self):
        time.sleep(300)
        if self.is_time_to_disconnect():
            logger.info("Time to disconnect..")
        else:
            self.check_and_disconnect()

    def is_time_to_disconnect(self):
        try:
            return(self._is_meeting_ended_by_host() or self.get_number_of_participants() <= 4)
        except Exception as e:
            logger.info(f"Unable to determine if it's time to disconnect {e}..")
            return False

    def get_number_of_participants(self) -> int:
        parent_element = self.safe_find_element(By.CLASS_NAME, 'footer-button__number-counter')
        children_element = parent_element.find_elements(By.XPATH, '*')
        try:
            return int(children_element[0].get_attribute('textContent'))
        except Exception as e:
            logger.error(f"Unable to get number of participats {e}")

    def list_all_span_text(self):
        spans = self.safe_find_elements(By.TAG_NAME, "span")
        for span in spans:
            print(span.text)

    def safe_find_element(self, by, value, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            logger.info(f"Successfully found element by {str(by)}={value}..")
            return element
        except (NoSuchElementException, TimeoutException, WebDriverException):
            return None
    
    def safe_find_elements(self, by, value, timeout=5):
        logger.info(f"Finding all elements by {str(by)}={value}..")
        try:
            elements = WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
            if elements:
                logger.info(f"Found {len(elements)} elements by {str(by)}={value}.")
            else:
                logger.info(f"No elements found by {str(by)}={value}.")
            return elements
        except TimeoutException:
            logger.info(f"Did not find elements by {str(by)}={value}.")
            return []

    def safe_click(self, by, value):
        """Finds an element and clicks it if present."""
        time.sleep(4) # delay every click
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

    def close(self):
        print("Closing Zoom bot...")
        self.driver.quit()

    def _check_valid_page(self):
        logger.info("Checking if page loaded properly..")
        return not self.safe_find_element(By.CLASS_NAME, 'error-message')

    def _disable_mic_and_camera(self):
        self.safe_click(By.ID, "preview-video-control-button"),
        self.safe_click(By.ID, "preview-audio-control-button")
        return all([
            self.safe_find_element(By.CSS_SELECTOR, '[aria-label="Start Video"]'),
            self.safe_find_element(By.CSS_SELECTOR, '[aria-label="Unmute"]')
        ])

    def _is_meeting_ended_by_host(self):
        end_body = self.safe_find_element(By.CLASS_NAME, "zm-modal-body-title")
        end_message = "This meeting has been ended by host"
        if end_body is not None and end_body.get_attribute('textContent') == end_message:
            logger.info(end_message)
            return True
        return False
