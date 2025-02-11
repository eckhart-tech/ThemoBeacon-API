from ..bases import CommandBase, Commands, MessageBase
from .conversions import decode_humidity, decode_temperature


class CommandIdentify(CommandBase):
    def __init__(self):
       super().__init__(Commands.Identify)


class CommandQuery(CommandBase):
    def __init__(self):
        super().__init__(Commands.Query)

class MessageQuery(MessageBase):
    def __init__(self, raw):
        super().__init__(raw)
        self.count = int.from_bytes(raw[1:3], byteorder='little')

class CommandDump(CommandBase):
    def __init__(self, offset=0, count=15):
        super().__init__(Commands.Dump, offset=offset, count=count)

    def payload(self):
        return self.offset.to_bytes(4, 'little') + self.count.to_bytes(4, 'little')

class DumpData:
    def __init__(self, n, temp, humidity):
        self.n = n
        self.temperature = temp
        self.humidity = humidity

    def __str__(self):
        return f'index = {self.n} t={self.temperature}, h={self.humidity}'

class MessageDump(MessageBase):
    def __init__(self,raw : bytes):
        super().__init__(raw)
        self.id = raw[0]
        self.count = raw[5]
        self.offset = int.from_bytes(raw[1:5], byteorder='little')

        records=[]
        for n in range(self.count):
            off = 6 + 2 * n
            t = decode_temperature(self.body[off:off + 2])
            off += self.count
            h = decode_humidity(self.body[off:off + 2])
            records.append(DumpData(n + self.offset, t, h))
        self.records = records

    def __bytes__(self):
        return self.body

    def __call__(self):
        return self.records

    def __str__(self):
        return '; '.join([str(r) for r in self.records])


