import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

class Spotify:
    
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET, proxies=None)
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
    def get_tracks(self):
        username = config.SPOTIFY_PLAYLIST.split(':')[2]
        playlist_id = config.SPOTIFY_PLAYLIST.split(':')[4]

        offset = 0
        limit = 100
        getTracks = True
        tracks = []

        while(getTracks):
            results = self.spotify.user_playlist_tracks(username, playlist_id, limit=limit, offset=offset, fields="items(track(name,uri)),limit,total,next")
            tracks += results["items"]
            offset += limit
    
            if(results["next"] == None):
                getTracks = False
        return tracks
    
    @staticmethod
    def get_playlist():
        username = config.SPOTIFY_PLAYLIST.split(':')[2]
        playlist_id = config.SPOTIFY_PLAYLIST.split(':')[4]
        return "https://open.spotify.com/user/%s/playlist/%s" % (username, playlist_id)
    
    