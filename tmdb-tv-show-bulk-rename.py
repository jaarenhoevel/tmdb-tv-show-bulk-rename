import os, configparser, argparse, re, shutil
import tmdbsimple as tmdb

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def collectFiles(directory):
    fileTypes = ['.mkv', '.mp4', '.avi', '.m4v']
    fileList = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(file_type) for file_type in fileTypes):
                fileList.append(os.path.join(root, file))

    return fileList


def extract_season_episode(string):
    pattern = r's(\d+)e(\d+)'
    match = re.search(pattern, string, re.IGNORECASE)
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        return season, episode
    else:
        return None

parser = argparse.ArgumentParser(description='Rename TV-show files with the help of TMDB database.')
parser.add_argument('directory', help='Directory containing the TV-show files to be renamed (and moved)')

args = parser.parse_args()

# Check source directory
directory = args.directory
if not os.path.isdir(directory):
    print("No such directory.")
    exit()

# Check for config in user config directory
configFile = os.path.expanduser("~/.config/tmdb-tv-show-bulk-rename/config.ini")
if not os.path.isfile(configFile):
    print("No config file found.")
    exit();

config = configparser.ConfigParser()
config.read(configFile)

# Get all video files from directory
videoFiles = collectFiles(directory)
print(f'Found {len(videoFiles)} video files.')

# Set API key
tmdb.API_KEY = config["TMDB"]["ApiKey"]

# Ask for TV-show name 
print("\n\nTV-show name:")
search = tmdb.Search()
search.tv(query=input(">>> "))

# Print all results
print("\nResults:")
for index, show in enumerate(search.results):    
    #print(show)
    print(f'{index + 1} - {show["name"]} ({show["first_air_date"][:4]})')
    print(f'{bcolors.OKGREEN}{show["overview"]}{bcolors.ENDC}\n')

print("Select a show:")
selectedIndex = int(input(">>> ")) - 1

# Generate name from selected show
selectedShow = search.results[selectedIndex]
showName = f'{selectedShow["name"]} ({selectedShow["first_air_date"][:4]})'

# Get show info and episode names
tmdbShow = tmdb.TV(selectedShow["id"]);
showDetails = tmdbShow.info();

numberOfEpisodes = showDetails["number_of_episodes"]

seasons = {}

for season in showDetails["seasons"]:
    seasons[season["season_number"]] = {"name": season["name"], "episodes": {}}

    tmdbSeason = tmdb.TV_Seasons(selectedShow["id"], season["season_number"]);
    seasonInfo = tmdbSeason.info();

    for episode in seasonInfo["episodes"]:
        seasons[season["season_number"]]["episodes"][episode["episode_number"]] = {"name": episode["name"], "allocated": False}

# Go through files and try to find it in episode list
renameList = {}
allocatedEpisodes = 0;

for videoFile in videoFiles:
    result = extract_season_episode(videoFile)
    if result:
        season, episode = result

        try:
            matchingEpisode = seasons[season]["episodes"][episode]
            if not matchingEpisode["allocated"]:
                #print(matchingEpisode["name"])
                matchingEpisode["allocated"] = True
                allocatedEpisodes += 1

                # Get movie file extension
                fileExtension = os.path.splitext(videoFile)[1]

                title = re.sub(r'[^\w_. -]', '', matchingEpisode['name'])

                relativePath = f"S{season:02d}E{episode:02d} - {title}{fileExtension}"
                print(f'{seasons[season]["name"]}/{relativePath}')

                renameList[videoFile] = {"filename": relativePath, "seasonDir": seasons[season]['name']}

            else:
                print(f"{bcolors.WARNING}Matching episode found is already allocated S{season:02d}E{episode:02d}{bcolors.ENDC}")
        except KeyError:
            print(f"{bcolors.WARNING}No matching episode found in show S{season:02d}E{episode:02d}{bcolors.ENDC}")
            pass

        
    else:
        print(f"{bcolors.WARNING}No season and episode information found in filename {videoFile}{bcolors.ENDC}")

print(f'\nSuccesfully allocated {allocatedEpisodes} out of {numberOfEpisodes} episodes!')

# Print target directories
targetDirectories = []
print("\n\nCopy TV-show to directory? [Skip and use current directory]")
for index, tDirectory in enumerate(config["Target Directories"]):
    print(f'{index + 1} - {tDirectory.upper()}')
    print(f'{bcolors.OKGREEN}{config["Target Directories"][tDirectory]}{bcolors.ENDC}\n')
    targetDirectories.append(config["Target Directories"][tDirectory])

targetDirectorySelection = input(">>> ")
if targetDirectorySelection != "":
    targetDirectory = targetDirectories[int(targetDirectorySelection) - 1]
else:
    targetDirectory = os.path.abspath(os.getcwd())

# Create directory for TV-show
try:
    os.mkdir(f'{targetDirectory}/{showName}')
except FileExistsError:
    print("Target directory already exists. Exiting...")
    exit()

# Finally, copy video files
for file, target in renameList.items():
    os.makedirs(f'{targetDirectory}/{showName}/{target["seasonDir"]}', exist_ok=True)

    finalPath = f'{targetDirectory}/{showName}/{target["seasonDir"]}/{target["filename"]}'

    if os.path.isfile(finalPath):
        print(f"Target file already exists: \n{file}\n\n")
        continue

    print(f'Copying \n{file} \nto \n{finalPath}\n\n')
    shutil.copy(file, finalPath)
