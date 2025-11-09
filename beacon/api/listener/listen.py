import bleak

from beacon.api.bases import BaseAction, Commands
from beacon.api.messages import MessageQuery, MessageDump


class Listener(BaseAction):

    CommandMapper = {
        Commands.Query : MessageQuery,
        Commands.Dump: MessageDump
    }

    def __init__(self,client,queue,commands=(),**kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.queue = queue
        self.commands=list(commands)



    def callback(self, sender: int, data: bytearray):
        if data is None:
            return
        try:
            command = Commands(data[0])
            if command not in self.commands:
                print(f'Ignoring {command}')
                return
            message = self.CommandMapper[command](data)
            print(f'Got : {message}')
            self.queue.put_nowait(message)
        except Exception as exc:
            print(str(exc))

    def listening_for(self,*args):
        self.commands = args

    async def run(self):
        try:
            await self.client.connect(timeout=self.get('timeout', 20))
            print('connected')
        except Exception as exc:
            print('exception ' + str(exc))
            return
        try:
            await self.client.start_notify(self.RX_CHAR_UUID, self.callback)
        except Exception as exc:
            print('exception ' + str(exc))
            return
