#!/usr/bin/env python

import argparse
import errno
from operator import itemgetter
import json
import logging
from os.path import exists
import sys

def load_tracks(filename):
    tracks = []
    with open(filename, 'r') as f:
        tracks = json.load(f)
        logger.info("loaded %d tracks from %s", len(tracks), filename)
    return tracks

parser = argparse.ArgumentParser(description="merge two spotify track json files")
parser.add_argument('-l', '--loglevel', dest='loglevel', help='logging level', action='store', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
parser.add_argument('-o', '--outfile', dest='outfile', help='output filename', action='store', default='out.json')
parser.add_argument('files', nargs=2, help="file1 file2")
args = parser.parse_args()

logger = logging.getLogger('merge_tracks_files')
logger.setLevel(logging.getLevelName(args.loglevel))
formatter = logging.Formatter('%(name)s - %(asctime)s (%(levelname)s): %(message)s')
formatter.datefmt = '%Y-%m-%d %H:%M:%S %z'
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

if not exists(args.files[0]) or not exists(args.files[1]):
    logger.critical("invalid input files provided")
    sys.exit(errno.EINVAL)

tracks1 = load_tracks(args.files[0])
tracks2 = load_tracks(args.files[1])
out_tracks = tracks2.copy()

for track in tracks1:
    if not track in tracks2:
        logger.debug('track %s not in second file', track['track']['name'])
        out_tracks.append(track)

sorted_out_tracks = sorted(out_tracks, key=itemgetter('played_at'))
with open(args.outfile, 'w') as f:
    logger.info('writing %d tracks to %s', len(sorted_out_tracks), args.outfile)
    f.write(json.dumps(sorted_out_tracks))
