import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import request
import time
import random
import logging

SPOTIFY_CLIENT_REDIRECT_URI = "https://localhost:2001/callback"
TIME_RATE = 30 # Volume percentage / seconds

class SpotifyHandler:

    # Initializes the Spotify handler. If no id or secret is given, it will ignore creating a static client
    # and instead presume this is done each call    
    def __init__(self, logger:logging.Logger, client_id:str|None=None, client_secret:str|None=None, headless:bool=False) -> None:
        self.logger = logger

        if client_id and client_secret:
            self.sp = self.create_spotipy_handler(client_secret, client_id, headless)
        else:
            self.sp = None

            logger.info(self.sp)

    # Generates a spotify client that either runs in the browser or headless
    def create_spotipy_handler(self, client_id:str, client_secret:str, headless:bool) -> spotipy.Spotify:  
        sp = spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope="user-read-playback-state,user-modify-playback-state", 
                    open_browser=not headless, 
                    client_id=client_id, 
                    client_secret=client_secret, 
                    redirect_uri=SPOTIFY_CLIENT_REDIRECT_URI
                )
            )

        sp.me()
        return sp

    # Pulls the name of a playlist by its uri
    def get_playlist_name(self, playlist_uri:str, client_id=None, client_secret=None, headless:bool=False) -> str:
        if not self.sp and client_secret and client_id:
            return self.create_spotipy_handler(client_id, client_secret, headless).sp.playlist(playlist_uri)['name']
        elif self.sp:
            print(self.sp)
            name = self.sp.playlist(playlist_uri)['name']
            return name
        else:
            self.logger.error('"get_playlist_name" called without sp or client info')
            return ""

    # Pulls all tracks from a playlist and extracts their 
    def get_tracks_in_playlist(self, playlist_uri:str, client_id=None, client_secret=None, headless:bool=False):
        if not self.sp and client_secret and client_id:
            sp = self.create_spotipy_handler(client_id, client_secret, headless)
        elif self.sp:
            sp = self.sp
        else:
            self.logger.error('"get_tracks_in_playlist" called without sp or client info')
            return []

        offset = 0
        playlist = []

        while True:
            response = sp.playlist_items(playlist_uri,
                offset=offset,
                fields='items.track.id,total',
                additional_types=['track']
            )

            if len(response['items']) == 0:
                break

            playlist += [f"spotify:track:{track['track']['id']}" for track in response['items']]
            offset = offset + len(response['items'])

        return playlist

    # Takes a playlist uri and tries to play it. If something already is playing it will fade it out,
    # switch playlist and fade in again
    def play_playlist(self, playlist_uri, shuffle=False, client_id=None, client_secret=None, headless:bool=False):
        if not self.sp and client_secret and client_id:
            sp = self.create_spotipy_handler(client_id, client_secret, headless)
        elif self.sp:
            sp = self.sp
        else:
            self.logger.error('"play_playlist" called without sp or client info')
            return False

        playlist = self.get_tracks_in_playlist(playlist_uri, client_id, client_secret, headless)

        # Just shuffle the playlist manually to get a shuffle
        if shuffle:
            random.shuffle(playlist)

        try:
            # Check if something already is playing
            if not sp.current_playback():
                self.logger.warning("No active device running")
                return False

            elif sp.current_playback()['is_playing']:
                original_volume = sp.current_playback()['device']['volume_percent']

                # Get the current volume. Breaks when its all the way down
                start_time = time.time()
                while current_volume := sp.current_playback()['device']['volume_percent'] > 0:
                    # Time since start of fade out
                    time_offset = time.time() - start_time
                    # Set the volume to either the original volume minus a factor of the time since
                    # start and the TIME_RATE constant, or to zero
                    sp.volume(max(original_volume - int(time_offset * TIME_RATE), 0))

                # Starts a new playlist
                sp.start_playback(uris=playlist)
                
                # Get the current volume again. Breaks when its at the same level as before
                start_time = time.time()
                while current_volume := sp.current_playback()['device']['volume_percent'] < original_volume:
                    time_offset = time.time() - start_time
                    # Set the volume to either a factor of the time since start and the TIME_RATE or 
                    # to the original volume
                    sp.volume(min(int(time_offset * TIME_RATE), original_volume))

            # If nothing is playing, just start the new playlist
            else:
                sp.start_playback(uris=playlist)
                
        except Exception as e:
            self.logger.error(f"Spotipy gave an exception: {e}")
            return False

        return True

    # Pause playback, regardless of which playlist is running at the moment
    def pause(self, client_id=None, client_secret=None, headless:bool=False):
        try:
            if not self.sp and client_secret and client_id:
                self.create_spotipy_handler(client_id, client_secret, headless).pause_playback()
            elif self.sp:
                return self.sp.pause_playback()
            else:
                self.logger.error('"pause" called without sp or client info')
        except Exception as e:
            self.logger.error(f"Spotipy gave an exception: {e}")
            return False

        return True