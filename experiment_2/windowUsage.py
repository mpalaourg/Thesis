import pandas
import os
import numpy as np
from math import floor
from collections import Counter

windowLength = 50   # seconds

# Check if a file is a Discharge Session and battery has drop
def isDischarge(df):
    batteryStatus = df['status'].unique()
    initialLevel = df.iloc[0]['level']
    finalLevel = df.iloc[-1]['level'] 
    return 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0
    
# Return the index of the sample that is 'distance' seconds away
def getIndex(start, time, distance):
    for idx in range(start, time.size):
        deltaT = round( (time[idx] - time[start]) / 1000.0 )
        if deltaT >= distance:
            return idx
    # for the last elements window won't be 'distance' seconds long
    return idx      

# Check the percentage of True and return the round value of the percentage.
def isEnable(column):
    enable = column.sum()/column.size
    enable = round(enable)
    return bool(enable)

# Return the category with most appearances in the window
def majorityVote(votes):
    vote_count = Counter(votes)
    majority = vote_count.most_common(1)
    return majority[0][0]

if __name__ == "__main__":
    print("Gettting the window measurements ...")
    current_directory = os.getcwd()
    # rawFiles has the files as exported and checked from the Database
    raw_directory = current_directory + '\\rawFiles'
    currentFileList = os.listdir(raw_directory)

    for csvFile in currentFileList:
        fileName = raw_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)

        if isDischarge(df):
            level = df.level
            voltage = df.voltage
            temperature = df.temperature 
            status = df.status
            health = df.health
            usage = df.usage
            wifi = df.WiFi
            GPS = df.GPS 
            cellular = df.Cellular
            hotspot = df.Hotspot
            interactive = df.isInteractive 
            bluetooth = df.Bluetooth
            RAM = df.RAM
            brightness = df.Brightness
            time = df.Timestamp
            
            start = 0 # start of first window
            windowTemperature, windowVoltage, windowUsage, windowRAM = [], [], [], []
            windowLevel, windowStatus, windowHealth, windowBrightness = [], [], [], []
            windowWiFi, windowCellular, windowHotspot, windowGPS, windowBluetooth, windowInteractive  = [], [], [], [], [], []
            while start != time.size-1:
                end = getIndex(start=start, time=time, distance=windowLength)
                # voltage, temperature, usage, RAM -> mean | boolean -> percentage of true - round to 0 or 1 - False or True
                # status and heath -> majority vote - Categorical data 
                windowLevel.append( floor(level[start:end].mean()) )
                windowVoltage.append( round(voltage[start:end].mean(), 4) )
                windowTemperature.append( round(temperature[start:end].mean(), 4) )
                windowStatus.append( majorityVote(status[start:end]) )
                windowHealth.append( majorityVote(health[start:end]) )
                windowUsage.append( round(usage[start:end].mean(), 4) )
                windowWiFi.append( isEnable(wifi[start:end]) )
                windowCellular.append( isEnable(cellular[start:end]) )
                windowHotspot.append( isEnable(hotspot[start:end]) )
                windowGPS.append( isEnable(GPS[start:end]) )
                windowBluetooth.append( isEnable(bluetooth[start:end]) )
                windowRAM.append( round(RAM[start:end].mean(), 4) )
                windowBrightness.append( round(brightness[start:end].mean(), 0) )
                windowInteractive.append( isEnable(interactive[start:end]) )
                
                prev_start = start
                start = end         # The start for the next window is at the end of the previous one
            # Create the new dataframe
            dfSave = pandas.DataFrame()
            dfSave["level"] = windowLevel
            dfSave["temperature"] = windowTemperature
            dfSave["voltage"] = windowVoltage
            dfSave["status"] = windowStatus
            dfSave["health"] = windowHealth
            dfSave["usage"] = windowUsage
            dfSave["WiFi"] = windowWiFi
            dfSave["Cellular"] = windowCellular
            dfSave["Hotspot"] = windowHotspot
            dfSave["GPS"] = windowGPS
            dfSave["Bluetooth"] = windowBluetooth
            dfSave["RAM"] = windowRAM
            dfSave["Brightness"] = windowBrightness
            dfSave["isInteractive"] = windowInteractive
            
            # windowFiles has the same Files, but grouped at time Windows for smoothing
            fileNameSave = current_directory + "\\windowFiles\\" + csvFile
            dfSave.to_csv(fileNameSave, ",", index=False) 
            print(f"Done with file: {fileNameSave}")
    print("Done with the window measurements.")
        