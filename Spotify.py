import subprocess
import datetime

import config

COMMAND_PREFIX = "!"
COMMAND_PLAY = ['play', 'start']
COMMAND_PAUSE = ['pause', 'stop']
COMMAND_NEXT = ['next', 'skip']
COMMAND_INFO = ['info', 'current', 'song']
COMMAND_HELP = ['help']
COMMAND_PLAYLIST = ['playlist', 'pl']
COMMAND_VOLUME_UP = ['volumeup', 'volup', 'vu']

USERS = {}
VOLUME = {}

class Spotify:
    
    @staticmethod
    def execute_command(command):
        return subprocess.check_output([" ".join([config.SPOTIFY_EXE, command])], stderr=subprocess.PIPE, shell=True)
        
    @staticmethod
    def clean_output(output):
        output = output.decode("utf-8").replace("\n", ":").split(":")
        return list(map(str.strip, output))
    
    @staticmethod
    def check_user(user):
        if user not in USERS or (user in USERS and USERS[user] < datetime.datetime.now()):
            return True
        return False
    
    @staticmethod
    def check_volume(user):
        if user not in VOLUME or (user in VOLUME and VOLUME[user] < datetime.datetime.now()):
            return True
        return False
    
    @staticmethod    
    def volume_down():
        if config.PLAYING_MAX:
            config.PLAYING_MAX = False
            Spotify.execute_command("vol 80")
        
    @staticmethod
    def handle_message(channel, user, message):
        if config.SLACK_CHANNEL == channel:
            if not message.startswith(COMMAND_PREFIX):
                return None
            
            command = message[len(COMMAND_PREFIX):]
            
            if command in COMMAND_PLAY:
                Spotify.execute_command(COMMAND_PLAY[0])
                return "Starting playback."
                
            if command in COMMAND_PAUSE:
                Spotify.execute_command(COMMAND_PAUSE[0])
                return "Stopping playback."
                                
            if command in COMMAND_NEXT:
                if Spotify.check_user(user): 
                    Spotify.execute_command(COMMAND_NEXT[0])
                    USERS[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.WAIT_TIME)
                else:
                    return "Already skipped in the last {} minutes. Try again later".format(config.WAIT_TIME)
            
            if command in COMMAND_INFO:
                return Spotify.get_current_song()
            
            if command in COMMAND_PLAYLIST:
                return config.SPOTIFY_PLAYLIST
            
            if command in COMMAND_HELP:
                  return "==========================================================\n" + \
                          "!help Shows a list of commands that can be used\n" + \
                          "!play Starts playback of Spotify\n" + \
                          "!pause Stops playback of Spotify\n" + \
                          "!next Skips to next song (Only allowed once per 15 min)\n" + \
                          "!info Shows the current playing song\n" + \
                          "!playlist Gives the link to the spotify playlist\n" + \
                          "!volumeup Plays the current song at max volume\n" + \
                          "==========================================================\n"
                          
            if command in COMMAND_VOLUME_UP and not config.PLAYING_MAX:
                if Spotify.check_volume(user):
                    VOLUME[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.VOLUME_TIME)
                    config.PLAYING_MAX = True
                    Spotify.execute_command("vol 100")
                    return "Volume maxed"
                else:
                    return "Already used volume up in the last {} minutes. Try again later".format(config.VOLUME_TIME)
                
        return None
        
    @staticmethod
    def get_current_song():
        result = Spotify.execute_command(COMMAND_INFO[0])
        output = Spotify.clean_output(result)
        return " - ".join([output[2], output[4]])