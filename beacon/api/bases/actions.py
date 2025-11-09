import asyncio
import traceback

import bleak

from .command import CommandBase


class BaseAction:
    # Transmit Handle 0x0021
    TX_CHAR_UUID = '0000fff5-0000-1000-8000-00805F9B34FB'
    # Read Handle 0x0024
    RX_CHAR_UUID = '0000fff3-0000-1000-8000-00805F9B34FB'

    def __init__(self,**kwargs):
        self.args = kwargs

    def __getitem__(self,key):
        return self.args[key]

    def get(self,key,default = None):
        return self.args.get(key,default)

    async def action(self,**kwargs):
        pass

    async def __call__(self):
        pass

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self())
        except bleak.exc.BleakDBusError as dber:
            print(dber.dbus_error)
        except Exception as exc:
            print('///' + str(exc))
            traceback.print_exc()

class CommandBaseAction(BaseAction):
    def __init__(self,mac : str, **kwargs):
        super().__init__(**kwargs)
        self.mac = mac
        self.client = bleak.BleakClient(self.mac)

    async def write(self,command : CommandBase):
        await self.client.write_gatt_char(self.TX_CHAR_UUID, bytes(command))

    async def tx(self):
        pass

    def rx(self,data) -> bool:
        return True

    def callback(self, sender: int, data: bytearray):
            if data is None:
                return
            try:
                self.rx(data)
            except Exception as exc:
                print(str(exc))


    async def __call__(self):
        try:
            await self.client.connect(timeout=self.get('timeout', 20))
            print('connected')
        except Exception as exc:
            print('exception ' + str(exc))
            return
        try:
            if not self.get('no_reply', False):
                await self.client.start_notify(self.RX_CHAR_UUID, self.callback)
            await self.tx()
        finally:
            await self.client.disconnect()








