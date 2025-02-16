
import bleak
import asyncio

import enum

from beacon.api.bases import BaseAction, CommandBase, Commands
from beacon.api.cmds import CommandQuery, CommandDump
from beacon.api.listener.listen import Listener
from beacon.api.messages import MessageQuery, MessageDump


class State(enum.Enum):
    Query = 1
    Dump = 2

class DumpProcessor(BaseAction):

    def __init__(self,mac):
        super().__init__()
        self.mac=mac
        self.client = bleak.BleakClient(self.mac)
        self.barrier = asyncio.Barrier(2)
        self.state = None
        self.count = 0

    async def write(self,command : CommandBase):
        await self.client.write_gatt_char(self.TX_CHAR_UUID, bytes(command))

    async def respond_to_query(self,query):
        self.count = query.count
        offset = 0
        while offset < self.count:
            c = min(self.count-offset,15)
            cmd = CommandDump(offset=offset, count=c)
            offset += c
            print(f'cmd {str(cmd)}')
            await self.write(cmd)

    def respond_to_dump(self,dump):
        if self.count>0:
            print(f'Got: {dump}')
            self.count-=1



    async def callback(self, sender: int, data: bytearray):
        if data is None:
            return
        should_exit = False
        try:
            command = Commands(data[0])
            if self.state == State.Query and command == Commands.Query:
                query = MessageQuery(data)
                await self.respond_to_query(query)
                self.state = State.Dump

            elif self.state == State.Dump and command == Commands.Dump:
                dump = MessageDump(data)
                self.respond_to_dump(dump)
                if self.count == 0:
                    should_exit = True
        except Exception as exc:
            print(str(exc))

        if should_exit:
            raise KeyboardInterrupt()

    async def run(self):
        try:
            await self.client.connect(timeout=self.get('timeout', 20))
            print('connected')
        except Exception as exc:
            print('exception ' + str(exc))
            return
        try:
            self.state = State.Query
            await self.client.start_notify(self.RX_CHAR_UUID, self.callback)
            await self.write(CommandQuery())
        except KeyboardInterrupt:
            print('Completed')
        except Exception as e:
            print(f'Unexpected error {e}')
        finally:
            await self.client.disconnect()













