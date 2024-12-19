import asyncpg
import logging

from config import DATABASE_URL
from datetime import timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Пул соединений для улучшения производительности
async def init_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)


async def init_db(pool):
    async with pool.acquire() as conn:
        try:
            # Создание таблицы подписчиков
            await conn.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                active BOOLEAN DEFAULT TRUE
            );''')

            # Создание таблицы игр
            await conn.execute('''CREATE TABLE IF NOT EXISTS games (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT NOT NULL,
                end_time TIMESTAMP NOT NULL,
                UNIQUE(name, link)
            );''')

            # Создание таблицы жанров
            await conn.execute('''CREATE TABLE IF NOT EXISTS genres (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );''')

            # Создание таблицы особенностей
            await conn.execute('''CREATE TABLE IF NOT EXISTS features (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );''')

            # Промежуточная таблица для связи игр и жанров
            await conn.execute('''CREATE TABLE IF NOT EXISTS game_genres (
                game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
                genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
                PRIMARY KEY (game_id, genre_id)
            );''')

            # Промежуточная таблица для связи игр и особенностей
            await conn.execute('''CREATE TABLE IF NOT EXISTS game_features (
                game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
                feature_id INTEGER REFERENCES features(id) ON DELETE CASCADE,
                PRIMARY KEY (game_id, feature_id)
            );''')

            await conn.execute('''CREATE TABLE IF NOT EXISTS user_genres (
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, genre_id)
            );''')
            await conn.execute('''CREATE TABLE IF NOT EXISTS user_features (
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            feature_id INTEGER REFERENCES features(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, feature_id)
            );''')
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise e


async def add_user(pool, user_id: int):
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO UPDATE SET active = TRUE;
            """, user_id)
    except Exception as e:
        logger.error(f"Ошибка при добавлении подписчика: {e}")
        raise e


async def disable_user(pool, user_id: int):
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
            UPDATE users SET active = FALSE WHERE user_id = $1;
            """, user_id)
    except Exception as e:
        logger.error(f"Ошибка при деактивации подписчика: {e}")
        raise e


async def get_users(pool):
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT user_id FROM users WHERE active = TRUE;')
            return [row['user_id'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении подписчиков: {e}")
        raise e


async def add_genre(pool, name: str):
    """Добавляет жанр в таблицу genres."""
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO genres (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;
            """, name)
    except Exception as e:
        logger.error(f"Ошибка при добавлении жанра: {e}")
        raise e

async def get_genre_name_by_id(pool, genre_id: int):
    """Получает все жанры из таблицы genres."""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetch("""
            SELECT name FROM genres WHERE id = $1;
            """, genre_id)
            return row[0]['name'] if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении жанров: {e}")
        raise e

async def get_genres(pool):
    """Получает все жанры из таблицы genres."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT name FROM genres;
            """)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении жанров: {e}")
        raise e


async def get_genres_with_id(pool):
    """Получает все жанры из таблицы genres."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT id, name FROM genres;
            """)
            return [(row['id'], row['name']) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении жанров: {e}")
        raise e


async def add_feature(pool, name: str):
    """Добавляет особенность в таблицу features."""
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO features (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;
            """, name)
    except Exception as e:
        logger.error(f"Ошибка при добавлении особенности: {e}")
        raise e


async def get_feature_name_by_id(pool, feature_id: int):
    """Получает все жанры из таблицы genres."""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetch("""
            SELECT name FROM features WHERE id = $1;
            """, feature_id)
            return row[0]['name'] if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении особенности: {e}")
        raise e


async def get_features(pool):
    """Получает все особенности из таблицы features."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT name FROM features;
            """)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении особенностей: {e}")
        raise e


async def get_features_with_id(pool):
    """Получает все особенности из таблицы features."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT id, name FROM features;
            """)
            return [(row['id'], row['name']) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении особенностей: {e}")
        raise e


async def save_games(pool, games):
    """Сохраняет игры и их жанры/особенности в БД."""
    try:
        async with pool.acquire() as conn:
            for game in games:
                # Сохранение игры
                await conn.execute("""
                INSERT INTO games (name, link, end_time) VALUES ($1, $2, $3)
                ON CONFLICT (name, link) DO UPDATE SET end_time = EXCLUDED.end_time;
                """, game['name'], game['link'], game['end_time'])

                # Получаем ID игры
                game_id = await conn.fetchval("""
                SELECT id FROM games WHERE name = $1 AND link = $2;
                """, game['name'], game['link'])

                # Сохранение жанров
                for genre in game.get('genres', []):
                    genre_id = await conn.fetchval("SELECT id FROM genres WHERE name = $1;", genre)
                    await conn.execute("""
                    INSERT INTO game_genres (game_id, genre_id) VALUES ($1, $2) ON CONFLICT DO NOTHING;
                    """, game_id, genre_id)

                # Сохранение особенностей
                for feature in game.get('features', []):
                    feature_id = await conn.fetchval("SELECT id FROM features WHERE name = $1;", feature)
                    await conn.execute("""
                    INSERT INTO game_features (game_id, feature_id) VALUES ($1, $2) ON CONFLICT DO NOTHING;
                    """, game_id, feature_id)
    except Exception as e:
        logger.error(f"Ошибка при сохранении игры: {e}")
        raise e


async def get_game_genres(pool, game_id: int):
    """Получить жанры для игры по её id."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT genres.name 
            FROM genres 
            JOIN game_genres ON genres.id = game_genres.genre_id
            WHERE game_genres.game_id = $1;
            """, game_id)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении жанров для игры {game_id}: {e}")
        raise e


async def get_game_features(pool, game_id: int):
    """Получить особенности для игры по её id."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT features.name 
            FROM features 
            JOIN game_features ON features.id = game_features.feature_id
            WHERE game_features.game_id = $1;
            """, game_id)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении особенностей для игры {game_id}: {e}")
        raise e


async def get_free_games(pool):
    """Получить все бесплатные игры с их жанрами и особенностями."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT id, name, link, end_time FROM games WHERE end_time > NOW();')

            free_games = []
            for row in rows:
                game_id = row['id']
                game_name = row['name']
                game_link = row['link']
                game_end_time = (row['end_time'] + timedelta(hours=3)).strftime('%d %b %Y %H:%M')

                # Получаем жанры и особенности игры
                genres = await get_game_genres(pool, game_id)
                features = await get_game_features(pool, game_id)

                free_games.append({
                    'name': game_name,
                    'link': game_link,
                    'end_time': game_end_time,
                    'genres': genres,
                    'features': features
                })

            return free_games
    except Exception as e:
        logger.error(f"Ошибка при получении бесплатных игр: {e}")
        raise e


# Функции для подписки на жанры и особенности с использованием пула
async def subscribe_genre(pool, user_id: int, genre_name: str):
    async with pool.acquire() as conn:
        genre_id = await conn.fetchval("SELECT id FROM genres WHERE name = $1", genre_name)
        if genre_id:
            await conn.execute("""
                INSERT INTO user_genres (user_id, genre_id) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id, genre_id) DO NOTHING;
            """, user_id, genre_id)


# Функции для подписки на жанры и особенности с использованием пула
async def subscribe_genre_by_id(pool, user_id: int, genre_id: int):
    async with pool.acquire() as conn:
        if genre_id:
            await conn.execute("""
                INSERT INTO user_genres (user_id, genre_id) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id, genre_id) DO NOTHING;
            """, user_id, genre_id)


async def unsubscribe_genre(pool, user_id: int, genre_name: str):
    async with pool.acquire() as conn:
        genre_id = await conn.fetchval("SELECT id FROM genres WHERE name = $1", genre_name)
        if genre_id:
            await conn.execute("""
                DELETE FROM user_genres WHERE user_id = $1 AND genre_id = $2;
            """, user_id, genre_id)

async def unsubscribe_genre_by_id(pool, user_id: int, genre_id: int):
    async with pool.acquire() as conn:
        if genre_id:
            await conn.execute("""
                DELETE FROM user_genres WHERE user_id = $1 AND genre_id = $2;
            """, user_id, genre_id)


async def subscribe_feature(pool, user_id: int, feature_name: str):
    async with pool.acquire() as conn:
        feature_id = await conn.fetchval("SELECT id FROM features WHERE name = $1", feature_name)
        if feature_id:
            await conn.execute("""
                INSERT INTO user_features (user_id, feature_id) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id, feature_id) DO NOTHING;
            """, user_id, feature_id)


async def subscribe_feature_by_id(pool, user_id: int, feature_id: int):
    async with pool.acquire() as conn:
        if feature_id:
            await conn.execute("""
                INSERT INTO user_features (user_id, feature_id) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id, feature_id) DO NOTHING;
            """, user_id, feature_id)


async def unsubscribe_feature(pool, user_id: int, feature_name: str):
    async with pool.acquire() as conn:
        feature_id = await conn.fetchval("SELECT id FROM features WHERE name = $1", feature_name)
        if feature_id:
            await conn.execute("""
                DELETE FROM user_features WHERE user_id = $1 AND feature_id = $2;
            """, user_id, feature_id)

async def unsubscribe_feature_by_id(pool, user_id: int, feature_id: int):
    async with pool.acquire() as conn:
        if feature_id:
            await conn.execute("""
                DELETE FROM user_features WHERE user_id = $1 AND feature_id = $2;
            """, user_id, feature_id)


async def get_user_genres(pool, user_id: int):
    """Получает все жанры, на которые подписан пользователь."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT genres.name
                FROM genres
                JOIN user_genres ON genres.id = user_genres.genre_id
                WHERE user_genres.user_id = $1;
            """, user_id)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении жанров для пользователя {user_id}: {e}")
        raise e


async def get_user_genres_with_id(pool, user_id: int):
    """Получает все жанры, на которые подписан пользователь."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT genres.id, genres.name
                FROM genres
                JOIN user_genres ON genres.id = user_genres.genre_id
                WHERE user_genres.user_id = $1;
            """, user_id)
            return [(row[0], row[1]) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении жанров для пользователя {user_id}: {e}")
        raise e


async def get_user_features(pool, user_id: int):
    """Получает все особенности, на которые подписан пользователь."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT features.name
                FROM features
                JOIN user_features ON features.id = user_features.feature_id
                WHERE user_features.user_id = $1;
            """, user_id)
            return [row['name'] for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении особенностей для пользователя {user_id}: {e}")
        raise e


async def get_user_features_with_id(pool, user_id: int):
    """Получает все особенности, на которые подписан пользователь."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                    SELECT features.id, features.name
                    FROM features
                    JOIN user_features ON features.id = user_features.feature_id
                    WHERE user_features.user_id = $1;
                """, user_id)
            return [(row[0], row[1]) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении особенностей для пользователя {user_id}: {e}")
        raise e
