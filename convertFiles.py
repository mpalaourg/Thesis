import os
import datetime
import json
import numpy as np
from scipy.io import loadmat

def get_dict(mess):
    discharge, charge, impedance = {}, {}, {}

    for i, element in enumerate(mess):

        kind = element[0][0]
        if kind == 'discharge':
            discharge[str(i)] = {}
            discharge[str(i)]["amb_temp"] = str(element[1][0][0])
            
            year, month, day, hour, minute, second = element[2][0][0:6]
            microsecond = (float(second) % 1) * 1000000
            date_time = datetime.datetime(int(year), int(month), 
                                          int(day), int(hour), int(minute), int(second), int(microsecond))        
            discharge[str(i)]["date_time"] = date_time.strftime("%d %b %Y, %H:%M:%S")
            
            data = element[3]
            discharge[str(i)]["Voltage_measured"] = data[0][0][0][0].tolist()
            discharge[str(i)]["Current_measured"] = data[0][0][1][0].tolist()
            discharge[str(i)]["Temperature_measured"] = data[0][0][2][0].tolist()
            discharge[str(i)]["Current_charge"] = data[0][0][3][0].tolist()
            discharge[str(i)]["Voltage_charge"] = data[0][0][4][0].tolist()
            discharge[str(i)]["Time"] = data[0][0][5][0].tolist()
            discharge[str(i)]["Capacity"] = data[0][0][6][0].tolist()
        
        if kind == 'charge':
            charge[str(i)] = {}
            charge[str(i)]["amb_temp"] = str(element[1][0][0])
            
            year, month, day, hour, minute, second = element[2][0][0:6]
            microsecond = (float(second) % 1) * 1000000
            date_time = datetime.datetime(int(year), int(month), 
                                          int(day), int(hour), int(minute), int(second), int(microsecond))        
            charge[str(i)]["date_time"] = date_time.strftime("%d %b %Y, %H:%M:%S")
            
            data = element[3]
            charge[str(i)]["Voltage_measured"] = data[0][0][0][0].tolist()
            charge[str(i)]["Current_measured"] = data[0][0][1][0].tolist()
            charge[str(i)]["Temperature_measured"] = data[0][0][2][0].tolist()
            charge[str(i)]["Current_charge"] = data[0][0][3][0].tolist()
            charge[str(i)]["Voltage_charge"] = data[0][0][4][0].tolist()
            charge[str(i)]["Time"] = data[0][0][5][0].tolist()
        
        if kind == 'impedance':
            impedance[str(i)] = {}
            impedance[str(i)]["amb_temp"] = str(element[1][0][0])
            
            year, month, day, hour, minute, second = element[2][0][0:6]
            microsecond = (float(second) % 1) * 1000000
            date_time = datetime.datetime(int(year), int(month), 
                                          int(day), int(hour), int(minute), int(second), int(microsecond))        
            impedance[str(i)]["date_time"] = date_time.strftime("%d %b %Y, %H:%M:%S")
            
            data = element[3]
            impedance[str(i)]["Sense_current"] = {}
            impedance[str(i)]["Battery_current"] = {}
            impedance[str(i)]["Current_ratio"] = {}
            impedance[str(i)]["Battery_impedance"] = {}
            impedance[str(i)]["Rectified_impedance"] = {}
            # TypeError: Object of type complex is not JSON serializable, i must use real and imag
            impedance[str(i)]["Sense_current"]["real"] = np.real(data[0][0][0][0]).tolist()
            impedance[str(i)]["Sense_current"]["imag"] = np.imag(data[0][0][0][0]).tolist()

            impedance[str(i)]["Battery_current"]["real"] = np.real(data[0][0][1][0]).tolist()
            impedance[str(i)]["Battery_current"]["imag"] = np.imag(data[0][0][1][0]).tolist()

            impedance[str(i)]["Current_ratio"]["real"] = np.real(data[0][0][2][0]).tolist()
            impedance[str(i)]["Current_ratio"]["imag"] = np.imag(data[0][0][2][0]).tolist()

            impedance[str(i)]["Battery_impedance"]["real"] = np.real(data[0][0][3]).tolist()
            impedance[str(i)]["Battery_impedance"]["imag"] = np.imag(data[0][0][3]).tolist()

            impedance[str(i)]["Rectified_impedance"]["real"] = np.real(data[0][0][4]).tolist()
            impedance[str(i)]["Rectified_impedance"]["imag"] = np.imag(data[0][0][4]).tolist()

            impedance[str(i)]["Re"] = float(data[0][0][5][0][0])
            impedance[str(i)]["Rct"] = float(data[0][0][6][0][0])
            
    return discharge, charge, impedance
def save_json(dictionary, name):
    with open(name + '.json', 'w') as f:
        json.dump(dictionary, f, indent=4)

if __name__== "__main__" :
    # .mat files must be at current directory
    currentDirectory = os.getcwd()
    # find all .mat files
    filenames = [f for f in os.listdir(currentDirectory) if f.endswith('.mat')]
    for filename in filenames:
        name = filename.split('.mat')[0]
        print(name)
        struct = loadmat(currentDirectory + '/' + filename)
        mess = struct[name][0][0][0][0]
        discharge, charge, impedance = get_dict(mess)
        save_json(discharge, name + '_Discharge')
        save_json(charge, name + '_Charge')
        save_json(impedance, name + '_Impedance')
        