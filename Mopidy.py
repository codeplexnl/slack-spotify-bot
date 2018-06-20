# -*- coding: utf-8 -*-
import subprocess
import datetime
import random
import requests

import config

USERS = {}
VOLUME = {}


class Mopidy:
    @staticmethod
    def set_volume(volumePercent):
        Mopidy.execute_command("volume {}".format(volumePercent))

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
    def execute_command(mopidyCommand):
        try:
            return subprocess.check_output("mpc {}".format(mopidyCommand), shell=True)
        except:
            print(mopidyCommand)

    @staticmethod
    def get_lyrics(artist=None, title=None):
        if artist is None and title is None:
            artist, title = Mopidy.get_current_song().split('-', 1)
        url = 'https://makeitpersonal.co/lyrics'
        data = {'artist': artist, 'title': title}
        r = requests.get(url, data)
        return r.content

    @staticmethod
    def get_current_song():
        output = Mopidy.execute_command("status")
        output = output.split("\n")
        return output[0]

    @staticmethod
    def get_queue(num):
        output = Mopidy.execute_command("playlist")
        output = output.split("\n")
        return output[1:num + 1]
    
    @staticmethod
    def next_song(user):
        if Mopidy.check_user(user):
            Mopidy.execute_command("next")
            USERS[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.WAIT_TIME)
        else:
            return "Already skipped in the last {} minutes. Try again later".format(config.WAIT_TIME)
            
    @staticmethod
    def add_track(track_uri):
        Mopidy.execute_command("add %s" % track_uri)
    
    @staticmethod
    def clear_queue():
        Mopidy.execute_command("clear")
    
    @staticmethod
    def enable_consume():
        Mopidy.execute_command("consume on")
    
    @staticmethod
    def shuffle():
        Mopidy.execute_command("shuffle")
            
    @staticmethod
    def play():
        Mopidy.execute_command("play")
        return "Starting playback."
        
    @staticmethod
    def pause():
        Mopidy.execute_command("pause")
        return "Stopping playback."
    
    
    @staticmethod
    def print_queue():
        queue = Mopidy.get_queue(config.QUEUE_LENGTH)
        numbers = "First {} numbers in the queue".format(len(queue))

        for idx, number in enumerate(queue):
            numbers += "\n{}. {}".format(str(idx + 1), number)
        return numbers
    
    @staticmethod
    def volume_up(user):
        if Mopidy.check_volume(user):
            VOLUME[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.VOLUME_TIME)
            config.PLAYING_MAX = True
            Mopidy.set_volume(100)
            return "Volume maxed"
        else:
            return "Already used volume up in the last {} minutes. Try again later".format(config.VOLUME_TIME)
    
    @staticmethod
    def delete_from_queue(user, params):
        error = "Please choose a number between 1 - {}".format(str(config.QUEUE_LENGTH))
        if Mopidy.check_user(user):
            try:
                params = int(params)
                if params is not None and int(config.QUEUE_LENGTH) >= params >= 1:
                    queue = Mopidy.get_queue(config.QUEUE_LENGTH)
                    song_info = queue[params - 1]
                    Mopidy.execute_command("del {}".format(params + 1))
                    USERS[user] = datetime.datetime.now() + datetime.timedelta(minutes=config.WAIT_TIME)
                    return "Removed {} from the queue".format(song_info)
                else:
                    return error
            except ValueError:
                return error
        else:
            return "Already skipped or deleted a song from the queue in the last {} minutes. " \
                   "Try again later".format(config.WAIT_TIME)

   
