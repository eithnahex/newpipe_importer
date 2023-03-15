import argparse
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from newpipe_importer.core.core import CreatePlaylistDatabaseException, add_all_from_playlist


parser = argparse.ArgumentParser()
parser.add_argument(
    "playlist_file",
    type=str,
    help="Path to playlist.txt file"
)
parser.add_argument(
    "--newpipezip",
    type=str,
    default=None,
    help="Path to NewpipeData.zip"
)
parser.add_argument(
    "--playlist_name",
    type=str,
    default=datetime.now().strftime("%d.%m.%Y"),
    help="Playlist name to tracks add"
)
parser.add_argument(
    "--backup",
    type=bool,
    default=False,
    choices=[True, False],
    help="Do a backup file before change. Default: False."
)


@contextmanager
def frame():
    try:
        print('---------------------------------------------')
        yield
    finally:
        print('---------------------------------------------')


def default_newpipe_file(args: argparse.Namespace):
    from os import listdir
    from os.path import isfile

    for f in listdir('.'):
        if isfile(f) and 'newpipe' in f.lower() and 'zip' in f.lower():
            path = Path('.', f)
            args.newpipezip = str(path)


def main() -> None:
    args = parser.parse_args()
    if args.newpipezip is None:
        default_newpipe_file(args)


    if args.newpipezip is None:
        with frame():
            print("Error. No newpipe .zip file")
        return


    with frame():
        print('playlist_file:', args.playlist_file)
        print('newpipezip:', args.newpipezip)
        print('playlist_name:', args.playlist_name)
        print('backup:', args.backup)


    try:
        results = add_all_from_playlist(args.newpipezip, args.playlist_file, args.playlist_name, args.backup)
    except CreatePlaylistDatabaseException as e:
        with frame():
            print(e)
            print(f"Error. Failed to create playlist with name: {args.playlist_name}.")
            return
    except Exception as e:
        with frame():
            print("Unknown error.")
            print(e)
        return
    
    with frame():
        print('DONE')
        print('newpipezip:', args.newpipezip)
        print('playlist_name:', args.playlist_name)

        for result in results:
            print(result.msg)

        if not any((True for x in results if x.status == 'ok')):
            print(f"Warning. Nothing to add.")


if __name__ == "__main__":
    main()
