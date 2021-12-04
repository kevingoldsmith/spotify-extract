#!/usr/bin/env python
import json
import os
from etlutils.datafiles import get_monthly_file_path
import spotipyinit
import trackdata

#load old tracks
filename = get_monthly_file_path('data', 'spotify_tracks', 2020, 10)
if os.path.exists(filename):
    with open(filename, 'r') as f:
        old_tracks = json.load(f)

sp = spotipyinit.init_spotipy()

ids = []
for track in old_tracks:
    ids.append(track['track']['id'])

print(len(ids))

trackdata.get_data_for_tracks(ids[:20], sp)