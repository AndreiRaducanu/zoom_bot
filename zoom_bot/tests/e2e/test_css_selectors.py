import pytest
from zoom_bot.app import ZoomBot


def test_css_selector_before_join():
    zoom_bot = ZoomBot('1', 'dummy_pass', 'test_user', 1)
    with pytest.raises(ValueError, match="Wrong password"):
        zoom_bot.join_meeting()