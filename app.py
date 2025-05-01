from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = []
user_roles = {}
online_users = {}

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    for msg in chat_history:
        emit('message', msg)
    emit('update_users', list(online_users.values()))

@socketio.on('register')
def handle_register(username):
    online_users[request.sid] = username
    emit('update_users', list(online_users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        del online_users[request.sid]
        emit('update_users', list(online_users.values()), broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = msg.get('username')
    text = msg.get('text')
    color = msg.get('color', '#000000')
    emoji = msg.get('emoji', '')
    
    # ✅ Tính giờ UTC+7
    now = datetime.utcnow() + timedelta(hours=7)
    time_str = now.strftime("%H:%M")

    role = user_roles.get(username, '')

    formatted_msg = {
        'time': time_str,
        'username': username,
        'text': text,
        'color': color,
        'emoji': emoji,
        'role': role
    }

    chat_history.append(formatted_msg)
    emit('message', formatted_msg, broadcast=True)

@socketio.on('clear')
def handle_clear():
    global chat_history
    chat_history = []
    emit('clear_chat', broadcast=True)

@socketio.on('set_role')
def handle_set_role(data):
    username = data.get('username')
    role_emoji = data.get('role')
    if username and role_emoji:
        user_roles[username] = role_emoji

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
