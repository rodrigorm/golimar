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

        self.friends = FriendsWindow(self, 'vertical belowright new')
        self.friends.create()

        vim.command('vertical resize 40')

        self.chats = ChatsWindow(self, 'belowright new')
        self.chats.create()

        vim.command('resize +5')

        self.messages.focus()
        self.compose = ComposeWindow(self, 'rightbelow new')
        self.compose.create()

        vim.command('resize 5')

        self.is_open = True
        self.update()
        # except Exception as e:
        #     self.is_open = False
        #     raise e

    def composeMessage(self):
        return self.compose.message()

    def composeClean(self):
        self.compose.clean()

    def setChat(self, chat):
        self.messages.setChat(chat)
        if self.has_focus():
            self.messages.markAsSeen()
        self.compose.clean()
        self.compose.focus()
        self.update()

    def render(self):
        self.friends.update()
        self.chats.update()
        self.messages.update()

    def bind(self):
        self.skype.RegisterEventHandler('MessageStatus', self.MessageStatus)
        self.skype.RegisterEventHandler('UserStatus', self.UserStatus)
        self.skype.RegisterEventHandler('ConnectionStatus', self.UserStatus)

    def unbind(self):
        self.skype.UnregisterEventHandler('MessageStatus', self.MessageStatus)
        self.skype.UnregisterEventHandler('UserStatus', self.UserStatus)
        self.skype.UnregisterEventHandler('ConnectionStatus', self.UserStatus)

    def MessageStatus(self, message, status):
        self.update()

    def UserStatus(self, status):
        self.update()

    def update(self):
        self.unbind()
        self.render()
        if self.has_focus():
            self.messages.markAsSeen()
        self.bind()

    def has_focus(self):
        return self.is_open and vim.eval('tabpagenr()') == self.tabnr

    def selectedFriend(self):
        return self.friends.selected()

    def selectedChat(self):
        return self.chats.selected()

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
        if  self.buffer_empty():
            return

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

    def get_line(self):
        return int(self._return_focus(self.__curry(self._get_line), True))

    def _get_line(self):
        self.focus()
        return vim.current.range.start

    def focus(self):
        vim.command(str(self.winnr()) + "wincmd w")

    def winnr(self):
        return int(vim.eval("bufwinnr('" + self.name + "')"))

    def _return_focus(self, callback, flag = True):
        if flag:
            return self.__return_focus(callback)
        else:
            return callback()

    def __return_focus(self, callback):
        prev_win = vim.eval('winnr()')
        result = callback()
        vim.command('%swincmd W' % prev_win)
        return result

    def __curry(self, callback, *args):
        return functools.partial(callback, *args)

class FriendsWindow(Window):
    name = "Friends"

    def on_create(self):
        self.update()
        vim.command('nnoremap <buffer> <cr> :python golimar.openSelectedFriend()<cr>')
        vim.command('set filetype=golimarfriends')

    def update(self):
        self.clean()

        for user in self.ui.skype.Friends:
            self.write('(' + user.OnlineStatus + ') ' + user.Handle)

        self.set_line(0)

    def selected(self):
        return self.ui.skype.Friends[self.get_line()]

class ChatsWindow(Window):
    name = "Chats"

    def on_create(self):
        self.update()
        vim.command('nnoremap <buffer> <cr> :python golimar.openSelectedChat()<cr>')

    def update(self):
        self.clean()

        for chat in self.ui.skype.RecentChats:
            self.write(self._topic(chat) + self._unseen(chat))

        self.set_line(0)

    def _topic(self, chat):
        if chat.Topic == '':
            for member in chat.Members:
                if member.Handle != self.ui.skype.CurrentUser.Handle:
                    return member.Handle
        else:
            return chat.Topic

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

    def selected(self):
        return self.ui.skype.RecentChats[self.get_line()]

class MessagesWindow(Window):
    name = 'Skype'

    def on_create(self):
        self.chat = None

    def setChat(self, chat):
        self.chat = chat
        self.update()

    def update(self):
        self.clean()

        if self.chat == None:
            return

        for message in self.chat.RecentMessages:
            self.write('[' + str(message.Datetime) + '] (' + message.FromHandle + ') ' + message.Body)

    def markAsSeen(self):
        if self.chat == None:
            return

        for message in self.chat.RecentMessages:
            if message.Status == 'RECEIVED':
                message.MarkAsSeen()

class ComposeWindow(Window):
    name = 'Compose'
    buftype = 'acwrite'

    def message(self):
        return '\n'.join(self.buffer)
