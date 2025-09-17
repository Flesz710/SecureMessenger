from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import uuid
from datetime import datetime
from database import DatabaseManager
from crypto_utils import CryptoManager
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secure_messenger_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Инициализация компонентов
db = DatabaseManager()
active_users = {}  # {session_id: {'user_id': int, 'username': str, 'display_name': str}}
active_secure_chats = {}  # {chat_key: {'participants': [], 'encryption_key': str}}

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """API регистрации"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        display_name = data.get('display_name', '').strip()
        password = data.get('password', '').strip()
        
        if not all([username, display_name, password]):
            return jsonify({'success': False, 'error': 'Заполните все поля'})
        
        success, result = db.register_user(username, display_name, password)
        
        if success:
            return jsonify({'success': True, 'secret_phrase': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/api/login', methods=['POST'])
def api_login():
    """API входа"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not all([username, password]):
            return jsonify({'success': False, 'error': 'Заполните все поля'})
        
        success, result = db.authenticate_user(username, password)
        
        if success:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            session['user_data'] = result
            active_users[session_id] = result
            
            return jsonify({'success': True, 'user_data': result, 'session_id': session_id})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/api/find_user', methods=['POST'])
def api_find_user():
    """API поиска пользователя"""
    try:
        data = request.get_json()
        display_name = data.get('display_name', '').strip()
        
        if not display_name:
            return jsonify({'success': False, 'error': 'Введите имя пользователя'})
        
        user_data = db.find_user_by_display_name(display_name)
        
        if user_data:
            return jsonify({'success': True, 'user_data': user_data})
        else:
            return jsonify({'success': False, 'error': 'Пользователь не найден'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/api/get_chats', methods=['GET'])
def api_get_chats():
    """API получения чатов"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            return jsonify({'success': False, 'error': 'Не авторизован'})
        
        user_id = active_users[session_id]['user_id']
        chats = db.get_user_chats(user_id)
        
        return jsonify({'success': True, 'chats': chats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/api/get_messages', methods=['POST'])
def api_get_messages():
    """API получения сообщений"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            return jsonify({'success': False, 'error': 'Не авторизован'})
        
        data = request.get_json()
        chat_id = data.get('chat_id')
        limit = data.get('limit', 50)
        
        messages = db.get_chat_messages(chat_id, limit)
        
        return jsonify({'success': True, 'messages': messages})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/api/create_chat', methods=['POST'])
def api_create_chat():
    """API создания чата"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            return jsonify({'success': False, 'error': 'Не авторизован'})
        
        data = request.get_json()
        user2_id = data.get('user_id')
        
        user1_id = active_users[session_id]['user_id']
        chat_id = db.get_or_create_private_chat(user1_id, user2_id)
        
        if chat_id:
            return jsonify({'success': True, 'chat_id': chat_id})
        else:
            return jsonify({'success': False, 'error': 'Не удалось создать чат'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

# WebSocket события
@socketio.on('connect')
def handle_connect():
    """Подключение клиента"""
    print(f'Клиент подключился: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Отключение клиента"""
    print(f'Клиент отключился: {request.sid}')
    
    # Удаляем из активных пользователей
    session_id = session.get('session_id')
    if session_id and session_id in active_users:
        del active_users[session_id]

@socketio.on('join_chat')
def handle_join_chat(data):
    """Присоединение к чату"""
    try:
        chat_id = data.get('chat_id')
        session_id = session.get('session_id')
        
        if session_id and session_id in active_users:
            join_room(f'chat_{chat_id}')
            emit('joined_chat', {'chat_id': chat_id})
            print(f'Пользователь {active_users[session_id]["display_name"]} присоединился к чату {chat_id}')
    except Exception as e:
        emit('error', {'message': f'Ошибка присоединения к чату: {str(e)}'})

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Покидание чата"""
    try:
        chat_id = data.get('chat_id')
        leave_room(f'chat_{chat_id}')
        emit('left_chat', {'chat_id': chat_id})
    except Exception as e:
        emit('error', {'message': f'Ошибка покидания чата: {str(e)}'})

@socketio.on('send_message')
def handle_send_message(data):
    """Отправка сообщения"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            emit('error', {'message': 'Не авторизован'})
            return
        
        chat_id = data.get('chat_id')
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'normal')
        
        if not content:
            emit('error', {'message': 'Сообщение не может быть пустым'})
            return
        
        sender_id = active_users[session_id]['user_id']
        sender_name = active_users[session_id]['display_name']
        
        # Сохраняем сообщение в базу данных
        success = db.save_message(chat_id, sender_id, content, None, message_type)
        
        if success:
            # Отправляем сообщение всем участникам чата
            message_data = {
                'chat_id': chat_id,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'content': content,
                'message_type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            
            emit('new_message', message_data, room=f'chat_{chat_id}')
            print(f'Сообщение отправлено в чат {chat_id}: {content[:50]}...')
        else:
            emit('error', {'message': 'Ошибка сохранения сообщения'})
            
    except Exception as e:
        emit('error', {'message': f'Ошибка отправки сообщения: {str(e)}'})

@socketio.on('create_secure_chat')
def handle_create_secure_chat(data):
    """Создание защищенного чата"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            emit('error', {'message': 'Не авторизован'})
            return
        
        chat_key = data.get('chat_key', '').strip()
        encryption_key = data.get('encryption_key', '').strip()
        
        if not chat_key:
            emit('error', {'message': 'Введите ключ чата'})
            return
        
        if chat_key in active_secure_chats:
            emit('error', {'message': 'Чат с таким ключом уже существует'})
            return
        
        # Создаем защищенный чат
        active_secure_chats[chat_key] = {
            'participants': [session_id],
            'encryption_key': encryption_key,
            'created_at': datetime.now().isoformat()
        }
        
        join_room(f'secure_chat_{chat_key}')
        
        emit('secure_chat_created', {
            'chat_key': chat_key,
            'is_creator': True
        })
        
        print(f'Создан защищенный чат: {chat_key}')
        
    except Exception as e:
        emit('error', {'message': f'Ошибка создания защищенного чата: {str(e)}'})

@socketio.on('join_secure_chat')
def handle_join_secure_chat(data):
    """Присоединение к защищенному чату"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            emit('error', {'message': 'Не авторизован'})
            return
        
        chat_key = data.get('chat_key', '').strip()
        encryption_key = data.get('encryption_key', '').strip()
        
        if not chat_key:
            emit('error', {'message': 'Введите ключ чата'})
            return
        
        if chat_key not in active_secure_chats:
            emit('error', {'message': 'Чат с таким ключом не найден'})
            return
        
        # Проверяем ключ шифрования
        stored_key = active_secure_chats[chat_key]['encryption_key']
        if stored_key and stored_key != encryption_key:
            emit('error', {'message': 'Неверный ключ шифрования'})
            return
        
        # Добавляем участника
        if session_id not in active_secure_chats[chat_key]['participants']:
            active_secure_chats[chat_key]['participants'].append(session_id)
        
        join_room(f'secure_chat_{chat_key}')
        
        emit('joined_secure_chat', {
            'chat_key': chat_key,
            'is_creator': False,
            'participants_count': len(active_secure_chats[chat_key]['participants'])
        })
        
        # Уведомляем создателя о новом участнике
        emit('participant_joined', {
            'chat_key': chat_key,
            'participant_name': active_users[session_id]['display_name']
        }, room=f'secure_chat_{chat_key}')
        
        print(f'Пользователь {active_users[session_id]["display_name"]} присоединился к защищенному чату {chat_key}')
        
    except Exception as e:
        emit('error', {'message': f'Ошибка присоединения к защищенному чату: {str(e)}'})

@socketio.on('send_secure_message')
def handle_send_secure_message(data):
    """Отправка зашифрованного сообщения"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in active_users:
            emit('error', {'message': 'Не авторизован'})
            return
        
        chat_key = data.get('chat_key', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            emit('error', {'message': 'Сообщение не может быть пустым'})
            return
        
        if chat_key not in active_secure_chats:
            emit('error', {'message': 'Чат не найден'})
            return
        
        if session_id not in active_secure_chats[chat_key]['participants']:
            emit('error', {'message': 'Вы не участник этого чата'})
            return
        
        sender_name = active_users[session_id]['display_name']
        
        # Шифруем сообщение
        crypto_manager = CryptoManager()
        encryption_key = active_secure_chats[chat_key]['encryption_key']
        
        if encryption_key:
            try:
                crypto_manager.set_key(encryption_key.encode())
                encrypted_content = crypto_manager.encrypt_message(content)
            except Exception as e:
                emit('error', {'message': f'Ошибка шифрования: {str(e)}'})
                return
        else:
            encrypted_content = content  # Без шифрования
        
        # Отправляем зашифрованное сообщение
        message_data = {
            'chat_key': chat_key,
            'sender_name': sender_name,
            'content': content,
            'encrypted_content': encrypted_content,
            'timestamp': datetime.now().isoformat()
        }
        
        emit('secure_message', message_data, room=f'secure_chat_{chat_key}')
        print(f'Зашифрованное сообщение отправлено в чат {chat_key}')
        
    except Exception as e:
        emit('error', {'message': f'Ошибка отправки зашифрованного сообщения: {str(e)}'})

@socketio.on('leave_secure_chat')
def handle_leave_secure_chat(data):
    """Покидание защищенного чата"""
    try:
        chat_key = data.get('chat_key', '').strip()
        
        if chat_key in active_secure_chats:
            session_id = session.get('session_id')
            if session_id in active_secure_chats[chat_key]['participants']:
                active_secure_chats[chat_key]['participants'].remove(session_id)
                
                # Если участников не осталось, удаляем чат
                if not active_secure_chats[chat_key]['participants']:
                    del active_secure_chats[chat_key]
                    print(f'Защищенный чат {chat_key} удален (нет участников)')
        
        leave_room(f'secure_chat_{chat_key}')
        emit('left_secure_chat', {'chat_key': chat_key})
        
    except Exception as e:
        emit('error', {'message': f'Ошибка покидания защищенного чата: {str(e)}'})

if __name__ == '__main__':
    print("🌐 Запуск веб-версии Secure Messenger...")
    print("📱 Откройте браузер и перейдите по адресу: http://localhost:5000")
    print("🔐 Для тестирования с друзьями используйте ваш IP адрес")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

