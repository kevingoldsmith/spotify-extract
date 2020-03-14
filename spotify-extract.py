#!/usr/bin/env python
import configparser
import os
import spotipy
import json

# string constant
NOT_SET_VALUE = 'NOT SET'

config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
client_id = config_parser.get('Login Parameters', 'client_id', fallback=NOT_SET_VALUE)
client_secret = config_parser.get('Login Parameters', 'client_secret', fallback=NOT_SET_VALUE)
access_token = config_parser.get('Login Parameters', 'access_token', fallback=NOT_SET_VALUE)

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

token = spotipy.util.prompt_for_user_token('intonarumori', 'user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative user-top-read', client_id, client_secret, redirect_uri='https://127.0.0.1:8080')

sp = spotipy.Spotify(auth=token)
played_tracks = []
results = sp.current_user_recently_played()
played_tracks.extend(results['items'])
cursors = results['cursors']
while cursors is not None:
    results = sp.current_user_recently_played(before=cursors['before'])
    played_tracks.extend(results['items'])
    cursors = results['cursors']

with open("recent_tracks.json", "w") as f:
    f.write(json.dumps(played_tracks, indent=2))
