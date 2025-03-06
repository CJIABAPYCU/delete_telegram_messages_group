from telethon import TelegramClient
import asyncio
import random
from datetime import datetime

#API
API_ID = 'your_api_id'  # https://my.telegram.org/
API_HASH = 'your_api_hash'  
PHONE_NUMBER = 'your_phone_number'  

# Лимит сообщений перед паузой
MESSAGE_LIMIT = 150
# Пауза после достижения лимита (в секундах)
PAUSE_DURATION = 300  # 5 минут

async def process_group(client, chat, start_date, end_date):
    me = await client.get_me()
    print(f"🔹 Обработка группы: {chat.title} за период {start_date.year}")

    # Счетчики
    total_messages = 0
    deleted_count = 0

    # Обрабатываем сообщения за указанный год
    async for message in client.iter_messages(chat, offset_date=end_date, reverse=True):
        # Если сообщение старше начала года, переходим к следующему году
        if message.date < start_date:
            break

        total_messages += 1

        # Выводим прогресс каждые 200 сообщений
        if total_messages % 200 == 0:
            print(f"🔹 Просмотрено {total_messages} сообщений в группе {chat.title} за {start_date.year}")

        # Удаляем свои сообщения
        if message.sender_id == me.id:
            try:
                await message.delete()
                deleted_count += 1
                print(f"✅ Удалено сообщение {message.id} в группе {chat.title}: {message.text}")
                # Случайная задержка
                await asyncio.sleep(random.uniform(0.5, 1.5))

                # Если достигнут лимит, делаем паузу
                if deleted_count >= MESSAGE_LIMIT:
                    print(f"🔹 Достигнут лимит ({MESSAGE_LIMIT} сообщений). Пауза {PAUSE_DURATION} секунд...")
                    await asyncio.sleep(PAUSE_DURATION)
                    deleted_count = 0
            except Exception as e:
                print(f"⚠ Ошибка удаления сообщения {message.id} в группе {chat.title}: {e}")

    # Итог по группе за год
    print(f"🔹 Группа {chat.title} за {start_date.year} обработана. Просмотрено {total_messages} сообщений, удалено {deleted_count}.")

async def delete_my_messages():
    try:
        async with TelegramClient(PHONE_NUMBER, API_ID, API_HASH) as client:
            # Получаем информацию о текущем пользователе
            me = await client.get_me()
            name = me.first_name or "Без имени"
            username = me.username or "Без username"
            print(f"🔹 Авторизован как: {name} (@{username})")

            # Собираем группы для обработки
            groups = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append(dialog.entity)

            # Определяем диапазоны дат для каждого года
            current_year = datetime.now().year
            for year in range(current_year, 2016, -1):  # Обрабатываем с текущего года до 2017
                if year > current_year:  # Пропускаем будущие годы
                    continue

                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31) if year < current_year else datetime.now()

                print(f"🔹 Начинаем обработку за {year} год...")
                for group in groups:
                    await process_group(client, group, start_date, end_date)
    except KeyboardInterrupt:
        print("🔹 Скрипт остановлен вручную.")
    except Exception as e:
        print(f"⚠ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(delete_my_messages())
