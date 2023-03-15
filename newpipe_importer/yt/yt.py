import yt_dlp
from newpipe_importer.core.db import StreamInfo


def _build_video_url(info: dict) -> dict:
    url = "https://www.youtube.com/watch?v={}".format(info['id'])
    info['url'] = url
    return info


def get_info(url: str, ydl_opts: dict | None = None) -> dict:
    # ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions
    ydl_opts = ydl_opts if ydl_opts else {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return _build_video_url(info)


def get_stream_info(url: str, ydl_opts: dict | None = None) -> StreamInfo:
    info = get_info(url, ydl_opts)
    return StreamInfo(
        url=info['url'],
        title=info['title'],
        duration=info['duration'],
        uploader=info['uploader'],
        uploader_url=info['uploader_url'],
        thumbnail_url=info['thumbnail'],
        view_count=info['view_count'],
        upload_date=info['upload_date'],
    )
