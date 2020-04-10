#!/usr/bin/env python
import configparser
import os
import spotipy
import json
import utils
import sys

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

# group tracks by year and month
grouped_tracks = {}
for track in played_tracks:
    played_at_str = track['played_at']
    played_at = utils.datetime_from_string(played_at_str)
    if not str(played_at.year) in grouped_tracks:
        grouped_tracks[str(played_at.year)] = {}
    if not str(played_at.month) in grouped_tracks[str(played_at.year)]:
        grouped_tracks[str(played_at.year)][str(played_at.month)] = []
    grouped_tracks[str(played_at.year)][str(played_at.month)].append(track)

for year in grouped_tracks.keys():
    for month in grouped_tracks[year]:
        print('adding tracks for {}-{}'.format(year, month))
        new_tracks = grouped_tracks[year][month]
        old_tracks = []

        #load old tracks
        filename = utils.get_monthly_filename('data', 'spotify', 'json', int(year), int(month))
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                old_tracks = json.load(f)
        print(filename)
        print('old_tracks: {}, new_tracks: {}'.format(len(old_tracks), len(new_tracks)))
        old_tracks.extend(new_tracks)
        print('extended_Tracks: {}'.format(len(old_tracks)))
        track_dict = {}
        for track in old_tracks:
            track_dict[track['played_at']] = track
        final_list = []
        for played_time in sorted(track_dict.keys()):
            final_list.append(track_dict[played_time])
        with open(filename, 'w') as f:
            f.write(json.dumps(final_list))


""" tracks = {}

with open('data/recent_tracks.json', 'r') as f:
    tracks = json.load(f)

# time is in UTC
last_played_time = tracks['items'][:1][0]['played_at']
print(last_played_time)
 """