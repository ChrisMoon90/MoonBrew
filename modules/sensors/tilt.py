import bluetooth._bluetooth as bluez
import blescan
import numpy as np

from modules.sensors.__init__ import SensorBase
from modules.app_config import socketio, cache


tilt_cache = {}

TILTS = {
    'a495bb10c5b14b44b5121370f02d74de': 'Red',
    'a495bb20c5b14b44b5121370f02d74de': 'Green',
    'a495bb30c5b14b44b5121370f02d74de': 'Black',
    'a495bb40c5b14b44b5121370f02d74de': 'Purple',
    'a495bb50c5b14b44b5121370f02d74de': 'Orange',
    'a495bb60c5b14b44b5121370f02d74de': 'Blue',
    'a495bb70c5b14b44b5121370f02d74de': 'Yellow',
    'a495bb80c5b14b44b5121370f02d74de': 'Pink',
}

def add_calibration_point(x, y, field):
    if isinstance(field, str) and field:
        x1, y1 = field.split("=")
        x = np.append(x, float(x1))
        y = np.append(y, float(y1))
    return x, y

def calcGravity(gravity, unitsGravity):
    sg = float(gravity)/1000
    if unitsGravity == u"Plato" or unitsGravity == u"°P":
        return ((135.997 * sg - 630.272) * sg + 1111.14) * sg - 616.868
    elif unitsGravity == u"Brix" or unitsGravity == u"°Bx":
        return ((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622
    else:
        return sg

def calcTemp(temp):
    f = float(temp)
    return f

def calibrate(tilt, equation):
    return eval(equation)
    
def distinct(objects): 
    seen = set()
    unique = []
    for obj in objects:
        if obj['uuid'] not in seen:
            unique.append(obj)
            seen.add(obj['uuid'])
    return unique

def executeTilt(sleep, dev, s_num):
    dev_id = 0
    while True:
        try:
            print("Starting Bluetooth connection")        
            sock = bluez.hci_open_dev(dev_id)
            blescan.hci_le_set_scan_parameters(sock)
            blescan.hci_enable_le_scan(sock)               
            while True:
                beacons = distinct(blescan.parse_events(sock, 10))
                #print(beacons)
                for beacon in beacons:
                    if beacon['uuid'] in TILTS.keys():
                        # print("Tilt Detected")
                        cache['SENSORS'][s_num]['cur_read'] = beacon['minor']
                        # cache[TILTS[beacon['uuid']]] = {'Temp': beacon['major'], 'Gravity': beacon['minor']}
                        print("Tilt data received: Temp %s Gravity %s" % (beacon['major'], beacon['minor']))
                socketio.sleep(sleep) #was 4
        except Exception as e:
            print("Error starting Bluetooth device, exception: %s" % str(e))
        print("Restarting Bluetooth process in 10 seconds")
        socketio.sleep(10)


class TiltAPI(SensorBase):
    def __init__(self):
        self.color = 'Orange' #Property.Select("Tilt Color", options=["Red", "Green", "Black", "Purple", "Orange", "Blue", "Yellow", "Pink"], description="Select the color of your Tilt")
        self.sensorType = 'Gravity' #Property.Select("Data Type", options=["Temperature", "Gravity"], description="Select which type of data to register for this sensor")  
        self.unitsGravity = 'SG' #Property.Select("Gravity Units", options=["SG", "Brix", "°Bx", "Plato", "°P"], description="Converts the gravity reading to this unit if the Data Type is set to Gravity")
        self.x_cal_1 = '' #Property.Text(label="Calibration Point 1", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
        self.x_cal_2 = '' #Property.Text(label="Calibration Point 2", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
        self.x_cal_3 = '' #Property.Text(label="Calibration Point 3", configurable=True, default_value="", description="Optional field for calibrating your Tilt. Enter data in the format uncalibrated=actual")
        self.calibration_equ = ''

        #Load calibration data points
        x = np.empty([0])
        y = np.empty([0])
        x, y = add_calibration_point(x, y, self.x_cal_1)
        x, y = add_calibration_point(x, y, self.x_cal_2)
        x, y = add_calibration_point(x, y, self.x_cal_3)
        
        # Create calibration equation
        if len(x) < 1:
            self.calibration_equ = "tilt"
        if len(x) == 1:
            self.calibration_equ = 'tilt + {0}'.format(y[0] - x[0])
        if len(x) > 1:
            A = np.vstack([x, np.ones(len(x))]).T
            m, c = np.linalg.lstsq(A, y)[0]
            self.calibration_equ = '{0}*tilt + {1}'.format(m, c)           
            print('Calibration equation: {0}'.format(self.calibration_equ))

        for i in range(len(self.active_i2c_devs)):
            dev_name = super().sensor_type('SG') # UPDATES S_COUNT TYPE TOTALS
            s_num = int(super().s_count['Total'] - 1)
            cache["INIT"].append({'function': self.execute_I2C, 'sleep': 0.5, 'dev': self.device_list[i], 's_num': s_num})
            cache["SENSORS"][s_num] = {'com_type': "i2c", 'dev_name': dev_name, 'cur_read': "{0:.3f}".format(0)}
           
    def read(self):
        if self.color in tilt_cache:
            if self.sensorType == "Gravity":
                reading = calcGravity(tilt_cache[self.color]['Gravity'], self.unitsGravity)
                reading = calibrate(reading, self.calibration_equ)
                reading = round(reading, 3)
                print("Gravity Reading = ", reading)
            else:
                reading = calcTemp(tilt_cache[self.color]['Temp'])
                reading = calibrate(reading, self.calibration_equ)
                reading = round(reading, 2)
            self.data_received(reading)

#RUN FOR DEBUGGING PURPOSES                    
if __name__ == '__main__':
    t = TiltAPI()
