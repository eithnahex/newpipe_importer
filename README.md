# About
> Newpipe_importer helps to add a list of YouTube tracks from a .txt file to the Newpipe database in order to import it later.

- You can use it on your Android device via [Termux](https://termux.dev)


# Deps

- `Python 3.10+`
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)


# Installation

```bash
pip install git+https://github.com/eithnahex/newpipe_importer
```


# Usage

- Open [NewPipe](https://newpipe.net/) app.
- Go to Settings -> Content -> Export database.
- Export content as `NewPipeData-<date>_<time>.zip` to some folder.
- Manually create a `playlist.txt` file. Each new line is a link to a YouTube track.
- Execute in terminal:
  ```
  newpipe_importer ./path/to/playlist.txt --newpipezip ./path/to/NewPipeData-<date>_<time>.zip
  ```
- Go to Settings -> Content -> Import database.
- Re-import the same updated `NewPipeData-<date>_<time>.zip`

> - newpipe_importer will generate a new playlist named `<date+time>` with your tracks from playlist.txt 
> - To specify the playlist name, use the `--playlist_name` argument


# Examples

- Specify the name of playlist
```bash
newpipe_importer playlist.txt --playlist_name NewPlaylistName
```

- if execute from directory with exported NewPipeData.zip
```bash
newpipe_importer playlist.txt
```

- Specify path to exported NewPipeData.zip
```bash
newpipe_importer playlist.txt --newpipezip ./path/to/NewPipeData.zip
```

<br>

```bash
newpipe_importer --help
```
```
usage: newpipe_importer [-h] [--newpipezip NEWPIPEZIP] [--playlist_name PLAYLIST_NAME]   
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