#!/usr/bin/env python3
"""
Создание пакета для распространения Secure Messenger
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_distribution_package():
    """Создание пакета для распространения"""
    
    print("📦 Создание пакета для распространения...")
    
    # Создаем папку для пакета
    package_dir = Path("SecureMessenger_Package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Файлы для включения в пакет
    files_to_copy = [
        "server.py",
        "client.py", 
        "database.py",
        "crypto_utils.py",
        "simple_web_server.py",
        "index.html",
        "start_messenger.py",
        "get_ip.py",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        "run_server.bat",
        "run_client.bat",
        "run_web.bat"
    ]
    
    # Копируем файлы
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"✅ Скопирован: {file}")
        else:
            print(f"⚠️  Файл не найден: {file}")
    
    # Создаем инструкцию для пользователей
    user_guide = package_dir / "ИНСТРУКЦИЯ_ДЛЯ_ПОЛЬЗОВАТЕЛЕЙ.txt"
    with open(user_guide, 'w', encoding='utf-8') as f:
        f.write("""
🔐 SECURE MESSENGER - ИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ

📋 ЧТО В ПАКЕТЕ:
- Secure Messenger - защищенный мессенджер
- 3 режима работы: десктопная версия, веб-версия, защищенные чаты
- End-to-end шифрование сообщений

🚀 БЫСТРЫЙ ЗАПУСК:

1. УСТАНОВИТЕ PYTHON (если не установлен):
   - Скачайте с https://python.org
   - При установке отметьте "Add Python to PATH"

2. УСТАНОВИТЕ ЗАВИСИМОСТИ:
   - Откройте командную строку в папке с файлами
   - Выполните: pip install -r requirements.txt

3. ЗАПУСТИТЕ МЕССЕНДЖЕР:
   - Двойной клик на: start_messenger.py
   - Или запустите: python start_messenger.py

📱 РЕЖИМЫ РАБОТЫ:

🖥️ ДЕСКТОПНАЯ ВЕРСИЯ:
- Графический интерфейс как в Telegram
- Регистрация и вход в систему
- Обычные чаты с историей сообщений
- Настройки профиля

🌐 ВЕБ-ВЕРСИЯ:
- Работает в браузере
- Подходит для тестирования
- Все функции десктопной версии

🛡️ ЗАЩИЩЕННЫЕ ЧАТЫ:
- End-to-end шифрование
- Автоматическое удаление при закрытии
- Двойная защита (ключ чата + ключ шифрования)
- Работает без регистрации

🔧 РУЧНОЙ ЗАПУСК:

СЕРВЕР:
- python server.py
- Или двойной клик на: run_server.bat

КЛИЕНТ:
- python client.py  
- Или двойной клик на: run_client.bat

ВЕБ-ВЕРСИЯ:
- python simple_web_server.py
- Или двойной клик на: run_web.bat
- Откройте браузер: http://localhost:8080

🌍 ДЛЯ ТЕСТИРОВАНИЯ С ДРУЗЬЯМИ:

1. Узнайте ваш IP адрес:
   - python get_ip.py

2. Запустите веб-сервер:
   - python simple_web_server.py

3. Друзья подключаются по адресу:
   - http://ВАШ_IP:8080

4. Или используйте ngrok для публичного доступа:
   - Скачайте ngrok с https://ngrok.com
   - Запустите: ngrok http 8080
   - Поделитесь полученной ссылкой

🔐 БЕЗОПАСНОСТЬ:

- Пароли хешируются с солью (PBKDF2)
- Сообщения шифруются AES-256
- Защищенные чаты автоматически удаляются
- Секретные фразы для восстановления паролей

❓ РЕШЕНИЕ ПРОБЛЕМ:

Проблема: "Модуль не найден"
Решение: pip install -r requirements.txt

Проблема: "Порт занят"  
Решение: Перезапустите компьютер или измените порт

Проблема: "Не подключается"
Решение: Проверьте брандмауэр и IP адрес

📞 ПОДДЕРЖКА:
- Проверьте README.md для подробной документации
- Проверьте DEPLOYMENT_GUIDE.md для развертывания
- Убедитесь, что Python 3.8+ установлен

🎉 УДАЧНОГО ИСПОЛЬЗОВАНИЯ!
""")
    
    print(f"✅ Создана инструкция: {user_guide}")
    
    # Создаем ZIP архив
    zip_path = "SecureMessenger_For_Friends.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
                print(f"📦 Добавлен в архив: {arcname}")
    
    print(f"\n🎉 ПАКЕТ СОЗДАН: {zip_path}")
    print(f"📁 Размер: {os.path.getsize(zip_path) / 1024 / 1024:.1f} MB")
    print(f"📤 Отправьте этот файл друзьям!")
    
    # Удаляем временную папку
    shutil.rmtree(package_dir)
    print("🧹 Временные файлы удалены")

if __name__ == "__main__":
    create_distribution_package()
    input("\nНажмите Enter для выхода...")

