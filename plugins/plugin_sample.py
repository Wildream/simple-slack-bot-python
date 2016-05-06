class Plugin(object):
    '''
    This is a sample plugin for SimpleSlackBot.

    '''

    def __init__(self):
        self.commands = {
            '^!hello': self.hello_handler,
        }

    def hello_handler(self, msg, user, chan):
        return 'Hello World!', chan
