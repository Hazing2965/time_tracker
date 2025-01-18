import os
from datetime import datetime, timedelta, time, timezone

from aiogram import Bot
from aiogram.types import FSInputFile

from config.config import MOSCOW_TIMEZONE, FORMAT_DATE_AND_TIME
from database.database import update_info, get_info, remove_old_record


def format_duration(duration):
    """Форматирует timedelta в строку вида ЧЧ:ММ."""
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = remainder // 60
    return f"{hours:02}:{minutes:02}"




from collections import defaultdict


def split_activity_by_days(activity):
    """Разбивает активность на части, если она переходит через полночь."""
    name, time_start, time_end = activity['name'], activity['time_start'], activity['time_end']
    activities = []

    while time_start.date() < time_end.date():
        # Длительность до полуночи
        end_of_day = datetime.combine(time_start.date(), time(23, 59, 59))
        duration = end_of_day - time_start + timedelta(seconds=1)
        activities.append({'name': name, 'date': time_start.date(), 'duration': duration})
        time_start = datetime.combine(time_start.date() + timedelta(days=1), time(0, 0))

    # Добавляем оставшуюся часть
    activities.append({'name': name, 'date': time_start.date(), 'duration': time_end - time_start})
    return activities

def split_activity_by_days_2(name, time_start, time_end):
    """Разбивает активность на части, если она переходит через полночь."""
    # Получаем запись
    activities = []

    while time_start.date() < time_end.date():
        # Длительность до полуночи
        end_of_day = datetime.combine(time_start.date(), time(23, 59, 59))
        duration = end_of_day - time_start + timedelta(seconds=1)
        activities.append({'name': name, 'time_start': time_start, 'time_end': end_of_day, 'duration': duration})
        time_start = datetime.combine(time_start.date() + timedelta(days=1), time(0, 0))

    # Добавляем оставшуюся часть
    activities.append({'name': name, 'time_start': time_start, 'time_end': time_end, 'duration': time_end - time_start})
    return activities

async def generate_report_sort(data, user_id):
    # Преобразуем данные из списка
    result = []
    daily_activities = {}
    # Проходимся по каждой записи и разбиваем на дни
    for item in data:
        time_start = datetime.strptime(item['time_start'], FORMAT_DATE_AND_TIME)
        time_end = datetime.strptime(item['time_end'], FORMAT_DATE_AND_TIME)
        # Приводим в дату пользователя
        time_start = time_start.replace(tzinfo=timezone(timedelta(hours=3)))
        time_end = time_end.replace(tzinfo=timezone(timedelta(hours=3)))
        timezone_user = await get_info(table='users',
                       where={'user_id': user_id},
                       fields=['timezone'])
        timezone_user = timezone_user[0].get('timezone') or 3

        # Переводим в другой часовой пояс (+7)
        time_start = time_start.astimezone(timezone(timedelta(hours=timezone_user))).replace(tzinfo=None)
        time_end = time_end.astimezone(timezone(timedelta(hours=timezone_user))).replace(tzinfo=None)

        name = item['name']

        # Разбиваем на дни, если нужно
        activity_parts = split_activity_by_days_2(name, time_start, time_end)
        for part in activity_parts:
            day_key = part['time_start'].date()
            if day_key not in daily_activities:
                daily_activities[day_key] = []

            daily_activities[day_key].append(part)

    # Проходимся по каждому дню отсортировано по дате начала
    for day_num, (day, activities) in enumerate(sorted(daily_activities.items()), 1):
        result.append(f"{day.strftime('%d.%m.%y')} {day_num} день")
        # Проходим по каждой активности в этот день
        for activity in activities:
            start_time = activity['time_start'].strftime('%H:%M')
            end_time = activity['time_end'].strftime('%H:%M')
            name = activity['name']
            # вычисляем сколько времени потребовалось для действия
            duration = format_duration(activity['duration'])
            result.append(f"с {start_time} до {end_time} - {name} ({duration})")
        result.append("")  # Пустая строка для разделения дней

    return "\n".join(result).strip()

async def generate_report_full(data, user_id):
    # Преобразуем данные в структуру с разбивкой по дням
    daily_totals = defaultdict(lambda: defaultdict(timedelta))

    for item in data:
        # Парсим строки времени
        time_start = datetime.strptime(item['time_start'], '%Y-%m-%d %H:%M:%S')
        time_end = datetime.strptime(item['time_end'], '%Y-%m-%d %H:%M:%S')
        # Приводим в дату пользователя

        time_start = time_start.replace(tzinfo=timezone(timedelta(hours=3)))
        time_end = time_end.replace(tzinfo=timezone(timedelta(hours=3)))

        timezone_user = await get_info(table='users',
                                       where={'user_id': user_id},
                                       fields=['timezone'])
        timezone_user = timezone_user[0].get('timezone') or 3

        # Переводим в другой часовой пояс (+7)
        time_start = time_start.astimezone(timezone(timedelta(hours=timezone_user))).replace(tzinfo=None)
        time_end = time_end.astimezone(timezone(timedelta(hours=timezone_user))).replace(tzinfo=None)

        # Разбиваем активность на части по дням
        activity_parts = split_activity_by_days({'name': item['name'], 'time_start': time_start, 'time_end': time_end})
        for part in activity_parts:
            daily_totals[part['date']][part['name']] += part['duration']

    # Формируем вывод
    result = []
    for day_num, (day, activities) in enumerate(sorted(daily_totals.items()), 1):
        result.append(f"{day_num} день:")
        # Сортируем активности по времени (убывание)
        sorted_activities = sorted(activities.items(), key=lambda x: x[1], reverse=True)
        for name, duration in sorted_activities:
            result.append(f"{name} - {format_duration(duration)}")
        result.append("")  # Пустая строка для разделения дней

    return "\n".join(result).strip()

async def stop_record(bot: Bot, user_id):
    # Получаем ID последней записи
    info = await get_info(table='users', where={"user_id": user_id}, fields=["action_id"])
    action_id_old = info[0].get('action_id')
    if action_id_old:
        # Устанавливаем время конца действия
        await update_info(fields={"time_end": datetime.now(MOSCOW_TIMEZONE).strftime(FORMAT_DATE_AND_TIME)}, table="records", where={"action_id": action_id_old})
        # Убираем из активных действие
        await update_info(fields={"action_id": None}, table="users", where={"user_id": user_id})
        # Получаем все записи
        info = await get_info(table='records', where={"user_id": user_id}, fields=['name', 'time_start', 'time_end'])
        # print(info) #[{'name': 'Работаю', 'time_start': '2025-01-01 18:24:22', 'time_end': '2025-01-01 18:25:21'}, ]
        # Формируем вывод
        report_file = await generate_report_sort(info, user_id)
        report_message = await generate_report_full(info, user_id)
        # Сохраняем в файл
        name_report = f'{user_id}_report_full.txt'
        with open(name_report, "w", encoding="utf-8") as file:
            file.write(report_file)
        try:
            await bot.send_message(user_id, report_message)
        except:
            name_mini_record_message = f'{user_id}_report_sort.txt'
            with open(name_mini_record_message, "w", encoding="utf-8") as file:
                file.write(report_message)
            await bot.send_document(chat_id=user_id, document=FSInputFile(path=report_file, filename='report_sort.txt'))
            os.remove(name_mini_record_message)
        await bot.send_document(chat_id=user_id, document=FSInputFile(path=name_report, filename='report_full.txt'))
        os.remove(name_report)
        await remove_old_record(user_id)


