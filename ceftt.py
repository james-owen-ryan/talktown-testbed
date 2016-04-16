# An example of embedding CEF browser in wxPython on Windows.
# Tested with wxPython 2.8.12.1 and 3.0.2.0.

# TODO: function that sets up server prior to running the page

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


from flask import Flask, render_template
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
"""
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
         {'data': str(random_p), 'count': session['receive_count']})
    print "PYTHON: random person %s" % random_p

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


def game_start():
    global done
    done = False
    global game
    game = Game()  # Objects of the class Game are Talk of the Town simulations
    # send a message to be displayed on the page
    print "Simulating a town's history..."
    # Simulate until the summer of 1979, when gameplay takes place
    try:
        game.establish_setting()  # This is the worldgen procedure
    except KeyboardInterrupt:  # Enter "ctrl+C" (a keyboard interrupt) to end worldgen early
        pass
    print "\nPreparing for gameplay..."
    game.enact_no_fi_simulation()  # This will tie up a few loose ends in the case of worldgen being terminated early
    print '\nIt is now the {date}, in the town of {city}, pop. {population}.\n'.format(
        date=game.date[0].lower() + game.date[1:],
        city=game.city.name,
        population=game.city.population
    )
    # Print out businesses in town
    print '\nThe following companies currently operate in {city}:\n'.format(
        city=game.city.name
    )
    for c in game.city.companies:
        print c
    # Print out former businesses in town to briefly explore its history
    for c in game.city.former_companies:
        print c
    # Procure and print out a random character in the town
    global p
    p = game.random_person
    print '\nRandom character: {random_character}\n'.format(
        random_character=p
    )
    # Print out this character's relationships with every other resident in town
    for r in game.city.residents:
        print p.relation_to_me(r)
    # Explore this person's mental models
    print "\n{random_character}'s mental models:\n".format(
        random_character=p.name
    )
    for person_home_or_business in p.mind.mental_models:
        print p.mind.mental_models[person_home_or_business]

    done == True
    global random_p
    random_p = p
    print "within game gen random p is %s" % random_p
"""
serverProc = subprocess.Popen([sys.executable, "server.py"],stderr=subprocess.STDOUT)
#thread.start_new_thread(game_start,())
time.sleep(5)
browserProc = subprocess.Popen([sys.executable, "browser.py"])
browserProc.wait()
serverProc.terminate()