
import enum


class Commands(enum.IntEnum):
    Query = 1
    Reset = 2
    Units = 3
    Identify = 4
    Dump = 7

    def __bytes__(self):
        return bytes([self])




class PacketBase:
    def __init__(self,command, **kwargs):
        self.command = command
        self.args = kwargs

    def __getitem__(self,key):
        return self.args[key]

    def get(self,key, default=None):
        return self.args.get(default)


    def __bytes__(self):
        return bytes([self.command]) + self.payload()

    def __str__(self):
        return bytes(self).hex('-',4)

    def payload(self):
        return bytes()

class CommandBase(PacketBase):
    def __init__(self,command,**kwargs):
        super().__init__(command,**kwargs)
        self.count = kwargs.get('count',0)
        self.offset = kwargs.get('offset',0)


class MessageBase(PacketBase):
    def __init__(self,raw : bytes):
        super().__init__(raw[0])
        self.body = raw[1:-1]

    def payload(self):
        return self.body
