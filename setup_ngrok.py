#!/usr/bin/env python3
"""
Автоматическая настройка ngrok для Secure Messenger
Альтернатива Heroku для России
"""

import subprocess
import sys
import time
import webbrowser
import os
import requests

def check_ngrok_installed():
    """Проверка установки ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok установлен")
            return True
        else:
            print("❌ ngrok не найден")
            return False
    except FileNotFoundError:
        print("❌ ngrok не установлен")
        return False

def install_ngrok_guide():
    """Инструкция по установке ngrok"""
    print("\n📥 УСТАНОВКА NGROK:")
    print("=" * 50)
    print("1. Перейдите на https://ngrok.com/download")
    print("2. Скачайте ngrok для Windows")
    print("3. Распакуйте ngrok.exe в папку с проектом")
    print("4. Зарегистрируйтесь на ngrok.com (бесплатно)")
    print("5. Получите токен авторизации")
    print("6. Выполните: ngrok authtoken YOUR_TOKEN")
    print("\n🔄 После установки запустите этот скрипт снова")

def check_ngrok_auth():
    """Проверка авторизации ngrok"""
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], capture_output=True, text=True)
        if "valid" in result.stdout.lower():
            print("✅ ngrok авторизован")
            return True
        else:
            print("❌ ngrok не авторизован")
            return False
    except:
        print("❌ Ошибка проверки авторизации ngrok")
        return False

def start_messenger_with_ngrok():
    """Запуск мессенджера с ngrok"""
    print("🚀 Запуск Secure Messenger с ngrok...")
    print("=" * 50)
    
    # Запускаем веб-сервер в фоне
    print("📡 Запуск веб-сервера...")
    server_process = subprocess.Popen([sys.executable, "simple_web_server.py"])
    
    # Ждем запуска сервера
    time.sleep(3)
    
    # Запускаем ngrok
    print("🌐 Запуск ngrok...")
    ngrok_process = subprocess.Popen(['ngrok', 'http', '8080'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
    
    # Ждем запуска ngrok
    time.sleep(5)
    
    # Получаем публичный URL
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['tunnels']:
                public_url = data['tunnels'][0]['public_url']
                print(f"\n🎉 ГОТОВО! Публичный URL: {public_url}")
                print(f"📤 Поделитесь этой ссылкой с друзьями!")
                print(f"🌐 Открываем в браузере...")
                
                # Открываем в браузере
                webbrowser.open(public_url)
                
                print(f"\n📋 ИНСТРУКЦИЯ ДЛЯ ДРУЗЕЙ:")
                print(f"1. Откройте браузер")
                print(f"2. Перейдите по ссылке: {public_url}")
                print(f"3. Выберите 'Зарегистрироваться' или 'Продолжить без регистрации'")
                print(f"4. Начните общение!")
                
                print(f"\n🛑 Для остановки нажмите Ctrl+C")
                
                try:
                    # Ждем завершения
                    server_process.wait()
                except KeyboardInterrupt:
                    print(f"\n🛑 Остановка серверов...")
                    server_process.terminate()
                    ngrok_process.terminate()
                    print(f"✅ Серверы остановлены")
            else:
                print("❌ Не удалось получить публичный URL")
        else:
            print("❌ Ошибка получения URL от ngrok")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("💡 Убедитесь, что ngrok запущен и доступен на localhost:4040")

def start_messenger_local():
    """Запуск мессенджера локально"""
    print("🏠 Запуск локального мессенджера...")
    print("=" * 50)
    
    # Получаем локальный IP
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"🏠 Ваш локальный IP: {local_ip}")
        print(f"📱 Для друзей в той же сети: http://{local_ip}:8080")
        
    except:
        print("❌ Не удалось определить локальный IP")
    
    # Запускаем веб-сервер
    print("📡 Запуск веб-сервера...")
    webbrowser.open("http://localhost:8080")
    subprocess.run([sys.executable, "simple_web_server.py"])

def show_alternatives():
    """Показать альтернативы Heroku"""
    print("🌐 АЛЬТЕРНАТИВЫ HEROKU ДЛЯ РОССИИ:")
    print("=" * 50)
    print("1. 🚇 ngrok - простой туннель (рекомендуется)")
    print("2. ☁️  Railway - https://railway.app")
    print("3. 🌟 Render - https://render.com")
    print("4. 🐳 Российский VPS - Timeweb, Beget, REG.RU")
    print("5. 🏠 Ваш ноутбук + ngrok")
    print()
    print("💡 ngrok - самый простой способ для тестирования!")

def main():
    """Главная функция"""
    print("🇷🇺 Настройка Secure Messenger для России")
    print("🚫 Heroku заблокирован, используем альтернативы")
    print("=" * 60)
    
    print("\nВыберите способ подключения:")
    print("1. 🚇 ngrok (для друзей из других городов)")
    print("2. 🏠 Локальная сеть (для друзей рядом)")
    print("3. 📥 Установить ngrok")
    print("4. 🌐 Показать альтернативы Heroku")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        if check_ngrok_installed():
            if check_ngrok_auth():
                start_messenger_with_ngrok()
            else:
                print("❌ ngrok не авторизован")
                print("💡 Выполните: ngrok authtoken YOUR_TOKEN")
        else:
            print("❌ ngrok не установлен")
            install_ngrok_guide()
            
    elif choice == "2":
        start_messenger_local()
        
    elif choice == "3":
        install_ngrok_guide()
        
    elif choice == "4":
        show_alternatives()
        
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

