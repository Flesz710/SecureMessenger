#!/usr/bin/env python3
"""
Простой веб-сервер для Secure Messenger
Использует только встроенные библиотеки Python
"""

import http.server
import socketserver
import json
import urllib.parse
import sqlite3
import hashlib
import os
import uuid
from datetime import datetime
from database import DatabaseManager
from crypto_utils import CryptoManager

# Инициализация базы данных
db = DatabaseManager()
active_users = {}  # {session_id: {'user_id': int, 'username': str, 'display_name': str}}
active_secure_chats = {}  # {chat_key: {'participants': [], 'encryption_key': str}}

class SecureMessengerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/api/status':
            self.send_api_response({'status': 'ok', 'message': 'Secure Messenger Web Server'})
            return
        return super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def handle_api_request(self):
        """Обработка API запросов"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/api/register':
                response = self.api_register(data)
            elif self.path == '/api/login':
                response = self.api_login(data)
            elif self.path == '/api/find_user':
                response = self.api_find_user(data)
            elif self.path == '/api/get_chats':
                response = self.api_get_chats(data)
            elif self.path == '/api/get_messages':
                response = self.api_get_messages(data)
            elif self.path == '/api/create_chat':
                response = self.api_create_chat(data)
            elif self.path == '/api/send_message':
                response = self.api_send_message(data)
            elif self.path == '/api/create_secure_chat':
                response = self.api_create_secure_chat(data)
            elif self.path == '/api/join_secure_chat':
                response = self.api_join_secure_chat(data)
            elif self.path == '/api/send_secure_message':
                response = self.api_send_secure_message(data)
            else:
                response = {'success': False, 'error': 'Неизвестный API endpoint'}
            
            self.send_api_response(response)
            
        except Exception as e:
            self.send_api_response({'success': False, 'error': f'Ошибка сервера: {str(e)}'})
    
    def send_api_response(self, data):
        """Отправка JSON ответа"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response)
    
    def api_register(self, data):
        """API регистрации"""
        try:
            username = data.get('username', '').strip()
            display_name = data.get('display_name', '').strip()
            password = data.get('password', '').strip()
            
            if not all([username, display_name, password]):
                return {'success': False, 'error': 'Заполните все поля'}
            
            success, result = db.register_user(username, display_name, password)
            
            if success:
                return {'success': True, 'secret_phrase': result}
            else:
                return {'success': False, 'error': result}
                
        except Exception as e:
            return {'success': False, 'error': f'Ошибка регистрации: {str(e)}'}
    
    def api_login(self, data):
        """API входа"""
        try:
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            if not all([username, password]):
                return {'success': False, 'error': 'Заполните все поля'}
            
            success, result = db.authenticate_user(username, password)
            
            if success:
                session_id = str(uuid.uuid4())
                active_users[session_id] = result
                return {'success': True, 'user_data': result, 'session_id': session_id}
            else:
                return {'success': False, 'error': result}
                
        except Exception as e:
            return {'success': False, 'error': f'Ошибка входа: {str(e)}'}
    
    def api_find_user(self, data):
        """API поиска пользователя"""
        try:
            display_name = data.get('display_name', '').strip()
            
            if not display_name:
                return {'success': False, 'error': 'Введите имя пользователя'}
            
            user_data = db.find_user_by_display_name(display_name)
            
            if user_data:
                return {'success': True, 'user_data': user_data}
            else:
                return {'success': False, 'error': 'Пользователь не найден'}
                
        except Exception as e:
            return {'success': False, 'error': f'Ошибка поиска: {str(e)}'}
    
    def api_get_chats(self, data):
        """API получения чатов"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            user_id = active_users[session_id]['user_id']
            chats = db.get_user_chats(user_id)
            
            return {'success': True, 'chats': chats}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка загрузки чатов: {str(e)}'}
    
    def api_get_messages(self, data):
        """API получения сообщений"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            chat_id = data.get('chat_id')
            limit = data.get('limit', 50)
            
            messages = db.get_chat_messages(chat_id, limit)
            
            return {'success': True, 'messages': messages}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка загрузки сообщений: {str(e)}'}
    
    def api_create_chat(self, data):
        """API создания чата"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            user2_id = data.get('user_id')
            
            user1_id = active_users[session_id]['user_id']
            chat_id = db.get_or_create_private_chat(user1_id, user2_id)
            
            if chat_id:
                return {'success': True, 'chat_id': chat_id}
            else:
                return {'success': False, 'error': 'Не удалось создать чат'}
                
        except Exception as e:
            return {'success': False, 'error': f'Ошибка создания чата: {str(e)}'}
    
    def api_send_message(self, data):
        """API отправки сообщения"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            chat_id = data.get('chat_id')
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'normal')
            
            if not content:
                return {'success': False, 'error': 'Сообщение не может быть пустым'}
            
            sender_id = active_users[session_id]['user_id']
            
            success = db.save_message(chat_id, sender_id, content, None, message_type)
            
            if success:
                return {'success': True, 'message': 'Сообщение отправлено'}
            else:
                return {'success': False, 'error': 'Ошибка сохранения сообщения'}
                
        except Exception as e:
            return {'success': False, 'error': f'Ошибка отправки сообщения: {str(e)}'}
    
    def api_create_secure_chat(self, data):
        """API создания защищенного чата"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            chat_key = data.get('chat_key', '').strip()
            encryption_key = data.get('encryption_key', '').strip()
            
            if not chat_key:
                return {'success': False, 'error': 'Введите ключ чата'}
            
            if chat_key in active_secure_chats:
                return {'success': False, 'error': 'Чат с таким ключом уже существует'}
            
            # Создаем защищенный чат
            active_secure_chats[chat_key] = {
                'participants': [session_id],
                'encryption_key': encryption_key,
                'created_at': datetime.now().isoformat(),
                'messages': []
            }
            
            return {'success': True, 'chat_key': chat_key, 'is_creator': True}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка создания защищенного чата: {str(e)}'}
    
    def api_join_secure_chat(self, data):
        """API присоединения к защищенному чату"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            chat_key = data.get('chat_key', '').strip()
            encryption_key = data.get('encryption_key', '').strip()
            
            if not chat_key:
                return {'success': False, 'error': 'Введите ключ чата'}
            
            if chat_key not in active_secure_chats:
                return {'success': False, 'error': 'Чат с таким ключом не найден'}
            
            # Проверяем ключ шифрования
            stored_key = active_secure_chats[chat_key]['encryption_key']
            if stored_key and stored_key != encryption_key:
                return {'success': False, 'error': 'Неверный ключ шифрования'}
            
            # Добавляем участника
            if session_id not in active_secure_chats[chat_key]['participants']:
                active_secure_chats[chat_key]['participants'].append(session_id)
            
            return {
                'success': True, 
                'chat_key': chat_key, 
                'is_creator': False,
                'participants_count': len(active_secure_chats[chat_key]['participants']),
                'messages': active_secure_chats[chat_key]['messages']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка присоединения к защищенному чату: {str(e)}'}
    
    def api_send_secure_message(self, data):
        """API отправки зашифрованного сообщения"""
        try:
            session_id = data.get('session_id')
            if not session_id or session_id not in active_users:
                return {'success': False, 'error': 'Не авторизован'}
            
            chat_key = data.get('chat_key', '').strip()
            content = data.get('content', '').strip()
            
            if not content:
                return {'success': False, 'error': 'Сообщение не может быть пустым'}
            
            if chat_key not in active_secure_chats:
                return {'success': False, 'error': 'Чат не найден'}
            
            if session_id not in active_secure_chats[chat_key]['participants']:
                return {'success': False, 'error': 'Вы не участник этого чата'}
            
            sender_name = active_users[session_id]['display_name']
            
            # Шифруем сообщение
            encryption_key = active_secure_chats[chat_key]['encryption_key']
            encrypted_content = content
            
            if encryption_key:
                try:
                    crypto_manager = CryptoManager()
                    crypto_manager.set_key(encryption_key.encode())
                    encrypted_content = crypto_manager.encrypt_message(content)
                except Exception as e:
                    return {'success': False, 'error': f'Ошибка шифрования: {str(e)}'}
            
            # Сохраняем сообщение
            message_data = {
                'sender_name': sender_name,
                'content': content,
                'encrypted_content': encrypted_content,
                'timestamp': datetime.now().isoformat()
            }
            
            active_secure_chats[chat_key]['messages'].append(message_data)
            
            return {'success': True, 'message': 'Зашифрованное сообщение отправлено'}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка отправки зашифрованного сообщения: {str(e)}'}

def start_web_server(port=8080):
    """Запуск веб-сервера"""
    print("🌐 Запуск веб-версии Secure Messenger...")
    print(f"📱 Откройте браузер и перейдите по адресу: http://localhost:{port}")
    print("🔐 Для тестирования с друзьями используйте ваш IP адрес")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", port), SecureMessengerHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == '__main__':
    start_web_server()
