import argparse
from collections import namedtuple
from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3
from typing import Literal
import zipfile

import yt_dlp

from newpipe_importer.core.db import add_stream, get_or_create_playlist
from newpipe_importer.yt.yt import get_stream_info


UnzippedPaths = namedtuple('UnzippedPaths', ['db', 'settings'])


class NothingToAddException(Exception):
    ...


def default_newpipe_file(args: argparse.Namespace):
    from os import listdir
    from os.path import isfile

    for f in listdir('.'):
        if isfile(f) and 'newpipe' in f.lower() and 'zip' in f.lower():
            path = Path('.', f)
            args.newpipezip = str(path)


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


@dataclass
class ResultTrack:
    msg: str
    status: Literal['ok', 'error']
    pass


def _fetch_track_urls_from_file(playlist_file: str) -> list[str]:
    with open(playlist_file, 'r', encoding='utf-8') as f:
        tracks_urls = f.readlines()
        return tracks_urls


def _validate_track_url(track: str) -> tuple[bool, str]:
    # TODO: impl
    return True, f"{track} url is ok"


def _add_tracks_from_playlist(playlist_file: str, playlist_name: str) -> list[ResultTrack]:
    tracks_urls = _fetch_track_urls_from_file(playlist_file)

    added, failed = [], []
    for url in tracks_urls:
        ok, msg = _validate_track_url(url)
        if not ok:
            failed.append(ResultTrack(
                f'Error. Bad track url: {url}. Cause: {msg}', 'error'))
            continue

        try:
            info = get_stream_info(url)
            playlist_id = get_or_create_playlist(playlist_name)
            add_stream(info, playlist_id)

            added.append(ResultTrack(
                f'Track added: {info.title}, {info.url}', 'ok'))

        except Exception as e:
            if isinstance(e, yt_dlp.utils.DownloadError) and "content from SME" in str(e):
                failed.append(
                    ResultTrack(f'Error. Track with url {url} unavailable due to SME (video blocked)', 'error')
                )
                continue
            if isinstance(e, sqlite3.IntegrityError) and "UNIQUE constraint failed: streams.service_id, streams.url" in str(e):
                failed.append(
                    ResultTrack(f'Error. Track with url {url} already exists', 'error')
                )
                continue
            failed.append(
                ResultTrack(f'Error. Failed to add track with {url}. Cause: {e}', 'error')
            )

    return [*added, *failed]


def add_all_from_playlist(playlist_file: str, playlist_name: str):
    results = _add_tracks_from_playlist(playlist_file, playlist_name)

    raise NotImplementedError()
    with open(playlist_file, 'r', encoding='utf-8') as f:
        tracks_urls = f.readlines()
    failed = 0
    for url in tracks_urls:
        try:
            add_stream(
                get_stream_info(url),
                get_or_create_playlist(playlist_name),
            )
            print("OK. Track added: {}".format(url))
        except yt_dlp.utils.DownloadError as e:
            if "content from SME" in str(e):
                failed += 1
                print(
                    "ERR. Track with url {} unavailable due to SME (video blocked)".format(url))
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: streams.service_id, streams.url" in str(e):
                failed += 1
                print("ERR. Track with url {} already exists".format(url))
        except Exception as e:
            failed += 1
            print("ERR. Video info download error. {}".format(e))

    if failed == len(tracks_urls):
        raise NothingToAddException("WARN. Nothing to add.")


@contextmanager
def frame():
    try:
        print('---------------------------------------------')
        yield
    finally:
        print('---------------------------------------------')
