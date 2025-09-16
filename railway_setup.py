#!/usr/bin/env python3
"""
Настройка Railway для Secure Messenger
Альтернатива Heroku для России
"""

import os
import subprocess
import sys

def create_railway_files():
    """Создание файлов для Railway"""
    print("📁 Создание файлов для Railway...")
    
    # Создаем Procfile
    with open('Procfile', 'w') as f:
        f.write('web: python simple_web_server.py')
    print("✅ Создан Procfile")
    
    # Создаем requirements.txt для Railway
    with open('requirements_railway.txt', 'w') as f:
        f.write('''cryptography==42.0.2
pyperclip==1.8.2
requests==2.31.0
''')
    print("✅ Создан requirements_railway.txt")
    
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
    
    # Создаем README для Railway
    with open('README_RAILWAY.md', 'w') as f:
        f.write('''# Secure Messenger - Railway Deployment

## 🚀 Развертывание на Railway

1. Зайдите на https://railway.app
2. Зарегистрируйтесь через GitHub
3. Создайте новый проект
4. Подключите этот репозиторий
5. Railway автоматически развернет приложение

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
''')
    print("✅ Создан README_RAILWAY.md")

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
        subprocess.run(['git', 'commit', '-m', 'Initial commit - Secure Messenger'], check=True)
        print("✅ Создан первый коммит")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Ошибка создания Git репозитория")
        return False
    except FileNotFoundError:
        print("❌ Git не установлен")
        print("💡 Установите Git с https://git-scm.com")
        return False

def show_railway_instructions():
    """Показать инструкции по Railway"""
    print("🚂 ИНСТРУКЦИИ ПО RAILWAY:")
    print("=" * 50)
    print("1. Зайдите на https://railway.app")
    print("2. Нажмите 'Login' и выберите 'Login with GitHub'")
    print("3. Авторизуйтесь через GitHub")
    print("4. Нажмите 'New Project'")
    print("5. Выберите 'Deploy from GitHub repo'")
    print("6. Выберите ваш репозиторий")
    print("7. Railway автоматически развернет приложение")
    print("8. Получите публичный URL")
    print("9. Поделитесь ссылкой с друзьями!")
    print()
    print("💡 Railway бесплатен и работает в России!")

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
    print("8. Выполните команды из инструкций GitHub")
    print()
    print("💡 GitHub бесплатен и работает в России!")

def main():
    """Главная функция"""
    print("🚂 Настройка Railway для Secure Messenger")
    print("🇷🇺 Альтернатива Heroku для России")
    print("=" * 50)
    
    print("\nВыберите действие:")
    print("1. 📁 Создать файлы для Railway")
    print("2. 📦 Создать Git репозиторий")
    print("3. 🚂 Показать инструкции по Railway")
    print("4. 🐙 Показать инструкции по GitHub")
    print("5. 🔄 Полная настройка (все шаги)")
    
    choice = input("\nВведите номер (1-5): ").strip()
    
    if choice == "1":
        create_railway_files()
        
    elif choice == "2":
        create_git_repo()
        
    elif choice == "3":
        show_railway_instructions()
        
    elif choice == "4":
        show_github_instructions()
        
    elif choice == "5":
        print("🔄 Полная настройка...")
        create_railway_files()
        if create_git_repo():
            show_github_instructions()
            show_railway_instructions()
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
