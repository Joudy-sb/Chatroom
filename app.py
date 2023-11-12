from flask import Flask, redirect, render_template, request, session, url_for
import random
from string import ascii_uppercase

app = Flask(__name__)

room_user = list()
room_keys = list()

def generate_key():
    while True:
        key = ""
        for i in range(0,4):
            key += random.choice(ascii_uppercase)
        if key not in room_keys:
            break
    return key

# Route handler for the "/room" URL
@app.route("/room")
def room():
    room_key = session.get("room")
    return render_template("room.html", room_key = room_key)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/create_room')
def create_room():
    return render_template('create_room.html')

@app.route('/process_create_room', methods=['POST'])
def process_create_room():
    user_name = request.form['name']
    room_user.append(user_name)
    room_key = generate_key()

    #session["name"] = user_name

    return redirect(url_for("room"))

@app.route('/join_room')
def join_room():
    return render_template('join_room.html')

@app.route('/process_join_room', methods=['POST'])
def process_join_room():
    user_name = request.form['name']
    room_key = request.form['key']

    if room_key not in room_keys:
        return render_template('join_room.html')
    
    session["room"] = room_key
    session["name"] = user_name
    
    return redirect(url_for("room"))
    
if __name__ == '__main__':
    app.run()
