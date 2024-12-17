import asyncio
import logging
import random
import locale

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import CHROME_DRIVER_PATH
from db import save_games

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


# Скраппер для бесплатных игр Epic Games Store
async def scrape_free_games():
    url = "https://store.epicgames.com/ru/free-games"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск без GUI
    options.add_argument("--disable-gpu")  # Отключить GPU (для headless-режима)
    options.add_argument("--no-sandbox")  # Отключить песочницу
    options.add_argument("--disable-dev-shm-usage")  # Использование shared memory
    options.add_argument("--remote-debugging-port=9222")  # Разрешить отладку
    options.add_argument("--disable-extensions")  # Отключить расширения
    options.add_argument("--disable-software-rasterizer")  # Отключить software rasterizer

    # Случайный выбор пользовательского агента
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver_path = CHROME_DRIVER_PATH
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    try:
        driver.get(url)
        await asyncio.sleep(2)  # Быстрая задержка перед скроллингом

        # Эмуляция действий пользователя
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(3):
            body.send_keys(Keys.PAGE_DOWN)
            await asyncio.sleep(random.uniform(1, 2))  # Уменьшили задержку

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        games = []
        # Ищем все карточки, содержащие текст "Сейчас бесплатно"
        game_cards = soup.find_all("div", string="Сейчас бесплатно")

        for card in game_cards:
            # Ищем родительский элемент с названием игры и ссылкой
            game_name = card.find_parent("div").find_parent("a").find("h6")
            game_link = card.find_parent("div").find_parent("a")['href']
            end_time_str = card.find_parent("div").find_parent("div").find('p').find('span').find('time')['datetime']

            # Извлекаем дату окончания раздачи
            end_time = None
            if end_time_str:
                try:
                    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    logging.warning(f"Не удалось распарсить дату: {end_time_str}")

            if game_name and game_link and end_time:
                games.append({
                    "name": game_name.get_text(strip=True),
                    "link": "https://store.epicgames.com" + game_link,  # Полный URL
                    "end_time": end_time
                })
        await save_games(games)
        return games
    finally:
        driver.quit()


async def schedule_scrape_free_games():
    while True:
        logging.info("Start scraping free-games...")

        # Сохраняем данные в бд
        await scrape_free_games()
        logging.info("Scraping free-games is done")
        # Скрапим каждые 20 минут
        await asyncio.sleep(1200)