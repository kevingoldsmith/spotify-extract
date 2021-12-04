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

requested_ids = ids[:30]

print(f'requested data records: {len(requested_ids)}')

test_data = trackdata.get_data_for_tracks(requested_ids, sp)

print(f'returned data length: {len(test_data)}')
