import logging
from logging.handlers import RotatingFileHandler
import sys
import os

LOG_DIR = "logs"
LOG_FILE = "app.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Создать папку logs, если нет
os.makedirs(LOG_DIR, exist_ok=True)

# Формат сообщений
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Создаём логгер
logger = logging.getLogger("camproject")
logger.setLevel(logging.DEBUG)

# Консольный вывод
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Запись в файл с ротацией
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Добавляем обработчики, если ещё не добавлены
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)