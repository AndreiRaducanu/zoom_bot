import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


class ZoomBot:
    def __init__(self, meeting_id, password, username, cooldown=1, headless=False):
        self.meeting_id = meeting_id
        self.password = password
        self.username = username
        self.cooldown = cooldown

        # Set up Chrome options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")

        if headless:
            self.chrome_options.add_argument("--headless")  # Run in headless mode

        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def safe_find_element(self, by, value, timeout=5):
        """Finds an element and returns it, or None if not found."""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except (NoSuchElementException, TimeoutException):
            return None
    
    def safe_find_elements(self, by, value, timeout=5):
        """Finds elements and returns them, or an empty list if not found."""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            return []
    
    def list_all_span_text(self):
        """Lists all span texts on the page."""
        print("Listing all span texts...")

        # Get all <span> elements on the page
        spans = self.safe_find_elements(By.TAG_NAME, "span")

        # Print the text of each <span> element
        for span in spans:
            print(span.text)

    def safe_click(self, by, value):
        """Finds an element and clicks it if present."""
        element = self.safe_find_element(by, value)
        if element:
            element.click()
            time.sleep(self.cooldown)  # Avoid accidental rate limiting
            return True
        return False

    def safe_send_keys(self, by, value, keys):
        """Finds an element and sends keys if present."""
        element = self.safe_find_element(by, value)
        if element:
            element.clear()
            element.send_keys(keys)
            return True
        return False

    def join_meeting(self):
        """Joins a Zoom meeting using the web client."""
        print(f"Joining Zoom Meeting {self.meeting_id} as {self.username}...")

        # Open Zoom web client
        self.driver.get(f"https://zoom.us/wc/join/{self.meeting_id}")
        time.sleep(1)  # Allow page to load

        # Handle cookie popups if present
        self.safe_click(By.ID, "onetrust-reject-all-handler")

        # Accept terms if present
        self.safe_click(By.ID, "wc_agree1")

        # Continue without mic/camera
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

        print("Successfully joined the meeting!")
    
        counter_element = self.driver.find_element(By.CLASS_NAME, "footer-button__number-counter")
        counter_value = counter_element.text
        print(counter_value)  # Output: "2"


    def close(self):
        """Closes the browser session."""
        print("Closing Zoom bot...")
        self.driver.quit()

    def __del__(self):
        """Ensure the WebDriver quits when the instance is deleted."""
        self.close()


# === Example Usage ===
if __name__ == "__main__":
    meeting_id = os.environ.get("ZOOM_MEETING_ID")
    meeintg_password = os.environ.get("ZOOM_MEETING_PASSWORD")
    username = os.environ.get("ZOOM_USERNAME")
    bot = ZoomBot(meeting_id="87452716996", password="5FCATQwjgTUYPp5frKblFiQbgqCEzy", username="Impostor", cooldown=1, headless=False)
    try:
        bot.join_meeting()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.close()
