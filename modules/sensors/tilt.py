print('Loading Tilt Module...')

import asyncio
from uuid import UUID
from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError
from bleak import BleakScanner

from modules.sensors.__init__ import SensorBase
from modules.app_config import socketio, cache

tilts = {
    'a495bb10-c5b1-4b44-b512-1370f02d74de': 'Red',
    'a495bb20-c5b1-4b44-b512-1370f02d74de': 'Green',
    'a495bb30-c5b1-4b44-b512-1370f02d74de': 'Black',
    'a495bb40-c5b1-4b44-b512-1370f02d74de': 'Purple',
    'a495bb50-c5b1-4b44-b512-1370f02d74de': 'Orange',
    'a495bb60-c5b1-4b44-b512-1370f02d74de': 'Blue',
    'a495bb70-c5b1-4b44-b512-1370f02d74de': 'Yellow',
    'a495bb80-c5b1-4b44-b512-1370f02d74de': 'Pink'
}

# def add_calibration_point(x, y, field):
#     if isinstance(field, str) and field:
#         x1, y1 = field.split("=")
#         x = np.append(x, float(x1))
#         y = np.append(y, float(y1))
#     return x, y

# def calibrate(tilt, equation):
#     return eval(equation)

ibeacon_format = Struct(
    "type_length" / Const(b"\x02\x15"),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "power" / Int8sl,
)

class Tilt(SensorBase):
    a_tilts = {}

    def get_tilt_cache():
        return Tilt.a_tilts

    def unique(uuid):
        if uuid not in Tilt.a_tilts.keys():
            Tilt.a_tilts[uuid] = {'temp': 0, 'sg': 0, 'txpower': 0, 'rssi': 0}
            print('Tilt Added: ', uuid)
            return True
        else:
            return False

    async def device_found(device, advertisement_data):
        try:
            ad_data = advertisement_data.manufacturer_data[0x004C]
            ibeacon = ibeacon_format.parse(ad_data)
            uuid = str(UUID(bytes=bytes(ibeacon.uuid)))
            for key in tilts: 
                if uuid == key:
                    if Tilt.unique(uuid):
                        type = 'SG'
                        print('go to sensor type')
                        dev_name = SensorBase.sensor_type(SensorBase, type)
                        s_num = SensorBase.s_count['Total'] - 1
                        print('s_num: ', s_num)
                        cache["SENSORS"][s_num] = {'com_type': 'ble', 'dev_name': dev_name, 'dev_id': uuid, 'cur_read': "{0:.3f}".format(0)}
                    rssi = advertisement_data.rssi
                    Tilt.a_tilts[uuid] = {'temp': ibeacon.major, 'sg': float(ibeacon.minor)/1000, 'txpower': ibeacon.power, 'rssi': rssi}
                    for key, val in cache['SENSORS'].items():
                        print(key, val)
                        if val['dev_id'] == uuid:
                            s_num = key
                    cache['SENSORS'][s_num]['cur_read'] = Tilt.a_tilts[uuid]['sg']
        except KeyError:
            pass
        except ConstError:
            pass
        except:
            print('Other device_found Error')


async def tilt_init(sleep):
    scanner = BleakScanner(Tilt.device_found) #add filter here later
    while True:
        await scanner.start()
        await asyncio.sleep(sleep)
        await scanner.stop()


cache["INIT"].append({"function": tilt_init, "sleep": 5})

# task = socketio.start_background_task(tilt_init, 123)
# asyncio.run(init())