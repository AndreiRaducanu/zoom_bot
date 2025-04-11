import pytest
from zoom_bot.app import ZoomBot

#TODO: Update to test all css selectors
def test_css_selector_before_join():
    zoom_bot = ZoomBot('123', 'dummy_password', 'test_user', 1)
    with pytest.raises(ValueError, match="Invalid meeting ID"):
        zoom_bot.join_meeting()