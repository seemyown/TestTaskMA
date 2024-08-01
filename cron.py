import datetime
import os
import time
from typing import Final

STATIC_PATH: Final[str] = './static'

NOW = time.time()
one_month = 30 * 24 * 60 * 60

for file in os.listdir(STATIC_PATH):
    file_path = os.path.join(STATIC_PATH, file)
    if os.path.isfile(file_path):
        file_created_time = os.path.getctime(file_path)
        if NOW - file_created_time > one_month:
            print(f"Найден файл старше месяца. {file_path}")
            os.remove(file_path)
            print(f"Файл {file_path} удален")
