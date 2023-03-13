from contextlib import contextmanager
from dataclasses import dataclass
import dataclasses
from pathlib import Path
import sqlite3
from typing import Any, Generator

print('path:', Path('.').resolve())
__db: sqlite3.Connection = None


def init_db(path: str) -> None:
    global __db
    __db = sqlite3.connect(path)


def close_db() -> None:
    global __db
    if __db:
        __db.close()


@contextmanager
def get_db() -> Generator[sqlite3.Cursor, None, None]:
    global __db
    cursor: sqlite3.Cursor = None
    try:
        cursor = __db.cursor()
        yield cursor
    finally:
        cursor.close()


def sql_format(val: Any) -> Any:
    match val:
        case str():
            return "'{}'".format(val)
        case _:
            return str(val)


@dataclass
class StreamInfo:
    url: str
    title: str
    duration: str
    uploader: str
    uploader_url: str
    thumbnail_url: str
    view_count: int
    upload_date: str

    def __iter__(self):
        return iter([getattr(self, f.name) for f in dataclasses.fields(StreamInfo)])

    def get_values(self) -> list:
        return [sql_format(getattr(self, f.name)) for f in dataclasses.fields(StreamInfo)]


def __get_last_index_in_playlist(playlist_id: int) -> int:
    """
    return last index of playlist with playlist_id
    return 0, if playlist with that id doesn't exist
    """
    with get_db() as db:
        sql = "SELECT MAX(join_index) FROM playlist_stream_join WHERE playlist_id={}".format(
            sql_format(playlist_id)
        )
        res = db.execute(sql).fetchone()[0]
        return res if res else 0


def get_or_create_playlist(name: str) -> int:
    with get_db() as db:
        sql = "SELECT uid FROM playlists WHERE name = {};".format(
            sql_format(name))
        playlist_id = db.execute(sql).fetchone()
        if playlist_id:
            return playlist_id[0]

        sql_create = "INSERT INTO playlists (name) VALUES ({});".format(
            sql_format(name))
        db.execute(sql_create)
        db.connection.commit()

        playlist_id = db.lastrowid
        return playlist_id


def add_stream(info: StreamInfo, playlist_id: int, stream_type: str = 'VIDEO_STREAM', service_id: int = 0):
    with get_db() as db:
        columns = ["stream_type", "service_id"]
        columns.extend([f.name for f in dataclasses.fields(StreamInfo)])

        values = [sql_format(stream_type), sql_format(service_id)]
        values.extend(info.get_values())

        sql = "INSERT INTO streams ({}) VALUES ({});".format(
            ', '.join(columns),
            ', '.join(values)
        )

        db.execute(sql)
        stream_id = db.lastrowid

        columns2 = ["playlist_id", "stream_id", "join_index"]
        values = [sql_format(playlist_id), sql_format(stream_id), sql_format(
            __get_last_index_in_playlist(playlist_id) + 1)]
        sql2 = "INSERT INTO playlist_stream_join ({}) VALUES ({});".format(
            ', '.join(columns2),
            ', '.join(values),
        )

        db.execute(sql2)

        db.connection.commit()
    pass
