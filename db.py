import asyncpg
from config import DATABASE_URL
from datetime import timedelta


async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE NOT NULL,
        active BOOLEAN DEFAULT TRUE
    );
    ''')
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        end_time TIMESTAMP NOT NULL,
        UNIQUE(name, link)
    );
    ''')
    await conn.close()


async def add_subscriber(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
        INSERT INTO subscribers (user_id) VALUES ($1) ON CONFLICT (user_id) DO UPDATE SET active = TRUE;
        """, user_id)
    finally:
        await conn.close()


async def disable_subscriber(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
        UPDATE subscribers SET active = FALSE WHERE user_id = $1;
        """, user_id)
    finally:
        await conn.close()


async def get_subscribers():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch('SELECT user_id FROM subscribers WHERE active = TRUE;')
        return [row['user_id'] for row in rows]
    finally:
        await conn.close()


async def save_games(games):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        for game in games:
            await conn.execute("""
            INSERT INTO games (name, link, end_time) VALUES ($1, $2, $3)
            ON CONFLICT (name, link) DO UPDATE SET end_time = EXCLUDED.end_time;
            """, game['name'], game['link'], game['end_time'])
    finally:
        await conn.close()


async def get_free_games():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch('SELECT name, link, end_time FROM games WHERE end_time > NOW();')
        return [{'name': row['name'], 'link': row['link'],
                 'end_time': (row['end_time'] + timedelta(hours=3)).strftime('%d %b %Y %H:%M')} for row in rows]
    finally:
        await conn.close()
