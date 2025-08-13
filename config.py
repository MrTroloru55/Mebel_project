import os

with open('C:\\Users\\user\\Desktop\\token.txt', 'r') as file:
    BOT_TOKEN = file.readline().strip()
#ADMIN_IDS = []


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "Data_base", "main.db")
print(f"Путь к базе данных: {DB_PATH}")