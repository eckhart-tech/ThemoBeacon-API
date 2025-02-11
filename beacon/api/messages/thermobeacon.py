import enum
from .conversions import decode_humidity, decode_temperature


class Responses(enum.IntEnum):
    Values = 1
    Ranges = 2
    Dump = 3



class ThermoBeaconBase:
    def __init__(self, response_type : Responses, key : int, value : bytes):
        self.response_type = response_type
        self.id = key
        self.raw = value

        self.button = False if value[1] == 0 else True
        self.mac = int.from_bytes(value[2:8],byteorder='little')

    def hex(self):
        return self.raw.hex()

    def __str__(self):
        return ''

class ThermoBeaconValues(ThermoBeaconBase):
    def __init__(self,key: int, value: bytes):
        super().__init__(Responses.Values, key, value)

        battery = int.from_bytes(value[8:10], byteorder='little')
        self.battery = battery * 100 / 3400
        self.temperature = decode_temperature(value[10:12])
        self.humidity = decode_humidity(value[12:14])
        self.uptime = int.from_bytes(value[14:18], byteorder='little')

    def __str__(self):
        return '\n'.join([f'MAC = [{self.mac}] ID = {self.id}',
                          f'Temperature = {self.temperature}',
                          f'Humidity = {self.humidity}',
                          f'Battery = {self.battery}',
                          f'Uptime = {self.uptime}'])

class ThermoBeaconRanges(ThermoBeaconBase):
    def __init__(self,key: int, value: bytes):
        super().__init__(Responses.Ranges, key, value)

        self.max = decode_temperature(value[8:10])
        self.max_at_time = int.from_bytes(value[10:14], byteorder='little')
        self.min = decode_temperature(value[14:16])
        self.min_at_time = int.from_bytes(value[16:20], byteorder='little')

    def __str__(self):
        return '\n'.join([f'MAC = [{self.mac}] ID = {self.id}',
                          f'Max temperature = {self.max} at {self.max_at_time}',
                          f'Min temperature = {self.min} at {self.min_at_time}'])


def makeThermoBeaconData(response):
        out = []
        for k, v in response:
            if len(v) == 18:
                out.append(ThermoBeaconValues(k, v))
            elif len(v) == 28:
                out.append(ThermoBeaconRanges(k, v))
        return out




