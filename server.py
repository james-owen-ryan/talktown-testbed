import os, sys
import subprocess
import thread
import wx
import time
import re
import uuid
import platform
import inspect
import struct
import time
from game import Game
import startgame


# from flask import Flask, render_template
# noinspection PyUnresolvedReferences
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import thread
import eventlet
eventlet.monkey_patch()

# done = False

#app = Flask(__name__)

#app = Flask(__name__, static_folder='static')
app = Flask(__name__, static_folder='js')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/js/<path:path>')
def send_js(path):
    #return send_from_directory('js', path)
    return send_from_directory(app.static_folder)

@app.route('/')
def index():
    return render_template('myhtml.html')

# server handling info requests
@socketio.on('get info', namespace='/test')
def send_info(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('return info',
         {'data': str(startgame.random_p), 'count': session['receive_count']})
    print "PYTHON: random person %s" % startgame.random_p

@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})
    print "PYTHON: The user wants to post '%s'. I'm going to call a JS callback\n" % (message['data'])


@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.on('ready', namespace='/test')
def ready():
    emit('ready response',
         {'data': str(startgame.ready), 'count': 000})

thread.start_new_thread(startgame.game_start,())
socketio.run(app)