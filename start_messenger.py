#!/usr/bin/env python3
"""
Простой запуск Secure Messenger
Автоматически запускает сервер и клиент
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import PyQt6
        import cryptography
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("📦 Установите зависимости: pip install -r requirements.txt")
        return False

def start_server():
    """Запуск сервера"""
    try:
        print("🚀 Запуск сервера...")
        subprocess.run([sys.executable, "server.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Ошибка запуска сервера")
    except KeyboardInterrupt:
        print("🛑 Сервер остановлен")

def start_client():
    """Запуск клиента"""
    try:
        print("📱 Запуск клиента...")
        subprocess.run([sys.executable, "client.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Ошибка запуска клиента")
    except KeyboardInterrupt:
        print("🛑 Клиент остановлен")

def start_web_server():
    """Запуск веб-сервера"""
    try:
        print("🌐 Запуск веб-сервера...")
        print("📱 Откройте браузер: http://localhost:8080")
        time.sleep(2)
        webbrowser.open("http://localhost:8080")
        subprocess.run([sys.executable, "simple_web_server.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Ошибка запуска веб-сервера")
    except KeyboardInterrupt:
        print("🛑 Веб-сервер остановлен")

def main():
    """Главная функция"""
    print("🔐 Secure Messenger - Запуск")
    print("=" * 40)
    
    # Проверяем зависимости
    if not check_dependencies():
        input("Нажмите Enter для выхода...")
        return
    
    print("\nВыберите режим запуска:")
    print("1. 🖥️  Десктопная версия (PyQt6)")
    print("2. 🌐 Веб-версия (браузер)")
    print("3. 🚀 Только сервер")
    print("4. 📱 Только клиент")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        # Десктопная версия
        print("\n🖥️  Запуск десктопной версии...")
        print("📝 Сервер запустится в фоне, клиент откроется в новом окне")
        
        # Запускаем сервер в отдельном потоке
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Ждем немного, чтобы сервер запустился
        time.sleep(3)
        
        # Запускаем клиент
        start_client()
        
    elif choice == "2":
        # Веб-версия
        print("\n🌐 Запуск веб-версии...")
        start_web_server()
        
    elif choice == "3":
        # Только сервер
        print("\n🚀 Запуск только сервера...")
        start_server()
        
    elif choice == "4":
        # Только клиент
        print("\n📱 Запуск только клиента...")
        start_client()
        
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Программа остановлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для выхода...")
