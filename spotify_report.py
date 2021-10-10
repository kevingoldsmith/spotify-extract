from collections import Counter
import datetime
import json
import os
from etlutils import datafiles

last_saved = datafiles.find_newest_saved_month('data', datetime.datetime.now().year, 'spotify_tracks')
filename = datafiles.get_monthly_file_path('data', 'spotify_tracks', last_saved[0], last_saved[1])

if os.path.exists(filename):
    with open(filename, 'r') as f:
        played_tracks = json.load(f)
else:
    print(f'Error loading file {filename}')

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
for item in sorted_artist_items[:10]:
    print(f"{artists[item[0]]['name']}, plays {item[1]}")

print('\n\nTRACKS')
for item in sorted_track_items[:10]:
    print(f"{tracks[item[0]]}, plays {item[1]}")
