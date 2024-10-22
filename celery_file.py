from init import make_celery, create_app
from models import User, OnlineStatus
from init import redis_client
import asyncio
from aiogram import Bot
from config import Config


bot = Bot(token=Config.BOT_TOKEN)

app = create_app()
celery = make_celery(app)


@celery.task(name="remove_inactive_users")
def remove_inactive_users():
    online_users = redis_client.smembers('online_users')
    status = OnlineStatus
    for user_id in online_users:
        user_id = user_id.decode()  # Расшифровываем байтовые строки (в Redis данные хранятся как байты)
        if not status.is_user_online(user_id):
            status.set_user_offline(user_id)


async def send_message(user_telegram_id: int, message: str):
    try:
        await bot.send_message(chat_id=user_telegram_id, text=f'В топовом чате пришло новое сообщение: {message}')
        print(f"Сообщение отправлено пользователю {user_telegram_id}: {message}")
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {user_telegram_id}: {e}")


@celery.task(name="send_telegram_notification")
def send_telegram_notification(user_telegram_id: int, message: str):
    if user_telegram_id is not None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если цикл событий уже запущен, используем create_task
            loop.create_task(send_message(user_telegram_id, message))
        else:
            # Если цикл событий не запущен, запускаем его
            loop.run_until_complete(send_message(user_telegram_id, message))