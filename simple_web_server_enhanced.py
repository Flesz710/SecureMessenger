#!/usr/bin/env python3
"""
Улучшенный веб-сервер для Secure Messenger с поддержкой keep-alive
"""

import http.server
import socketserver
import json
import os
import sys
import threading
import time
from datetime import datetime
import urllib.parse

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from server import SecureMessengerServer
    from database import DatabaseManager
    from crypto_utils import CryptoUtils
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все файлы проекта находятся в той же папке")
    sys.exit(1)

class EnhancedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Улучшенный HTTP обработчик с API поддержкой"""
    
    def __init__(self, *args, **kwargs):
        self.messenger_server = None
        super().__init__(*args, **kwargs)
    
    def set_messenger_server(self, server):
        """Устанавливает ссылку на сервер мессенджера"""
        self.messenger_server = server
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            # Главная страница
            self.path = '/index.html'
            return super().do_GET()
        elif self.path == '/health':
            # Health check для keep-alive
            self.send_health_response()
        elif self.path.startswith('/api/'):
            # API запросы
            self.handle_api_request()
        else:
            # Статические файлы
            return super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Отправляет health check ответ"""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self.server.start_time,
                "messenger_status": "running" if self.messenger_server else "stopped"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())
            
        except Exception as e:
            self.send_error(500, f"Health check error: {e}")
    
    def handle_api_request(self):
        """Обработка API запросов"""
        try:
            # Парсим путь API
            api_path = self.path[5:]  # Убираем '/api/'
            
            # Читаем данные запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if post_data:
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    request_data = {}
            else:
                request_data = {}
            
            # Обрабатываем запрос
            response_data = self.process_api_request(api_path, request_data)
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            print(f"API Error: {e}")
            error_response = {"success": False, "error": str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def process_api_request(self, api_path, request_data):
        """Обрабатывает API запросы"""
        if not self.messenger_server:
            return {"success": False, "error": "Messenger server not available"}
        
        try:
            # Создаем фиктивный клиент для обработки запроса
            class MockClient:
                def __init__(self, request_data):
                    self.request_data = request_data
                    self.response_data = {}
                
                def send(self, data):
                    self.response_data = data
                
                def recv(self, size):
                    return b''
            
            mock_client = MockClient(request_data)
            
            # Обрабатываем запрос через сервер мессенджера
            if api_path == 'login':
                return self.messenger_server.handle_login(request_data)
            elif api_path == 'register':
                return self.messenger_server.handle_register(request_data)
            elif api_path == 'get_chats':
                return self.messenger_server.handle_get_chats(request_data)
            elif api_path == 'get_messages':
                return self.messenger_server.handle_get_messages(request_data)
            elif api_path == 'send_message':
                return self.messenger_server.handle_send_message(request_data)
            elif api_path == 'create_chat':
                return self.messenger_server.handle_create_chat(request_data)
            elif api_path == 'find_user':
                return self.messenger_server.handle_find_user(request_data)
            elif api_path == 'create_secure_chat':
                return self.messenger_server.handle_create_secure_chat(request_data)
            elif api_path == 'join_secure_chat':
                return self.messenger_server.handle_join_secure_chat(request_data)
            elif api_path == 'send_secure_message':
                return self.messenger_server.handle_send_secure_message(request_data)
            elif api_path == 'get_secure_messages':
                return self.messenger_server.handle_get_secure_messages(request_data)
            else:
                return {"success": False, "error": f"Unknown API endpoint: {api_path}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def log_message(self, format, *args):
        """Переопределяем логирование для более чистого вывода"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

class EnhancedWebServer:
    """Улучшенный веб-сервер с поддержкой keep-alive"""
    
    def __init__(self, port=8080):
        self.port = port
        self.messenger_server = None
        self.httpd = None
        self.keep_alive_thread = None
        self.running = False
    
    def start_messenger_server(self):
        """Запускает сервер мессенджера в отдельном потоке"""
        try:
            print("🚀 Запуск сервера мессенджера...")
            self.messenger_server = SecureMessengerServer()
            
            # Запускаем сервер в отдельном потоке
            messenger_thread = threading.Thread(
                target=self.messenger_server.start_server,
                daemon=True
            )
            messenger_thread.start()
            
            print("✅ Сервер мессенджера запущен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска сервера мессенджера: {e}")
            return False
    
    def start_keep_alive(self):
        """Запускает keep-alive в отдельном потоке"""
        def keep_alive_worker():
            while self.running:
                try:
                    # Отправляем ping на себя
                    import requests
                    response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"💓 Keep-alive ping успешен")
                    else:
                        print(f"⚠️ Keep-alive ping неуспешен: {response.status_code}")
                except Exception as e:
                    print(f"❌ Keep-alive ошибка: {e}")
                
                # Ждем 5 минут
                time.sleep(300)
        
        self.keep_alive_thread = threading.Thread(target=keep_alive_worker, daemon=True)
        self.keep_alive_thread.start()
        print("💓 Keep-alive запущен")
    
    def start_server(self):
        """Запускает веб-сервер"""
        try:
            # Запускаем сервер мессенджера
            if not self.start_messenger_server():
                return False
            
            # Создаем HTTP сервер
            handler = EnhancedHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", self.port), handler)
            self.httpd.start_time = time.time()
            
            # Устанавливаем ссылку на сервер мессенджера
            self.httpd.RequestHandlerClass.set_messenger_server = lambda self, server: setattr(self, 'messenger_server', server)
            
            # Устанавливаем ссылку для всех обработчиков
            for handler_instance in self.httpd.RequestHandlerClass.__dict__.values():
                if hasattr(handler_instance, 'set_messenger_server'):
                    handler_instance.set_messenger_server(self.messenger_server)
            
            self.running = True
            
            # Запускаем keep-alive
            self.start_keep_alive()
            
            print(f"🌐 Веб-сервер запущен на порту {self.port}")
            print(f"📱 Откройте: http://localhost:{self.port}")
            print(f"💓 Health check: http://localhost:{self.port}/health")
            print("🛑 Нажмите Ctrl+C для остановки")
            
            # Запускаем сервер
            self.httpd.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервера...")
            self.stop_server()
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            return False
    
    def stop_server(self):
        """Останавливает сервер"""
        self.running = False
        
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        
        if self.messenger_server:
            self.messenger_server.stop_server()
        
        print("✅ Сервер остановлен")

def main():
    """Основная функция"""
    print("🔐 Secure Messenger - Улучшенный веб-сервер")
    print("=" * 50)
    
    # Получаем порт из переменной окружения или используем по умолчанию
    port = int(os.getenv('PORT', 8080))
    
    # Создаем и запускаем сервер
    server = EnhancedWebServer(port)
    server.start_server()

if __name__ == "__main__":
    main()
