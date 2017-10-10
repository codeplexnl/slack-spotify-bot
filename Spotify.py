import subprocess
import datetime
import random

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

USERS = {}
VOLUME = {}


class Spotify:
    @staticmethod
    def set_volume(volumePercent):
        Spotify.execute_command("volume {}".format(volumePercent))

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
    def execute_command(spotifyCommand):
        return subprocess.check_output("mpc {}".format(spotifyCommand), shell=True)

    @staticmethod
    def handle_message(channel, user, message):
        if config.SLACK_CHANNEL == channel:
            if not message.startswith(COMMAND_PREFIX):
                return None

            command, params = Spotify.get_command_and_params(message[len(COMMAND_PREFIX):])

            if command in COMMAND_QUEUE:
                queue = Spotify.get_queue(config.QUEUE_LENGTH)
                numbers = "First {} numbers in the queue".format(len(queue))

                for idx, number in enumerate(queue):
                    numbers += "\n{}. {}".format(str(idx+1), number)
                return numbers

            if command in COMMAND_PLAY:
                Spotify.execute_command("play")
                return "Starting playback."

            if command in COMMAND_PAUSE:
                Spotify.execute_command("pause")
                return "Stopping playback."

            if command in COMMAND_NEXT:
                if Spotify.check_user(user):
                    Spotify.execute_command("next")
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
                       "!queue gets the next songs in the queue\n" + \
                       "!delete <pos> Deletes a song from the queue (Only allowed once per 15 min, shared with next)\n" + \
                       "!random <a> <b> Return a random integer N such that a <= N <= b. )\n" + \
                       "==========================================================\n"

            if command in COMMAND_VOLUME_UP and not config.PLAYING_MAX:
                if Spotify.check_volume(user):
                    VOLUME[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.VOLUME_TIME)
                    config.PLAYING_MAX = True
                    Spotify.set_volume(100)
                    return "Volume maxed"
                else:
                    return "Already used volume up in the last {} minutes. Try again later".format(config.VOLUME_TIME)

            if command in COMMAND_DELETE:
                if params is not None:
                    try:
                        params = int(params)
                        if 5 > params > 1 and Spotify.check_user(user):
                            Spotify.execute_command("del {}".format(params))
                            USERS[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.WAIT_TIME)
                        else:
                            return "Already skipped or deleted a song from the queue in the last {} minutes. " \
                                   "Try again later".format(config.WAIT_TIME)
                    except ValueError:
                        return "Please choose a number between 1 - {}".format(str(config.QUEUE_LENGTH))

            if command in COMMAND_RANDOM:
                if params is not None:
                    param_first, param_second = params.split(None, 1)
                    try:
                        param_first = int(param_first)

                        if param_second.__eq__(''):
                            return random.randint(1, int(param_first))
                        elif param_second.isdigit():
                            return random.randint(param_first, int(param_second))
                        else:
                            return random.randint(1, 10)
                    except ValueError:
                        return random.randint(1, 10)

        return None

    @staticmethod
    def get_current_song():
        output = Spotify.execute_command("status")
        output = output.split("\n")
        return output[0]

    @staticmethod
    def get_queue(num):
        output = Spotify.execute_command("playlist")
        output = output.split("\n")
        return output[1:num + 1]

    @staticmethod
    def get_command_and_params(message):
        if len(message.split()) > 1:
            command, params = message.split(None, 1)
            return command, params

        return message, None
