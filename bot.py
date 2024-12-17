import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import add_subscriber, disable_subscriber, get_subscribers, get_free_games
import logging

logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())

# Клавиатура с командами
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="/help")],
        [KeyboardButton(text="/subscribe"), KeyboardButton(text="/unsubscribe")],
        [KeyboardButton(text="/free_game")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Этот бот @{(await bot.get_me()).username} посвящен раздачам и бесплатным играм в Epic Games Store.",
        reply_markup=get_main_keyboard()
    )

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/subscribe - Подписаться на уведомления о раздачах\n"
        "/unsubscribe - Отписаться от уведомлений о раздачах\n"
        "/free_game - Узнать текущие бесплатные игры"
    )
    await message.answer(help_text)

# Команда /subscribe
@dp.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    await add_subscriber(message.from_user.id)
    await message.answer("Вы подписались на уведомления о раздачах игр в Epic Games Store!")

# Команда /unsubscribe
@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    await disable_subscriber(message.from_user.id)
    await message.answer("Вы отписались от уведомлений о раздачах игр в Epic Games Store!")

# Команда /free_game
@dp.message(Command("free_game"))
async def cmd_free_game(message: Message):
    games = await get_free_games()
    if games:
        message_text = "Сейчас в раздаче:\n"
        for game in games:
            message_text += f"- <a href='{game['link']}'>{game['name']}</a> бесплатно до {game['end_time']} по МСК\n"
        await message.answer(message_text)
    else:
        await message.answer("В данный момент бесплатных игр нет.")

# Уведомление подписчиков
async def notify_subscribers():
    previous_games = set()
    while True:
        # Получаем список бесплатных игр
        games = await get_free_games()

        # Преобразуем игры в набор для удобства сравнения
        games_set = set((game['name'], game['link'], game['end_time']) for game in games)

        # Находим новые игры, которых не было в предыдущем списке
        new_games = games_set - previous_games

        if new_games:
            subscribers = await get_subscribers()
            for user_id in subscribers:
                try:
                    # Формируем сообщение с новыми играми
                    message_text = "Появились новые раздачи:\n"
                    for game_name, game_link, game_end_time in new_games:
                        message_text += f"- <a href='{game_link}'>{game_name}</a> бесплатно до {game_end_time} по МСК\n"
                    # Отправляем сообщение пользователю
                    await bot.send_message(user_id, message_text)
                except Exception as e:
                    logging.error(f"Failed to notify user {user_id}: {e}")

            # Обновляем предыдущие игры для следующего сравнения
            previous_games = games_set

        # Проверка раздач каждые 20 минут
        await asyncio.sleep(1200)
