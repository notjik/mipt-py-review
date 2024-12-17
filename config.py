import os

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')