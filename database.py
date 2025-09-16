import sqlite3
import hashlib
import os
import uuid
from datetime import datetime
from crypto_utils import CryptoManager

class DatabaseManager:
    def __init__(self, db_path="messenger.db"):
        self.db_path = db_path
        self.crypto_manager = CryptoManager()
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                secret_phrase TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица чатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица участников чатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                FOREIGN KEY (chat_id) REFERENCES chats (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender_id INTEGER,
                content TEXT,
                encrypted_content TEXT,
                message_type TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
        ''')
        
        # Таблица защищенных чатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secure_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                encryption_key TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        salt = os.urandom(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + hash_obj.hex()
    
    def verify_password(self, password, stored_hash):
        """Проверка пароля"""
        try:
            salt_hex = stored_hash[:32]
            hash_hex = stored_hash[32:]
            salt = bytes.fromhex(salt_hex)
            stored_hash_bytes = bytes.fromhex(hash_hex)
            
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return hash_obj == stored_hash_bytes
        except:
            return False
    
    def register_user(self, username, display_name, password):
        """Регистрация нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем, что пользователь не существует
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Пользователь с таким именем уже существует"
            
            # Генерируем секретную фразу
            secret_phrase = self.generate_secret_phrase()
            
            # Хешируем пароль
            password_hash = self.hash_password(password)
            
            # Добавляем пользователя
            cursor.execute('''
                INSERT INTO users (username, display_name, password_hash, secret_phrase)
                VALUES (?, ?, ?, ?)
            ''', (username, display_name, password_hash, secret_phrase))
            
            conn.commit()
            conn.close()
            
            return True, secret_phrase
        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"
    
    def generate_secret_phrase(self):
        """Генерация секретной фразы для восстановления"""
        words = [
            "apple", "banana", "cherry", "dragon", "eagle", "forest", "garden", "house",
            "island", "jungle", "knight", "lemon", "mountain", "ocean", "planet", "queen",
            "river", "star", "tiger", "umbrella", "village", "water", "xylophone", "yellow"
        ]
        phrase = []
        for _ in range(4):
            phrase.append(words[os.urandom(1)[0] % len(words)])
        return "-".join(phrase)
    
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, password_hash, display_name FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()
            
            conn.close()
            
            if not user_data:
                return False, "Пользователь не найден"
            
            user_id, password_hash, display_name = user_data
            
            if self.verify_password(password, password_hash):
                return True, {"user_id": user_id, "username": username, "display_name": display_name}
            else:
                return False, "Неверный пароль"
        except Exception as e:
            return False, f"Ошибка аутентификации: {str(e)}"
    
    def find_user_by_display_name(self, display_name):
        """Поиск пользователя по имени аккаунта"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, display_name FROM users WHERE display_name = ?", (display_name,))
            user_data = cursor.fetchone()
            
            conn.close()
            
            if user_data:
                return {"user_id": user_data[0], "username": user_data[1], "display_name": user_data[2]}
            return None
        except Exception as e:
            return None
    
    def get_user_chats(self, user_id):
        """Получение чатов пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT c.id, c.chat_type, c.created_at,
                       (SELECT COUNT(*) FROM messages WHERE chat_id = c.id) as message_count,
                       (SELECT content FROM messages WHERE chat_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
                FROM chats c
                JOIN chat_participants cp ON c.id = cp.chat_id
                WHERE cp.user_id = ?
                ORDER BY c.created_at DESC
            ''', (user_id,))
            
            chats = cursor.fetchall()
            conn.close()
            
            return [{"chat_id": chat[0], "chat_type": chat[1], "created_at": chat[2], 
                    "message_count": chat[3], "last_message": chat[4]} for chat in chats]
        except Exception as e:
            return []
    
    def create_chat(self, chat_type, participants):
        """Создание нового чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Создаем чат
            cursor.execute("INSERT INTO chats (chat_type) VALUES (?)", (chat_type,))
            chat_id = cursor.lastrowid
            
            # Добавляем участников
            for user_id in participants:
                cursor.execute("INSERT INTO chat_participants (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
            
            conn.commit()
            conn.close()
            
            return chat_id
        except Exception as e:
            return None
    
    def get_or_create_private_chat(self, user1_id, user2_id):
        """Получение или создание приватного чата между двумя пользователями"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ищем существующий приватный чат
            cursor.execute('''
                SELECT c.id FROM chats c
                JOIN chat_participants cp1 ON c.id = cp1.chat_id
                JOIN chat_participants cp2 ON c.id = cp2.chat_id
                WHERE c.chat_type = 'private' 
                AND cp1.user_id = ? AND cp2.user_id = ?
            ''', (user1_id, user2_id))
            
            existing_chat = cursor.fetchone()
            
            if existing_chat:
                conn.close()
                return existing_chat[0]
            
            # Создаем новый чат
            chat_id = self.create_chat("private", [user1_id, user2_id])
            conn.close()
            
            return chat_id
        except Exception as e:
            return None
    
    def save_message(self, chat_id, sender_id, content, encrypted_content=None, message_type="normal"):
        """Сохранение сообщения"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (chat_id, sender_id, content, encrypted_content, message_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, sender_id, content, encrypted_content, message_type))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def get_chat_messages(self, chat_id, limit=50):
        """Получение сообщений чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.id, m.sender_id, m.content, m.encrypted_content, m.message_type, m.created_at,
                       u.display_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.chat_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            ''', (chat_id, limit))
            
            messages = cursor.fetchall()
            conn.close()
            
            return [{"id": msg[0], "sender_id": msg[1], "content": msg[2], 
                    "encrypted_content": msg[3], "message_type": msg[4], 
                    "created_at": msg[5], "sender_name": msg[6]} for msg in messages]
        except Exception as e:
            return []
    
    def create_secure_chat_session(self, chat_id, encryption_key):
        """Создание защищенной сессии чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO secure_chats (chat_id, encryption_key, session_id)
                VALUES (?, ?, ?)
            ''', (chat_id, encryption_key, session_id))
            
            conn.commit()
            conn.close()
            
            return session_id
        except Exception as e:
            return None
    
    def get_secure_chat_session(self, chat_id):
        """Получение защищенной сессии чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT encryption_key, session_id FROM secure_chats
                WHERE chat_id = ? ORDER BY created_at DESC LIMIT 1
            ''', (chat_id,))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if session_data:
                return {"encryption_key": session_data[0], "session_id": session_data[1]}
            return None
        except Exception as e:
            return None
    
    def clear_secure_chat(self, chat_id):
        """Очистка защищенного чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Удаляем сообщения защищенного чата
            cursor.execute("DELETE FROM messages WHERE chat_id = ? AND message_type = 'secure'", (chat_id,))
            
            # Удаляем сессию
            cursor.execute("DELETE FROM secure_chats WHERE chat_id = ?", (chat_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
