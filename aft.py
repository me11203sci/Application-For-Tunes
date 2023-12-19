'''
Application For Tunes - Python Implementation

Author(s): Melesio Albavera <ma6hv@mst.edu>
Created: 18 December 2023
Updated: 18 December 2023
Version: 0.0
Description:
    TODO
Notes:
    TODO
'''
from dotenv import dotenv_values, find_dotenv # type: ignore
from InquirerPy import prompt # type: ignore
from InquirerPy.validator import EmptyInputValidator # type: ignore
import requests
import sys
from typing import Final


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


if __name__ == '__main__':
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

    question: list[dict] = [
    ]

    # Main loop.
    while True:
        query: str = str(
            prompt(
                {
                    'type' : 'input',
                    'message' : '\nEnter search query:',
                    'qmark' : '',
                    'amark' : '',
                    'validate' : EmptyInputValidator(),
                },
                style={'answer' : '#ffffff'}
            )[0]
        )

        search_mode: str = str(
            prompt(
                {
                    'type' : 'list',
                    'message' : 'Search by:',
                    'choices' : ['Song'],
                    'qmark' : '',
                    'amark' : '',
                    'pointer' : '>',
                },
                style={'answer' : '#ffffff'}
            )[0]
        )

        match search_mode:
            case 'Song':
                # Query Spotify.
                song_search_response: dict = requests.get(
                    f'https://api.spotify.com/v1/search?q={query}&type=track&'
                    f'limit=50',
                    headers=authorization_header
                ).json()

                # Parse relevant metadata per track.
                tracks: list[dict] = [
                    {
                        'title' : track['name'],
                        'track_number' : track['track_number'],
                        'year' : track['album']['release_date'].split('-')[0],
                        'album_title' : track['album']['name'],
                        'total_tracks' : track['album']['total_tracks'],
                        'image_link' : track['album']['images'][0]['url'],
                        'artist' : track['artists'][0]['name'],
                        'duration' :
                            f'{track["duration_ms"] // 60000}:'
                            f'{track["duration_ms"] // 1000 % 60:02}',
                        'isrc' : track['external_ids']['isrc']
                    }
                    for track in song_search_response['tracks']['items']
                ]

                formated_choices: list = format_song_results(tracks)

                selection: dict = prompt(
                    {
                        'type' : 'list',
                        'message' :
                            f'Top 50 results:\n'
                            f'  ┌{"─" * 32}┬{"─" * 32}┬{"─" * 32}┬{"─" * 12}┬'
                            f'{"─" * 8}┐\n  │{"Title":<32}│{"Album":<32}│'
                            f'{"Artist":<32}│{"ISRC":<12}│Duration│\n  ├'
                            f'{"─" * 32}┼{"─" * 32}┼{"─" * 32}┼{"─" * 12}┼'
                            f'{"─" * 8}┤',
                        'choices' : formated_choices,
                        'qmark' : '',
                        'amark' : '',
                        'pointer' : '>',
                        'show_cursor' : False,
                        'transformer' : 
                            lambda result:
                                f'\n  {result}\n  └{"─" * 32}┴{"─" * 32}┴'
                                f'{"─" * 32}┴{"─" * 12}┴{"─" * 8}┘',
                        'filter' :
                            lambda result:
                                tracks[formated_choices.index(result)],
                    },
                    style={'answer' : '#ffffff'}
                )

        continue_session: bool = bool(
            prompt(
                {
                    'type' : 'confirm',
                    'message' : 'Search again?:',
                    'qmark' : '',
                    'amark' : '',
                },
                style={'answer' : '#ffffff'}
            )[0]
        )

        if not continue_session:
            break
