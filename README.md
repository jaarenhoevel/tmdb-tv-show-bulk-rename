# tmdb-tv-show-bulk-rename
Simple script renaming whole TV-Show file directories optimized for Kodi library scan.

## Features:
- Query TMDB for shows based on search term and display short overview
- Rename episode video files to "S(season)E(episode) - (episode name)"
- Move episodes to folders named by seasons
- Copy file structure to one of the specified library directories
- Displays warnings when: Multiple files for same episode were found; Some files already exist in target directory; No matching episode was found on TMDB for given season and episode number in video filename
- Overview how many episodes were found compared to episode count on TMDB

## Prerequisites for input directory:
- Video files with the following extensions: `.mkv`, `.mp4`, `.avi`, `.m4v`. Any other file types will be ignored
- Filename of each episode must contain season and episode number. Examples: `S01E08`, `s12e04`

## Preperation:
Install the dependencies via pip:
- `tmdbsimple`
- `configparser`
- `argparse`

Copy configuration example to `~/.config/tmdb-tv-show-bulk-rename/config.ini`, add TMDB api key and edit directories if needed.

## Usage:
`python ./tmdb-tv-show-bulk-rename.py [tv-show-folder]`
