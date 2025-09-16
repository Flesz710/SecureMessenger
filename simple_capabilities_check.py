#!/usr/bin/env python3
"""
Простая проверка возможностей ноутбука для развертывания Secure Messenger
"""

import socket
import platform
import os

def get_system_info():
    """Получение информации о системе"""
    print("🖥️  ИНФОРМАЦИЯ О СИСТЕМЕ:")
    print("=" * 50)
    
    # Операционная система
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.architecture()[0]}")
    print(f"Процессор: {platform.processor()}")
    
    # Python версия
    print(f"Python: {platform.python_version()}")
    
    print()

def get_network_info():
    """Получение сетевой информации"""
    print("🌐 СЕТЕВАЯ ИНФОРМАЦИЯ:")
    print("=" * 50)
    
    try:
        # Локальный IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"Локальный IP: {local_ip}")
        
        # Проверка подключения к интернету
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex(("8.8.8.8", 53))
        s.close()
        
        if result == 0:
            print("✅ Подключение к интернету: ЕСТЬ")
        else:
            print("❌ Подключение к интернету: НЕТ")
            
    except Exception as e:
        print(f"❌ Ошибка получения сетевой информации: {e}")
    
    print()

def check_port_availability(port=8080):
    """Проверка доступности порта"""
    print(f"🔌 ПРОВЕРКА ПОРТА {port}:")
    print("=" * 50)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', port))
        s.close()
        
        if result == 0:
            print(f"❌ Порт {port} занят")
            return False
        else:
            print(f"✅ Порт {port} свободен")
            return True
    except Exception as e:
        print(f"❌ Ошибка проверки порта: {e}")
        return False

def check_python_dependencies():
    """Проверка зависимостей Python"""
    print("🐍 ПРОВЕРКА PYTHON ЗАВИСИМОСТЕЙ:")
    print("=" * 50)
    
    dependencies = [
        'PyQt6',
        'cryptography', 
        'pyperclip'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - не установлен")
            missing.append(dep)
    
    if missing:
        print(f"\n💡 Установите недостающие зависимости:")
        print(f"pip install {' '.join(missing)}")
    
    print()

def get_recommendations():
    """Получение рекомендаций"""
    print("💡 РЕКОМЕНДАЦИИ ДЛЯ РАЗВЕРТЫВАНИЯ:")
    print("=" * 50)
    
    print("🌐 ВАРИАНТЫ РАЗВЕРТЫВАНИЯ НА ВАШЕМ НОУТБУКЕ:")
    print()
    
    print("1. 🏠 ЛОКАЛЬНАЯ СЕТЬ (САМЫЙ ПРОСТОЙ):")
    print("   ✅ Друзья в той же Wi-Fi сети")
    print("   ✅ Простое подключение по IP")
    print("   ✅ Не требует интернета")
    print("   ✅ Не нагружает ноутбук")
    print("   ❌ Только для друзей рядом")
    print()
    
    print("2. 🌍 ИНТЕРНЕТ (ваш ноутбук как сервер):")
    print("   ✅ Друзья из других городов")
    print("   ✅ Полный контроль")
    print("   ❌ Требует настройки роутера")
    print("   ❌ Нужен статический IP или DDNS")
    print("   ❌ Нагружает ноутбук")
    print()
    
    print("3. 🚇 NGROK (РЕКОМЕНДУЕТСЯ):")
    print("   ✅ Простая настройка")
    print("   ✅ Друзья из любых городов")
    print("   ✅ Временный доступ")
    print("   ✅ Не требует настройки сети")
    print("   ❌ Ограничения бесплатной версии")
    print()
    
    print("4. ☁️  ОБЛАЧНЫЙ ХОСТИНГ:")
    print("   ✅ Не нагружает ваш ноутбук")
    print("   ✅ Всегда доступен")
    print("   ✅ Друзья из любых городов")
    print("   ❌ Требует загрузки кода")
    print("   ❌ Ограничения бесплатных планов")
    print()

def test_messenger_startup():
    """Тест запуска мессенджера"""
    print("🚀 ТЕСТ ЗАПУСКА МЕССЕНДЖЕРА:")
    print("=" * 50)
    
    # Проверяем наличие файлов
    required_files = [
        'server.py',
        'client.py',
        'simple_web_server.py',
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
    print("🔍 ПРОВЕРКА ВОЗМОЖНОСТЕЙ НОУТБУКА ДЛЯ SECURE MESSENGER")
    print("=" * 70)
    print()
    
    try:
        get_system_info()
        get_network_info()
        port_available = check_port_availability()
        check_python_dependencies()
        files_ok = test_messenger_startup()
        get_recommendations()
        
        print("🎯 ИТОГОВАЯ ОЦЕНКА:")
        print("=" * 50)
        
        if files_ok and port_available:
            print("✅ ВАШ НОУТБУК ГОТОВ для развертывания мессенджера!")
            print()
            print("🚀 РЕКОМЕНДУЕМЫЕ СПОСОБЫ:")
            print("1. 🏠 Локальная сеть - для друзей рядом")
            print("2. 🚇 ngrok - для друзей из других городов")
            print("3. ☁️  Облачный хостинг - для постоянного использования")
        else:
            print("⚠️  ЕСТЬ ПРОБЛЕМЫ:")
            if not files_ok:
                print("❌ Отсутствуют файлы мессенджера")
            if not port_available:
                print("❌ Порт 8080 занят")
            print()
            print("💡 Рекомендуется: облачный хостинг")
        
        print()
        print("🔧 БЫСТРЫЙ СТАРТ:")
        print("1. Для локальной сети: python simple_web_server.py")
        print("2. Для ngrok: python setup_for_friends.py")
        print("3. Для облачного хостинга: загрузите на Heroku/Railway")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
