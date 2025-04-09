import logging
from threading import current_thread

class ContextFilter(logging.Filter):
    def filter(self, record):
        thread_name = current_thread().name
        if hasattr(current_thread(), '_username'):
            record.username = current_thread()._username
        elif 'ZoomBotThread' in thread_name:
            parts = thread_name.split('-')
            record.username = parts[-1] if len(parts) > 2 else thread_name
        else:
            record.username = thread_name
        return True

class RepetitiveMessageFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.blocked_phrases = [
            "footer-button__number-counter"
            # Add other repetitive phrases here
        ]
    
    def filter(self, record):
        message = record.getMessage()
        return not any(phrase in message for phrase in self.blocked_phrases)


def configure_logging():
    formatter = logging.Formatter(
        "%(asctime)s - [%(username)s] - %(levelname)s - %(message)s"
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    handler.addFilter(ContextFilter())
    handler.addFilter(RepetitiveMessageFilter())
    
    logging.getLogger('selenium.webdriver.remote').setLevel(logging.WARNING)
    logging.getLogger('selenium.webdriver.common').setLevel(logging.WARNING)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True
    )
    
    return logging.getLogger(__name__)
