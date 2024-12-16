from telegram import Bot
from environs import Env

env = Env()
env.read_env()

TELEGRAM_BOT_TOKEN = env("API_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_message(chat_id: int, text: str):
    await bot.send_message(chat_id=chat_id, text=text)

async def send_photo(chat_id: int, photo_path: str):
    await bot.send_photo(chat_id=chat_id, photo=open(photo_path, "rb"))