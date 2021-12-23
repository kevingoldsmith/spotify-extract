#!/usr/bin/env python
import argparse
from collections import Counter
import configparser
import csv
from datetime import datetime
import json
import logging
import os
from etlutils import datafiles


config_parser = configparser.ConfigParser()
config_parser.read('update-config.ini')
logging_level = config_parser.get('Logging Parameters', 'logging_level', fallback=logging.INFO)
logging_file = config_parser.get('Logging Parameters', 'logging_file', fallback=None)

arg_parser = argparse.ArgumentParser(description="generate a yearly report from saved Spotify plays")
arg_parser.add_argument('--year', help='which year to generate the report for (assumes you have the data)', action='store', default=datetime.now().year, type=int)
arg_parser.add_argument('--top', help='set the number for the artist/album count', action='store', default=10, type=int)
args = arg_parser.parse_args()
top_count = int(args.top)
year = int(args.year)

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

logger.info(f"gathering data for year: {year}")

months = []
artists = {}
albums = {}
tracks = {}
track_list = [] # tracks are for the year, the monthly isn't that interesting
artist_year_list = []

for month in range(1,13):
    month_file = datafiles.get_monthly_file_path('data', 'spotify_tracks', year, month)
    if os.path.exists(month_file):
        month_data = {
            'month':month
        }
        
        logger.debug(f"loading month: {month}")
        with open(month_file, 'r') as f:
            month_data['tracks'] = json.load(f)
        logger.info(f"loaded month: {month}, {len(month_data['tracks'])} tracks")

        artist_list = []
        album_list = []
        for track in month_data['tracks']:
            for artist in track['track']['artists']:
                if not artist['id'] in artists:
                    artists[artist['id']] = artist
                artist_list.append(artist['id'])

            albums[track['track']['album']['id']] = track['track']['album']
            album_list.append(track['track']['album']['id'])

            tracks[track['track']['id']] = track['track']['name']
            track_list.append(track['track']['id'])
        
        artist_year_list.extend(artist_list)
        artist_items = Counter(artist_list)
        sorted_artist_items = sorted(artist_items.items(), key=lambda pair: pair[1], reverse=True)
        for artist_iter in sorted_artist_items:
            if not 'plays_by_month' in artists[artist_iter[0]]:
                artists[artist_iter[0]]['plays_by_month'] = [0]*12
            artists[artist_iter[0]]['plays_by_month'][month-1] = artist_iter[1]

        album_items = Counter(album_list)
        sorted_album_items = sorted(album_items.items(), key=lambda pair: pair[1], reverse=True)

        month_data['top_artists'] = sorted_artist_items[:top_count]
        month_data['top_albums'] = sorted_album_items[:top_count]
        months.append(month_data)
    else:
        logger.info(f"missing month: {month}")

top_artist_ids_for_year = []

# monthly data
for month in months:
    print(f"MONTH: {month['month']}")
    print(f"tracks played: {len(month['tracks'])}")
    print("\tTOP ARTISTS:")
    top_artist_ids_for_year.extend(month['top_artists'])
    for artist in month['top_artists']:
        print(f"\t\t{artists[artist[0]]['name']}, plays {artist[1]}")
    print("\tTOP ALBUMS:")
    for album in month['top_albums']:
        print(f"\t\t{albums[album[0]]['name']}, plays: {album[1]}")

# yearly data
track_items = Counter(track_list)
sorted_track_items = sorted(track_items.items(), key=lambda pair: pair[1], reverse=True)
print('\n\nTRACKS')
for item in sorted_track_items[:top_count]:
    print(f"{tracks[item[0]]}, plays {item[1]}")

artist_year_items = Counter(artist_year_list)
sorted_artist_year_items = sorted(artist_year_items.items(), key=lambda pair: pair[1], reverse=True)
for top_artist in sorted_artist_year_items[:20]:
    print(f"{artists[top_artist[0]]['name']} ({top_artist[1]}): {artists[top_artist[0]]['plays_by_month']}")

with open(f'top-artists-{year}.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['artist', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
    for top_artist in sorted_artist_year_items[:20]:
        row = [artists[top_artist[0]]['name']]
        row.extend(artists[top_artist[0]]['plays_by_month'])
        writer.writerow(row)
