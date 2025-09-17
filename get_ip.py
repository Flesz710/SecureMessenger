#!/usr/bin/env python3
"""
Скрипт для получения IP адреса для тестирования с друзьями
"""

import socket
import requests

def get_local_ip():
    """Получение локального IP адреса"""
    try:
        # Создаем временное соединение для определения IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Не удалось определить"

def get_external_ip():
    """Получение внешнего IP адреса"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "Не удалось определить"

def main():
    print("🌐 Информация о сетевых адресах для Secure Messenger")
    print("=" * 60)
    
    local_ip = get_local_ip()
    external_ip = get_external_ip()
    
    print(f"🏠 Локальный IP адрес: {local_ip}")
    print(f"🌍 Внешний IP адрес: {external_ip}")
    print()
    
    if local_ip != "Не удалось определить":
        print("📱 Для тестирования в локальной сети:")
        print(f"   http://{local_ip}:8080")
        print()
        print("👥 Друзья в той же сети могут подключиться по этому адресу")
        print()
    
    if external_ip != "Не удалось определить":
        print("🌍 Для тестирования из интернета:")
        print(f"   http://{external_ip}:8080")
        print()
        print("⚠️  Внимание: Убедитесь, что:")
        print("   1. Порт 8080 открыт в брандмауэре")
        print("   2. Настроен проброс портов в роутере")
        print("   3. Используется надежный пароль")
        print()
    
    print("🚀 Рекомендуется использовать ngrok для безопасного тестирования:")
    print("   1. Скачайте ngrok с https://ngrok.com")
    print("   2. Запустите: ngrok http 8080")
    print("   3. Поделитесь полученной ссылкой с друзьями")
    print()
    print("🛡️  Для остановки сервера нажмите Ctrl+C")

if __name__ == '__main__':
    main()

