# tmdb-tv-show-bulk-rename
Simple script renaming whole TV-Show file directories optimized for Kodi library scan.

## Features:
- Query TMDB for shows based on search term and display short overview
- Rename episode video files to "S(season)E(episode) - (episode name)"
- Move episodes to folders named by seasons
- Copy file structure to one of the specified library directories

## Preperation:
Install the dependencies via pip:
- tmdbsimple
- configparser
- argparse

Copy configuration example to `~/.config/tmdb-movie-rename/config.ini`, add TMDB api key and edit directories if needed.

## Usage:
`python ./tmdb-movie-rename.py [tv-show-folder]`
