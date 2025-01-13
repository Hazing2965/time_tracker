import json
import logging
import random
import uuid
from datetime import datetime

import aiosqlite

from config.config import PATH_DB, MOSCOW_TIMEZONE, FORMAT_DATE_AND_TIME

# Инициализируем логгер
logger = logging.getLogger(__name__)

async def create_database():

    # Желаемая структура базы данных
    desired_schema = { # Пользователи
        "users": {
            "user_id": "INTEGER PRIMARY KEY",
            "action_id": "TEXT",
            "date_start": "TEXT",
            "date_last": "TEXT",
            "action_list": "TEXT",
        },
        "records": {  # Записи
            "action_id": "TEXT PRIMARY KEY",
            "user_id": "INTEGER",
            "name": "TEXT",
            "time_start": "TEXT",
            "time_end": "TEXT",
        }
    }

    async with aiosqlite.connect(PATH_DB) as db:
        # Получить список существующих таблиц
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            existing_tables = {row[0] async for row in cursor}

        # Обработать каждую таблицу из желаемой схемы
        for table_name, columns in desired_schema.items():
            if table_name not in existing_tables:
                # Создать таблицу, если её нет
                columns_sql = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())
                await db.execute(f"CREATE TABLE {table_name} ({columns_sql});")
                logger.info(f"Created table: {table_name}")
            else:
                # Проверить структуру существующей таблицы
                async with db.execute(f"PRAGMA table_info({table_name});") as cursor:
                    current_columns = {row[1]: row[2] async for row in cursor}

                # Определить недостающие столбцы
                for column_name, column_type in columns.items():
                    if column_name not in current_columns:
                        await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
                        logger.info(f"Added column: {table_name} ({column_name} {column_type})")

        await db.commit()

async def new_user(user_id):
    async with aiosqlite.connect(PATH_DB) as db:
        # Проверить, существует ли пользователь
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            # Пользователь не существует — добавляем
            if user is None:
                date_now = datetime.now(MOSCOW_TIMEZONE).strftime(FORMAT_DATE_AND_TIME)
                await db.execute("INSERT INTO users (user_id, date_start) VALUES (?, ?)", (user_id, date_now))
                await db.commit()


# data1 = await get_info(user_id, [name, age, sex])
async def get_info(user_id, fields):
    async with aiosqlite.connect(PATH_DB) as db:
        # Создаем строку для запроса с нужными полями
        fields_str = ", ".join(fields)

        # Выполняем запрос
        query = f"SELECT {fields_str} FROM users WHERE user_id = ?"
        async with db.execute(query, (user_id,)) as cursor:
            row = await cursor.fetchone()

        # Если пользователь найден, создаем словарь из полей и возвращаем
        if row:
            return {field: row[idx] for idx, field in enumerate(fields)}

        # Если пользователь не найден, возвращаем None
        return None

# await update_info(user_id, {'age': 30, 'name': 'Ted'})
async def update_info(user_id, fields):
    async with aiosqlite.connect(PATH_DB) as db:
        # Генерация строки SET для SQL-запроса
        set_clause = ", ".join([f"{key} = ?" for key in fields.keys()])
        values = list(fields.values()) + [user_id]

        # Формируем и выполняем запрос
        query = f"UPDATE users SET {set_clause} WHERE user_id = ?"
        await db.execute(query, values)
        await db.commit()


async def update_last_send(user_id):
    async with aiosqlite.connect(PATH_DB) as db:
        date_now = datetime.now(MOSCOW_TIMEZONE).strftime(FORMAT_DATE_AND_TIME)
        await db.execute('UPDATE users SET date_last = ? WHERE user_id = ?', (date_now, user_id))
        await db.commit()

async def save_list_to_db(user_id: int, words: list):
    """
    Сохраняет список слов в базу данных.
    :param user_id: Идентификатор пользователя
    :param words: Список слов
    """
    async with aiosqlite.connect(PATH_DB) as db:
        # Создание таблицы, если её нет
        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_words (
            user_id INTEGER PRIMARY KEY,
            word_list TEXT
        )
        """)
        await db.commit()

        # Преобразование списка в JSON
        word_list_json = json.dumps(words, ensure_ascii=False)

        # Сохранение данных
        await db.execute("""
        INSERT OR REPLACE INTO user_words (user_id, word_list)
        VALUES (?, ?)
        """, (user_id, word_list_json))
        await db.commit()

async def get_list_from_db(user_id: int):
    """
    Получает список слов из базы данных.
    :param user_id: Идентификатор пользователя
    :return: Список слов
    """
    async with aiosqlite.connect(PATH_DB) as db:
        async with db.execute("""
        SELECT action_list FROM users WHERE user_id = ?
        """, (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result[0]:
                return json.loads(result[0])
            else:
                return []
            # return json.loads(result[0]) if result else []


async def add_action_db(user_id, action_name):
    action_id = f"{user_id}_{uuid.uuid4().hex}"
    date_now = datetime.now(MOSCOW_TIMEZONE).strftime(FORMAT_DATE_AND_TIME)


    # Подключение к базе данных
    async with aiosqlite.connect(PATH_DB) as db:
        # Узнаём id предыдущей активности
        async with db.execute('SELECT action_id FROM users WHERE user_id = ?', (user_id,)) as cursor:
            action_id_old = await cursor.fetchone()
        # Если она была
        if action_id_old != None:
            action_id_old = action_id_old[0]
            # Устанавливаем время конца предыдущей активности
            await db.execute('UPDATE records SET time_end = ? WHERE action_id = ?', (date_now, action_id_old))
        # Создаём новую активность
        await db.execute("INSERT INTO records (action_id, user_id, name, time_start) VALUES (?, ?, ?, ?)", (action_id, user_id, action_name, date_now))
        # Записываем пользователю активность которая происходит
        await db.execute('UPDATE users SET action_id = ? WHERE user_id = ?', (action_id, user_id))
        # Получаем предыдущие записи пользователя
        async with db.execute("SELECT action_list FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            action_list = json.loads(result[0]) if result[0] else []
        if len(action_list) > 6:
            action_list.pop(0)
        action_list.append(action_name)
        if len(action_list) > 6:
            action_list.pop(0)
        # Преобразование списка в JSON
        action_list_json = json.dumps(action_list, ensure_ascii=False)
        # Сохранение данных
        await db.execute('UPDATE users SET action_list = ? WHERE user_id = ?', (action_list_json, user_id))
        await db.commit()




    return action_id