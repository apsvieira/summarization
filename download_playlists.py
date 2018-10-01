import argparse
import os
from subprocess import Popen, PIPE

import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--playlists',
                    help="File specifying playlists to download",
                    required=True)
parser.add_argument('--max_per_list',
                    help="Maximum number of videos to download from each playlist",
                    default=10)
parser.add_argument('-s', '--simulate',
                    type=bool,
                    help="Simulation, do not download or save any data to disk",
                    required=False)
parser.add_argument('--randomize',
                    required=True,
                    help="If true, download videos from playlist in random order.")

if __name__ == '__main__':
    opts = parser.parse_args()
    playlists_file = opts.playlists
    max_per_list = opts.max_per_list
    randomize = opts.randomize

    # Construct argument list for youtube-dl from command line arguments
    standard_commands = ["--yes-playlist", "--reject-title=\"\[Deleted video\]\""]
    standard_commands.append('-s') if opts.simulate is not None else None
    standard_commands.append("--max-downloads={}".format(max_per_list))
    standard_commands.append("--playlist-random") if randomize else None

    # Get path to youtube-dl script in current environment
    with Popen(["where", "youtube-dl"], stdout=PIPE) as where:
        youtube_dl = where.stdout.read().decode()

    # Transform Windows format path (\ separated) to POSIX-like (/ format). Remove line ending.
    youtube_dl = youtube_dl.replace('\\', '/').replace('\r\n', '')

    with open(playlists_file, 'r') as f:
        playlists = yaml.load(f)['playlists']

    for candidate, playlist in playlists.items():
        playlist_path = os.path.relpath(candidate)
        try:
            os.mkdir(playlist_path)
        except FileExistsError:
            print("Tried to create a folder that already exists. Moving on without creating new folder.")

        with Popen([youtube_dl, *standard_commands, playlist], stdout=PIPE, cwd=playlist_path) as p:
            print(p.stdout.read())
