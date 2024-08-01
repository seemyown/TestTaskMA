#! bin/bash

# Скрипт запуска сервиса. Запускается из корневой директории.
# Создаем папку для статических файлов
PYTHON_BIN="/usr/bin/python3"
CRON_SCRIPT="./cron"
mkdir "static"

CRON="0 0 * * * $PYTHON_BIN $CRON_SCRIPT"
# Создаем крон задачу

(crontab -l grep -F "CRON_SCRIPT") || (crontab -l; echo "CRON") | crontab -