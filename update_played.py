import json
with open('data/recent_tracks.json', 'r') as f:
    tracks = json.load(f)
# time is in UTC
last_played_time = tracks['items'][:1][0]['played_at']
print(last_played_time)
