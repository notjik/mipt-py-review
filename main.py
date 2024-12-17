import asyncio

from db import init_db
from bot import notify_subscribers, dp, bot
from scraper import schedule_scrape_free_games


# Главная функция
async def main():
    await init_db()
    asyncio.create_task(schedule_scrape_free_games())
    asyncio.create_task(notify_subscribers())
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
