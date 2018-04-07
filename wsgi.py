#!/usr/bin/python

import sqlite3
import requests
import xml.etree.ElementTree as ET
import time
from xml.sax.saxutils import escape, unescape
from flask import Flask, jsonify,render_template
from threading import Timer, Thread 

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracks(artist text, title text)''')
    conn.close()

def insert(artist,title):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('INSERT INTO tracks (artist,title) VALUES (?,?)',(artist,title))
    conn.commit()
    conn.close()

def all_tracks():
    conn = sqlite3.connect('example.db')
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
        
@app.route("/api/v1/tracks")
def apiAll():
    tracks = set(all_tracks())
    attributed_tracks = []
    for track in list(tracks):
        at = {'artist': track[0], 'title': track[1]}
        attributed_tracks.append(at)
    return jsonify(attributed_tracks)

@app.route("/")
def index():
    return app.send_static_file('index.html')
    

#https://gist.github.com/chadselph/4ff85c8c4f68aa105f4b#file-flaskwithcron-py-L18
class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None

if __name__ == "__main__":
    create_db()
    scheduler = Scheduler(120, fetch_data)
    scheduler.start()
    app.run()
    scheduler.stop()
