import pandas
import numpy as np
import math
from itertools import accumulate
#from pandas.api.types import CategoricalDtype
from statistics import mean
import glob
import os
from collections import Counter
'''
################################## Get the 1 min window ##################################
def majorityVote(votes):
    vote_count = Counter(votes)
    majority = vote_count.most_common(1)
    return majority[0][0]

def truePercentage(arr):
    ON = np.count_nonzero(arr)
    return ON/len(arr)

def getMinuteWindow():
    print("Gettting the window measurements ...")
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)
    
    # ref link status: https://developer.android.com/reference/android/os/BatteryManager#BATTERY_STATUS_CHARGING
    #statusCat = CategoricalDtype(categories=[1, 2, 3, 4, 5], ordered=False)
    # ref link health: https://developer.android.com/reference/android/os/BatteryManager#BATTERY_HEALTH_DEAD
    #healthCat = CategoricalDtype(categories=[1, 2, 3, 4, 5, 6], ordered=False)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        batteryStatus = df['status'].unique()
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        if 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0:
            sampleFreq = df["SampleFreq"]
            windowFreqs = []
            
            usage, voltage, temperature = df["usage"], df["voltage"], df["temperature"]
            windowUsage, windowVoltage, windowTemperature = [usage[0]], [voltage[0]], [temperature[0]]
            minuteUsage, minuteVoltage, minuteTemperature = [], [], []
            
            status, health = df["status"], df["health"]
            windowStatus, windowHealth = [status[0]], [health[0]]
            minuteStatus, minuteHealth = [], []

            wifi, cellular, hotspot, GPS, bluetooth, interactive = df["WiFi"], df["Cellular"], df["Hotspot"], df["GPS"], df["Bluetooth"], df["isInteractive"]
            windowWiFi, windowCellular, windowHotspot = [wifi[0]], [cellular[0]], [hotspot[0]] 
            windowGPS, windowBluetooth, windowInteractive =  [GPS[0]], [bluetooth[0]], [interactive[0]]
            minuteWiFi, minuteCellular, minuteHotspot, minuteGPS, minuteBluetooth, minuteInteractive  = [], [], [], [], [], []

            RAM, brightness = df["RAM"], df["Brightness"]
            windowRAM, windowBrightness = [RAM[0]], [brightness[0]]
            minuteRAM, minuteBrightness = [], []

            level, timestamp = df["level"].astype('float64'), df["Timestamp"]
            windowLevel, windowTimestamp = [level[0]], [timestamp[0]]
            minuteLevel, minuteTimestamp = [], []

            timeUntilNow = 0
            for index in range(1, sampleFreq.size):
                timeUntilNow += sampleFreq[index]
                windowFreqs.append( sampleFreq[index] )
                windowUsage.append( usage[index] )
                windowVoltage.append( voltage[index] )
                windowTemperature.append( temperature[index] )
                
                windowStatus.append( status[index] )
                windowHealth.append( health[index] )

                windowWiFi.append( wifi[index] )
                windowCellular.append( cellular[index] )
                windowHotspot.append( hotspot[index] )
                windowGPS.append( GPS[index] )
                windowBluetooth.append( bluetooth[index] )
                windowInteractive.append( interactive[index] )
                
                windowRAM.append( RAM[index] )
                windowBrightness.append( brightness[index] )
                windowLevel.append( level[index] )
                windowTimestamp.append( timestamp[index] )

                if timeUntilNow >= 60:
                    # Window has the values inside the 1min Window
                    minuteUsage.append( mean(windowUsage) )
                    minuteVoltage.append( mean(windowVoltage) )
                    minuteTemperature.append( mean(windowTemperature) )

                    minuteStatus.append( majorityVote(windowStatus) )
                    minuteHealth.append( majorityVote(windowHealth) )

                    minuteWiFi.append( truePercentage(windowWiFi) )
                    minuteCellular.append( truePercentage(windowCellular) )
                    minuteHotspot.append( truePercentage(windowHotspot) )
                    minuteGPS.append( truePercentage(windowGPS) )
                    minuteBluetooth.append( truePercentage(windowBluetooth) )
                    minuteInteractive.append( truePercentage(windowInteractive) )

                    minuteRAM.append( mean(windowRAM) )
                    minuteBrightness.append( mean(windowBrightness) )
                    minuteLevel.append( mean(windowLevel) ) # with ot withour round( mean(windowLevel) )
                    minuteTimestamp.append( windowTimestamp[-1] )
                    timeUntilNow -= windowFreqs[0]
                    del windowUsage[0], windowVoltage[0], windowTemperature[0], windowFreqs[0]
                    del windowHealth[0], windowStatus[0]
                    del windowWiFi[0], windowCellular[0], windowHotspot[0], windowGPS[0], windowBluetooth[0], windowInteractive[0]
                    del windowRAM[0], windowBrightness[0], windowLevel[0], windowTimestamp[0]
                    
            
            # Create the new dataframe
            dfSave = pandas.DataFrame()
            dfSave["level"] = minuteLevel         # int , mean return floor( float )
            dfSave["status"] = minuteStatus
            dfSave["health"] = minuteHealth
            dfSave["temperature"] = minuteTemperature
            dfSave["voltage"] = minuteVoltage
            dfSave["usage"] = minuteUsage
            dfSave["WiFi"] = minuteWiFi
            dfSave["Cellular"] = minuteCellular
            dfSave["Hotspot"] = minuteHotspot
            dfSave["GPS"] = minuteGPS
            dfSave["Bluetooth"] = minuteBluetooth
            dfSave["RAM"] = minuteRAM
            dfSave["Brightness"] = minuteBrightness
            dfSave["isInteractive"] = minuteInteractive
            dfSave["Timestamp"] = minuteTimestamp

            fileNameSave = current_directory + "\\windowFiles\\" + csvFile
            dfSave.to_csv(fileNameSave, ",", index=False) 
            print(f"Done with file: {fileNameSave}")
    print("Done with the window measurements.")
'''
################################## Shift the features k-times ##################################

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

def k_shift(column, k=5, name="array"):
    df = pandas.DataFrame(column)
    prev_shifted = df.copy()
    columnNames = [f"{name}[t]"]
    for i in range(1, k+1):
        columnNames.append(f"{name}[t-{i}]")
        curr_shifted = prev_shifted.shift(periods=1, axis=0, fill_value=0)
        df = pandas.concat([df, curr_shifted], ignore_index=True, axis = 1)
        prev_shifted = curr_shifted.copy()
    df.columns = columnNames
    return df

def shiftColumns():
    print("Shifting columns ...")
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        batteryStatus = df['status'].unique()
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        if 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0:
            voltage = df["voltage"]
            temperature = df["temperature"]
            # Feature for usage. Very unstable -> Time window
            size = math.ceil(60/df.iloc[-1]["SampleFreq"])
            usage = getWindow(df["usage"], size)
            RAM = df["RAM"]
            brightness = df["Brightness"]
            
            shiftedVoltage = k_shift(voltage, name="voltage")
            shiftedTemperature = k_shift(temperature, name="temperature")
            shiftedUsage = k_shift(usage, name="usage")
            shiftedRAM = k_shift(RAM, name="RAM")
            shiftedBrightness = k_shift(brightness, name="brightness")

            # Create the new dataframe
            dfSave = pandas.DataFrame()
            dfSave["level"] = df["level"]
            dfSave = dfSave.join(shiftedTemperature)
            dfSave = dfSave.join(shiftedVoltage)
            dfSave["status"] = df["status"]
            dfSave["health"] = df["health"]
            dfSave = dfSave.join(shiftedUsage)
            dfSave["WiFi"] = df["WiFi"]
            dfSave["Hotspot"] = df["Hotspot"]
            dfSave["Hotspot"] = df["Hotspot"]
            dfSave["GPS"] = df["GPS"]
            dfSave["Bluetooth"] = df["Bluetooth"]
            dfSave = dfSave.join(shiftedRAM)
            dfSave = dfSave.join(shiftedBrightness)
            dfSave["isInteractive"] = df["isInteractive"]
            dfSave["Timestamp"] = df["Timestamp"]
            fileNameSave = current_directory + "\\shiftFiles\\" + csvFile
            dfSave.to_csv(fileNameSave, ",", index=False) 
            print(f"Done with file: {fileNameSave}")
    print("Done with shifting.")

################################## Compute the output ##################################
def dSOC_dt(df, start, end):
    initialLevel = df.iloc[start]['level']
    finalLevel = df.iloc[end]['level']
    if initialLevel - finalLevel != 0:
        duration = (df.Timestamp.iloc[end] - df.Timestamp.iloc[start]) / 1000
        currentRate = (initialLevel - finalLevel) / duration
    else:
        currentRate = 0
    
    deltaT = np.array([(df.Timestamp[i + 1] - df.Timestamp[i])/1000 for i in range(start,end)])
    dSOC = [currentRate*deltaT[i] for i in range(deltaT.size)]
    return dSOC

def computeOutput():
    print("Computing the output ...")
    current_directory = os.getcwd()
    shift_directory = current_directory + '\\shiftFiles'
    currentFileList = os.listdir(shift_directory)
    
    for csvFile in currentFileList:
        fileName = shift_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        level = df.level
        uniqueLevels = level.unique()
        prevIdx = 0
        output = []
        for i in uniqueLevels[1:]:
            currIdx = level.eq(i).idxmax()  # get the index where value of level is changing
            output = output + dSOC_dt(df, prevIdx, currIdx) 
            prevIdx = currIdx
        df = df[0:currIdx]                  # Throw the last row with same battery
        
        deltaT = np.array([(df.Timestamp[i + 1] - df.Timestamp[i])/1000 for i in range(len(df)-1)])
        deltaT = np.concatenate((np.array([0]), deltaT))
        deltaT = pandas.DataFrame(deltaT, columns=['deltaT'])
        df = df.join(deltaT)
            
        #output = [dSOC*df.deltaT[i] for i in range(df["level"].size)]
        output = list( accumulate(output) )
        output = k_shift(output, k=1, name="output")
        output = output.reindex(['output[t-1]', 'output[t]'], axis="columns")
        df = df.join(output)
        df.to_csv(fileName, ",", index=False)
        print(f"Done with: {fileName}")
    print("Done with the output.")

################################## Combine the files ##################################
def combineAllUsers(currentFileList, shift_directory):
    combined_csv = []
    for f in currentFileList:
        fileName = shift_directory + "\\" + f
        df = pandas.read_csv(fileName)
        combined_csv.append(df)
    return combined_csv

def combinePerUser(UserFileList, shift_directory):
    combined_csv = []
    for f in UserFileList:
        fileName = shift_directory + "\\" + f
        df = pandas.read_csv(fileName)
        combined_csv.append(df)
    return combined_csv

def combine():
    print("Combining the files...")
    current_directory = os.getcwd()
    shift_directory = current_directory + '\\shiftFiles'
    currentFileList = os.listdir(shift_directory)

    combined_csv = combineAllUsers(currentFileList, shift_directory)
    combinedAll_csv = pandas.concat(combined_csv)       
    combinedAll_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
    
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        combined_csv = combinePerUser(userFileList, shift_directory)
        combinedPer_csv = pandas.concat(combined_csv)       
        combinedPer_csv.to_csv( f"{current_directory}\\combined\\{user}-combined_csv.csv", index=False, encoding='utf-8-sig')
    print("Done combining the files.")
