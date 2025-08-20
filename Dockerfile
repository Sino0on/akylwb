# Устанавливаем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt в рабочую директорию
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем исходный код проекта в рабочую директорию
COPY . /app/

# Создаем директорию для хранения медиа файлов
RUN mkdir -p /app/media

# Открываем порт для приложения
EXPOSE 8000

# Запускаем команду для миграции и запуска сервера
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8020"]