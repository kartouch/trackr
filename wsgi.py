#!/usr/bin/env python

import sqlite3
import requests
import os
from flask import Flask, jsonify
from apscheduler.scheduler import Scheduler
import HTMLParser
import urllib2
import sys
import json

application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!102ine10i2en19919199129'

db_name = os.environ['TRACKR_DATA'] + '/trackr.db'
timer = 120
conn = sqlite3.connect(db_name, timeout=10, isolation_level=None)
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY AUTOINCREMENT,
       artist text, title text,checked boolean,
       CONSTRAINT track_unique UNIQUE (artist, title));""")


def insert(artist, title):
    current_tracks = all_tracks()
    c.execute('INSERT INTO tracks (artist,title,checked) VALUES (?,?,?)',
              (artist, title, False))
    conn.commit()
    actual_tracks = all_tracks()
    if len(current_tracks) != len(actual_tracks):
        print "Added %s - %s" % (artist, title)


def mark_as_checked(idx):
    c.execute('UPDATE tracks SET checked=? WHERE id=?', (1, idx))
    conn.commit()


def all_tracks():
    c.execute('SELECT * from tracks where checked = 0;')
    tracks = c.fetchall()
    track_list = []
    for track in tracks:
        at = {
            'id': track[0],
            'artist': track[1],
            'title': track[2],
            'checked': track[3]
        }
        track_list.append(at)
    return track_list


def unescape(string):
    string = urllib2.unquote(string).decode('utf8')
    return HTMLParser.HTMLParser().unescape(string).encode(
        sys.getfilesystemencoding())


def fetch_data():
    url = "http://www.ipcast.de/metadata/onair_DEFJAY.xsl"
    data = requests.get(url)
    track = json.loads(
        data.content.replace('onair({"now":', '').replace('});', ''))
    t = track['title'].split(' - ')
    insert(t[0], t[1])


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
