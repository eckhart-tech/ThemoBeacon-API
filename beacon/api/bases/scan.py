import asyncio
import bleak
from .actions import BaseAction

class AdvertisingResponse:
    def __init__(self, device : bleak.BLEDevice, advert : bleak.AdvertisementData):
        self.mac = device.address.lower()
        self.device_name = device.name
        self.name = advert.local_name
        self.details = device.details
        self.data = advert.manufacturer_data
        self.rssi = advert.rssi
        self.tx_power = advert.tx_power

    def __iter__(self):
        for k, v in self.data.items():
            yield k, v

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, item):
        return item in self.data.keys()

    def __str__(self):
        return f'[{self.mac}] {self.name}({self.device_name}) {self.rssi}'

    def name_is(self, name: str):
        return self.name is not None and self.name == name

class ScannerAction(BaseAction):

    def __init__(self, timeout: int = 20):
        super().__init__()
        self.timeout = timeout

    def check(self, response):
        return True

    def action(self,response):
        pass

    def callback(self, device : bleak.BLEDevice, ad_data : bleak.AdvertisementData):
        response = AdvertisingResponse(device,ad_data)
        if self.check(response):
            self.action(response)

    async def __call__(self):
        scanner = bleak.BleakScanner(self.callback)
        await scanner.start()
        await asyncio.sleep(self.timeout)
        await scanner.stop()

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self())
        except KeyboardInterrupt:
            print()
            return