import os

BOT_TOKEN = '8011663522:AAHwJS_Tgpsnb7vT2lLEWZIcgUZyqmww_uk'
#ADMIN_IDS = []


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "Data_base", "main.db")
print(f"Путь к базе данных: {DB_PATH}")