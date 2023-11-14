from flask import Flask, redirect, render_template, request, session, url_for
import random
from string import ascii_uppercase
from flask_socketio import SocketIO, emit, leave_room, send, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "line&joods"
socketio = SocketIO(app)

room_users = {}
room_keys = set()
message_history = {}


def generate_key():
    while True: 
        key = ""
        for i in range(0,4):
            key += random.choice(ascii_uppercase)
        if key not in room_keys:
            room_keys.add(key)
            break
    return key

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/create_room')
def create_room():
    return render_template('create_room.html')

@app.route("/room")
def room():
    room_key = session.get("room")
    return render_template("room.html", room_key=room_key)

@app.route('/process_create_room', methods=['POST'])
def process_create_room():
    user_name = request.form['name']
    room_key = generate_key()

    room_users[room_key] = [user_name]

    session["name"] = user_name
    session["room"] = room_key

    room_users.setdefault(room_key, []).append(user_name)

    return redirect(url_for("room"))

@app.route('/join_room')
def join_room_view():
    return render_template('join_room.html')

@app.route('/process_join_room', methods=['POST'])
def process_join_room():
    user_name = request.form['name']
    room_key = request.form['key']

    if room_key not in room_keys:
        return render_template('join_room.html', error='Room does not exist.')
    
    room_users.setdefault(room_key, []).append(user_name)
    
    session["room"] = room_key
    session["name"] = user_name
    
    return redirect(url_for("room"))

@socketio.on('connect')
def connect():
    user_name = session.get('name')
    room_key = session.get('room')

    if not user_name or not room_key:
        return False 

    if room_key not in room_keys:
        send({"name": user_name, "message": "Room does not exist."}, room=room_key)
        return False 

    join_room(room=room_key)
    send({"name": user_name, "message": "has entered the room"}, room=room_key)

    print(f"{user_name} joined room {room_key}")

@socketio.on('disconnect')
def disconnect():
    user_name = session.get("name")
    room_key = session.get("room")
    leave_room(room_key)
    
    if not room_key:
        print(f"{user_name} has disconnected and was not in any room.")
        return False

    if room_key in room_keys:
        room_users[room_key].remove(user_name)

        if not room_users[room_key]:
            del room_users[room_key]
            room_keys.remove(room_key)

        send({"name": user_name, "message": "has left the room"}, room=room_key)

    print(f"{user_name} left room {room_key}")

@socketio.on('message')
def message(data):
    user_name = session.get("name")
    room_key = session.get("room")

    if room_key not in room_keys:
        return False
    
    content = {
        "name": user_name,
        "message": data['data']
    }

    if room_key not in message_history:
        message_history[room_key] = []
    
    message_history[room_key].append(content)

    send(content, to=room_key)
    print(f"{user_name} said: {data['data']}")

@socketio.on('request_history')
def handle_request_history():
    room_key = session.get('room')
    if room_key in message_history:
        for msg in message_history[room_key]:
            emit('message', msg, room=request.sid)


if __name__ == "__main__":
    socketio.run(app, debug=True)