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
def home():
    return render_template('home.html')

@app.route('/create_room')
def create_room():
    return render_template('create_room.html')

@app.route("/room")
def room():
    room_key = session.get("room")
    user_name = session.get("name")

    if room_key is None or user_name is None or room_key not in room_keys:
        return redirect(url_for("home"))
    
    return render_template("room.html", room_key=room_key, messages=message_history[room_key])

@app.route('/process_create_room', methods=['POST'])
def process_create_room():
    user_name = request.form['name']
    room_key = generate_key() # automatically add the room key to list of keys

    session["name"] = user_name
    session["room"] = room_key

    # create a room key and store the members in the room
    room_users.setdefault(room_key, []).append(user_name)

    # create a message history 
    if room_key not in message_history:
        message_history[room_key] = []

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
    
    # add user to the room
    room_users[room_key].append(user_name)
    
    session["room"] = room_key
    session["name"] = user_name
    
    return redirect(url_for("room"))

@socketio.on('connect')
def connect(auth):
    user_name = session.get('name')
    room_key = session.get('room')

    # an error in the session information
    if not user_name or not room_key:
        return  

    # if room does no exist, error
    if room_key not in room_keys:
        leave_room(room_key)
        return 

    join_room(room=room_key)

    send({"name": user_name, "message": "has entered the room"}, to=room_key)

    print(f"{user_name} joined room {room_key}")

@socketio.on('disconnect')
def disconnect():
    user_name = session.get("name")
    room_key = session.get("room")
    leave_room(room_key)

    # Check if room_key exists in room_users dictionary
    if room_key and room_key in room_users:

        # Perform action with room_users[room_key]
        if user_name in room_users[room_key]:
            room_users[room_key].remove(user_name)

            # if there are no more users
            if not room_users[room_key]:
                del room_users[room_key]
                room_keys.remove(room_key)

        send({"name": user_name, "message": "has left the room"}, room=room_key)
        print(f"{user_name} left room {room_key}")
    else:
        print(f"Attempted to disconnect from an unknown room {room_key}")


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
    
    # append messages sent to history
    message_history[room_key].append(content)

    send(content, to=room_key)

    print(f"{user_name} said: {data['data']}")

if __name__ == "__main__":
    socketio.run(app, debug=True)