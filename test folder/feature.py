import pandas
import numpy as np
import matplotlib.pyplot as plt
import os
import math

# dV/dt | dT/dt
def getDerivative(field, time):
    d_dt = [0.0]
    for index in range(1, field.size):
        curr_d_dt = (field[index] - field[index-1]) / ( (time[index] - time[index-1]) / 1000.0 )
        d_dt.append(curr_d_dt)
    return d_dt

# Get window of a given array
def getWindow(arr, size=6):
    # size according to sampleFreq, to be 1 minute (5-10)
    window, new_arr = np.array([np.nan] * size), np.array([np.nan] * len(arr))
    for count in range( len(arr) ):
        if count < size:
            window[count] = arr[count]
            new_arr[count] = np.nanmean(window)
        else:
            window[count%size] = arr[count]
            new_arr[count] = np.nanmean(window)    
    return new_arr

def MyCumsum(arr):
    arr = np.array(arr)
    result = []
    untilNow = 0
    for i, x in enumerate(arr):
        if x > 0:
            untilNow += x
        else:
            untilNow = 0
        result.append(untilNow)
    return result

if __name__ == "__main__":
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        batteryStatus = df['status'].unique()
        if 3 in batteryStatus and not 2 in batteryStatus:
            '''The idea is to break the sequence data, to data which they can stand alone without
                mainting the order. '''
            
            # Features for Voltage and Temperature, to get the connection with previous sample #
            df["dVdt"] = getDerivative(df["voltage"], df["Timestamp"])
            df["dTdt"] = getDerivative(df["temperature"], df["Timestamp"])
            
            # Feature for usage. Very unstable -> Time window
            size = math.ceil(60/df.iloc[-1]["SampleFreq"])
            df["usageWindow"] = getWindow(df["usage"], size)
            # Features from True | False
            df["WiFi_ConUsage"] = MyCumsum( df["WiFi"] )
            df["Cellular_ConUsage"] = MyCumsum( df["Cellular"] )
            df["Hotspot_ConUsage"] = MyCumsum( df["Hotspot"] )
            df["GPS_ConUsage"] = MyCumsum( df["GPS"] )
            df["Bluetooth_ConUsage"] = MyCumsum( df["Bluetooth"] )
            df["Screen_ConUsage"] = MyCumsum( df["isInteractive"] )
            
            df.to_csv(fileName, ",", index=False)
            print(f"Done with: {fileName}")            