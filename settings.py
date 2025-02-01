from os import getenv
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_BOT_TOKEN = getenv('BOT_TOKEN')

IMEI_API = getenv('LOCAL_API')
IMEI_CHECK_URL = getenv('IMEI_CHECK_URL')
SERVICEID = 12

SECRET_KEY = getenv('SECRET_KEY')

DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_NAME = getenv('DB_NAME')
DB_HOST = getenv('DB_HOST')
