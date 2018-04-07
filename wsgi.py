#!/usr/bin/python

import sqlite3
import requests
import xml.etree.ElementTree as ET
import time
from xml.sax.saxutils import escape, unescape
from flask import Flask, jsonify,render_template
import threading
from apscheduler.scheduler import Scheduler


conn = sqlite3.connect('trackr.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tracks(artist text, title text)''')
conn.close()

application = Flask(__name__)
   

def insert(artist,title):
    conn = sqlite3.connect('trackr.db')
    c = conn.cursor()
    c.execute('INSERT INTO tracks (artist,title) VALUES (?,?)',(artist,title))
    conn.commit()
    conn.close()

def all_tracks():
    conn = sqlite3.connect('trackr.db')
    c = conn.cursor()
    c.execute('SELECT * from tracks')
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_data():    
    html_escape_table = { "&": "&amp;",'"': "&quot;","'": "&apos;",">": "&gt;","<": "&lt;"}

    url = "http://www.defjay.com/onair/playlist/playlist.xml"
    data = requests.get(url)

    xml = ET.fromstring(data.content)
    artist = xml.find('./Current/Artist').text
    title = xml.find('./Current/Title').text
    a = unescape(artist, html_escape_table)
    t = unescape(title, html_escape_table)  
    print "Found %s - %s" % (a,t)
    insert(a,t)

@application.before_first_request
def initialize():
    apsched = Scheduler()
    apsched.start()
    apsched.add_interval_job(fetch_data, seconds=120)

@application.route("/api/v1/tracks")
def apiAll():
    tracks = set(all_tracks())
    attributed_tracks = []
    for track in list(tracks):
        at = {'artist': track[0], 'title': track[1]}
        attributed_tracks.append(at)
    return jsonify(attributed_tracks)

@application.route("/")
def index():
    return application.send_static_file('index.html')
    

if __name__ == "__main__":
    application.run()
