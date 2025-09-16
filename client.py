import sys
import socket
import threading
import json
import pyperclip
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QTextEdit, QLabel,
                            QMessageBox, QLineEdit, QStyle, QSplitter, QTabWidget,
                            QListWidget, QListWidgetItem, QDialog, QFormLayout,
                            QDialogButtonBox, QCheckBox, QFrame, QStackedWidget,
                            QScrollArea, QGridLayout, QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
from crypto_utils import CryptoManager

class NetworkThread(QThread):
    """Поток для сетевого взаимодействия"""
    message_received = pyqtSignal(str)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def run(self):
        """Запуск сетевого потока"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            self.connection_status.emit(True, "Подключено")
            
            # Получаем сообщения
            while self.running:
                try:
                    message = self.receive_message()
                    if message:
                        self.message_received.emit(message)
                    else:
                        break
                except Exception as e:
                    print(f"Ошибка получения сообщения: {e}")
                    break
                    
        except Exception as e:
            self.connection_status.emit(False, f"Ошибка подключения: {e}")
        finally:
            self.stop()
    
    def send_message(self, message):
        """Отправка сообщения"""
        try:
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes).to_bytes(4, 'big')
            self.socket.send(message_length + message_bytes)
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
    
    def receive_message(self):
        """Получение сообщения"""
        try:
            # Получаем длину сообщения
            length_data = self.socket.recv(4)
            if not length_data:
                return None
                
            message_length = int.from_bytes(length_data, 'big')
            
            # Получаем само сообщение
            message_data = b''
            while len(message_data) < message_length:
                chunk = self.socket.recv(min(message_length - len(message_data), 1024))
                if not chunk:
                    return None
                message_data += chunk
                
            return message_data.decode('utf-8')
            
        except Exception as e:
            print(f"Ошибка получения сообщения: {e}")
            return None
    
    def stop(self):
        """Остановка потока"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

class LoginDialog(QDialog):
    """Диалог входа в систему"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Вход в Secure Messenger")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Форма входа
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        form_layout.addRow("Логин:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        form_layout.addRow("Пароль:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.login_btn = QPushButton('Войти')
        self.forgot_password_btn = QPushButton('Забыл пароль')
        self.back_btn = QPushButton('Назад')
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.forgot_password_btn)
        buttons_layout.addWidget(self.back_btn)
        
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.login_btn.clicked.connect(self.accept)
        self.forgot_password_btn.clicked.connect(self.show_forgot_password)
        self.back_btn.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'username': self.username_input.text(),
            'password': self.password_input.text()
        }
    
    def show_forgot_password(self):
        """Показать диалог восстановления пароля"""
        secret_phrase, ok = QLineEdit.getText(self, 'Восстановление пароля', 
                                            'Введите секретную фразу:')
        if ok and secret_phrase:
            QMessageBox.information(self, 'Восстановление', 
                'Функция восстановления пароля будет добавлена в следующей версии.')
    
    def accept(self):
        """Проверка данных перед принятием"""
        if not self.username_input.text() or not self.password_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return
        super().accept()

class RegisterDialog(QDialog):
    """Диалог регистрации"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация")
        self.setModal(True)
        self.setFixedSize(450, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Регистрация в Secure Messenger")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Форма регистрации
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        form_layout.addRow("Логин:", self.username_input)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Введите имя аккаунта")
        form_layout.addRow("Имя аккаунта:", self.display_name_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        form_layout.addRow("Пароль:", self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Подтвердите пароль")
        form_layout.addRow("Подтвердите пароль:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.register_btn = QPushButton('Зарегистрироваться')
        self.back_btn = QPushButton('Назад')
        
        buttons_layout.addWidget(self.register_btn)
        buttons_layout.addWidget(self.back_btn)
        
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.register_btn.clicked.connect(self.accept)
        self.back_btn.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'username': self.username_input.text(),
            'display_name': self.display_name_input.text(),
            'password': self.password_input.text(),
            'confirm_password': self.confirm_password_input.text()
        }
    
    def accept(self):
        """Проверка данных перед принятием"""
        if not all([self.username_input.text(), self.display_name_input.text(), 
                   self.password_input.text(), self.confirm_password_input.text()]):
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return
        
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают!')
            return
        
        super().accept()

class SecureModeDialog(QDialog):
    """Диалог защищенного режима"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Защищенный режим")
        self.setModal(True)
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Защищенный режим")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Кнопки
        self.join_chat_btn = QPushButton('Подключиться к существующему диалогу')
        self.create_chat_btn = QPushButton('Создать новый диалог')
        self.back_btn = QPushButton('Назад')
        
        layout.addWidget(self.join_chat_btn)
        layout.addWidget(self.create_chat_btn)
        layout.addWidget(self.back_btn)
        
        # Подключаем события
        self.join_chat_btn.clicked.connect(self.join_existing_chat)
        self.create_chat_btn.clicked.connect(self.create_new_chat)
        self.back_btn.clicked.connect(self.reject)
    
    def join_existing_chat(self):
        """Подключиться к существующему диалогу"""
        dialog = JoinSecureChatDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.parent().handle_join_secure_chat(data)
            self.accept()
    
    def create_new_chat(self):
        """Создать новый диалог"""
        dialog = CreateSecureChatDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.parent().handle_create_secure_chat(data)
            self.accept()

class JoinSecureChatDialog(QDialog):
    """Диалог подключения к существующему защищенному чату"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подключение к диалогу")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Подключение к диалогу")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Поле для ключа
        layout.addWidget(QLabel("Ключ диалога:"))
        self.chat_key_input = QLineEdit()
        self.chat_key_input.setPlaceholderText("Введите ключ диалога")
        layout.addWidget(self.chat_key_input)
        
        # Поле для ключа шифрования
        layout.addWidget(QLabel("Ключ шифрования:"))
        self.encrypt_key_input = QLineEdit()
        self.encrypt_key_input.setPlaceholderText("Введите ключ шифрования")
        layout.addWidget(self.encrypt_key_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.connect_btn = QPushButton('Подключиться')
        self.cancel_btn = QPushButton('Отмена')
        
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.connect_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'chat_key': self.chat_key_input.text(),
            'encrypt_key': self.encrypt_key_input.text()
        }
    
    def accept(self):
        if not self.chat_key_input.text() or not self.encrypt_key_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return
        super().accept()

class CreateSecureChatDialog(QDialog):
    """Диалог создания нового защищенного чата"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание диалога")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Создание диалога")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Поле для ключа
        layout.addWidget(QLabel("Ключ диалога:"))
        self.chat_key_input = QLineEdit()
        self.chat_key_input.setPlaceholderText("Введите ключ диалога")
        layout.addWidget(self.chat_key_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.create_btn = QPushButton('Создать')
        self.cancel_btn = QPushButton('Отмена')
        
        buttons_layout.addWidget(self.create_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.create_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'chat_key': self.chat_key_input.text()
        }
    
    def accept(self):
        if not self.chat_key_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите ключ диалога!')
            return
        super().accept()

class SecureChatDialog(QDialog):
    """Диалог защищенного чата"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Защищенный чат")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Защищенный чат")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Поле для ключа чата
        layout.addWidget(QLabel("Ключ к чату:"))
        self.chat_key_input = QLineEdit()
        self.chat_key_input.setPlaceholderText("Введите ключ к чату")
        layout.addWidget(self.chat_key_input)
        
        # Кнопка подключения
        self.connect_btn = QPushButton('Подключиться')
        layout.addWidget(self.connect_btn)
        
        # Поле для ключа шифрования (изначально скрыто)
        self.encrypt_key_label = QLabel("Ключ шифрования:")
        self.encrypt_key_label.setVisible(False)
        layout.addWidget(self.encrypt_key_label)
        
        self.encrypt_key_input = QLineEdit()
        self.encrypt_key_input.setPlaceholderText("Введите ключ шифрования")
        self.encrypt_key_input.setVisible(False)
        layout.addWidget(self.encrypt_key_input)
        
        # Кнопка входа в чат (изначально скрыта)
        self.enter_chat_btn = QPushButton('Войти в чат')
        self.enter_chat_btn.setVisible(False)
        layout.addWidget(self.enter_chat_btn)
        
        # Кнопка назад
        self.back_btn = QPushButton('Назад')
        layout.addWidget(self.back_btn)
        
        # Подключаем события
        self.connect_btn.clicked.connect(self.connect_to_chat)
        self.enter_chat_btn.clicked.connect(self.accept)
        self.back_btn.clicked.connect(self.reject)
    
    def connect_to_chat(self):
        """Подключение к чату"""
        if not self.chat_key_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите ключ к чату!')
            return
        
        # Имитация проверки ключа
        if len(self.chat_key_input.text()) > 10:  # Простая проверка
            QMessageBox.information(self, 'Успех', 'Подключение выполнено!')
            self.chat_key_input.setEnabled(False)
            self.connect_btn.setEnabled(False)
            self.encrypt_key_label.setVisible(True)
            self.encrypt_key_input.setVisible(True)
            self.enter_chat_btn.setVisible(True)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Чат с таким ключом не найден!')
    
    def get_data(self):
        return {
            'chat_key': self.chat_key_input.text(),
            'encrypt_key': self.encrypt_key_input.text()
        }
    
    def accept(self):
        """Проверка данных перед принятием"""
        if not self.encrypt_key_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите ключ шифрования!')
            return
        super().accept()

class SettingsDialog(QDialog):
    """Диалог настроек"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Настройки")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Форма настроек
        form_layout = QFormLayout()
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Введите новое имя аккаунта")
        form_layout.addRow("Имя аккаунта:", self.display_name_input)
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password_input.setPlaceholderText("Введите текущий пароль")
        form_layout.addRow("Текущий пароль:", self.old_password_input)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Введите новый пароль")
        form_layout.addRow("Новый пароль:", self.new_password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Подтвердите новый пароль")
        form_layout.addRow("Подтвердите пароль:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton('Сохранить')
        self.cancel_btn = QPushButton('Отмена')
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'display_name': self.display_name_input.text(),
            'old_password': self.old_password_input.text(),
            'new_password': self.new_password_input.text(),
            'confirm_password': self.confirm_password_input.text()
        }

class WelcomeScreen(QWidget):
    """Экран приветствия с тремя кнопками"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Secure Messenger")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #0078d7; 
            margin: 40px 0;
        """)
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel("Защищенный мессенджер с end-to-end шифрованием")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px; 
            color: #888; 
            margin: 20px 0;
        """)
        layout.addWidget(subtitle_label)
        
        # Кнопки
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.login_btn = QPushButton('Войти')
        self.login_btn.setFixedSize(300, 50)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
        """)
        
        self.register_btn = QPushButton('Зарегистрироваться')
        self.register_btn.setFixedSize(300, 50)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        self.guest_btn = QPushButton('Продолжить без регистрации')
        self.guest_btn.setFixedSize(300, 50)
        self.guest_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.register_btn)
        buttons_layout.addWidget(self.guest_btn)
        
        layout.addLayout(buttons_layout)
        
        # Подключаем события
        self.login_btn.clicked.connect(self.show_login)
        self.register_btn.clicked.connect(self.show_register)
        self.guest_btn.clicked.connect(self.show_secure_chat)
    
    def show_login(self):
        """Показать диалог входа"""
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.parent.handle_login(data)
    
    def show_register(self):
        """Показать диалог регистрации"""
        dialog = RegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.parent.handle_register(data)
    
    def show_secure_chat(self):
        """Показать диалог защищенного чата"""
        dialog = SecureChatDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.parent.handle_secure_chat(data)

class MainMessengerWindow(QWidget):
    """Главное окно мессенджера"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user = None
        self.chats = []
        self.current_chat = None
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        
        # Левая панель - чаты
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Поиск пользователей
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск пользователей...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        self.settings_btn = QPushButton('⚙')
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: #ffffff;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.settings_btn.clicked.connect(self.show_settings)
        search_layout.addWidget(self.settings_btn)
        
        left_layout.addLayout(search_layout)
        
        # Кнопки управления чатами
        chats_buttons = QHBoxLayout()
        self.new_chat_btn = QPushButton('Новый чат')
        self.secure_chat_btn = QPushButton('Защищенный режим')
        
        self.new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        self.secure_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        chats_buttons.addWidget(self.new_chat_btn)
        chats_buttons.addWidget(self.secure_chat_btn)
        left_layout.addLayout(chats_buttons)
        
        # Список чатов
        self.chats_list = QListWidget()
        self.chats_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        left_layout.addWidget(self.chats_list)
        
        # Правая панель - сообщения
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Заголовок чата
        self.chat_title = QLabel("Выберите чат")
        self.chat_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        right_layout.addWidget(self.chat_title)
        
        # Область сообщений
        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        self.messages_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.messages_display)
        
        # Поле ввода сообщения
        message_input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        message_input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton('Отправить')
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        message_input_layout.addWidget(self.send_btn)
        
        right_layout.addLayout(message_input_layout)
        
        # Добавляем панели в основной layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        # Подключаем обработчики событий
        self.new_chat_btn.clicked.connect(self.show_new_chat_dialog)
        self.secure_chat_btn.clicked.connect(self.show_secure_mode)
    
    def show_settings(self):
        """Показать диалог настроек"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            # Здесь будет обработка изменения настроек
            QMessageBox.information(self, 'Успех', 'Настройки сохранены!')
    
    def show_new_chat_dialog(self):
        """Показать диалог нового чата"""
        display_name, ok = QLineEdit.getText(self, 'Новый чат', 'Введите имя пользователя:')
        if ok and display_name:
            QMessageBox.information(self, 'Информация', f'Поиск пользователя: {display_name}')
            # Здесь будет логика создания чата
    
    def show_secure_mode(self):
        """Показать защищенный режим"""
        self.parent.show_secure_mode()
    
    def send_message(self):
        """Отправка сообщения"""
        if not self.message_input.text():
            return
        
        message = self.message_input.text()
        self.messages_display.append(f"Вы: {message}")
        self.message_input.clear()

class SecureChatWindow(QWidget):
    """Окно защищенного чата"""
    def __init__(self, chat_key, encrypt_key=None, is_creator=False, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.chat_key = chat_key
        self.encrypt_key = encrypt_key
        self.is_creator = is_creator
        self.crypto_manager = CryptoManager()
        self.participant_connected = False
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Защищенный чат")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(title_label)
        
        # Информация о чате
        info_label = QLabel(f"Ключ чата: {self.chat_key[:10]}...")
        info_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(info_label)
        
        # Статус диалога
        self.status_label = QLabel("Ожидание собеседника" if self.is_creator else "Подключение...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #ffa500; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Поле для ключа шифрования (только для создателя)
        if self.is_creator:
            self.encrypt_key_label = QLabel("Ключ шифрования:")
            self.encrypt_key_label.setStyleSheet("color: #e0e0e0; font-size: 12px;")
            layout.addWidget(self.encrypt_key_label)
            
            self.encrypt_key_input = QLineEdit()
            self.encrypt_key_input.setPlaceholderText("Введите ключ шифрования")
            self.encrypt_key_input.setStyleSheet("""
                QLineEdit {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: #f0f0f0;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #0078d7;
                }
            """)
            layout.addWidget(self.encrypt_key_input)
            
            self.set_encrypt_key_btn = QPushButton('Установить ключ')
            self.set_encrypt_key_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.set_encrypt_key_btn.clicked.connect(self.set_encryption_key)
            layout.addWidget(self.set_encrypt_key_btn)
        
        # Область сообщений
        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        self.messages_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                color: #e0e0e0;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.messages_display)
        
        # Поле ввода сообщения
        message_input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        message_input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton('Отправить')
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003e6b;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        message_input_layout.addWidget(self.send_btn)
        
        layout.addLayout(message_input_layout)
        
        # Кнопка выхода
        self.exit_btn = QPushButton('Выйти из чата')
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.exit_btn.clicked.connect(self.exit_chat)
        layout.addWidget(self.exit_btn)
    
    def send_message(self):
        """Отправка зашифрованного сообщения"""
        if not self.message_input.text():
            return
        
        try:
            message = self.message_input.text()
            # Здесь будет шифрование сообщения
            encrypted_message = f"[ЗАШИФРОВАНО] {message}"
            self.messages_display.append(f"Вы: {encrypted_message}")
            self.message_input.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка шифрования: {e}')
    
    def set_encryption_key(self):
        """Установка ключа шифрования"""
        if not self.encrypt_key_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите ключ шифрования!')
            return
        
        self.encrypt_key = self.encrypt_key_input.text()
        self.encrypt_key_input.setEnabled(False)
        self.set_encrypt_key_btn.setEnabled(False)
        QMessageBox.information(self, 'Успех', 'Ключ шифрования установлен!')
    
    def update_status(self, status, color="#ffa500"):
        """Обновление статуса диалога"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
    
    def participant_joined(self):
        """Собеседник присоединился"""
        self.participant_connected = True
        self.update_status("Собеседник подключен", "#28a745")
    
    def exit_chat(self):
        """Выход из защищенного чата"""
        reply = QMessageBox.question(self, 'Выход', 
                                   'Вы уверены, что хотите выйти? Все данные будут удалены.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.show_welcome_screen()

class SecureMessengerClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.crypto_manager = CryptoManager()
        self.network_thread = None
        self.connected = False
        self.current_user = None
        self.initUI()
        
    def initUI(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('Secure Messenger')
        self.setGeometry(200, 200, 1000, 700)
        
        # Устанавливаем иконку
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.setWindowIcon(icon)
        
        # Создаем стек виджетов для переключения между экранами
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Создаем экраны
        self.welcome_screen = WelcomeScreen(self)
        self.main_messenger = MainMessengerWindow(self)
        
        # Добавляем экраны в стек
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.main_messenger)
        
        # Показываем экран приветствия
        self.show_welcome_screen()
        
        # Подключаемся к серверу
        self.connect_to_server()
    
    def connect_to_server(self):
        """Подключение к серверу"""
        try:
            self.network_thread = NetworkThread('localhost', 5000)
            self.network_thread.message_received.connect(self.handle_received_message)
            self.network_thread.connection_status.connect(self.handle_connection_status)
            self.network_thread.start()
        except Exception as e:
            print(f"Ошибка подключения: {e}")
    
    def handle_connection_status(self, connected, message):
        """Обработка статуса подключения"""
        self.connected = connected
        print(f"Статус подключения: {message}")
    
    def handle_received_message(self, message):
        """Обработка полученного сообщения"""
        try:
            message_data = json.loads(message)
            print(f"Получено сообщение: {message_data}")
        except json.JSONDecodeError:
            print(f"Ошибка декодирования JSON: {message}")
    
    def show_welcome_screen(self):
        """Показать экран приветствия"""
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def show_main_messenger(self):
        """Показать главное окно мессенджера"""
        self.stacked_widget.setCurrentWidget(self.main_messenger)
    
    def handle_login(self, data):
        """Обработка входа в систему"""
        if not self.connected:
            QMessageBox.warning(self, 'Ошибка', 'Нет подключения к серверу!')
            return
        
        # Отправляем запрос на сервер
        message = {
            'type': 'auth',
            'username': data['username'],
            'password': data['password']
        }
        
        if self.network_thread:
            self.network_thread.send_message(json.dumps(message))
        
        # Показываем главное окно мессенджера
        self.show_main_messenger()
    
    def handle_register(self, data):
        """Обработка регистрации"""
        if not self.connected:
            QMessageBox.warning(self, 'Ошибка', 'Нет подключения к серверу!')
            return
        
        # Отправляем запрос на сервер
        message = {
            'type': 'register',
            'username': data['username'],
            'display_name': data['display_name'],
            'password': data['password']
        }
        
        if self.network_thread:
            self.network_thread.send_message(json.dumps(message))
        
        QMessageBox.information(self, 'Успех', 'Регистрация выполнена! Теперь войдите в систему.')
    
    def show_secure_mode(self):
        """Показать диалог защищенного режима"""
        dialog = SecureModeDialog(self)
        dialog.exec()
    
    def handle_join_secure_chat(self, data):
        """Обработка подключения к существующему защищенному чату"""
        # Создаем окно защищенного чата (не создатель)
        secure_chat_window = SecureChatWindow(data['chat_key'], data['encrypt_key'], False, self)
        self.stacked_widget.addWidget(secure_chat_window)
        self.stacked_widget.setCurrentWidget(secure_chat_window)
        
        # Имитация успешного подключения
        QTimer.singleShot(2000, secure_chat_window.participant_joined)
    
    def handle_create_secure_chat(self, data):
        """Обработка создания нового защищенного чата"""
        # Создаем окно защищенного чата (создатель)
        secure_chat_window = SecureChatWindow(data['chat_key'], None, True, self)
        self.stacked_widget.addWidget(secure_chat_window)
        self.stacked_widget.setCurrentWidget(secure_chat_window)
        
        # Показываем информацию о созданном чате
        QMessageBox.information(self, 'Успех', 
            f'Диалог создан!\nКлюч диалога: {data["chat_key"]}\nПередайте этот ключ собеседнику.')
    
    def handle_secure_chat(self, data):
        """Обработка защищенного чата"""
        # Создаем окно защищенного чата
        secure_chat_window = SecureChatWindow(data['chat_key'], data['encrypt_key'], self)
        self.stacked_widget.addWidget(secure_chat_window)
        self.stacked_widget.setCurrentWidget(secure_chat_window)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.network_thread:
            self.network_thread.stop()
            self.network_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Современный темный стиль
    modern_stylesheet = """
        QWidget {
            font-family: 'Segoe UI', 'Cantarell', 'Helvetica Neue', sans-serif;
            font-size: 10pt;
            color: #e0e0e0;
            background-color: #1e1e1e;
        }
        QMainWindow {
            background-color: #1e1e1e;
        }
        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 5px;
            color: #f0f0f0;
        }
        QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
            border: 1px solid #0078d7;
        }
        QPushButton {
            background-color: #0078d7;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #003e6b;
        }
        QPushButton:disabled {
            background-color: #555;
            color: #888;
        }
        QMessageBox {
            background-color: #2b2b2b;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
        QFrame {
            border: 1px solid #555;
            border-radius: 5px;
            padding: 10px;
        }
        QDialog {
            background-color: #1e1e1e;
        }
    """
    app.setStyleSheet(modern_stylesheet)
    
    ex = SecureMessengerClient()
    ex.show()
    sys.exit(app.exec())
