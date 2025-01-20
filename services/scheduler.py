from datetime import datetime, timedelta

from aiogram import Bot

from config.config import MOSCOW_TIMEZONE, FORMAT_DATE_AND_TIME, ADMIN_ID
from database.database import get_info
from services.services import stop_record


async def delete_24_hour(bot: Bot):
    # Получаем записи с незаполненными end_date
    records = await get_info(table='records', where={'time_end': None}, fields=['time_start', 'time_end', 'user_id'])
    # Проходимся по каждой
    for record in records:
        # Сравниваем прошло ли 24 часа с момента начала записи
        time_start = record.get('time_start')
        if time_start:
            time_start = datetime.strptime(time_start, FORMAT_DATE_AND_TIME)
            date_now = datetime.now(MOSCOW_TIMEZONE).replace(tzinfo=None)
            if date_now - time_start >= timedelta(hours=24):
                # Если прошло, то получаем user_id и делаем ему /stop
                # уведомляя что прошло больше 24 часов с момента открытия действия
                user_id = record.get('user_id')
                if user_id:
                    try:
                        await bot.send_message(user_id, 'Уже прошло больше 24 часов после начала действия, '
                                                        'запись завершается в автоматическом режиме')
                        await stop_record(bot, user_id)
                    except Exception as e:
                        await bot.send_message(ADMIN_ID, f'Ошибка при автоматическом завершении записи у пользователя: '
                                                         f'{user_id}\n\n{e}')
