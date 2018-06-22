import time

from slack import Slack
from Mopidy import Mopidy
from Spotify import Spotify
from CommandHandler import CommandHandler
import config

if __name__ == "__main__":
    spotify = Spotify()
    Mopidy.clear_queue()
    tracks = spotify.get_tracks()
    for track in tracks:
        Mopidy.add_track(track["track"]["uri"])
    
    Mopidy.enable_consume()
    Mopidy.shuffle()
    Mopidy.play()
    
    slack = Slack(config.SLACK_TOKEN)
    READ_WEBSOCKET_DELAY = 1
    song = None
    Mopidy.set_volume(config.VOLUME)
    config.PLAYING_MAX = False
    if slack.connect():
        while True:
            try:    
                channel, user, message = slack.read_message()
                response = CommandHandler.handle_message(channel, user, message)
                if response is not None:
                    slack.send_message(response, channel)
            
                current_song = Mopidy.get_current_song()
                if song != current_song:
                    slack.send_message(current_song, config.SLACK_CHANNEL)
                    song = current_song
                    Mopidy.set_volume(config.VOLUME)
                    config.PLAYING_MAX = False
                time.sleep(READ_WEBSOCKET_DELAY)
            except:
                if(!slack.connect()):
                    slack = Slack(config.SLACK_TOKEN)
                    slack.connect()
    else:
        print("error connecting")