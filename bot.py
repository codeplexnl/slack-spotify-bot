import time

from slack import Slack
from Spotify import Spotify
import config



if __name__ == "__main__":
    slack = Slack(config.SLACK_TOKEN)
    READ_WEBSOCKET_DELAY = 1
    song = None
    Spotify.set_volume(config.VOLUME)
    config.PLAYING_MAX = False
    if slack.connect():
        while True:
            channel, user, message = slack.read_message()
            response = Spotify.handle_message(channel, user, message)
            if response is not None:
                slack.send_message(response, channel)
            
            current_song = Spotify.get_current_song()
            if song != current_song:
                slack.send_message(current_song, config.SLACK_CHANNEL)
                song = current_song
                Spotify.set_volume(config.VOLUME)
                config.PLAYING_MAX = False
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("error connecting")    