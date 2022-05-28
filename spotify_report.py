#!/usr/bin/env python

import argparse
from collections import Counter
from datetime import date, datetime, timedelta
import json
import os
from etlutils import datafiles
from etlutils.date import datetime_from_zulutime_string

def get_played_tracks(timespan):
    today = date.today()

    if timespan == 'year':
        start_day = date(today.year, 1, 1)
    elif timespan == 'month':
        start_day = date(today.year, today.month, 1)
    elif timespan == 'week':
        start_day = today - timedelta(days=(today.weekday()+1) % 7)
    elif timespan == 'day':
        start_day = today
    else:
        print(timespan)
        return []

    loaded_tracks = []
    current_month = start_day
    filename = datafiles.get_monthly_file_path('data', 'spotify_tracks', current_month.year, current_month.month)
    done = False
    while not done:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                print(f'loading: {filename}')
                loaded_tracks.extend(json.load(f))
        else:
            print(f'Error loading file {filename}')
        done = current_month.month == today.month and current_month.year == today.year
        current_month = current_month + timedelta(days=31)
        current_month = date(current_month.year,current_month.month, 1)
        filename = datafiles.get_monthly_file_path('data', 'spotify_tracks', current_month.year, current_month.month)

    if timespan == 'year' or timespan == 'month':
        return loaded_tracks
    
    played_tracks = []
    start_day_dt = datetime.combine(start_day, datetime.min.time())
    for track in loaded_tracks:
        track_dt = datetime_from_zulutime_string(track['played_at'])
        if start_day_dt <= track_dt:
            played_tracks.append(track)
    
    return played_tracks


def format_leading_zeros(number, maximum=10):
    if maximum < 10:
        return '{0}'.format(number)
    elif maximum < 100:
        return '{:02d}'.format(number)
    elif maximum < 1000:
        return '{:03d}'.format(number)
    return '{:04d}'.format(number)


parser = argparse.ArgumentParser(description="generate a report from saved Spotify plays")
parser.add_argument('--span', help='set the timespan (day, week, month, year)', action='store', default='month', choices=['day', 'week', 'month', 'year'])
parser.add_argument('--top', help='set the number for the artist/track/album count', action='store',    default=10, type=int)
args = parser.parse_args()
top_count = int(args.top)
timespan = args.span

played_tracks = get_played_tracks(timespan)

artists = {}
tracks = {}
albums = {}
artist_list = []
track_list = []
album_list = []
for track in played_tracks:
    for artist in track['track']['artists']:
        artists[artist['id']] = artist
        artist_list.append(artist['id'])
    tracks[track['track']['id']] = track['track']['name']
    albums[track['track']['album']['id']] = track['track']['album']
    track_list.append(track['track']['id'])
    album_list.append(track['track']['album']['id'])

artist_items = Counter(artist_list)
sorted_artist_items = sorted(artist_items.items(), key=lambda pair: pair[1], reverse=True)

track_items = Counter(track_list)
sorted_track_items = sorted(track_items.items(), key=lambda pair: pair[1], reverse=True)

album_items = Counter(album_list)
sorted_album_items = sorted(album_items.items(), key=lambda pair: pair[1], reverse=True)

print(f'\n\nTOTAL PLAYED TRACKS: {len(played_tracks)}')

print('\nARTISTS')
count = 0
for item in sorted_artist_items[:top_count]:
    count+=1
    print(f"{format_leading_zeros(count, top_count)}. {artists[item[0]]['name']}, plays {item[1]}")

print('\n\nALBUMS')
count = 0
for item in sorted_album_items[:top_count]:
    count+=1
    album = albums[item[0]]
    print(f"{format_leading_zeros(count, top_count)}. {album['name']}, {album['artists'][0]['name']}, plays {item[1]}")

print('\n\nTRACKS')
count = 0
for item in sorted_track_items[:top_count]:
    count+=1
    print(f"{format_leading_zeros(count, top_count)}. {tracks[item[0]]}, plays {item[1]}")

print('\n\nRECENT PLAYS')
rp = played_tracks[-top_count:].copy()
rp.reverse()
for item in rp:
    print(f"{item['track']['artists'][0]['name']} - {item['track']['name']}")