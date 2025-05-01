from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = []  # Lưu lịch sử chat
user_roles = {}    # Lưu role emoji của từng user
online_users = {}  # Lưu danh sách người dùng online, key: sid, value: username

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    for msg in chat_history:
        emit('message', msg)
    emit('update_users', list(online_users.values()))  # Gửi danh sách user online

@socketio.on('register')
def handle_register(username):
    online_users[request.sid] = username  # Lưu sid và username
    emit('update_users', list(online_users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # Khi user ngắt kết nối, xóa username khỏi online_users
    if request.sid in online_users:
        del online_users[request.sid]
        emit('update_users', list(online_users.values()), broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = msg.get('username')
    text = msg.get('text')
    color = msg.get('color', '#000000')
    emoji = msg.get('emoji', '')
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    role = user_roles.get(username, '')

    formatted_msg = {
        'time': now,
        'username': username,
        'text': text,
        'color': color,
        'emoji': emoji,
        'role': role
    }
    print(formatted_msg)

    chat_history.append(formatted_msg)
    emit('message', formatted_msg, broadcast=True)

@socketio.on('clear')
def handle_clear():
    global chat_history
    chat_history = []
    print("Chat history cleared.")
    emit('clear_chat', broadcast=True)

@socketio.on('set_role')
def handle_set_role(data):
    username = data.get('username')
    role_emoji = data.get('role')
    if username and role_emoji:
        user_roles[username] = role_emoji
        print(f"Set role for {username}: {role_emoji}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
