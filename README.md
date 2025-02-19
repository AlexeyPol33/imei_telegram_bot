![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Aiohttp](https://img.shields.io/badge/Aiohttp-2C5BB4?style=for-the-badge)
![Asyncpg](https://img.shields.io/badge/Asyncpg-323232?style=for-the-badge&logo=postgresql&logoColor=red)
![Psycopg2](https://img.shields.io/badge/Psycopg2-336791?style=for-the-badge&logo=postgresql&logoColor=white)
# 📱 IMEI Telegram Bot

&#x20;       &#x20;

**IMEI Telegram Bot** — это высокоуровневый программный агент, реализованный в виде телеграм-бота, предназначенного для проверки легитимности пользователей посредством сверки с белым списком и, при наличии разрешения, предоставления информации об устройстве, ассоциированном с переданным IMEI.

## 🚀 Функциональные возможности

- Обработка IMEI-номера, предоставленного пользователем.
- Верификация принадлежности пользователя к доверенному списку (white list).
- Предоставление детализированной информации об устройстве в случае успешной аутентификации.

## 🛠 Технологический стек

- **Язык программирования**: Python 3.x
- **Используемые библиотеки**:
  - `aiohttp` — асинхронные HTTP-запросы
  - `python-telegram-bot` — API-обертка для работы с Telegram
  - `asyncpg` — высокопроизводительный PostgreSQL-драйвер
  - `httpx` — асинхронный HTTP-клиент
  - `python-dotenv` — управление переменными окружения
  - `cryptography` — обеспечение криптографической безопасности
  - `psycopg2` — драйвер для работы с PostgreSQL
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker

## 🔧 Установка и развертывание

### 1️⃣ Клонирование репозитория

```sh
git clone https://github.com/AlexeyPol33/imei_telegram_bot.git
cd imei_telegram_bot
```

### 2️⃣ Конфигурирование переменных окружения

Создайте `.env` файл и добавьте в него:

```ini
IMEI_CHECK_TOKEN= #Your imeicheck token
BOT_TOKEN= #Your bot token
LOCAL_API='http://localhost:8080'
IMEI_CHECK_URL='https://api.imeicheck.net'
SECRET_KEY= #Your secret key

DB_USER= #Your database login
DB_PASSWORD = #Your database password
DB_NAME='whitelist' #Or your database name
DB_HOST = 'localhost'
```

### 3️⃣ Установка зависимостей

```sh
pip install -r requirements.txt
```

### 4️⃣ Запуск бота в локальной среде
```sh
python app.py
```
```sh
python bot.py
```

### 📦 Развертывание с использованием Docker
Не реализованно

## 📬 Контактная информация

📢 **Telegram**: [@Alexey\_Poltavskiy](https://t.me/Alexey_Poltavskiy)\
📧 **Email**: [79776177342@yandex.ru](mailto:79776177342@yandex.ru)

