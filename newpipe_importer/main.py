import argparse
from datetime import datetime
import os

from newpipe_importer.core.core import NothingToAddException, add_all_from_playlist, cleanup, default_newpipe_file, frame, rezip, unzip
from newpipe_importer.core.db import close_db, init_db


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


def main() -> None:
    args = parser.parse_args()
    if args.newpipezip is None:
        default_newpipe_file(args)

    print('playlist_file:', args.playlist_file)
    print('newpipezip:', args.newpipezip)
    print('playlist_name:', args.playlist_name)
    print('backup:', args.backup)

    if args.newpipezip is None:
        print("ERR. No newpipe .zip file")
        return

    unzipped = unzip(args.newpipezip)
    init_db(unzipped.db)

    try:
        add_all_from_playlist(args.playlist_file, args.playlist_name)
    except NothingToAddException as e:
        print(e)
        close_db()
        cleanup(*unzipped)
        return
    except Exception as e:
        print("ERR.")
        close_db()
        cleanup(*unzipped)
        raise e
    finally:
        close_db()

    if args.backup:
        os.rename(
            args.newpipezip,
            f'backup_{datetime.now().strftime("%d.%m.%Y %H.%M.%S")}__{args.newpipezip}'
        )

    rezip(args.newpipezip, *unzipped)
    cleanup(*unzipped)

    print('DONE')
    print('newpipezip:', args.newpipezip)
    print('playlist_name:', args.playlist_name)


if __name__ == "__main__":
    main()
