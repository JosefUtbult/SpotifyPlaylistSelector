import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import request
import time
import random

SPOTIFY_CLIENT_REDIRECT_URI = "https://localhost:2001/callback"
TIME_RATE = 8 # Volume percentage / seconds

class SpotifyHandler:
    # Generates a spotify client that either runs in the browser or headless
    def __init__(self, logger, client_id, client_secret, headless=False):
        self.logger = logger

        logger.info(f"{client_id} {client_secret}")

        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyOAuth(
                scope="user-read-playback-state,user-modify-playback-state", 
                open_browser=not headless, 
                client_id=client_id, 
                client_secret=client_secret, 
                redirect_uri=SPOTIFY_CLIENT_REDIRECT_URI
            )
        )

    # Pulls the name of a playlist by its uri
    def get_playlist_name(self, playlist_uri):
        return self.sp.playlist(playlist_uri)['name']

    # Pulls all tracks from a playlist and extracts their 
    def get_tracks_in_playlist(self, playlist_uri):
        offset = 0
        playlist = []

        while True:
            response = self.sp.playlist_items(playlist_uri,
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
    def play_playlist(self, playlist_uri, shuffle=False):
        playlist = self.get_tracks_in_playlist(playlist_uri)

        # Just shuffle the playlist manually to get a shuffle
        if shuffle:
            random.shuffle(playlist)

        try:
            # Check if something already is playing
            if not self.sp.current_playback():
                self.logger.warning("No active device running")
                return False

            elif self.sp.current_playback()['is_playing']:
                original_volume = self.sp.current_playback()['device']['volume_percent']

                # Get the current volume. Breaks when its all the way down
                start_time = time.time()
                while current_volume := self.sp.current_playback()['device']['volume_percent'] > 0:
                    # Time since start of fade out
                    time_offset = time.time() - start_time
                    # Set the volume to either the original volume minus a factor of the time since
                    # start and the TIME_RATE constant, or to zero
                    self.sp.volume(max(original_volume - int(time_offset * TIME_RATE), 0))

                # Starts a new playlist
                self.sp.start_playback(uris=playlist)
                
                # Get the current volume again. Breaks when its at the same level as before
                start_time = time.time()
                while current_volume := self.sp.current_playback()['device']['volume_percent'] < original_volume:
                    time_offset = time.time() - start_time
                    # Set the volume to either a factor of the time since start and the TIME_RATE or 
                    # to the original volume
                    self.sp.volume(min(int(time_offset * TIME_RATE), original_volume))

            # If nothing is playing, just start the new playlist
            else:
                self.sp.start_playback(uris=playlist)
                
        except Exception as e:
            self.logger.error(f"Spotipy gave an exception: {e}")
            return False

        return True
