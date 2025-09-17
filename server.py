import socket
import threading
import json
import logging
from datetime import datetime
from database import DatabaseManager

class SecureMessengerServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.clients = {}  # {client_socket: {'user_id': int, 'username': str, 'address': tuple}}
        self.server_socket = None
        self.running = False
        self.db = DatabaseManager()
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Запуск сервера"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            self.logger.info(f"Сервер запущен на {self.host}:{self.port}")
            print(f"Сервер запущен на {self.host}:{self.port}")
            print("Ожидание подключений...")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.logger.info(f"Новое подключение от {address}")
                    
                    # Создаем поток для обработки клиента
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"Ошибка при принятии подключения: {e}")
                        
        except Exception as e:
            self.logger.error(f"Ошибка запуска сервера: {e}")
            print(f"Ошибка запуска сервера: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, address):
        """Обработка клиентского подключения"""
        try:
            while self.running:
                try:
                    message = self.receive_message(client_socket)
                    if not message:
                        break
                        
                    message_data = json.loads(message)
                    message_type = message_data.get('type', 'unknown')
                    
                    if message_type == 'auth':
                        self.handle_auth(client_socket, message_data)
                    elif message_type == 'register':
                        self.handle_register(client_socket, message_data)
                    elif message_type == 'find_user':
                        self.handle_find_user(client_socket, message_data)
                    elif message_type == 'create_chat':
                        self.handle_create_chat(client_socket, message_data)
                    elif message_type == 'get_chats':
                        self.handle_get_chats(client_socket, message_data)
                    elif message_type == 'get_messages':
                        self.handle_get_messages(client_socket, message_data)
                    elif message_type == 'send_message':
                        self.handle_send_message(client_socket, message_data)
                    elif message_type == 'create_secure_chat':
                        self.handle_create_secure_chat(client_socket, message_data)
                    elif message_type == 'join_secure_chat':
                        self.handle_join_secure_chat(client_socket, message_data)
                    elif message_type == 'clear_chat_history':
                        self.handle_clear_chat_history(client_socket, message_data)
                    elif message_type == 'close_secure_chat':
                        self.handle_close_secure_chat(client_socket, message_data)
                    elif message_type == 'auto_close_secure_chat':
                        self.handle_auto_close_secure_chat(client_socket, message_data)
                    elif message_type == 'get_chat_info':
                        self.handle_get_chat_info(client_socket, message_data)
                    elif message_type == 'change_display_name':
                        self.handle_change_display_name(client_socket, message_data)
                    elif message_type == 'disconnect':
                        break
                        
                except json.JSONDecodeError:
                    self.logger.warning(f"Неверный формат JSON от {address}")
                except Exception as e:
                    self.logger.error(f"Ошибка обработки сообщения от {address}: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Ошибка обработки клиента {address}: {e}")
        finally:
            self.remove_client(client_socket)
    
    def handle_auth(self, client_socket, message_data):
        """Обработка аутентификации"""
        username = message_data.get('username', '')
        password = message_data.get('password', '')
        
        success, result = self.db.authenticate_user(username, password)
        
        if success:
            user_data = result
            self.clients[client_socket] = {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'display_name': user_data['display_name']
            }
            
            response = {
                'type': 'auth_response',
                'success': True,
                'user_data': user_data
            }
        else:
            response = {
                'type': 'auth_response',
                'success': False,
                'error': result
            }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_register(self, client_socket, message_data):
        """Обработка регистрации"""
        username = message_data.get('username', '')
        display_name = message_data.get('display_name', '')
        password = message_data.get('password', '')
        
        success, result = self.db.register_user(username, display_name, password)
        
        if success:
            response = {
                'type': 'register_response',
                'success': True,
                'secret_phrase': result
            }
        else:
            response = {
                'type': 'register_response',
                'success': False,
                'error': result
            }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_find_user(self, client_socket, message_data):
        """Обработка поиска пользователя"""
        display_name = message_data.get('display_name', '')
        user_data = self.db.find_user_by_display_name(display_name)
        
        response = {
            'type': 'find_user_response',
            'success': user_data is not None,
            'user_data': user_data
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_clear_chat_history(self, client_socket, message_data):
        """Обработка очистки истории чатов"""
        if client_socket not in self.clients:
            return
        
        user_id = self.clients[client_socket]['user_id']
        success = self.db.clear_user_chat_history(user_id)
        
        response = {
            'type': 'clear_chat_history_response',
            'success': success
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_create_chat(self, client_socket, message_data):
        """Обработка создания чата"""
        if client_socket not in self.clients:
            return
        
        user1_id = self.clients[client_socket]['user_id']
        user2_id = message_data.get('user_id')
        
        chat_id = self.db.get_or_create_private_chat(user1_id, user2_id)
        
        response = {
            'type': 'create_chat_response',
            'success': chat_id is not None,
            'chat_id': chat_id
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_get_chats(self, client_socket, message_data):
        """Обработка получения чатов"""
        if client_socket not in self.clients:
            return
        
        user_id = self.clients[client_socket]['user_id']
        chats = self.db.get_user_chats(user_id)
        
        response = {
            'type': 'get_chats_response',
            'chats': chats
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_get_messages(self, client_socket, message_data):
        """Обработка получения сообщений"""
        chat_id = message_data.get('chat_id')
        limit = message_data.get('limit', 50)
        
        messages = self.db.get_chat_messages(chat_id, limit)
        
        response = {
            'type': 'get_messages_response',
            'chat_id': chat_id,
            'messages': messages
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_send_message(self, client_socket, message_data):
        """Обработка отправки сообщения"""
        if client_socket not in self.clients:
            return
        
        sender_id = self.clients[client_socket]['user_id']
        chat_id = message_data.get('chat_id')
        content = message_data.get('content', '')
        encrypted_content = message_data.get('encrypted_content')
        message_type = message_data.get('message_type', 'normal')
        
        success = self.db.save_message(chat_id, sender_id, content, encrypted_content, message_type)
        
        if success:
            # Отправляем сообщение всем участникам чата
            self.broadcast_to_chat(chat_id, {
                'type': 'new_message',
                'chat_id': chat_id,
                'sender_id': sender_id,
                'sender_name': self.clients[client_socket]['display_name'],
                'content': content,
                'encrypted_content': encrypted_content,
                'message_type': message_type,
                'timestamp': datetime.now().isoformat()
            }, exclude=client_socket)
    
    def handle_create_secure_chat(self, client_socket, message_data):
        """Обработка создания защищенного чата"""
        if client_socket not in self.clients:
            return
        
        chat_key = message_data.get('chat_key')
        encryption_key = message_data.get('encryption_key')
        
        # Создаем защищенную сессию
        session_data = self.db.create_secure_chat_session(chat_key, encryption_key)
        
        if session_data:
            response = {
                'type': 'create_secure_chat_response',
                'success': True,
                'chat_key': session_data['chat_key'],
                'session_id': session_data['session_id']
            }
        else:
            response = {
                'type': 'create_secure_chat_response',
                'success': False,
                'error': 'Не удалось создать защищенный чат'
            }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_join_secure_chat(self, client_socket, message_data):
        """Обработка присоединения к защищенному чату"""
        if client_socket not in self.clients:
            return
        
        chat_key = message_data.get('chat_key')
        encryption_key = message_data.get('encryption_key')
        
        # Проверяем сессию
        session_data = self.db.get_secure_chat_session(chat_key)
        
        if session_data:
            # Если ключ шифрования не предоставлен или совпадает
            if not encryption_key or session_data['encryption_key'] == encryption_key:
                # Получаем существующие сообщения
                messages = self.db.get_secure_messages(chat_key)
                
                response = {
                    'type': 'join_secure_chat_response',
                    'success': True,
                    'chat_key': chat_key,
                    'session_id': session_data['session_id'],
                    'participants_count': 1,  # Пока упрощенно
                    'messages': messages
                }
            else:
                response = {
                    'type': 'join_secure_chat_response',
                    'success': False,
                    'error': 'Неверный ключ шифрования'
                }
        else:
            response = {
                'type': 'join_secure_chat_response',
                'success': False,
                'error': 'Защищенный чат не найден'
            }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_send_secure_message(self, client_socket, message_data):
        """Обработка отправки защищенного сообщения"""
        if client_socket not in self.clients:
            return
        
        sender_id = self.clients[client_socket]['user_id']
        chat_key = message_data.get('chat_key')
        content = message_data.get('content', '')
        
        success = self.db.save_secure_message(chat_key, sender_id, content)
        
        response = {
            'type': 'send_secure_message_response',
            'success': success
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_get_secure_messages(self, client_socket, message_data):
        """Обработка получения защищенных сообщений"""
        chat_key = message_data.get('chat_key')
        messages = self.db.get_secure_messages(chat_key)
        
        response = {
            'type': 'get_secure_messages_response',
            'success': True,
            'messages': messages
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_close_secure_chat(self, client_socket, message_data):
        """Обработка закрытия защищенного чата"""
        if client_socket not in self.clients:
            return
        
        chat_key = message_data.get('chat_key')
        success = self.db.close_secure_chat(chat_key)
        
        response = {
            'type': 'close_secure_chat_response',
            'success': success
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_auto_close_secure_chat(self, client_socket, message_data):
        """Обработка автоматического закрытия защищенного чата"""
        chat_key = message_data.get('chat_key')
        success = self.db.close_secure_chat(chat_key)
        
        response = {
            'type': 'auto_close_secure_chat_response',
            'success': success
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_get_chat_info(self, client_socket, message_data):
        """Обработка получения информации о чате"""
        if client_socket not in self.clients:
            return
        
        user_id = self.clients[client_socket]['user_id']
        chat_id = message_data.get('chat_id')
        chat_info = self.db.get_chat_info(user_id, chat_id)
        
        response = {
            'type': 'get_chat_info_response',
            'success': chat_info is not None,
            'chat_info': chat_info
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def handle_change_display_name(self, client_socket, message_data):
        """Обработка изменения имени пользователя"""
        if client_socket not in self.clients:
            return
        
        user_id = self.clients[client_socket]['user_id']
        new_display_name = message_data.get('new_display_name')
        
        success = self.db.change_display_name(user_id, new_display_name)
        
        if success:
            # Обновляем информацию о пользователе в клиентах
            self.clients[client_socket]['display_name'] = new_display_name
        
        response = {
            'type': 'change_display_name_response',
            'success': success
        }
        
        self.send_message(client_socket, json.dumps(response))
    
    def broadcast_to_chat(self, chat_id, message, exclude=None):
        """Отправка сообщения всем участникам чата"""
        # Получаем участников чата из базы данных
        # Это упрощенная версия - в реальном приложении нужно кэшировать участников
        for client_socket in self.clients:
            if client_socket != exclude:
                try:
                    self.send_message(client_socket, json.dumps(message))
                except Exception as e:
                    self.logger.error(f"Ошибка отправки сообщения клиенту: {e}")
                    self.remove_client(client_socket)
    
    def receive_message(self, client_socket):
        """Получение сообщения от клиента"""
        try:
            # Получаем длину сообщения (4 байта)
            length_data = client_socket.recv(4)
            if not length_data:
                return None
                
            message_length = int.from_bytes(length_data, 'big')
            
            # Получаем само сообщение
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(min(message_length - len(message_data), 1024))
                if not chunk:
                    return None
                message_data += chunk
                
            return message_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Ошибка получения сообщения: {e}")
            return None
    
    def send_message(self, client_socket, message):
        """Отправка сообщения клиенту"""
        try:
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes).to_bytes(4, 'big')
            client_socket.send(message_length + message_bytes)
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
    
    def remove_client(self, client_socket):
        """Удаление клиента из списка"""
        if client_socket in self.clients:
            username = self.clients[client_socket]['display_name']
            del self.clients[client_socket]
            client_socket.close()
            
            self.logger.info(f"Пользователь {username} отключился")
    
    def stop(self):
        """Остановка сервера"""
        self.running = False
        
        # Закрываем все клиентские соединения
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        
        # Закрываем серверный сокет
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("Сервер остановлен")
        print("Сервер остановлен")

if __name__ == '__main__':
    server = SecureMessengerServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки...")
        server.stop()
