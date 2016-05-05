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
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import thread
import eventlet
eventlet.monkey_patch()

if hasattr(sys, "frozen"):
  serverProc = subprocess.Popen(["server.exe"],stderr=subprocess.STDOUT)
  time.sleep(1)
  browserProc = subprocess.Popen(["browser.exe"])
  browserProc.wait()
  serverProc.terminate()
else:
  serverProc = subprocess.Popen([sys.executable, "server.py"],stderr=subprocess.STDOUT)
  time.sleep(1)
  browserProc = subprocess.Popen([sys.executable, "browser.py"])
  browserProc.wait()
  serverProc.terminate()