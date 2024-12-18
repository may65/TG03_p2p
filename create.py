import sqlite3

# Подключение к базе данных (или создание)
conn = sqlite3.connect('school_data.db')
cursor = conn.cursor()

# Создание таблицы students
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    grade TEXT
)
''')

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()