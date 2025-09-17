#!/usr/bin/env python3
"""
Keep-Alive скрипт для предотвращения засыпания Render
"""

import requests
import time
import os
from datetime import datetime

def ping_render():
    """Отправляет ping на Render для предотвращения засыпания"""
    try:
        # Получаем URL из переменной окружения
        render_url = os.getenv('RENDER_URL', 'https://secure-messenger.onrender.com')
        
        # Отправляем GET запрос
        response = requests.get(f"{render_url}/", timeout=10)
        
        if response.status_code == 200:
            print(f"[{datetime.now()}] ✅ Ping успешен - статус: {response.status_code}")
            return True
        else:
            print(f"[{datetime.now()}] ⚠️ Ping неуспешен - статус: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ❌ Ошибка ping: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Запуск Keep-Alive для Render...")
    print(f"URL: {os.getenv('RENDER_URL', 'https://secure-messenger.onrender.com')}")
    
    ping_count = 0
    success_count = 0
    
    while True:
        try:
            ping_count += 1
            print(f"\n--- Ping #{ping_count} ---")
            
            if ping_render():
                success_count += 1
            
            print(f"Успешных ping: {success_count}/{ping_count}")
            
            # Ждем 10 минут (600 секунд)
            print("⏰ Ожидание 10 минут до следующего ping...")
            time.sleep(600)
            
        except KeyboardInterrupt:
            print("\n🛑 Остановка Keep-Alive...")
            break
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            time.sleep(60)  # Ждем минуту при ошибке

if __name__ == "__main__":
    main()
