#!/usr/bin/env python

import configparser
import os
import spotipy
import json
import logging
from etlutils.date import datetime_from_zulutime_string
from etlutils.datafiles import get_monthly_file_path
from spotipyinit import init_spotipy

config_parser = configparser.ConfigParser()
config_parser.read('update-config.ini')
logging_level = config_parser.get('Logging Parameters', 'logging_level', fallback=logging.INFO)
logging_file = config_parser.get('Logging Parameters', 'logging_file', fallback=None)

# initalize logging
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(module)s - (%(levelname)s): %(message)s')
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

sp = init_spotipy()
played_tracks = []
results = sp.current_user_recently_played()
played_tracks.extend(results['items'])
logger.info('loaded %d tracks', len(played_tracks))
cursors = results['cursors']
while cursors is not None:
    results = sp.current_user_recently_played(before=cursors['before'])
    if len(results['items']) > 0:
        played_tracks.extend(results['items'])
        logger.info('loaded %d tracks', len(played_tracks))
    cursors = results['cursors']

# group tracks by year and month
grouped_tracks = {}
for track in played_tracks:
    played_at_str = track['played_at']
    played_at = datetime_from_zulutime_string(played_at_str)
    if not str(played_at.year) in grouped_tracks:
        grouped_tracks[str(played_at.year)] = {}
    if not str(played_at.month) in grouped_tracks[str(played_at.year)]:
        grouped_tracks[str(played_at.year)][str(played_at.month)] = []
    grouped_tracks[str(played_at.year)][str(played_at.month)].append(track)

for year in grouped_tracks.keys():
    for month in grouped_tracks[year]:
        logger.info('adding tracks for %s-%s', year, month)
        new_tracks = grouped_tracks[year][month]
        old_tracks = []

        #load old tracks
        filename = get_monthly_file_path('data', 'spotify_tracks', int(year), int(month))
        if os.path.exists(filename):
            logger.info('loading %s', filename)
            with open(filename, 'r') as f:
                old_tracks = json.load(f)
            logger.info('loaded %d tracks from %s', len(old_tracks), filename)

        old_tracks.extend(new_tracks)
        track_dict = {}
        for track in old_tracks:
            track_dict[track['played_at']] = track
        final_list = []
        for played_time in sorted(track_dict.keys()):
            final_list.append(track_dict[played_time])

        with open(filename, 'w') as f:
            logger.info('writing %d tracks to %s', len(final_list), filename)
            f.write(json.dumps(final_list))
