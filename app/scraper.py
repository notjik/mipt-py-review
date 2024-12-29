import asyncio
import logging

from datetime import datetime
from bs4 import BeautifulSoup
from selenium.common import WebDriverException

from db import save_games, add_genre, add_feature
from webdriver import make_driver, emulate_user

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_free_games(pool):
    url = "https://store.epicgames.com/ru/free-games"
    driver = make_driver()
    games = []
    try:
        driver.get(url)
        emulate_user(driver)

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        if soup.find(string='Please complete a security check to continue') or \
                soup.find(string='This site can’t be reached'):
            raise WebDriverException('Bypass failed')

        game_cards = soup.find_all("div", string="Сейчас бесплатно")

        for card in game_cards:
            game_name = card.find_parent("div").find_parent("a").find("h6")
            game_link = card.find_parent("div").find_parent("a")['href']
            end_time_str = card.find_parent("div").find_parent("div").find('p').find('span').find('time')['datetime']

            end_time = None
            if end_time_str:
                try:
                    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    logger.warning(f"Не удалось распарсить дату: {end_time_str}")

            if game_name and game_link and end_time:
                games.append({
                    "name": game_name.get_text(strip=True),
                    "link": "https://store.epicgames.com" + game_link,
                    "end_time": end_time
                })
        return games
    except WebDriverException as e:
        logger.error(f"WebDriverException occurred during scraping free games: {e}")
    finally:
        driver.quit()
        games = await scrape_games_categories(games)
        await save_games(pool, games)
        logger.info(f"End scrape free games")
    return []


async def scrape_games_categories(games):
    for game in games:
        url = game['link']

        driver = make_driver()

        try:
            driver.get(url)
            emulate_user(driver)

            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            if soup.find(string='Please complete a security check to continue') or \
                    soup.find(string='This site can’t be reached') or \
                    soup.find(
                        string="Этот контент в настоящее время недоступен на вашей платформе или в вашем регионе."
                    ):
                raise WebDriverException('Bypass failed')

            genres = []
            genres_labels = soup.find("div", string="Жанры").find_parent("div").find_all("a")

            for label in genres_labels:
                genres.append(label.get_text(strip=True))

            features = []
            features_labels = soup.find("div", string="Особенности").find_parent("div").find_all("a")

            for label in features_labels:
                features.append(label.get_text(strip=True))

            game['genres'] = genres
            game['features'] = features
        except WebDriverException as e:
            logger.error(f"WebDriverException occurred during scraping categories free game ({game['link']}): {e}")
        finally:
            driver.quit()
            logger.info(f"End scrape categories from {game['name']}")
    return games


async def scrape_categories(pool):
    url = "https://store.epicgames.com/ru/browse?sortBy=releaseDate&sortDir=DESC&category=Game&count=40"
    driver = make_driver()

    genres = []
    features = []
    try:
        driver.get(url)
        emulate_user(driver)

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        if soup.find(string='Please complete a security check to continue') or \
                soup.find(string='This site can’t be reached'):
            raise WebDriverException('Bypass failed')

        genre_button = soup.find('span', string='Жанр')
        if genre_button:
            genre_parent = genre_button.find_parent('div').find_next_sibling('div')
            genre_items = genre_parent.find_all('span')
            for item in genre_items:
                text = item.get_text(strip=True)
                if text:
                    genres.append(text)

        feature_button = soup.find('span', string='Особенности')
        if feature_button:
            feature_parent = feature_button.find_parent('div').find_next_sibling('div')
            feature_items = feature_parent.find_all('span')
            for item in feature_items:
                text = item.get_text(strip=True)
                if text:
                    features.append(text)
        return genres, features
    except WebDriverException as e:
        logger.error(f"WebDriverException occurred during scraping categories: {e}")
    finally:
        driver.quit()
        for genre in genres:
            await add_genre(pool, genre)
        for feature in features:
            await add_feature(pool, feature)
        logger.info(f"End scrape categories")
    return [], []


async def schedule_scrape_free_games(pool):
    logger.info("Start schedule scraping free-games...")
    games = await scrape_free_games(pool)
    logger.info("Schedule Scraping free-games is done" if games else "Schedule scraping free-games ended with error")
    await asyncio.sleep(1200)


async def schedule_scrape_categories(pool):
    logger.info("Start schedule scraping categories...")
    categories = await scrape_categories(pool)
    logger.info(
        "Schedule scraping categories is done" if categories else "Schedule scraping categories ended with error")
    await asyncio.sleep(21600)
