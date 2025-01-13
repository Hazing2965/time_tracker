from datetime import timezone, timedelta

from dotenv import load_dotenv
from os import getenv


load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
PATH_DB = 'database.db'
MOSCOW_TIMEZONE = timezone(timedelta(hours=3))
FORMAT_DATE_AND_TIME = "%Y-%m-%d %H:%M:%S"
TEST_MODE = True