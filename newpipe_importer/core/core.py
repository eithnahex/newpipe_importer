from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import sqlite3
from typing import Literal
import zipfile

import yt_dlp

from newpipe_importer.core.db import add_stream, close_db, get_or_create_playlist, init_db
from newpipe_importer.yt.yt import get_stream_info


UnzippedPaths = namedtuple('UnzippedPaths', ['db', 'settings'])


class StreamInfoException(Exception):
    ...


class CreatePlaylistDatabaseException(Exception):
    ...


def unzip(path: str) -> UnzippedPaths:
    path: Path = Path(path)
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


def rezip(zip_path: str, *file_paths: str, backup: bool = False):
    zip_path: Path = Path(zip_path)
    
    if backup:
        os.rename(
            zip_path,
            Path(zip_path.parent, f'backup_{datetime.now().strftime("%d.%m.%Y %H.%M.%S")}__{zip_path.name}')
        )

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
        tracks_urls = [line.strip() for line in f.readlines()]
        return tracks_urls


def _validate_track_url(track: str) -> tuple[bool, str]:
    # TODO: impl
    return True, f"{track} url is ok"


def _add_tracks_from_playlist(playlist_file: str, playlist_name: str) -> list[ResultTrack]:
    tracks_urls = _fetch_track_urls_from_file(playlist_file)

    try:
        playlist_id = get_or_create_playlist(playlist_name)
    except Exception as e:
        raise CreatePlaylistDatabaseException from e


    added, failed = [], []
    for url in tracks_urls:
        ok, msg = _validate_track_url(url)
        if not ok:
            failed.append(ResultTrack(
                f'Error. Bad track url: [{url}]. Cause: {msg}', 'error'))
            continue

        info = get_stream_info(url)

        try:
            add_stream(info, playlist_id)

            added.append(ResultTrack(
                f'Track added: [{info.title}]({info.url})', 'ok'))

        except Exception as e:
            if isinstance(e, yt_dlp.utils.DownloadError) and "content from SME" in str(e):
                failed.append(
                    ResultTrack(f'Error. Track with url [{url}] unavailable due to SME (video blocked)', 'error')
                )
                continue
            if isinstance(e, sqlite3.IntegrityError) and "UNIQUE constraint failed: streams.service_id, streams.url" in str(e):
                failed.append(
                    ResultTrack(f'Error. Track with url [{url}] already exists', 'error')
                )
                continue
            failed.append(
                ResultTrack(f'Error. Failed to add track with [{url}]. Cause: {e}', 'error')
            )

    return [*added, *failed]


def add_all_from_playlist(newpipezip:str, playlist_file: str, playlist_name: str, backup: bool) -> list[ResultTrack]:

    unzipped = unzip(newpipezip)
    init_db(unzipped.db)

    results = []
    try:
        results = _add_tracks_from_playlist(playlist_file, playlist_name)
    except Exception as e:
        close_db()
        cleanup(*unzipped)
        raise e

    close_db()
    rezip(newpipezip, *unzipped, backup=backup)
    cleanup(*unzipped)

    return results
