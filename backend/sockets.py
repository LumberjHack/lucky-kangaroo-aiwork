from flask import request
from extensions import socketio

@socketio.on('connect')
def on_connect():
    return True

@socketio.on('join')
def on_join(data):
    room = data.get('room')
    if room:
        from flask_socketio import join_room
        join_room(room)
        socketio.emit('system', {"message": f"joined {room}"}, to=room)

@socketio.on('message')
def on_message(data):
    room = data.get('room')
    msg = data.get('message')
    if room and msg:
        socketio.emit('message', {"from": request.sid, "message": msg}, to=room)

