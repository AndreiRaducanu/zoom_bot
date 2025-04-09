import pytest
from unittest.mock import MagicMock, patch
from zoom_bot.bot import ZoomBot
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def fake_driver():
    """Mocked WebDriver instance."""
    mock_driver = MagicMock()
    return mock_driver

@pytest.fixture(autouse=True)
def fast_sleep():
    with patch("time.sleep", return_value=None):
        yield

@pytest.fixture
def bot(fake_driver):
    """ZoomBot instance using a mocked driver."""
    return ZoomBot(
        meeting_id="123456789",
        password="testpass",
        username="TestUser",
        driver=fake_driver
    )


def test_safe_find_element_found(bot):
    element = MagicMock()
    with patch("zoom_bot.bot.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.return_value = element
        found = bot.safe_find_element(By.ID, "some-id")
        assert found is element


def test_safe_click_success(bot):
    element = MagicMock()
    element.click = MagicMock()
    bot.safe_find_element = MagicMock(return_value=element)
    result = bot.safe_click(By.ID, "clickable")
    assert result is True
    element.click.assert_called_once()


def test_safe_click_fail(bot):
    bot.safe_find_element = MagicMock(return_value=None)
    result = bot.safe_click(By.ID, "non-clickable")
    assert result is False


def test_safe_send_keys_success(bot):
    element = MagicMock()
    bot.safe_find_element = MagicMock(return_value=element)
    result = bot.safe_send_keys(By.ID, "input-field", "hello")
    assert result is True
    element.send_keys.assert_called_with("hello")


def test_safe_send_keys_fail(bot):
    bot.safe_find_element = MagicMock(return_value=None)
    result = bot.safe_send_keys(By.ID, "input-field", "hello")
    assert result is False


def test__is_meeting_ended_by_host_true(bot):
    element = MagicMock()
    element.get_attribute.return_value = "This meeting has been ended by host"
    bot.safe_find_element = MagicMock(return_value=element)
    assert bot._is_meeting_ended_by_host() is True


def test__is_meeting_ended_by_host_false(bot):
    element = MagicMock()
    element.get_attribute.return_value = "Some other text"
    bot.safe_find_element = MagicMock(return_value=element)
    assert bot._is_meeting_ended_by_host() is False


def test_get_number_of_participants_valid(bot):
    child = MagicMock()
    child.get_attribute.return_value = "7"
    parent = MagicMock()
    parent.find_elements.return_value = [child]
    bot.safe_find_element = MagicMock(return_value=parent)
    assert bot.get_number_of_participants() == 7

def test_disable_mic_and_camera_fail(bot):
    bot.safe_click = MagicMock()
    bot.safe_find_element = MagicMock(side_effect=[None, None])  # Fails both checks
    assert bot._disable_mic_and_camera() is False

def test_check_valid_page_invalid(bot):
    bot.safe_find_element = MagicMock(return_value=MagicMock())
    assert bot._check_valid_page() is False

def test_join_meeting_wrong_password(bot):
    bot.driver.get = MagicMock()
    bot._check_valid_page = MagicMock(return_value=True)
    bot._disable_mic_and_camera = MagicMock(return_value=True)
    bot.safe_click = MagicMock()
    bot.safe_send_keys = MagicMock()
    bot.safe_find_element = MagicMock(side_effect=[
        MagicMock(),  # error-for-pwd (not first check)
    ])

    with pytest.raises(ValueError, match="Wrong password"):
        bot.join_meeting()

def test_is_time_to_disconnect_true(bot):
    bot._is_meeting_ended_by_host = MagicMock(return_value=True)
    assert bot.is_time_to_disconnect() is True

def test_is_time_to_disconnect_participants(bot):
    bot._is_meeting_ended_by_host = MagicMock(return_value=False)
    bot.get_number_of_participants = MagicMock(return_value=3)
    assert bot.is_time_to_disconnect() is True

def test_is_time_to_disconnect_false(bot):
    bot._is_meeting_ended_by_host = MagicMock(return_value=False)
    bot.get_number_of_participants = MagicMock(return_value=10)
    assert bot.is_time_to_disconnect() is False

def test_safe_find_elements_timeout(bot):
    with patch("zoom_bot.bot.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = TimeoutException()
        elements = bot.safe_find_elements(By.CLASS_NAME, "some-class")
        assert elements == []

def test_close(bot):
    bot.driver.quit = MagicMock()
    bot.close()
    bot.driver.quit.assert_called_once()

def test_get_number_of_participants_invalid_number(bot, caplog):
    child = MagicMock()
    child.get_attribute.return_value = "not-a-number"
    parent = MagicMock()
    parent.find_elements.return_value = [child]
    bot.safe_find_element = MagicMock(return_value=parent)

    with caplog.at_level(logging.ERROR):
        result = bot.get_number_of_participants()
    
    assert result is None or result == 0
    assert "Unable to get number of participats" in caplog.text
