FROM python:3.12.3
LABEL authors="rodin"

# Устанавливаем необходимые пакеты и генерируем локаль
RUN apt-get update && apt-get install -y wget curl unzip chromium-driver libpq-dev locales-all &&  \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY /app /app

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска
CMD ["python", "main.py"]
