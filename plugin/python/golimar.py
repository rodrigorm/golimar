import os
import sys
import inspect

directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(directory)
sys.path.append(directory + '/skype4py')

import golimar.client

class Golimar:
    """Acts as a facade layer to the skype client.
    """
    def __init__(self):
        self.client = golimar.client.Client()

    def open(self):
        self.client.open()

    def send(self):
        self.client.send()

    def chatWith(self, username):
        self.client.chatWith(username)

    def searchChat(self, chatname):
        self.client.searchChat(chatname)
