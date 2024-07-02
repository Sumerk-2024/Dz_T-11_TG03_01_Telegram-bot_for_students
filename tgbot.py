import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
import sqlite3
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API_TOKEN из переменных окружения
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Настройка логирования для получения информации о работе бота
logging.basicConfig(level=logging.INFO)


# Определение состояний для FSM (Finite State Machine)
class Form(StatesGroup):
    name = State()  # Состояние для имени
    age = State()   # Состояние для возраста
    grade = State()  # Состояние для класса (grade)


# Функция для инициализации базы данных и создания таблицы students
def init_db():
    conn = sqlite3.connect('school_data.db')  # Подключение к базе данных
    cur = conn.cursor()  # Создание курсора для выполнения SQL-запросов
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL)
    ''')  # Создание таблицы students, если она не существует
    conn.commit()  # Применение изменений
    conn.close()  # Закрытие соединения

# Вызов функции для инициализации базы данных
init_db()


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")  # Отправка сообщения пользователю
    await state.set_state(Form.name)  # Установка состояния на Form.name


# Обработчик для состояния Form.name
@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)  # Сохранение введенного имени
    await message.answer("Сколько тебе лет?")  # Запрос возраста
    await state.set_state(Form.age)  # Установка состояния на Form.age


# Обработчик для состояния Form.age
@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохранение введенного возраста
    await message.answer("В каком ты классе?")  # Запрос класса (grade)
    await state.set_state(Form.grade)  # Установка состояния на Form.grade


# Обработчик для состояния Form.grade
@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)  # Сохранение введенного класса
    user_data = await state.get_data()  # Получение всех данных пользователя

    # Сохранение данных пользователя в базу данных
    conn = sqlite3.connect('school_data.db')  # Подключение к базе данных
    cur = conn.cursor()  # Создание курсора для выполнения SQL-запросов
    cur.execute('''
    INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
    (user_data['name'], int(user_data['age']), user_data['grade']))  # Вставка данных в таблицу
    conn.commit()  # Применение изменений
    conn.close()  # Закрытие соединения

    await message.answer(f"Спасибо, {user_data['name']}! Твои данные сохранены.")  # Подтверждение сохранения данных
    await state.clear()  # Очистка состояния


# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)  # Запуск поллинга

if __name__ == '__main__':
    asyncio.run(main())  # Запуск основного события
