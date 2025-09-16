import os
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

class CryptoManager:
    def __init__(self):
        self.key = None
        self.fernet = None
        
    def generate_key_from_password(self, password, salt=None):
        """Генерация ключа из пароля с использованием PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.key = key
        self.fernet = Fernet(key)
        return salt
        
    def set_key(self, key):
        """Установка готового ключа"""
        self.key = key
        self.fernet = Fernet(key)
        
    def encrypt_message(self, message, salt=None):
        """Шифрование сообщения"""
        if not self.fernet:
            raise ValueError("Ключ не установлен")
            
        if salt is None:
            salt = os.urandom(16)
            
        # Генерируем ключ с солью
        self.generate_key_from_password(self.key.decode(), salt)
        
        # Шифруем сообщение
        encrypted_message = self.fernet.encrypt(message.encode())
        
        # Возвращаем соль + зашифрованное сообщение
        return base64.urlsafe_b64encode(salt + encrypted_message).decode()
        
    def decrypt_message(self, encrypted_data):
        """Расшифрование сообщения"""
        if not self.fernet:
            raise ValueError("Ключ не установлен")
            
        try:
            # Декодируем данные
            data = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Извлекаем соль и зашифрованное сообщение
            salt = data[:16]
            encrypted_message = data[16:]
            
            # Генерируем ключ с солью
            self.generate_key_from_password(self.key.decode(), salt)
            
            # Расшифровываем сообщение
            decrypted_message = self.fernet.decrypt(encrypted_message)
            return decrypted_message.decode()
            
        except InvalidToken:
            raise ValueError("Неверный ключ или поврежденные данные")
        except Exception as e:
            raise ValueError(f"Ошибка расшифрования: {str(e)}")
            
    def generate_random_key(self):
        """Генерация случайного ключа"""
        key = Fernet.generate_key()
        self.key = key
        self.fernet = Fernet(key)
        return key
        
    def get_key_b64(self):
        """Получение ключа в base64 формате"""
        if self.key:
            return self.key.decode()
        return None
        
    def hash_password(self, password):
        """Хеширование пароля для хранения"""
        salt = os.urandom(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.b64encode(salt + hash_obj).decode()
        
    def verify_password(self, password, stored_hash):
        """Проверка пароля"""
        try:
            data = base64.b64decode(stored_hash.encode())
            salt = data[:16]
            stored_hash_bytes = data[16:]
            
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return hash_obj == stored_hash_bytes
        except:
            return False
