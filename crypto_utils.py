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
    
    def generate_key(self):
        """Генерация нового ключа Fernet"""
        key = Fernet.generate_key()
        return key.decode()  # Возвращаем как строку
    
    def encrypt_message(self, message, key):
        """Шифрование сообщения с заданным ключом"""
        try:
            # Если ключ строка, конвертируем в bytes
            if isinstance(key, str):
                key = key.encode()
            
            # Создаем Fernet с ключом
            fernet = Fernet(key)
            
            # Шифруем сообщение
            encrypted_message = fernet.encrypt(message.encode())
            return encrypted_message.decode()  # Возвращаем как строку
        except Exception as e:
            raise ValueError(f"Ошибка шифрования: {e}")
    
    def decrypt_message(self, encrypted_message, key):
        """Расшифровка сообщения с заданным ключом"""
        try:
            # Если ключ строка, конвертируем в bytes
            if isinstance(key, str):
                key = key.encode()
            
            # Создаем Fernet с ключом
            fernet = Fernet(key)
            
            # Если сообщение строка, конвертируем в bytes
            if isinstance(encrypted_message, str):
                encrypted_message = encrypted_message.encode()
            
            # Расшифровываем сообщение
            decrypted_message = fernet.decrypt(encrypted_message)
            return decrypted_message.decode()
        except Exception as e:
            raise ValueError(f"Ошибка расшифровки: {e}")
            
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
