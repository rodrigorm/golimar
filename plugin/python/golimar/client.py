import golimar.ui.vimui
import Skype4Py

class Client:
    def __init__(self):
        self.skype = Skype4Py.Skype(Transport='dbus', Events=self)
        self.ui = golimar.ui.vimui.Ui(self.skype)

    def open(self):
        self.ui.open()

    def send(self):
        self.chat.SendMessage(self.ui.composeMessage())
        self.ui.composeClean()

    def chatWith(self, username):
        self.setChat(self.skype.CreateChatWith(username))

    def searchChat(self, chatname):
        for chat in self.skype.Chats:
            if chat.Topic == chatname:
                self.setChat(chat)
                return

    def setChat(self, chat):
        self.chat = chat
        self.ui.setChat(self.chat)

    def render(self):
        self.ui.render()

    def openSelectedFriend(self):
        self.setChat(self.skype.CreateChatWith(self.ui.selectedFriend().Handle))

    def openSelectedChat(self):
        self.setChat(self.ui.selectedChat())
