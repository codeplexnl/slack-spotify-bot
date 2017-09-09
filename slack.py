from slackclient import SlackClient


class Slack:
    def __init__(self, token):
        self.client = SlackClient(token)
    
    def send_message(self, message, channel):
        self.client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
    
    def read_message(self):
        events = self.client.rtm_read()
        for event in events:
            if 'channel' in event and 'text' in event and 'user' in event:
                return event['channel'], event['user'], event['text']
        return None, None, None
        
    def connect(self):
        return self.client.rtm_connect()