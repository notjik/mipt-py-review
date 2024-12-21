import asyncio
import re
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db import add_user, get_users, \
    get_free_games, \
    get_features, get_genres, \
    subscribe_feature, unsubscribe_feature, subscribe_genre, unsubscribe_genre, \
    get_user_genres, get_user_features, get_genres_with_id, get_user_genres_with_id, subscribe_genre_by_id, \
    get_genre_name_by_id, get_features_with_id, get_user_features_with_id, subscribe_feature_by_id, \
    get_feature_name_by_id, unsubscribe_feature_by_id, unsubscribe_genre_by_id
from keyboards import *

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Этот бот @{(await bot.get_me()).username} посвящен раздачам и бесплатным играм в Epic Games Store.",
        reply_markup=get_main_keyboard()
    )
    await add_user(dp['pool'], message.from_user.id)


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/profile - Посмотреть свои подписки\n"
        "/subscribe - Подписаться на уведомления о раздачах\n"
        "/unsubscribe - Отписаться от уведомлений о раздачах\n"
        "/free_game - Узнать текущие бесплатные игры\n"
        "/free_game_from_subscriptions - Узнать текущие бесплатные игры"
    )
    await message.answer(help_text)


# Команда /profile
@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user_genres = await get_user_genres(dp['pool'], message.from_user.id)
    user_features = await get_user_features(dp['pool'], message.from_user.id)
    await message.answer(("Ваши подписки\n" +
                          (("\nЖанры:\n" + "\n".join(user_genres) + "\n") if user_genres else "") +
                          (("\nОсобенности:\n" + "\n".join(user_features) + "\n") if user_features else "")) \
                             if user_genres or user_features else "Вы пока ни на что не подписаны")


# Команда /subscribe - показывает меню подписок
@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    await message.answer("Выберите, на что хотите подписаться:", reply_markup=get_action_keyboard(True))


# Обработка подписки на жанр
@dp.callback_query(lambda c: '_subscribe_genre' in c.data)
async def process_genre_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    genres = await get_genres_with_id(dp['pool'])
    user_genres = await get_user_genres_with_id(dp['pool'], user_id)

    # Пытаемся извлечь страницу из callback_data для пагинации
    match = re.match(r"_page_subscribe_genres_(\d+)", callback_query.data)
    if match:
        page = int(match.group(1))
        # Обновляем клавиатуру для выбранной страницы жанров
        await callback_query.message.edit_text("Выберите жанр для подписки:",
                                               reply_markup=get_genre_keyboard(
                                                   genres, user_genres, True, page=page
                                               ))
        await callback_query.answer()

    # Обработка подписки на жанр
    match = re.match(r"_subscribe_genre_(\d+)", callback_query.data)
    if match:
        genre_id = int(match.group(1))
        # Оформляем подписку на жанр
        await subscribe_genre_by_id(dp['pool'], user_id, genre_id)
        genre_name = await get_genre_name_by_id(dp['pool'], genre_id)
        # Перенаправляем на текущую страницу жанров
        await callback_query.message.edit_text(f"Вы подписались на жанр: {genre_name}",
                                               reply_markup=get_genre_keyboard(
                                                   genres, user_genres, True
                                               ))
        await callback_query.answer()


# Обработка подписки на особенность
@dp.callback_query(lambda c: '_subscribe_feature' in c.data)
async def process_feature_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    features = await get_features_with_id(dp['pool'])
    user_features = await get_user_features_with_id(dp['pool'], user_id)

    # Пытаемся извлечь страницу из callback_data для пагинации
    match = re.match(r"_page_subscribe_features_(\d+)", callback_query.data)
    if match:
        page = int(match.group(1))
        # Обновляем клавиатуру для выбранной страницы особенностей
        await callback_query.message.edit_text("Выберите особенность для подписки:",
                                               reply_markup=get_feature_keyboard(
                                                   features, user_features, True, page=page
                                               ))
        await callback_query.answer()

    # Обработка подписки на особенность
    match = re.match(r"_subscribe_feature_(\d+)", callback_query.data)
    if match:
        feature_id = int(match.group(1))
        # Оформляем подписку на особенность
        await subscribe_feature_by_id(dp['pool'], user_id, feature_id)
        feature_name = await get_feature_name_by_id(dp['pool'], feature_id)
        # Перенаправляем на текущую страницу особенностей
        await callback_query.message.edit_text(f"Вы подписались на особенность: {feature_name}",
                                               reply_markup=get_feature_keyboard(
                                                   features, user_features, True
                                               ))
        await callback_query.answer()


# Обработка подписки на все жанры и особенности
@dp.callback_query(lambda c: c.data == '_subscribe_all')
async def subscribe_all(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Подписка на все жанры
    genres = await get_genres(dp['pool'])
    for genre in genres:
        await subscribe_genre(dp['pool'], user_id, genre)

    # Подписка на все особенности
    features = await get_features(dp['pool'])
    for feature in features:
        await subscribe_feature(dp['pool'], user_id, feature)

    await callback_query.message.edit_text("Вы подписались на все жанры и особенности!",
                                           reply_markup=get_void_inline())
    await callback_query.answer()


# Обработка кнопки "Назад" для возврата в меню подписок
@dp.callback_query(lambda c: c.data == '_back_to_menu_subscribe')
async def back_to_menu_subscribe(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите, на что хотите подписаться:",
                                           reply_markup=get_action_keyboard(True))
    await callback_query.answer()


# Обработка кнопки "Назад" для возврата в меню отписок
@dp.callback_query(lambda c: c.data == '_back_to_menu_unsubscribe')
async def back_to_menu_subscribe(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите, от чего хотите отписаться:",
                                           reply_markup=get_action_keyboard(False))
    await callback_query.answer()


# Команда /unsubscribe - показывает меню отписок
@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    await message.answer("Выберите, от чего хотите отписаться:", reply_markup=get_action_keyboard(False))


# Обработка отписки от жанра
@dp.callback_query(lambda c: '_unsubscribe_genre' in c.data)
async def process_genre_unsubscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    genres = await get_genres_with_id(dp['pool'])

    # Пытаемся извлечь страницу из callback_data для пагинации
    match = re.match(r"_page_unsubscribe_genres_(\d+)", callback_query.data)
    if match:
        page = int(match.group(1))
        user_genres = await get_user_genres_with_id(dp['pool'], user_id)
        # Обновляем клавиатуру для выбранной страницы жанров
        await callback_query.message.edit_text("Выберите жанр, от которого хотите отписаться:",
                                               reply_markup=get_genre_keyboard(genres, user_genres, False, page=page))
        await callback_query.answer()

    # Обработка отписки от жанра
    match = re.match(r"_unsubscribe_genre_(\d+)", callback_query.data)
    if match:
        genre_id = int(match.group(1))
        # Оформляем отписку от жанра
        await unsubscribe_genre_by_id(dp['pool'], user_id, genre_id)
        genre_name = await get_genre_name_by_id(dp['pool'], genre_id)
        user_genres = await get_user_genres_with_id(dp['pool'], user_id)
        # Перенаправляем на текущую страницу жанров
        await callback_query.message.edit_text(f"Вы отписались от жанра: {genre_name}",
                                               reply_markup=get_genre_keyboard(genres, user_genres, False))
        await callback_query.answer()


# Обработка отписки от особенности
@dp.callback_query(lambda c: '_unsubscribe_feature' in c.data)
async def process_feature_unsubscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    features = await get_features_with_id(dp['pool'])

    # Пытаемся извлечь страницу из callback_data для пагинации
    match = re.match(r"_page_unsubscribe_features_(\d+)", callback_query.data)
    if match:
        page = int(match.group(1))
        # Обновляем клавиатуру для выбранной страницы особенностей
        user_features = await get_user_features_with_id(dp['pool'], user_id)
        await callback_query.message.edit_text("Выберите особенность, от которой хотите отписаться:",
                                               reply_markup=get_feature_keyboard(features, user_features, False,
                                                                                 page=page))
        await callback_query.answer()

    # Обработка отписки от особенности
    match = re.match(r"_unsubscribe_feature_(\d+)", callback_query.data)
    if match:
        feature_id = int(match.group(1))
        # Оформляем отписку от особенности
        await unsubscribe_feature_by_id(dp['pool'], user_id, feature_id)
        feature_name = await get_feature_name_by_id(dp['pool'], feature_id)
        user_features = await get_user_features_with_id(dp['pool'], user_id)
        # Перенаправляем на текущую страницу особенностей
        await callback_query.message.edit_text(f"Вы отписались от особенности: {feature_name}",
                                               reply_markup=get_feature_keyboard(features, user_features, False))
        await callback_query.answer()


# Обработка отписки от всех жанров и особенностей
@dp.callback_query(lambda c: c.data == '_unsubscribe_all')
async def unsubscribe_all(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Отписка от всех жанров
    genres = await get_genres(dp['pool'])
    for genre in genres:
        await unsubscribe_genre(dp['pool'], user_id, genre)

    # Отписка от всех особенностей
    features = await get_features(dp['pool'])
    for feature in features:
        await unsubscribe_feature(dp['pool'], user_id, feature)

    await callback_query.message.edit_text("Вы отписались от всех жанров и особенностей!",
                                           reply_markup=get_void_inline())
    await callback_query.answer()


# Команда /free_game
@dp.message(Command("free_game"))
async def cmd_free_game(message: Message):
    games = await get_free_games(dp['pool'])
    if games:
        message_text = "Сейчас в раздаче:\n"
        for game in games:
            message_text += f"- <a href='{game['link']}'>{game['name']}</a> бесплатно до {game['end_time']} по МСК\n"
        await message.answer(message_text)
    else:
        await message.answer("В данный момент бесплатных игр нет.")


# Команда /free_game_from_subscriptions
@dp.message(Command("free_game_from_subscriptions"))
async def cmd_free_game_from_subscriptions(message: Message):
    games = await get_free_games(dp['pool'])
    user_genres = set(await get_user_genres(dp['pool'], message.from_user.id))  # Подписки по жанрам
    user_features = set(await get_user_features(dp['pool'], message.from_user.id))  # Подписки по особенностям
    likely_games = []
    message_text = "Сейчас в раздаче:\n"
    for game in games:
        if set(game['genres']) & user_genres or set(game['features']) & user_features:
            likely_games.append(
                f"- <a href='{game['link']}'>{game['name']}</a> бесплатно до {game['end_time']} по МСК\n")
    await message.answer(
        message_text + ''.join(likely_games) if likely_games else "В данный момент бесплатных игр нет.")


# Уведомление пользователей
async def notify_subscribers(pool):
    # Запоминаем все игры на старте
    previous_games = set((game['name'], game['link'], game['end_time'], frozenset(game['genres']),
                          frozenset(game['features'])) for game in await get_free_games(pool))
    # Бесконечный цикл для постоянной проверки
    while True:
        # Получаем список бесплатных игр с жанрами и особенностями
        games = await get_free_games(pool)

        # Преобразуем игры в набор для удобства сравнения
        games_set = set((game['name'], game['link'], game['end_time'], frozenset(game['genres']),
                         frozenset(game['features'])) for game in games)

        # Находим новые игры, которых не было в предыдущем списке
        new_games = games_set - previous_games

        if new_games:
            # Получаем подписчиков и их жанры и особенности
            subscribers = await get_users(pool)

            for user_id in subscribers:
                try:
                    # Получаем подписки пользователя
                    user_genres = set(await get_user_genres(pool, user_id))  # Подписки по жанрам
                    user_features = set(await get_user_features(pool, user_id))  # Подписки по особенностям

                    # Формируем список новых игр, которые подходят для данного пользователя
                    relevant_games = []
                    for game in new_games:
                        game_name, game_link, game_end_time, game_genres, game_features = game

                        # Проверяем, совпадают ли жанры или особенности игры с подписками пользователя
                        if user_genres & game_genres or user_features & game_features:
                            relevant_games.append((game_name, game_link, game_end_time))

                    # Если есть подходящие игры для пользователя
                    if relevant_games:
                        message_text = "Появились новые раздачи:\n"
                        for game_name, game_link, game_end_time in relevant_games:
                            message_text += f"- <a href='{game_link}'>{game_name}</a> бесплатно до {game_end_time} по МСК\n"

                        # Отправляем сообщение пользователю
                        await bot.send_message(user_id, message_text)

                except Exception as e:
                    logging.error(f"Failed to notify user {user_id}: {e}")

            # Обновляем предыдущие игры для следующего сравнения
            previous_games = games_set

        # Проверка раздач каждые 20 минут
        await asyncio.sleep(1200)
