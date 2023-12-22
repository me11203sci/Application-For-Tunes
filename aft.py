'''
Application For Tunes - Python Implementation

Author(s): Melesio Albavera <ma6hv@mst.edu>
Created: 18 December 2023
Updated: 20 December 2023
Version: 0.3
Description:
    TODO
Notes:
    TODO
'''
from argparse import ArgumentParser, Namespace
from alive_progress import alive_bar # type: ignore
import eyed3 # type: ignore
from eyed3.id3.frames import ImageFrame # type: ignore
from dotenv import dotenv_values, find_dotenv # type: ignore
from InquirerPy import prompt # type: ignore
from InquirerPy.validator import EmptyInputValidator # type: ignore
from io import BytesIO
import music_tag # type: ignore
from os import makedirs, system
from os.path import isdir, isfile
from PIL import Image # type: ignore
import requests
import sys
from typing import Any, Final
from urllib.request import urlopen
from yt_dlp import YoutubeDL # type: ignore


class AudioSourceSelectInterrupt(Exception):
    def __init__(self, discard_result: dict) -> None:
        super().__init__()


def raise_audio_select_interrupt(result) -> None:
    '''
    TODO: Numpy-Style Documentation String

    Parameters
    ----------

    Returns
    -------
    '''
    raise AudioSourceSelectInterrupt(result)


def format_song_results(data: list[dict]) -> list[str]:
    '''
    TODO: Numpy-Style Documentation String

    Parameters
    ----------

    Returns
    -------
    '''
    # Add padding to track attributes.
    formated_attributes: list[tuple[str, ...]] = [
        (
            f'{track["title"]:<32}',
            f'{track["album_title"]:<32}',
            f'{track["artist"]:<32}',
            f'{track["isrc"]}',
            f'{track["duration"]}',
        )
        for track in data
    ]

    # If padded attribute string exceeds cell width, truncate it.
    return [
        {0: f'│{t[0]}│', 1: f'│{t[0][:27] + " ... "}│'}[len(t[0]) > 32]
        + {0: f'{t[1]}│', 1: f'{t[1][:27] + " ... "}│'}[len(t[1]) > 32]
        + {0: f'{t[2]}│', 1: f'{t[2][:27] + " ... "}│'}[len(t[2]) > 32]
        + f'{t[3]}│{t[4]:<8}│'
        for t in formated_attributes 
    ]


def format_album_results(data: list[dict]) -> list[str]:
    '''
    TODO: Numpy-Style Documentation String

    Parameters
    ----------

    Returns
    -------
    '''
    # Add padding to albums attributes.
    formated_attributes: list[tuple[str, ...]] = [
        (
            f'{album["album_title"]:<32}',
            f'{album["artist"]:<32}',
            f'{album["total_tracks"]:<12}',
            f'{album["year"]}',
        )
        for album in data
    ]

    # If padded attribute string exceeds cell width, truncate it.
    return [
        {0: f'│{a[0]}│', 1: f'│{a[0][:27] + " ... "}│'}[len(a[0]) > 32]
        + {0: f'{a[1]}│', 1: f'{a[1][:27] + " ... "}│'}[len(a[1]) > 32]
        + f'{a[2]}│{a[3]}│'
        for a in formated_attributes 
    ]


def get_audio_source_url(query_result: dict) -> str:
    '''
    TODO: Numpy-Style Documentation String

    Parameters
    ----------

    Returns
    -------
    '''
    index: Any = 0

    formated_choices: list = []
    for result in query_result:
        video_title: str = result["title"]
        channel: str = result["author"]
        link: str = f'https://www.youtube.com/watch?v={result["videoId"]}'
        formated_choices.append(
            {
                0: f'│{video_title:<32}│',
                1: f'│{video_title:<32}'[:28] + ' ... │'
            }[len(video_title) > 32]
            + {
                0: f'{channel:<32}│',
                1: f'{channel:<32}'[:28] + ' ... │'
            }[len(channel) > 32]
            + f'{link:<48}│'
        )

    try:
        index = prompt(
            {
                'type' : 'list',
                'message' :
                    f'\nSelect audio source (Ctrl-c to cancel):'
                    f'\n  ┌{"─" * 32}┬{"─" * 32}┬{"─" * 48}┐'
                    f'\n  │{"Video Title":<32}│{"Channel":<32}│'
                    f'{"Youtube Link":<48}│'
                    f'\n  ├{"─" * 32}┼{"─" * 32}┼{"─" * 48}┤',
                'choices' : formated_choices,
                'qmark' : '',
                'amark' : '',
                'pointer' : '>',
                'show_cursor' : False,
                'transformer' : raise_audio_select_interrupt,
                'filter' :
                    lambda result:
                        formated_choices.index(result),
            },
            style={'answer' : '#ffffff'}
        )[0]
    except AudioSourceSelectInterrupt:
        sys.stdout.write('\033[2KAudio source selected.\r')
        sys.stdout.flush()

    except KeyboardInterrupt:
        sys.stdout.write(
            '\033[A\033[2K\033[A\033[2K\033[A\033[2K\033[A\033[2K\033[A\033[2K'
            'No audio source selected.\r'
        )
        return ''

    return f'https://www.youtube.com/watch?v={query_result[index]["videoId"]}'


def download_song(track_metadata: dict, scale_image: bool) -> None:
    '''
    TODO: Numpy-Style Documentation String

    Parameters
    ----------

    Returns
    -------
    '''
    song_name: str = track_metadata['title'].replace('/', '\\')
    artist: str = track_metadata['artist']
    query: str = track_metadata['query']
    filename: str = f'{track_metadata["output_folder"]}{song_name}'

    # Set up ouput folder if it does not exist already.
    if not isdir(track_metadata["output_folder"]):
        makedirs(track_metadata["output_folder"])

    # Check if the file already exists.
    if isfile(f'{filename}.mp3'):
        return

    # Special characters break later A.P.I. queries.
    character_encodings: dict = str.maketrans({
        ' ' : '+',
        '$' : '%24',
        '#' : '%23',
        '&' : '%26',
        ',' : '%2C',
        '?' : '%3F',
        ':' : '%3A'
    })

    invidious_search_result: dict = requests.get(
        'https://vid.puffyan.us/api/v1/search/?q='
        + '{0}+{1}+{2}'.format(
            song_name.replace('\'', '').translate(character_encodings),
            artist.replace('\'', '').translate(character_encodings),
            query.replace('\'', '').translate(character_encodings)
        )
        + '&type=video'
    ).json()

    audio_source_url: str = get_audio_source_url(invidious_search_result)

    # No audio source was selected.
    if not audio_source_url:
        return

    # Youtube Downloader configuration options.
    options: dict = {
        'outtmpl' : filename,
        'noprogress' : True,
        'quiet' : True,
        'format': 'bestaudio/best',
        'concurrent_fragment_downloads': 32,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(options) as youtube_downloader:
        youtube_downloader.download(audio_source_url)

    # Write ID3tags to mp3 file.
    mp3_tags = music_tag.load_file(f'{filename}.mp3') # type: ignore
    mp3_tags['tracktitle'] = song_name # type: ignore
    mp3_tags['album'] = track_metadata['album_title'] # type: ignore
    mp3_tags['artist'] = artist # type: ignore
    mp3_tags['year'] = track_metadata['year'] # type: ignore
    mp3_tags['tracknumber'] = track_metadata['track_number'] # type: ignore
    mp3_tags['totaltracks'] = track_metadata['total_tracks'] # type: ignore
    mp3_tags.save() # type: ignore

    # Read image data and rescale if nessessary.
    image_data: bytes = urlopen(track_metadata['image_link']).read()
    if scale_image:
        image = Image.open(BytesIO(image_data), 'r') # type: ignore
        image.thumbnail((480, 480))
        image.save((buffer := BytesIO()), format=image.format)
        image_data = buffer.getvalue()

    # Write image data.
    audiofile = eyed3.load(f'{filename}.mp3') # type: ignore
    audiofile.tag.images.set( # type: ignore
        ImageFrame.FRONT_COVER,
        image_data,
        'image/jpeg'
    )
    audiofile.tag.save() # type: ignore

    return


if __name__ == '__main__':
    # Parse flags.
    parser: ArgumentParser = ArgumentParser(
        description=(
            'Search for and download mp3 files and their corresponding '
            'metadata.'
        )
    )
    parser.add_argument(
        '-d',
        '--downscale_image',
        help='Downscale album art to 480 x 480 for display on small devices.',
        dest='downscale_art',
        default=False,
        action='store_true'
    )
    parsed_arguments: Namespace = parser.parse_args()
    downscale_art: bool = parsed_arguments.downscale_art

    # Make my A.S.C.I.I. escape code work on Windows.
    system('')

    # Print A.S.C.I.I. text splash screen from file.
    try:
        with open('splash.txt', 'r') as splash_text:
            for line in splash_text:
                print(line, end='')
    except OSError:
        print('Splash screen file not found.')
        sys.exit(0)

    # Verify that 'env_path' exists and contains the nessessary credentials.
    try:
        env_path: Final[str] = find_dotenv(
            '.env',
            raise_error_if_not_found=True
        )
        credentials: Final[dict] = dotenv_values(env_path)
        assert credentials['spotify_id'] 
        assert credentials['spotify_secret'] 
    except (AssertionError, OSError): 
        print('Valid Spotify credentials not found.')
        sys.exit(0)

    print('Valid Spotify credentials found.')

    # Request valid Spotify Access Token
    authorization: dict = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type' : 'client_credentials',
            'client_id' : credentials['spotify_id'],
            'client_secret' : credentials['spotify_secret']
        },
        headers={'Content-Type' : 'application/x-www-form-urlencoded'}
    ).json()

    # Create authorization header.
    authorization_header: dict = {}
    try:
        authorization_header = {
            'Authorization' : f'Bearer {authorization["access_token"]}'
        }
    except KeyError:
        print(
            'Authorization token request failed, perhaps credentials are '
            'invalid?'
        )

    query: str = ''
    search_mode: str = ''
    output_folder: str = './output/'

    # Main loop.
    while True:
        try:
            query = str(
                prompt(
                    {
                        'type' : 'input',
                        'message' : '\nEnter search query (Ctrl-c to cancel):',
                        'qmark' : '',
                        'amark' : '',
                        'validate' : EmptyInputValidator(),
                    },
                    style={'answer' : '#ffffff'}
                )[0]
            )

            search_mode = str(
                prompt(
                    {
                        'type' : 'list',
                        'message' : 'Search by (Ctrl-c to cancel):',
                        'choices' : ['Album', 'Song'],
                        'qmark' : '',
                        'amark' : '',
                        'pointer' : '>',
                        'filter' : lambda result:
                            {
                                'Album' : 'album',
                                'Song' : 'track',
                            }[result],
                    },
                    style={'answer' : '#ffffff'}
                )[0]
            )
        except KeyboardInterrupt:
            print('Search cancelled.')

        initial_query_response: dict = {}
        if search_mode:
            # Query Spotify.
            initial_query_response = requests.get(
                f'https://api.spotify.com/v1/search?q={query}&type='
                f'{search_mode}&limit=50',
                headers=authorization_header
            ).json()

        selection: list = []
        match search_mode:
            case 'track':
                tracks: list[dict] = []
                for track in initial_query_response['tracks']['items']:
                    parsed_metadata: dict = {
                        'title' : track['name'],
                        'track_number' : track['track_number'],
                        'year' : track['album']['release_date'].split('-')[0],
                        'album_title' : track['album']['name'],
                        'total_tracks' : track['album']['total_tracks'],
                        'artist' : track['artists'][0]['name'],
                        'duration' :
                            f'{track["duration_ms"] // 60000}:'
                            f'{track["duration_ms"] // 1000 % 60:02}',
                        'isrc' : track['external_ids']['isrc'],
                        'query' : query,
                    }

                    # May not contain image; use a placeholder image.
                    try:
                        parsed_metadata['image_link'] = (
                            track['album']['images'][0]['url']
                        )

                    except IndexError:
                        parsed_metadata['image_link'] = (
                            'https://i.imgur.com/yOJQUID.png'
                        )

                    tracks.append(parsed_metadata)

                formated_choices: list = format_song_results(tracks)

                song_search_header: str = (
                    f'Top 50 results (Ctrl-c to cancel):\n'
                    f'  ┌{"─" * 32}┬{"─" * 32}┬{"─" * 32}┬{"─" * 12}┬{"─" * 8}'
                    f'┐\n  │{"Title":<32}│{"Album":<32}│{"Artist":<32}│'
                    f'{"ISRC":<12}│Duration│\n  '
                    f'├{"─" * 32}┼{"─" * 32}┼{"─" * 32}┼{"─" * 12}┼{"─" * 8}┤'
                )

                try:
                    selection = list(
                        prompt(
                            {
                                'type' : 'list',
                                'message' : song_search_header,
                                'choices' : formated_choices,
                                'qmark' : '',
                                'amark' : '',
                                'pointer' : '>',
                                'show_cursor' : False,
                                'transformer' : 
                                    lambda result:
                                        f'\n  {result}\n  └{"─" * 32}┴'
                                        f'{"─" * 32}┴{"─" * 32}┴{"─" * 12}┴'
                                        f'{"─" * 8}┘',
                                'filter' :
                                    lambda result:
                                        tracks[formated_choices.index(result)],
                            },
                            style={'answer' : '#ffffff'}
                        ).values()
                    )
                except KeyboardInterrupt:
                    print('Search cancelled.')

            case 'album':
                # Parse relevant metadata per track.
                albums: list[dict] = [
                    {
                        'year' : album['release_date'].split('-')[0],
                        'album_title' : album['name'],
                        'total_tracks' : album['total_tracks'],
                        'artist' : album['artists'][0]['name'],
                        'image_link' : album['images'][0]['url'],
                        'id' : album['id'],
                    }
                    for album in initial_query_response['albums']['items']
                ]

                formated_choices = format_album_results(albums)
                
                album_search_header: str = (
                    f'Top 50 results (Ctrl-c to cancel):\n'
                    f'  ┌{"─" * 32}┬{"─" * 32}┬{"─" * 12}┬{"─" * 4}┐\n'
                    f'  │{"Album":<32}│{"Artist":<32}│Total Tracks│Year'
                    f'│\n  ├{"─" * 32}┼{"─" * 32}┼{"─" * 12}┼{"─" * 4}┤'
                )

                try:
                    selection = list(
                        prompt(
                            {
                                'type' : 'list',
                                'message' : album_search_header,
                                'choices' : formated_choices,
                                'qmark' : '',
                                'amark' : '',
                                'pointer' : '>',
                                'show_cursor' : False,
                                'transformer' : 
                                    lambda result:
                                        f'\n  {result}\n  └{"─" * 32}┴'
                                        f'{"─" * 32}┴{"─" * 12}┴'
                                        f'{"─" * 4}┘',
                                'filter' :
                                    lambda result:
                                        albums[formated_choices.index(result)],
                            },
                            style={'answer' : '#ffffff'}
                        ).values()
                    )

                    output_folder = f'./output/{selection[0]["album_title"]}/'

                    # Query Spotify for the album trackslist.
                    album_query_response = requests.get(
                        f'https://api.spotify.com/v1/albums/'
                        f'{selection[0]["id"]}/tracks',
                        headers=authorization_header
                    ).json()

                    # Parse relevant metadata per track.
                    tracks = [
                        {
                            'title' : track['name'],
                            'track_number' : track['track_number'],
                            'year' : selection[0]['year'],
                            'album_title' : selection[0]['album_title'],
                            'total_tracks' : selection[0]['total_tracks'], 
                            'image_link' : selection[0]['image_link'],
                            'artist' : selection[0]['artist'],
                            'query' : query,
                        }
                        for track in album_query_response['items']
                    ]

                    selection = tracks

                except KeyboardInterrupt:
                    print('Search cancelled.')

            # Catch user cancellation.
            case _:
                pass

        # Track progress of downloading selected song(s).
        if selection:
            with alive_bar(
                enrich_print=False,
                unit=' songs',
                calibrate=1
            ) as progress_bar:
                # Iterate through selected tracks. 
                for entry in selection:
                    entry['output_folder'] = output_folder

                    progress_bar.title(
                        f'Downloading \'{entry["title"]}\' by '
                        f'\'{entry["artist"]}\':'
                    )

                    download_song(entry, downscale_art)

                    progress_bar()

        continue_session: bool = bool(
            prompt(
                {
                    'type' : 'confirm',
                    'message' : 'Continue session?:',
                    'qmark' : '',
                    'amark' : '',
                },
                raise_keyboard_interrupt=False,
                style={'answer' : '#ffffff'}
            )[0]
        )

        if not continue_session:
            break
