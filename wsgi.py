#!/usr/bin/python

import sqlite3
import requests
import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape
from flask import Flask, jsonify,render_template,current_app, request, Response
from apscheduler.scheduler import Scheduler
from flask_socketio import SocketIO, send, emit
from functools import wraps


application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!102ine10i2en19919199129'
socketio = SocketIO(application)

db_name = 'trackr.db'
timer = 15
conn = sqlite3.connect(db_name)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY AUTOINCREMENT,artist text, title text,checked boolean,CONSTRAINT track_unique UNIQUE (artist, title));")
conn.close()

def insert(artist,title):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('INSERT INTO tracks (artist,title,checked) VALUES (?,?,?)',(artist,title,False))
    conn.commit()
    conn.close()
    print "Added %s - %s" % (artist,title)

def mark_as_checked(idx):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('UPDATE tracks SET checked=? WHERE id=?',(True,idx))
    conn.commit()
    conn.close()

def all_tracks():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT * from tracks where checked = 0;')
    tracks = c.fetchall()
    conn.close()
    track_list = []
    for track in tracks:
        at = {'id': track[0] ,'artist': track[1], 'title': track[2], 'checked': track[3] }
        track_list.append(at)
    return track_list

def fetch_data():    
    html_escape_table = { "&": "&amp;",'"': "&quot;","'": "&apos;",">": "&gt;","<": "&lt;"}

    url = "http://www.defjay.com/onair/playlist/playlist.xml"
    data = requests.get(url)

    xml = ET.fromstring(data.content)
    artist = xml.find('./Current/Artist').text
    title = xml.find('./Current/Title').text
    a = unescape(artist, html_escape_table)
    t = unescape(title, html_escape_table)  
    insert(a,t)        

def background_thread():
    with application.app_context():
        while True:
            socketio.emit('tracks',all_tracks())
            socketio.sleep(45)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.environ['TRACKR_USER'] and password == os.environ['TRACKR_PASSWD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@application.before_first_request   
def initialize():
    apsched = Scheduler()
    apsched.start()
    apsched.add_interval_job(fetch_data, seconds=timer)

@application.route("/api/v1/tracks")
def apiAll():
    return jsonify(all_tracks())

@application.route("/")
@requires_auth
def index():
    return application.send_static_file('index.html')

@application.route("/tracks/<id>", methods=["POST"])
@requires_auth
def checked(id):
    mark_as_checked(id)
    socketio.emit('tracks',all_tracks())
    return jsonify({"status": 200})

@socketio.on('connect')
def connect():
    socketio.start_background_task(target=background_thread)

@socketio.on('tracks')
def update_tracks():
    emit('tracks',all_tracks())
    