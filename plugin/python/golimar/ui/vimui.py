import functools

import vim

class Ui:
    def __init__(self, skype):
        self.skype = skype
        self.is_open = False
        self.tabnr = None

    def open(self):
        if self.is_open:
            return

        # try:
        self.messages = MessagesWindow(self, 'tabnew')
        self.messages.create()

        self.tabnr = vim.eval('tabpagenr()')

        self.contacts = ContactsWindow(self, 'vertical belowright new')
        self.contacts.create()

        self.chats = ChatsWindow(self, 'belowright new')
        self.chats.create()

        self.messages.focus()
        self.compose = ComposeWindow(self, 'rightbelow new')
        self.compose.create()

        self.is_open = True
        # except Exception as e:
        #     self.is_open = False
        #     raise e

    def composeMessage(self):
        return self.compose.message()

    def composeClean(self):
        self.compose.clean()

    def setChat(self, chat):
        self.messages.setChat(chat)
        self.compose.clean()
        self.compose.focus()

    def render(self):
        self.contacts.update()
        self.chats.update()
        self.messages.update()

class Window:
    name = 'WINDOW'
    open_cmd = 'new'
    buftype = 'nofile'

    def __init__(self, ui, open_cmd):
        self.buffer = None
        self.ui = ui
        self.open_cmd = open_cmd
        self.is_open = False

    def create(self):
        """ create window """
        vim.command('silent ' + self.open_cmd + ' ' + self.name)
        vim.command('setlocal buftype=' + self.buftype + ' modifiable winfixheight winfixwidth nobackup noswapfile')
        self.buffer = vim.current.buffer
        self.is_open = True
        self.on_create()

    def on_create(self):
        """ callback """

    def clean(self):
        self.buffer[:] = []

    def write(self, msg, return_focus = True, after = 'normal G'):
        self._return_focus(self.__curry(self._write, msg, after), return_focus)

    def _write(self, msg, after = 'normal G'):
        if not self.is_open:
            self.create()
        if self.buffer_empty():
            self.buffer[:] = str(msg.encode('utf-8')).split('\n')
        else:
            self.buffer.append(str(msg.encode('utf-8')).split('\n'))
        self.command(after)

    def buffer_empty(self):
        if len(self.buffer) == 1 \
                and len(self.buffer[0]) == 0:
            return True
        else:
            return False

    def command(self, cmd):
        """ go to my window & execute command """
        winnr = self.getwinnr()
        if winnr != int(vim.eval("winnr()")):
            vim.command(str(winnr) + 'wincmd w')
        vim.command(cmd)

    def getwinnr(self):
        return int(vim.eval("bufwinnr('"+self.name+"')"))

    def set_line(self, lineno, return_focus = True):
        self._return_focus(self.__curry(self._set_line, lineno), return_focus)

    def _set_line(self, lineno):
        self.focus()
        vim.command("normal %sgg" % str(lineno))

    def focus(self):
        vim.command(str(self.winnr()) + "wincmd w")

    def winnr(self):
        return int(vim.eval("bufwinnr('" + self.name + "')"))

    def _return_focus(self, callback, flag = True):
        if flag:
            self.__return_focus(callback)
        else:
            callback()

    def __return_focus(self, callback):
        prev_win = vim.eval('winnr()')
        callback()
        vim.command('%swincmd W' % prev_win)

    def __curry(self, callback, *args):
        return functools.partial(callback, *args)

class ContactsWindow(Window):
    name = "Contacts"

    def on_create(self):
        self.update()
        self.set_line(0)
        self.ui.skype.RegisterEventHandler('UserStatus', self.UserStatus)
        self.ui.skype.RegisterEventHandler('ConnectionStatus', self.UserStatus)

    def UserStatus(self, status):
        self.update()
        self.set_line(0)

    def update(self):
        self.clean()

        for user in self.ui.skype.Friends:
            self.write('(' + user.OnlineStatus + ') ' + user.Handle)

class ChatsWindow(Window):
    name = "Chats"

    def on_create(self):
        self.update()
        self.set_line(0)
        self.ui.skype.RegisterEventHandler('MessageStatus', self.MessageStatus)

    def MessageStatus(self, message, status):
        self.update()
        self.set_line(0)

    def update(self):
        self.clean()

        for chat in self.ui.skype.RecentChats:
            if chat.Topic == '':
                self.write(chat.Members[0].Handle + self._unseen(chat))
            else:
                self.write(chat.Topic + self._unseen(chat))

    def _unseen(self, chat):
        count = self.unseenCount(chat)
        if count:
            return ' [' + str(count) + ']'

        return ''

    def unseenCount(self, chat):
        result = 0
        for message in chat.RecentMessages:
            if message.Status == 'RECEIVED':
                result += 1

        return result

class MessagesWindow(Window):
    name = 'Skype'

    def on_create(self):
        self.chat = None
        self.ui.skype.RegisterEventHandler('MessageStatus', self.MessageStatus)

    def setChat(self, chat):
        self.chat = chat
        self.update()

    def MessageStatus(self, message, status):
        self.update()

    def update(self):
        self.clean()

        if self.chat == None:
            return

        for message in self.chat.RecentMessages:
            self.write('(' + message.FromHandle + ') ' + message.Body)
            if message.Status == 'RECEIVED':
                message.MarkAsSeen()

class ComposeWindow(Window):
    name = 'Compose'
    buftype = 'acwrite'

    def message(self):
        return '\n'.join(self.buffer)
