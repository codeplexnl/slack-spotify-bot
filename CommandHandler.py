from Mopidy import Mopidy
import config

COMMAND_PREFIX = "!"
COMMAND_PLAY = ['play', 'start']
COMMAND_PAUSE = ['pause', 'stop']
COMMAND_NEXT = ['next', 'skip']
COMMAND_INFO = ['info', 'current', 'song']
COMMAND_HELP = ['help']
COMMAND_PLAYLIST = ['playlist', 'pl']
COMMAND_QUEUE = ['queue', 'q']
COMMAND_VOLUME_UP = ['volumeup', 'volup', 'vu']
COMMAND_DELETE = ['delete', 'del', 'd']
COMMAND_RANDOM = ['random', 'rand', 'roll']
COMMAND_LYRICS = ['lyrics', 'lyr']

class CommandHandler:
    @staticmethod
    def get_command_and_params(message):
        if len(message.split()) > 1:
            command, params = message.split(None, 1)
            return command, params

        return message, None
        
    @staticmethod
    def handle_message(channel, user, message):
        if config.SLACK_CHANNEL == channel:
            if not message.startswith(COMMAND_PREFIX):
                return None

            command, params = CommandHandler.get_command_and_params(message[len(COMMAND_PREFIX):])

# Start mopidy commands
            if command in COMMAND_QUEUE:
                return Mopidy.print_queue()

            if command in COMMAND_PLAY:
                return Mopidy.play()

            if command in COMMAND_PAUSE:
                return Mopidy.pause()
            if command in COMMAND_NEXT:
                return Mopidy.next_song(user)

            if command in COMMAND_INFO:
                return Mopidy.get_current_song()
                
            if command in COMMAND_VOLUME_UP and not config.PLAYING_MAX:
               return Mopidy.volume_up(user)

            if command in COMMAND_DELETE:
                return Mopidy.delete_from_queue(user, params)
# End mopidy commands

            if command in COMMAND_PLAYLIST:
                return Spotify.get_playlist()

            if command in COMMAND_HELP:
                return "==========================================================\n" + \
                       "!help Shows a list of commands that can be used\n" + \
                       "!play Starts playback of Mopidy\n" + \
                       "!pause Stops playback of Mopidy\n" + \
                       "!next Skips to next song (Only allowed once per 15 min)\n" + \
                       "!info Shows the current playing song\n" + \
                       "!playlist Gives the link to the spotify playlist\n" + \
                       "!volumeup Plays the current song at max volume\n" + \
                       "!queue gets the next songs in the queue\n" + \
                       "!delete <pos> Deletes a song from the queue (Only allowed once per 15 min, shared with next)\n" + \
                       "!random <a> <b> Return a random integer N such that a <= N <= b. )\n" + \
                       "!lyrics (<artist> - <title>) Shows the lyrics of current song or given song\n" + \
                       "==========================================================\n"

            
            if command in COMMAND_RANDOM:
                default = random.randint(1, 10)
                if params is not None:
                    try:
                        param_first, param_second = params.split(None, 1)
                        param_first = int(param_first)

                        if param_second.__eq__(''):
                            return random.randint(1, int(param_first))
                        elif param_second.isdigit():
                            return random.randint(param_first, int(param_second))
                        else:
                            return default
                    except ValueError:
                        return default
                else:
                    return default

            if command in COMMAND_LYRICS:
                if params is not None:
                    try:
                        artist, title = params.split('-', 1)
                        return Mopidy.get_lyrics(artist, title)
                    except ValueError:
                        return 'Format your song as <artist> - <title>'
                else:
                    return Mopidy.get_lyrics()

        return None