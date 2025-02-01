from os import getenv
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_BOT_TOKEN = getenv('BOT_TOKEN')
IMEI_API = getenv('LOCAL_API')