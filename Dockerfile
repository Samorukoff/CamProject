# 1. Базовый образ
FROM python:3.11-slim

# 2. Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# 4. Рабочая директория
WORKDIR /app

# 5. Копируем только файлы зависимостей (для кэширования)
COPY pyproject.toml poetry.lock* ./

# 6. Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry check && \
    poetry install --no-interaction --no-ansi

# 7. Копируем остальной проект
COPY . .

# 8. Установка переменных окружения
ENV PYTHONUNBUFFERED=1

# 9. Копируем entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 10. Указываем запуск через entrypoint
ENTRYPOINT ["/entrypoint.sh"]
