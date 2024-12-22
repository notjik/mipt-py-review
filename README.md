# susu-mipt-py-review

## О проекте

Этот проект выполнен в рамках курса "Python" бакалавриата ЮУРГУ - МФТИ (блокирующая работа Web Code Review). Проект
представляет собой телеграм-бота на aiogram 3.15.0 с использованием базы данных PostgreSQL 16, уведомляющего
пользователя о появлении новых [бесплатных игр](https://store.epicgames.com/ru/free-games)
на [Epic Games](https://store.epicgames.com/).

Бот работает по принципам асинхронного программирования. Он адаптируется под предпочтения пользователя, который выбирает
жанры и особенности игр, и в дальнейшем получает уведомления только о тех раздачах, которые ему интересны. Кроме того,
бот предоставляет возможность просматривать текущие раздачи как с учетом предпочтений, так и все доступные раздачи
подряд.

Ссылка на бота: [@epicgames_free_games_bot](https://t.me/epicgames_free_games_bot)

## Структура проекта

```plaintext
susu-mipt-py-review/
├── app/                   # Основная директория приложения
│   ├── bot.py             # Алгоритмы работы бота (хендлеры, коллбэки и уведомления)
│   ├── config.py          # Конфигурационные настройки
│   ├── db.py              # Взаимодействие с базой данных Postgres
│   ├── keyboards.py       # Функции создания клавиатур (Reply, Inline)
│   ├── main.py            # Основной файл проекта
│   ├── requirements.txt   # Список зависимостей приложения
│   └── scraper.py         # Функции скрапинга с Epic Games
├── .env.example           # Файл с названиями переменных виртуального окружения
├── .gitignore             # Файл с перечислением игнорируемых файлов и директорий
├── build.sh               # Сценарий запуска проекта
├── docker-compose.yml     # Конфигурация запуска проекта в docker-контейнерах
├── Dockerfile             # Конфигурация контейнера приложения
└── README.md              # Описание проекта
```

## Быстрый запуск проекта

1. Склонируйте репозиторий в директорию.
2. Создайте файл `.env` и укажите переменные окружения:

```dotenv
BOT_TOKEN=<YOUR_API_TOKEN>
POSTGRES_HOST=db
POSTGRES_PORT=<YOUR_POSTGRES_PORT>
POSTGRES_USER=<YOUR_POSTGRES_USER>
POSTGRES_PASSWORD=<YOUR_POSTGRES_USER_PASSWORD>
POSTGRES_DB=<YOUR_POSTGRES_DB>
WEBDRIVER_PATH=/usr/bin/chromedriver
```

3. Запустите [./build.sh](./build.sh):

```bash
#!/bin/bash
docker-compose up --build
```

> **Примечание:** Для запуска проекта необходимо установить `docker` и `docker-compose`.

## Пояснение к самостоятельному запуску

### Docker Compose

Docker Compose собирает два сервиса: базу данных и веб-приложение с ботом. Вы можете отключить сервис с базой данных и
привязать свою PostgreSQL, указав ее в `.env` файле.

### Установка и настройка PostgreSQL

1. Установите PostgreSQL 16 на вашем компьютере. Для этого
   следуйте [официальной документации](https://www.postgresql.org/download/), подходящей для вашей операционной системы.
2. Создайте базу данных и пользователя.

```sql
CREATE
DATABASE <YOUR_POSTGRES_DB>;
CREATE
USER <YOUR_POSTGRES_USER> WITH PASSWORD '<YOUR_POSTGRES_USER_PASSWORD>';
GRANT ALL PRIVILEGES ON DATABASE
<YOUR_POSTGRES_DB> TO <YOUR_POSTGRES_USER>;
```

### Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта и добавьте в него следующие строки, заменив значения на ваши.

### Установка и настройка WebDriver

1. Установите [ChromeDriver](https://sites.google.com/chromium.org/driver/downloads), который соответствует версии
   вашего браузера.
2. Укажите путь к ChromeDriver в переменной `WEBDRIVER_PATH` в `.env` файле.

### WebDriver

Поскольку скрапер работает с использованием Selenium, необходимо установить веб-драйвер. Вы можете использовать свой, но
также потребуется изменить [app/scraper.py](app/scraper.py) и `.env`, указав путь к вашему драйверу.

### Установка зависимостей и запуск проекта

1. Установите зависимости, указанные в `requirements.txt`. Рекомендуется использовать виртуальное окружение.

```bash
python -m venv venv
source venv/bin/activate   # Для Windows используйте venv\Scripts\activate
pip install -r app/requirements.txt
```

2. Запустите проект.
```bash
python app/main.py
```

## Отказ от ответственности

Данный проект был написан исключительно в образовательных целях. Автор не несет никакой ответственности за использование
данного продукта сторонними лицами. Все права принадлежат их правообладателям.