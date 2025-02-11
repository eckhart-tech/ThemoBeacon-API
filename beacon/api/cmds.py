from .bases import CommandBaseAction
from .messages import CommandIdentify, CommandQuery, CommandDump, MessageQuery, MessageDump


class IdentifyAction(CommandBaseAction):

    def __init__(self,mac,**kwargs):
        super().__init__(mac,noReply=True,**kwargs)

    async def tx(self):
        command = CommandIdentify()
        await self.write(command)


class QueryAction(CommandBaseAction):

    def __init__(self,mac,**kwargs):
        super().__init__(mac,**kwargs)

    async def tx(self):
        command = CommandQuery()
        await self.write(command)


    def rx(self,data):
        if data is not None:
            msg = MessageQuery(data)
            print(f'N={msg.count} raw={data.hex()}')
            return True
        else:
            return False

class DumpAction(CommandBaseAction):

    def __init__(self,mac,count,**kwargs):
        super().__init__(mac,**kwargs)
        self.count=count
        self.data=[]

    def rx(self,data):
        if data is not None:
            msg = MessageDump(data)
            self.data.extend(msg())
            print(msg.offset, msg.count, str(msg))
        return len(self.data)>=self.count

    async def tx(self):
        cnt = 0
        while cnt < self.count:
            c = 15 if self.count - cnt > 15 else self.count - cnt
            cmd = CommandDump(offset=cnt,count=c)
            cnt += c
            print(f'cmd {str(cmd)}')
            await self.write(cmd)





