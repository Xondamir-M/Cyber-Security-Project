import sqlite3

conn = sqlite3.connect('password_manager.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Database table list:", tables)

conn.close()
