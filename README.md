# ThermoBeacon API tools

* _global_ : scan for BLE devices
* _discover [-mac `addr`]_  : Scan for ThermoBeacon devices (optionally select on mac address)
* _identify -mac `addr`_ : Make device with give mac self-identify
* _dump -mac `addr` -n `number` [-t `timeout=20`]_ : Dump `number` records of logged data
* _query -mac `addr` [-t `timeout=20`]_ : Query device for details
