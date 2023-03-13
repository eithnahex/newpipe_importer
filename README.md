# Deps

- `Python 3.10+`
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)


# Installation

```bash
pip install git+https://github.com/eithnahex/newpipe_importer
```


# Usage

```bash
newpipe_importer playlist.txt
```

```bash
newpipe_importer playlist.txt --playlist_name NewPlaylist
```

- `playlist.txt` should contain lines with links to YouTube tracks
- example track:
    - https://www.youtube.com/watch?v=BaW_jenozKc

<br><br>

```bash
newpipe_importer --help
```
```
usage: newpipe_importer.exe [-h] [--newpipezip NEWPIPEZIP] [--playlist_name PLAYLIST_NAME]   
                            [--backup {True,False}]
                            playlist_file

positional arguments:
  playlist_file         Path to playlist txt file

options:
  -h, --help            show this help message and exit
  --newpipezip NEWPIPEZIP
                        Path to Newpipe .zip
  --playlist_name PLAYLIST_NAME
                        Playlist name to tracks add
  --backup {True,False}
                        Do a backup file before change. Default: False.
```