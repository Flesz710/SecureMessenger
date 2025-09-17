#!/usr/bin/env python3
"""
Тестовый скрипт для проверки поиска пользователей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def test_user_search():
    """Тестирование поиска пользователей"""
    print("🔍 Тестирование поиска пользователей...")
    
    db = DatabaseManager()
    
    # Получаем всех пользователей
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, display_name FROM users")
        users = cursor.fetchall()
        
        print(f"📊 Найдено пользователей в базе: {len(users)}")
        
        for user in users:
            user_id, username, display_name = user
            print(f"  - ID: {user_id}, Логин: {username}, Имя: {display_name}")
            
            # Тестируем поиск по имени
            found_user = db.find_user_by_display_name(display_name)
            if found_user:
                print(f"    ✅ Поиск по имени '{display_name}' - найден")
            else:
                print(f"    ❌ Поиск по имени '{display_name}' - НЕ найден")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_user_search()
