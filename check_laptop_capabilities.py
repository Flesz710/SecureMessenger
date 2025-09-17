#!/usr/bin/env python3
"""
Проверка возможностей ноутбука для развертывания Secure Messenger
"""

import socket
import subprocess
import sys
import platform
import psutil
import os

def get_system_info():
    """Получение информации о системе"""
    print("🖥️  ИНФОРМАЦИЯ О СИСТЕМЕ:")
    print("=" * 50)
    
    # Операционная система
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.architecture()[0]}")
    print(f"Процессор: {platform.processor()}")
    
    # Память
    memory = psutil.virtual_memory()
    print(f"RAM: {memory.total / (1024**3):.1f} GB (доступно: {memory.available / (1024**3):.1f} GB)")
    
    # Диск
    disk = psutil.disk_usage('/')
    print(f"Диск: {disk.total / (1024**3):.1f} GB (свободно: {disk.free / (1024**3):.1f} GB)")
    
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

def check_firewall():
    """Проверка настроек брандмауэра"""
    print("🔥 ПРОВЕРКА БРАНДМАУЭРА:")
    print("=" * 50)
    
    try:
        # Проверяем статус брандмауэра Windows
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout
            if "ON" in output:
                print("⚠️  Брандмауэр Windows включен")
                print("💡 Возможно потребуется открыть порт 8080")
            else:
                print("✅ Брандмауэр Windows отключен")
        else:
            print("❓ Не удалось проверить статус брандмауэра")
            
    except Exception as e:
        print(f"❌ Ошибка проверки брандмауэра: {e}")
    
    print()

def check_python_dependencies():
    """Проверка зависимостей Python"""
    print("🐍 ПРОВЕРКА PYTHON ЗАВИСИМОСТЕЙ:")
    print("=" * 50)
    
    dependencies = [
        'PyQt6',
        'cryptography', 
        'pyperclip',
        'psutil'
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

def test_server_performance():
    """Тест производительности сервера"""
    print("⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ:")
    print("=" * 50)
    
    # Проверяем CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU загрузка: {cpu_percent}%")
    
    if cpu_percent < 50:
        print("✅ CPU: Хорошая производительность")
    elif cpu_percent < 80:
        print("⚠️  CPU: Средняя загрузка")
    else:
        print("❌ CPU: Высокая загрузка")
    
    # Проверяем память
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    print(f"RAM загрузка: {memory_percent}%")
    
    if memory_percent < 70:
        print("✅ RAM: Достаточно памяти")
    elif memory_percent < 90:
        print("⚠️  RAM: Средняя загрузка")
    else:
        print("❌ RAM: Мало свободной памяти")
    
    print()

def get_recommendations():
    """Получение рекомендаций"""
    print("💡 РЕКОМЕНДАЦИИ:")
    print("=" * 50)
    
    # Проверяем систему
    memory = psutil.virtual_memory()
    cpu_count = psutil.cpu_count()
    
    print("📊 ВОЗМОЖНОСТИ ВАШЕГО НОУТБУКА:")
    
    if memory.total >= 4 * 1024**3:  # 4GB
        print("✅ RAM: Достаточно для мессенджера")
    else:
        print("⚠️  RAM: Мало памяти, возможны проблемы")
    
    if cpu_count >= 2:
        print("✅ CPU: Достаточно ядер")
    else:
        print("⚠️  CPU: Мало ядер, возможны задержки")
    
    print("\n🌐 ВАРИАНТЫ РАЗВЕРТЫВАНИЯ:")
    print("1. 🏠 ЛОКАЛЬНАЯ СЕТЬ:")
    print("   - Друзья в той же Wi-Fi сети")
    print("   - Простое подключение по IP")
    print("   - Не требует интернета")
    
    print("\n2. 🌍 ИНТЕРНЕТ (ваш ноутбук как сервер):")
    print("   - Друзья из других городов")
    print("   - Требует настройки роутера")
    print("   - Нужен статический IP или DDNS")
    
    print("\n3. ☁️  ОБЛАЧНЫЙ ХОСТИНГ:")
    print("   - Heroku, Railway, Render (бесплатно)")
    print("   - Не нагружает ваш ноутбук")
    print("   - Всегда доступен")
    
    print("\n4. 🚇 NGROK (туннель):")
    print("   - Простая настройка")
    print("   - Временный доступ")
    print("   - Не требует настройки сети")
    
    print()

def main():
    """Главная функция"""
    print("🔍 ПРОВЕРКА ВОЗМОЖНОСТЕЙ НОУТБУКА ДЛЯ SECURE MESSENGER")
    print("=" * 70)
    print()
    
    try:
        get_system_info()
        get_network_info()
        check_port_availability()
        check_firewall()
        check_python_dependencies()
        test_server_performance()
        get_recommendations()
        
        print("🎯 ИТОГОВАЯ ОЦЕНКА:")
        print("=" * 50)
        
        # Простая оценка
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        
        score = 0
        if memory.total >= 4 * 1024**3:
            score += 1
        if cpu_count >= 2:
            score += 1
        if check_port_availability():
            score += 1
        
        if score >= 2:
            print("✅ ВАШ НОУТБУК ПОДХОДИТ для развертывания мессенджера!")
            print("💡 Рекомендуется: локальная сеть или ngrok")
        else:
            print("⚠️  ВАШ НОУТБУК МОЖЕТ ИМЕТЬ ОГРАНИЧЕНИЯ")
            print("💡 Рекомендуется: облачный хостинг")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")

