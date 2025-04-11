import os
from pathlib import Path
import random
import sys
import logging
import threading
import time
from typing import Dict, List
from dotenv import dotenv_values
from zoom_bot.bot import ZoomBot
from zoom_bot.infrastructure.logging import configure_logging

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logger = configure_logging()

env_path = Path("/home/ubuntu/.env")
env_data = dotenv_values(env_path)
logger.info((f"Loaded .env from: {env_path}"))


class ZoomBotManager:
    def __init__(self):
        self.bots: List[ZoomBot] = []
        self.threads: List[threading.Thread] = []
        self.bot_status: Dict[str, str] = {} 
        self.lock = threading.Lock()  
        self.running = False
    
    def add_bot(self, meeting_id: str, password: str, username: str):
        bot = ZoomBot(
            meeting_id=meeting_id,
            password=password,
            username=username,
            cooldown=random.uniform(5, 11)  # Random cooldown to avoid detection
        )
        self.bots.append(bot)
        self.bot_status[username] = "Ready"
        return bot
    
    def add_bots_from_config(self, config: List[Dict]):

        for bot_config in config:
            self.add_bot(
                meeting_id=bot_config["meeting_id"],
                password=bot_config["password"],
                username=bot_config["username"]
            )

    def start_bot(self, bot: ZoomBot):
        if not hasattr(threading.current_thread(), '_username'):
            threading.current_thread()._username = bot.username
        try:
            with self.lock:
                self.bot_status[bot.username] = "Starting"
            
            logger.info(f"Starting bot for user: {bot.username}")
            bot.join_meeting()
            
            with self.lock:
                self.bot_status[bot.username] = "Connected"
                
        except Exception as e:
            logger.error(f"Bot {bot.username} failed: {e}")
            with self.lock:
                self.bot_status[bot.username] = f"Error: {str(e)}"
        finally:
            bot.close()
            with self.lock:
                self.bot_status[bot.username] = "Disconnected"
    

    def run_all(self, max_threads: int = 20):
        self.running = True
        logger.info(f"Starting {len(self.bots)} bots")
        
        for bot in self.bots:
            while threading.active_count() >= max_threads:
                time.sleep(1)
            
            thread = threading.Thread(target=self.start_bot, args=(bot,))
            thread.start()
            self.threads.append(thread)
            logger.info(f"Started thread for {bot.username} (Threads: {threading.active_count()})")
        
        logger.info(f"Total threads launched: {len(self.threads)}")  # Should match bot count
    

    def monitor_bots(self):
        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            logger.info("\n=== Zoom Bot Status ===")  
            with self.lock:
                for username, status in self.bot_status.items():
                    logger.info(f"{username}: {status}")  
            time.sleep(2)
    
    def shutdown(self):
        self.running = False
        logger.info("Shutting down all bots...")
        for bot in self.bots:
            try:
                bot.close()
            except:
                pass
        
        for thread in self.threads:
            thread.join(timeout=5)
        
        logger.info("All bots have been shut down")

def load_config() -> List[Dict]:
    meeting_id = os.environ.get("ZOOM_MEETING_ID", "123")
    meeting_password = os.environ.get("ZOOM_MEETING_PASSWORD", "pass")

    num_users = int(os.environ.get("NUM_USERS", 2))
    users = []
    
    for i in range(1, num_users + 1):
        username = os.environ.get(f"ZOOM_USERNAME_{i}", f"Student{i}")
        users.append({
            "meeting_id": meeting_id,
            "password": meeting_password,
            "username": username
        })
    
    return users


def get_users(index=1, users=None) -> List[Dict]:
    if users is None:
        users = []
        logger.info("Loading user configurations...")

    try:
        prefix = f"USER{index}_"
        name = env_data.get(f"{prefix}NAME")
        meeting_id = env_data.get(f"{prefix}MEETING_ID")
        password = env_data.get(f"{prefix}PASSWORD")

        if not all([name, meeting_id, password]):
            logger.info(f"No more users found after index {index-1}")
            return users

        users.append({
            "username": name,
            "meeting_id": meeting_id,
            "password": password
        })
        logger.info(f"Added user {index}: {name}")
        return get_users(index + 1, users)
    except Exception as e:
        logger.error(f"Error loading user config at index {index}: {str(e)}")
        return users

def main():
    threading.current_thread()._username = "Main"
    logger.info("Initializing bot manager..")
    manager = ZoomBotManager()
    
    logger.info("Getting user info..")
    users = get_users()
    logger.info("Add bots to manager..")
    manager.add_bots_from_config(users)
    
    monitor_thread = threading.Thread(
        target=manager.monitor_bots,
        name="MonitorThread",
        daemon=True
    )
    logger.info("Starting thread..")
    monitor_thread.start()
    
    try:
        manager.run_all(max_threads=20)
        while any(t.is_alive() for t in manager.threads):
            time.sleep(1)
        
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal...")
    finally:
        manager.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()