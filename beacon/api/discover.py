from .bases import ScannerAction
from .messages import Responses,makeThermoBeaconData




class GlobalScan(ScannerAction):

    def __init__(self):
        super().__init__(timeout = 540)

    def action(self,response):
        for key, value in response:
            print(f'Found {response.name}@{key}: [{response.mac}] {value.hex()}')


class DiscoveryScan(ScannerAction):

    def __init__(self, name : str = 'ThermoBeacon', response_type : Responses = Responses.Values):
        super().__init__(timeout=540)
        self.response_type = response_type
        self.name = name
        self.macs = []
        self.beacons = []

    def check(self, response):
        if response.name_is(self.name) :
            return response.mac not in self.macs
        else:
            return False

    def action(self, response):
        replies = makeThermoBeaconData(response)
        adverts = [r for r in replies if r.response_type==self.response_type]
        if len(adverts)>0:
            self.macs.append(response.mac)
            self.beacons.append(adverts[0])
            print(f'Found {response.name}@{adverts[0].id}: [{response.mac}] {adverts[0].hex()}')


class BeaconScan(ScannerAction):
    def __init__(self, mac, name : str = 'ThermoBeacon', response_type : Responses = Responses.Values):
        super().__init__( timeout=40)
        self.target = mac
        self.name=name
        self.response_type = response_type
        self.results = dict()

    def check(self, response):
        return  response.name_is(self.name) and response.mac == self.target

    def action(self, response):
        replies = makeThermoBeaconData(response)
        adverts = [r for r in replies if r.response_type == self.response_type]
        if len(adverts) > 0:
            ad = adverts[0]
            print(f'Found {response.name}@{ad.id} : ')
            print(str(ad))





