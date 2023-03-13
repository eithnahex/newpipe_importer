import argparse
from collections import namedtuple
from datetime import datetime
import os
from pathlib import Path
import sqlite3
import zipfile

from db import add_stream, close_db, get_or_create_playlist, init_db
from yt.yt import get_stream_info


parser = argparse.ArgumentParser()
parser.add_argument(
    "playlist_file",
    type=str,
    help="Path to playlist txt file"
)
parser.add_argument(
    "--newpipezip",
    type=str,
    default=None,
    help="Path to Newpipe .zip"
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


def default_newpipe_file(args: argparse.Namespace):
    from os import listdir
    from os.path import isfile

    for f in listdir('.'):
        if isfile(f) and 'newpipe' in f.lower() and 'zip' in f.lower():
            path = Path('.', f)
            args.newpipezip = path.resolve()


UnzippedPaths = namedtuple('UnzippedPaths', ['db', 'settings'])


def unzip(path: str) -> UnzippedPaths:
    path = Path(path)
    with zipfile.ZipFile(path, mode='r') as zip:
        zip.extractall(path.parent)
        db = None
        settings = None
        for name in zip.namelist():
            if '.db' in name:
                db = name
            if '.settings' in name:
                settings = name

        return UnzippedPaths(Path(path.parent, db), Path(path.parent, settings))


def rezip(zip_path: str, *file_paths: str):
    with zipfile.ZipFile(zip_path, mode='w') as zip:
        for file in file_paths:
            file = Path(file)
            zip.write(
                file,
                file.name,
                compress_type=zip.compression,
                compresslevel=zip.compresslevel
            )


def cleanup(*file_paths: str):
    for f in file_paths:
        os.remove(f)


def add_all_from_playlist(playlist_file: str, playlist_name: str):
    with open(playlist_file, 'r', encoding='utf-8') as f:
        tracks_urls = f.readlines()
    for url in tracks_urls:
        try:
            add_stream(
                get_stream_info(url),
                get_or_create_playlist(playlist_name),
            )
            print("OK. Track added: {}".format(url))
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: streams.service_id, streams.url" in str(e):
                print("ERR. Track with url {} already exists".format(url))


def main() -> None:
    args = parser.parse_args()
    if args.newpipezip is None:
        default_newpipe_file(args)

    print('playlist_file:', args.playlist_file)
    print('newpipezip:', args.newpipezip)
    print('playlist_name:', args.playlist_name)
    print('backup:', args.backup)

    unzipped = unzip(args.newpipezip)
    init_db(unzipped.db)

    try:
        add_all_from_playlist(args.playlist_file, args.playlist_name)
    except Exception as e:
        print("ERR. {}".format(e))
        cleanup(*unzipped)
        return
    finally:
        close_db()

    if args.backup:
        new_zip = Path("NewData.zip")
    else:
        new_zip = Path(args.newpipezip)

    rezip(new_zip, *unzipped)
    cleanup(*unzipped)


if __name__ == "__main__":
    main()
