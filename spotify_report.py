import argparse
from collections import Counter
from datetime import date, timedelta
import json
import os
from etlutils import datafiles


def get_played_tracks(timespan):
    today = date.today()

    if timespan == 'year':
        start_day = date(today.year, 1, 1)
    elif timespan == 'month':
        start_day = date(today.year, today.month, 1)
    elif timespan == 'week':
        start_day = today - timedelta(days=(today.weekday()+1) % 7)
    elif timespan == 'date':
        start_day = today
    else:
        print(timespan)
        return []

    last_saved = datafiles.find_newest_saved_month('data', today.year, 'spotify_tracks')
    filename = datafiles.get_monthly_file_path('data', 'spotify_tracks', last_saved[0], last_saved[1])

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            played_tracks = json.load(f)
    else:
        print(f'Error loading file {filename}')

    return played_tracks


parser = argparse.ArgumentParser(description="generate a report from saved Spotify plays")
parser.add_argument('--span', help='set the timespan (day, week, month, year)', action='store', nargs=1, default='month', choices=['day', 'week', 'month', 'year'])
parser.add_argument('--top', help='set the number for the artist/track/album count', action='store', nargs=1, default=10, type=int)
args = parser.parse_args()
top_count = int(args.top[0])
timespan = args.span[0]

played_tracks = get_played_tracks(timespan)

artists = {}
tracks = {}
artist_list = []
track_list = []
for track in played_tracks:
    for artist in track['track']['artists']:
        artists[artist['id']] = artist
        artist_list.append(artist['id'])
    tracks[track['track']['id']] = track['track']['name']
    track_list.append(track['track']['id'])

artist_items = Counter(artist_list)
sorted_artist_items = sorted(artist_items.items(), key=lambda pair: pair[1], reverse=True)

track_items = Counter(track_list)
sorted_track_items = sorted(track_items.items(), key=lambda pair: pair[1], reverse=True)

print('ARTISTS')
for item in sorted_artist_items[:top_count]:
    print(f"{artists[item[0]]['name']}, plays {item[1]}")

print('\n\nTRACKS')
for item in sorted_track_items[:top_count]:
    print(f"{tracks[item[0]]}, plays {item[1]}")
