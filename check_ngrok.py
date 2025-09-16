#!/usr/bin/env python3
"""
Проверка установки ngrok и инструкции по настройке
"""

import os
import subprocess
import sys

def check_ngrok_installed():
    """Проверка установки ngrok"""
    print("🔍 ПРОВЕРКА УСТАНОВКИ NGROK:")
    print("=" * 50)
    
    # Проверяем наличие файла ngrok.exe
    ngrok_path = "ngrok.exe"
    if os.path.exists(ngrok_path):
        print("✅ ngrok.exe найден в папке проекта")
        return True
    else:
        print("❌ ngrok.exe не найден в папке проекта")
        return False

def check_ngrok_command():
    """Проверка команды ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok доступен в командной строке")
            return True
        else:
            print("❌ ngrok не работает в командной строке")
            return False
    except FileNotFoundError:
        print("❌ ngrok не найден в PATH")
        return False

def show_installation_guide():
    """Показать инструкцию по установке"""
    print("\n📥 ИНСТРУКЦИЯ ПО УСТАНОВКЕ NGROK:")
    print("=" * 50)
    print("1. Перейдите на https://ngrok.com/download")
    print("2. Скачайте ngrok для Windows")
    print("3. Распакуйте ngrok.exe в папку:")
    print(f"   {os.getcwd()}")
    print("4. Зарегистрируйтесь на https://ngrok.com (бесплатно)")
    print("5. Получите токен авторизации")
    print("6. Выполните: ngrok authtoken YOUR_TOKEN")
    print("\n🔄 После установки запустите этот скрипт снова")

def show_quick_start():
    """Показать быстрый старт"""
    print("\n🚀 БЫСТРЫЙ СТАРТ:")
    print("=" * 50)
    print("1. Запустите мессенджер:")
    print("   python simple_web_server.py")
    print()
    print("2. В другом терминале запустите ngrok:")
    print("   ngrok http 8080")
    print()
    print("3. Скопируйте публичную ссылку (например: https://abc123.ngrok.io)")
    print("4. Поделитесь ссылкой с друзьями!")
    print()
    print("🛑 Для остановки нажмите Ctrl+C")

def test_messenger_startup():
    """Тест запуска мессенджера"""
    print("\n🚀 ТЕСТ ЗАПУСКА МЕССЕНДЖЕРА:")
    print("=" * 50)
    
    # Проверяем наличие файлов
    required_files = [
        'simple_web_server.py',
        'index.html',
        'database.py',
        'crypto_utils.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - не найден")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ Все файлы мессенджера найдены")
        return True

def main():
    """Главная функция"""
    print("🚇 ПРОВЕРКА NGROK ДЛЯ SECURE MESSENGER")
    print("=" * 50)
    
    # Проверяем установку ngrok
    ngrok_file = check_ngrok_installed()
    ngrok_command = check_ngrok_command()
    
    # Проверяем мессенджер
    messenger_ok = test_messenger_startup()
    
    print("\n🎯 ИТОГОВАЯ ОЦЕНКА:")
    print("=" * 50)
    
    if ngrok_file and ngrok_command and messenger_ok:
        print("✅ ВСЕ ГОТОВО! ngrok и мессенджер настроены")
        show_quick_start()
    elif messenger_ok:
        if not ngrok_file:
            print("❌ ngrok не установлен")
            show_installation_guide()
        elif not ngrok_command:
            print("❌ ngrok не настроен")
            print("💡 Выполните: ngrok authtoken YOUR_TOKEN")
        else:
            print("⚠️  Есть проблемы с ngrok")
    else:
        print("❌ Проблемы с мессенджером")
        print("💡 Убедитесь, что все файлы на месте")
    
    print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Установите ngrok (если не установлен)")
    print("2. Зарегистрируйтесь на ngrok.com")
    print("3. Получите токен авторизации")
    print("4. Выполните: ngrok authtoken YOUR_TOKEN")
    print("5. Запустите мессенджер: python simple_web_server.py")
    print("6. Запустите ngrok: ngrok http 8080")
    print("7. Поделитесь полученной ссылкой с друзьями!")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
