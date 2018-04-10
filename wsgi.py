#!/usr/bin/python

import sqlite3
import requests
import os
import xml.etree.ElementTree as ET
from flask import Flask, jsonify,render_template,current_app, request, Response
from apscheduler.scheduler import Scheduler
from functools import wraps
import HTMLParser
import urllib2
import sys

application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!102ine10i2en19919199129'

db_name = os.environ['TRACKR_DATA']+'/trackr.db'
timer = 120
conn = sqlite3.connect(db_name,timeout=10)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY AUTOINCREMENT,artist text, title text,checked boolean,CONSTRAINT track_unique UNIQUE (artist, title));")
conn.close()

def insert(artist,title):
    current_tracks = all_tracks()
    conn = sqlite3.connect(db_name,timeout=10)
    c = conn.cursor()
    c.execute('INSERT INTO tracks (artist,title,checked) VALUES (?,?,?)',(artist,title,False))
    conn.commit()
    conn.close()
    actual_tracks = all_tracks()
    if len(current_tracks) != len(actual_tracks):
        print "Added %s - %s" % (artist,title)
        
def mark_as_checked(idx):
    conn = sqlite3.connect(db_name,timeout=10)
    c = conn.cursor()
    c.execute('UPDATE tracks SET checked=? WHERE id=?',(1,idx))
    conn.commit()
    conn.close()

def all_tracks():
    conn = sqlite3.connect(db_name,timeout=10)
    c = conn.cursor()
    c.execute('SELECT * from tracks where checked = 0;')
    tracks = c.fetchall()
    conn.close()
    track_list = []
    for track in tracks:
        at = {'id': track[0] ,'artist': track[1], 'title': track[2], 'checked': track[3] }
        track_list.append(at)
    return track_list

def unescape(string):
    string = urllib2.unquote(string).decode('utf8')
    return HTMLParser.HTMLParser().unescape(string).encode(sys.getfilesystemencoding())

def fetch_data():    
    url = "http://www.defjay.com/onair/playlist/playlist.xml"
    data = requests.get(url)

    xml = ET.fromstring(data.content)
    artist = xml.find('./Current/Artist').text
    title = xml.find('./Current/Title').text
    a = unescape(artist)
    t = unescape(title)
    insert(a,t)        

@application.before_first_request   
def initialize():
    apsched = Scheduler()
    apsched.start()
    apsched.add_interval_job(fetch_data, seconds=timer)

@application.route("/api/v1/tracks")
def apiAll():
    return jsonify(all_tracks())

@application.route("/")
def index():
    return application.send_static_file('index.html')

@application.route("/api/v1/tracks/<id>/checked", methods=["POST"])
def checked(id):
    mark_as_checked(id)
    return jsonify({"status": 200})
