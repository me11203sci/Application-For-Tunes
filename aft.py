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
from dotenv import dotenv_values, find_dotenv
import requests
import sys
from typing import Final


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
    authorization_response: dict = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type' : 'client_credentials',
            'client_id' : credentials['spotify_id'],
            'client_secret' : credentials['spotify_secret']
        },
        headers={'Content-Type' : 'application/x-www-form-urlencoded'}
    ).json()

    authorization_header: dict = {}
    # Create authorization header.
    try:
        authorization_token: str = authorization_response['access_token']

        authorization_header = {
            'Authorization' : f'Bearer {authorization_token}'
        }
    except KeyError:
        print(
            'Authorization token request failed, perhaps credentials are '
            'invalid?'
        )
