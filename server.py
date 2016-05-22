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
from flask import Flask, render_template, session, request, send_from_directory, abort, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import thread
from threading import Thread
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Serve up JS + sprites
@app.route('/<path:path>')
def send_js(path):
    return send_from_directory(app.static_folder, path)

@app.route('/')
def index():
    #return render_template('game.html')
    # V uncomment if redirecting V
    return render_template('loading.html')

@app.route('/game')
def game():
    return render_template('game.html')

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

@socketio.on('get_lot_json', namespace='/gameplay')
def send_lot_json(message):
    emit('return lots',
         {'data': startgame.json_lot_type_dict, 'count': session['receive_count']})

@socketio.on('get_block_json', namespace='/gameplay')
def send_block_json(message):
    emit('return blocks',
         {'data': startgame.json_block_coordinates_list, 'count': session['receive_count']})


@socketio.on('ready', namespace='/gameplay')
def ready():
    emit('ready response',
         {'data': str(startgame.ready), 'count': 000})

@socketio.on('change view', namespace='/gameplay')
def change_view():
    emit('redirect', {'url': url_for('game')})




thread.start_new_thread(startgame.game_start,())
socketio.run(app)