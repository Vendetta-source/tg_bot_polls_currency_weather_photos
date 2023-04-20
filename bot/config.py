import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')
PHOTOS_API_KEY = os.getenv('PHOTOS_API_KEY')

if BOT_TOKEN is None:
    logging.error("The bot token was not found in environment variables")
    exit(1)
