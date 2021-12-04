#!/usr/bin/env python
import configparser
import logging
import os
import sys
import spotipy

logger = logging.getLogger('root')

def init_spotipy():
    # string constant
    NOT_SET_VALUE = 'NOT SET'

    config_parser = configparser.ConfigParser()
    config_parser.read('spotipy-config.ini')
    client_id = config_parser.get('Login Parameters', 'client_id', fallback=NOT_SET_VALUE)
    client_secret = config_parser.get('Login Parameters', 'client_secret', fallback=NOT_SET_VALUE)
#    access_token = config_parser.get('Login Parameters', 'access_token', fallback=NOT_SET_VALUE)
    user_name = config_parser.get('Login Parameters', 'user_name', fallback=NOT_SET_VALUE)

    if os.environ.get("SPOTIPY_CLIENT_ID", NOT_SET_VALUE) is NOT_SET_VALUE:
        if client_id is NOT_SET_VALUE:
            print('ERROR: Environment variable is not set and client id not read from config file')
            logger.error('Environment variable is not set and client id not read from config file')
            sys.exit(1)
        os.environ['SPOTIPY_CLIENT_ID'] = client_id

    if os.environ.get("SPOTIPY_CLIENT_SECRET", NOT_SET_VALUE) is NOT_SET_VALUE:
        if client_secret is NOT_SET_VALUE:
            print('ERROR: Environment variable is not set and client secret not read from config file')
            logger.error('Environment variable is not set and client secret not read from config file')
            sys.exit(1)
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret

    if os.environ.get("SPOTIFY_USER_NAME", NOT_SET_VALUE) is NOT_SET_VALUE:
        if user_name is NOT_SET_VALUE:
            print('ERROR: Environment variable is not set and user name not read from config file')
            logging.error('Environment variable is not set and user name not read from config file')
            sys.exit(1)
        os.environ['SPOTIFY_USER_NAME'] = user_name

    token = spotipy.util.prompt_for_user_token(user_name, 'user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative user-top-read', client_id, client_secret, redirect_uri='https://127.0.0.1:8080')

    sp = spotipy.Spotify(auth=token)
    logger.debug('spotipy initialized')

    return sp