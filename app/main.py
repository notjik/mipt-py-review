import asyncio
import logging
from db import init_db_pool, init_db
from bot import notify_subscribers, dp, bot
from scraper import scrape_categories, schedule_scrape_free_games, schedule_scrape_categories

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Главная функция
async def main():
    pool = await init_db_pool()
    await init_db(pool)

    # Запускаем все фоновые задачи с ожиданием их завершения
    tasks = [
        asyncio.create_task(schedule_scrape_categories(pool)),
        asyncio.create_task(schedule_scrape_free_games(pool)),
        asyncio.create_task(notify_subscribers(pool))
    ]

    dp['pool'] = pool

    await scrape_categories(pool) # Хочу чтобы выполнялось до всего остального кода

    try:
        pooling_task = [asyncio.create_task(dp.start_polling(bot))]
        # Ожидаем запуска бота и завершения фоновых задач
        gather = asyncio.gather(*tasks, *pooling_task, return_exceptions=True)
        await gather
    finally:
        # Закрытие бота и пула соединений с базой данных
        await dp.stop_polling()
        await bot.close()
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
