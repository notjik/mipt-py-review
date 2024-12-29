import os
import locale

from dotenv import load_dotenv

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
WEBDRIVER_PATH = os.getenv('WEBDRIVER_PATH')