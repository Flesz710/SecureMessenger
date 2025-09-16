#!/usr/bin/env python3
"""
Настройка Render для Secure Messenger
Альтернатива ngrok для России
"""

import os
import subprocess
import sys

def create_render_files():
    """Создание файлов для Render"""
    print("📁 Создание файлов для Render...")
    
    # Создаем requirements.txt для Render
    with open('requirements_render.txt', 'w') as f:
        f.write('''cryptography==42.0.2
pyperclip==1.8.2
requests==2.31.0
''')
    print("✅ Создан requirements_render.txt")
    
    # Создаем .gitignore
    with open('.gitignore', 'w') as f:
        f.write('''__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
messenger.db
server.log
''')
    print("✅ Создан .gitignore")
    
    # Создаем README для Render
    with open('README_RENDER.md', 'w') as f:
        f.write('''# Secure Messenger - Render Deployment

## 🚀 Развертывание на Render

1. Зайдите на https://render.com
2. Зарегистрируйтесь
3. Создайте Web Service
4. Подключите GitHub репозиторий
5. Render автоматически развернет приложение

## 📱 Использование

После развертывания вы получите публичный URL.
Поделитесь им с друзьями для тестирования мессенджера.

## 🔐 Функции

- Регистрация и вход в систему
- Обычные чаты с историей
- Защищенные чаты с шифрованием
- End-to-end шифрование сообщений

## 🛡️ Безопасность

- Пароли хешируются с солью (PBKDF2)
- Сообщения шифруются AES-256
- Защищенные чаты автоматически удаляются

## 🌐 Настройки Render

- **Build Command:** `pip install -r requirements_render.txt`
- **Start Command:** `python simple_web_server.py`
- **Port:** 8080
- **Environment:** Python 3.11
''')
    print("✅ Создан README_RENDER.md")
    
    # Создаем Procfile для Render
    with open('Procfile', 'w') as f:
        f.write('web: python simple_web_server.py')
    print("✅ Создан Procfile")

def create_git_repo():
    """Создание Git репозитория"""
    print("📦 Создание Git репозитория...")
    
    try:
        # Инициализируем Git
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git репозиторий инициализирован")
        
        # Добавляем файлы
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Файлы добавлены в Git")
        
        # Создаем коммит
        subprocess.run(['git', 'commit', '-m', 'Initial commit - Secure Messenger for Render'], check=True)
        print("✅ Создан первый коммит")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Ошибка создания Git репозитория")
        return False
    except FileNotFoundError:
        print("❌ Git не установлен")
        print("💡 Установите Git с https://git-scm.com")
        return False

def show_render_instructions():
    """Показать инструкции по Render"""
    print("🌟 ИНСТРУКЦИИ ПО RENDER:")
    print("=" * 50)
    print("1. Зайдите на https://render.com")
    print("2. Нажмите 'Get Started for Free'")
    print("3. Зарегистрируйтесь через GitHub или email")
    print("4. Нажмите 'New +' → 'Web Service'")
    print("5. Выберите 'Build and deploy from a Git repository'")
    print("6. Подключите ваш GitHub репозиторий")
    print("7. Настройте параметры:")
    print("   - Name: secure-messenger")
    print("   - Build Command: pip install -r requirements_render.txt")
    print("   - Start Command: python simple_web_server.py")
    print("   - Port: 8080")
    print("8. Нажмите 'Create Web Service'")
    print("9. Render автоматически развернет приложение")
    print("10. Получите публичный URL")
    print("11. Поделитесь ссылкой с друзьями!")
    print()
    print("💡 Render бесплатен и работает в России!")

def show_github_instructions():
    """Показать инструкции по GitHub"""
    print("🐙 ИНСТРУКЦИИ ПО GITHUB:")
    print("=" * 50)
    print("1. Зайдите на https://github.com")
    print("2. Зарегистрируйтесь или войдите")
    print("3. Нажмите 'New repository'")
    print("4. Назовите репозиторий (например: secure-messenger)")
    print("5. Выберите 'Public'")
    print("6. НЕ отмечайте 'Add README'")
    print("7. Нажмите 'Create repository'")
    print("8. Выполните команды из инструкций GitHub:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/secure-messenger.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("💡 GitHub бесплатен и работает в России!")

def show_render_vs_ngrok():
    """Сравнение Render и ngrok"""
    print("🆚 СРАВНЕНИЕ RENDER И NGROK:")
    print("=" * 50)
    print("RENDER:")
    print("✅ Постоянный URL")
    print("✅ Не требует запуска на вашем компьютере")
    print("✅ Всегда доступен")
    print("✅ Бесплатно")
    print("✅ Работает в России")
    print("❌ Требует GitHub репозиторий")
    print("❌ Сложнее настройка")
    print()
    print("NGROK:")
    print("✅ Простая настройка")
    print("✅ Быстрый запуск")
    print("✅ Не требует GitHub")
    print("❌ URL меняется при перезапуске")
    print("❌ Требует запуск на вашем компьютере")
    print("❌ Ограничения бесплатной версии")
    print()
    print("💡 РЕКОМЕНДАЦИЯ: Render для постоянного использования!")

def main():
    """Главная функция"""
    print("🌟 Настройка Render для Secure Messenger")
    print("🇷🇺 Альтернатива ngrok для России")
    print("=" * 50)
    
    print("\nВыберите действие:")
    print("1. 📁 Создать файлы для Render")
    print("2. 📦 Создать Git репозиторий")
    print("3. 🌟 Показать инструкции по Render")
    print("4. 🐙 Показать инструкции по GitHub")
    print("5. 🆚 Сравнить Render и ngrok")
    print("6. 🔄 Полная настройка (все шаги)")
    
    choice = input("\nВведите номер (1-6): ").strip()
    
    if choice == "1":
        create_render_files()
        
    elif choice == "2":
        create_git_repo()
        
    elif choice == "3":
        show_render_instructions()
        
    elif choice == "4":
        show_github_instructions()
        
    elif choice == "5":
        show_render_vs_ngrok()
        
    elif choice == "6":
        print("🔄 Полная настройка...")
        create_render_files()
        if create_git_repo():
            show_github_instructions()
            show_render_instructions()
        else:
            print("❌ Не удалось создать Git репозиторий")
            print("💡 Установите Git и попробуйте снова")
        
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
