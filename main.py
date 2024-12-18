from config import TOKEN
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import os
from aiogram.types import FSInputFile  # Добавляем импорт для работы с файлами
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import sqlite3

# Настройка хранилища
storage = MemoryStorage()

# Создание бота
bot = Bot(token=TOKEN)

# Создание диспетчера
dp = Dispatcher(storage=storage)

# Создание роутера
router = Router()

# Регистрация роутера в диспетчере
dp.include_router(router)

# Обработчик команды /start
@router.message(CommandStart())
async def start(message: Message):
    await message.answer("start")

# Определяем состояния для машины состояний
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Обработчик команды /add_student
@router.message(Command("add_student"))
async def add_student(message: Message, state: FSMContext):
    await message.answer("Введите имя ученика:")
    await state.set_state(StudentForm.name)

# Обработчик ввода имени
@router.message(StudentForm.name)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите возраст ученика:")
    await state.set_state(StudentForm.age)

# Обработчик ввода возраста
@router.message(StudentForm.age)
async def enter_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("Введите класс ученика:")
        await state.set_state(StudentForm.grade)
    except ValueError:
        await message.answer("Возраст должен быть числом. Попробуйте снова.")

# Обработчик ввода класса
@router.message(StudentForm.grade)
async def enter_grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    age = user_data.get("age")
    grade = message.text

    # Сохраняем данные в базу данных
    try:
        conn = sqlite3.connect('school_data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
        conn.commit()
        conn.close()

        await message.answer(f"Данные ученика сохранены:\nИмя: {name}\nВозраст: {age}\nКласс: {grade}")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        await message.answer("Произошла ошибка при сохранении данных.")

    # Завершаем работу состояния
    await state.clear()

# Обработчик команды /see_bd
@router.message(Command("see_bd"))
async def see_bd(message: Message):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('school_data.db')
        cursor = conn.cursor()

        # Получаем данные из таблицы students
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        conn.close()

        # Проверяем, есть ли данные
        if not rows:
            await message.answer("В базе данных пока нет записей.")
            return

        # Формируем сообщение с данными
        response_message = "Список учеников:\n"
        for row in rows:
            student_id, name, age, grade = row
            response_message += f"ID: {student_id}, Имя: {name}, Возраст: {age}, Класс: {grade}\n"

        # Отправляем данные пользователю
        await message.answer(response_message)
    except Exception as e:
        print(f"Ошибка при чтении базы данных: {e}")
        await message.answer("Произошла ошибка при получении данных из базы.")

# Обработчик команды /help
@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("help")
    await message.answer("/add_student")
    await message.answer("/see_bd")

# Основная функция
async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

# Исполнение программы
if __name__ == "__main__":
    asyncio.run(main())
