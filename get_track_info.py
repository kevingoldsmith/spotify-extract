#!/usr/bin/env python
import configparser
import os
import spotipy
import json
import sys
import logging
from etlutils.datafiles import get_monthly_file_path

# string constant
NOT_SET_VALUE = 'NOT SET'

config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
client_id = config_parser.get('Login Parameters', 'client_id', fallback=NOT_SET_VALUE)
client_secret = config_parser.get('Login Parameters', 'client_secret', fallback=NOT_SET_VALUE)
access_token = config_parser.get('Login Parameters', 'access_token', fallback=NOT_SET_VALUE)
logging_level = config_parser.get('logging', 'logging_level', fallback=logging.INFO)
logging_file = config_parser.get('logging', 'logging_file', fallback=None)

if os.environ.get("SPOTIPY_CLIENT_ID", NOT_SET_VALUE) is NOT_SET_VALUE:
    if client_id is NOT_SET_VALUE:
        print('ERROR: Environment variable is not set and client id not read from config file')
        sys.exit(1)
    os.environ['SPOTIPY_CLIENT_ID'] = client_id

if os.environ.get("SPOTIPY_CLIENT_SECRET", NOT_SET_VALUE) is NOT_SET_VALUE:
    if client_secret is NOT_SET_VALUE:
        print('ERROR: Environment variable is not set and client secret not read from config file')
        sys.exit(1)
    os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret

logger = logging.getLogger('get_track_info')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(asctime)s (%(levelname)s): %(message)s')
formatter.datefmt = '%Y-%m-%d %H:%M:%S %z'
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

if logging_file:
    fh = logging.FileHandler(logging_file)
    fh.setLevel(logging_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

token = spotipy.util.prompt_for_user_token('intonarumori', 'user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative user-top-read', client_id, client_secret, redirect_uri='https://127.0.0.1:8080')

sp = spotipy.Spotify(auth=token)

id = "5ObtaYq6nPnKliDjfMFjAI"

info = sp.track(id)
analysis = sp.audio_analysis(id)
features = sp.audio_features(tracks=[id])

tracks_info = dict()
tracks_info[id] = {
    "info": info,
    "analysis": analysis,
    "features": features,
    "plays": []
}

with open("tracks.json", 'w') as f:
    f.write(json.dumps(tracks_info))
