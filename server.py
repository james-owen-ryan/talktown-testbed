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
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import thread
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_folder='js')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Serve up JS files
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(app.static_folder)

@app.route('/')
def index():
    return render_template('myhtml.html')

# -------------------------------- #
#  query handlers                  #
# -------------------------------- #

#TODO: return name of city OR person
@socketio.on('get_random_person', namespace='/gameplay')
def send_random_person(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('return info',
        {'data': str(startgame.random_p), 'count': session['receive_count']})

@socketio.on('get_city_name', namespace='/gameplay')
def send_city_name(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('return info',
        {'data': str(startgame.city_name), 'count': session['receive_count']})

#todo: Pass json of lots, rename things for clarity
@socketio.on('get_city', namespace='/gameplay')
def send_city(message):
    print "sending back city"
    emit('return city',
         {'data': str(startgame.lot), 'count': session['receive_count']})

@socketio.on('my event', namespace='/gameplay')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})
    print "PYTHON: The user wants to post '%s'. I'm going to call a JS callback\n" % (message['data'])


@socketio.on('disconnect request', namespace='/gameplay')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/gameplay')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/gameplay')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.on('ready', namespace='/gameplay')
def ready():
    emit('ready response',
         {'data': str(startgame.ready), 'count': 000})

thread.start_new_thread(startgame.game_start,())
socketio.run(app)