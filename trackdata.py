#!/usr/bin/env python
import spotipy
import json
import os


__trackdata = None
__datafile = 'data/tracks.json'
__include_analysis = False #analyses take up A LOT of space, don't get them by default


def __load_track_data():
    global __trackdata
    try:
        with open(__datafile, 'r') as f:
            __trackdata = json.load(f)
            print('loaded track data')
    except:
        __trackdata = dict()
        print('exception')


def __save_track_data():
    global __trackdata
    if __trackdata is not None:
        with open(__datafile, 'w') as f:
            f.write(json.dumps(__trackdata))


def __fetch_missing_data(ids_to_fetch, sp:spotipy.Spotify):
    global __trackdata

    if __trackdata is None:
        __load_track_data()

    if len(ids_to_fetch) > 0:
        # page the ids into groups of < 100
        id_pages = [ids_to_fetch[i:i+99] for i in range(0, len(ids_to_fetch), 99)]
        for ids in id_pages:
            fetched_tracks = sp.tracks(tracks=ids)['tracks']
            fetched_features = sp.audio_features(tracks=ids)
            if __include_analysis:
                fetched_analyses = []
                for id in ids:
                    track_analysis = sp.audio_analysis(id)
                    track_analysis['id'] = id
                    fetched_analyses.append(track_analysis)
            
            # add new data to cache
            for id in ids:
                __trackdata[id] = {
                }
            
            for track in fetched_tracks:
                __trackdata[track['id']]['info'] = track

            if __include_analysis:
                for track in fetched_analyses:
                    __trackdata[track['id']]['analysis'] = track
            
            for track in fetched_features:
                __trackdata[track['id']]['features'] = track

        print(f'new trackdata length: {len(__trackdata)}')

        __save_track_data()


def get_data_for_tracks(tracklist, sp:spotipy.Spotify):
    global __trackdata

    if __trackdata is None:
        __load_track_data()
    
    print(f'trackdata length: {len(__trackdata)}')
    
    # get missing data
    ids_to_fetch = [id for id in tracklist if id not in __trackdata]
    __fetch_missing_data(ids_to_fetch, sp)

    # return the useful parts
    return_data = {}
    for id in tracklist:
        return_data[id] = __trackdata[id]

    return return_data

"""         track_data = {}
        cached_data = __trackdata[id]
        genre_set = set()
        for artist in cached_data['info']['artists']:
            if 'genres' in artist:
                genre_set.union(set(artist['genres']))
            
        track_data['artist_genres'] = list(genre_set)
        return_data[id] = track_data

    print(return_data)
 """
