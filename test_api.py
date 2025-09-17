#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API защищенных чатов
"""

import requests
import json

def test_api():
    """Тестирование API"""
    base_url = "http://localhost:8080/api"
    
    print("🧪 Тестирование API защищенных чатов")
    print("=" * 50)
    
    # Тест 1: Создание защищенного чата
    print("\n1️⃣ Тест создания защищенного чата...")
    try:
        response = requests.post(f"{base_url}/create_secure_chat", json={
            "session_id": "test_session",
            "chat_key": "test123",
            "encryption_key": None
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Создание чата: {data}")
        else:
            print(f"❌ Ошибка создания чата: {response.status_code}")
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    
    # Тест 2: Отправка защищенного сообщения
    print("\n2️⃣ Тест отправки защищенного сообщения...")
    try:
        response = requests.post(f"{base_url}/send_secure_message", json={
            "session_id": "test_session",
            "chat_key": "test123",
            "content": "Тестовое сообщение"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Отправка сообщения: {data}")
        else:
            print(f"❌ Ошибка отправки сообщения: {response.status_code}")
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    
    # Тест 3: Закрытие защищенного чата
    print("\n3️⃣ Тест закрытия защищенного чата...")
    try:
        response = requests.post(f"{base_url}/close_secure_chat", json={
            "session_id": "test_session",
            "chat_key": "test123"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Закрытие чата: {data}")
        else:
            print(f"❌ Ошибка закрытия чата: {response.status_code}")
            print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    
    # Тест 4: Health check
    print("\n4️⃣ Тест health check...")
    try:
        response = requests.get("http://localhost:8080/health")
        
        if response.status_code == 200:
            print(f"✅ Health check: {response.json()}")
        else:
            print(f"❌ Ошибка health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    test_api()
