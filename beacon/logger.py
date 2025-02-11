import bleak
import asyncio
from api.messages.thermobeacon import ThermoBeaconValues

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

def decode_temperature(b:bytes) -> float:
    result = int.from_bytes(b, byteorder='little')/16.0
    if result>4000:
        result -= 4096
    return result

'''
decode humidity value from byte(2) array
'''

def decode_humidity(b:bytes) -> float:
    result = int.from_bytes(b, byteorder='little')/16.0
    if result>4000:
        result -= 4096
    return result

class ThermoBeaconValues(ThermoBeaconBase):
    def __init__(self,key: int, value: bytes):
        self.id = key
        self.raw = value

        self.button = False if value[1] == 0 else True
        self.mac = int.from_bytes(value[2:8], byteorder='little')
        battery = int.from_bytes(value[8:10], byteorder='little')
        self.battery = battery * 100 / 3400
        self.temperature = decode_temperature(value[10:12])
        self.humidity = decode_humidity(value[12:14])
        self.uptime = int.from_bytes(value[14:18], byteorder='little')

    def hex(self):
        return self.raw.hex()

    def __str__(self):
        return '\n'.join([f'MAC = [{self.mac}] ID = {self.id}',
                          f'Temperature = {self.temperature}',
                          f'Humidity = {self.humidity}',
                          f'Battery = {self.battery}',
                          f'Uptime = {self.uptime}'])

class ScanForUpdates:

    def __init__(self, name : str = 'ThermoBeacon', response_length : int = 18, timeout : int = 540):
        self.timeout = timeout
        self.response_length = response_length
        self.name = name
        self.macs = []
        self.beacons = []

    def check(self, response):
        if response.name_is(self.name) :
            return response.mac not in self.macs
        else:
            return False

    def action(self, response):
        received = []
        for k, v in response:
            if len(v) == 18:
                received.append(ThermoBeaconValues(k, v))
        if len(received)>0:
            rcv = received[0]
            self.macs.append(response.mac)
            self.beacons.append(rcv)
            print(f'Found {response.name}@{rcv.id}: [{response.mac}] {rcv.hex()}')

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
            print(f'Got {len(self.beacons)} records')
            for beacon in self.beacons:
                print(str(beacon))
        except KeyboardInterrupt:
            print()
            return


