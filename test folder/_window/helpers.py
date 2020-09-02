import pandas
import numpy as np
from pandas.api.types import CategoricalDtype
from statistics import mean
import glob
import os
from collections import Counter

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

            level = df["level"].astype('float64')
            windowLevel = [level[0]]
            minuteLevel = []
            '''
            level, timestamp = df["level"].astype('float64'), df["Timestamp"]
            windowLevel, windowTimestamp = [level[0]], [timestamp[0]]
            minuteLevel, minuteDrop = [], []
            '''

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
                #windowTimestamp.append( timestamp[index] )

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
                    '''
                    if len(minuteLevel) == 1:
                        prevLevel = minuteLevel[-1]
                    # It's a sliding window, where each instance of the window
                    # its away "sampleFreq" second
                    currLevel = prevLevel - windowFreqs[-1]*dSOC_dt(windowLevel, windowTimestamp)
                    minuteDrop.append( currLevel )
                    prevLevel = currLevel
                    '''
                    timeUntilNow -= windowFreqs[0]
                    del windowUsage[0], windowVoltage[0], windowTemperature[0], windowFreqs[0]
                    del windowHealth[0], windowStatus[0]
                    del windowWiFi[0], windowCellular[0], windowHotspot[0], windowGPS[0], windowBluetooth[0], windowInteractive[0]
                    del windowRAM[0], windowBrightness[0], windowLevel[0]       # windowTimestamp[0]
                    
            
            # Create the new dataframe
            dfSave = pandas.DataFrame()
            dfSave["minuteLevel"] = minuteLevel         # int , mean return floor( float )
            dfSave["minuteStatus"] = minuteStatus
            dfSave["minuteHealth"] = minuteHealth
            dfSave["minuteTemperature"] = minuteTemperature
            dfSave["minuteVoltage"] = minuteVoltage
            dfSave["minuteUsage"] = minuteUsage
            dfSave["minuteWiFi"] = minuteWiFi
            dfSave["minuteCellular"] = minuteCellular
            dfSave["minuteHotspot"] = minuteHotspot
            dfSave["minuteGPS"] = minuteGPS
            dfSave["minuteBluetooth"] = minuteBluetooth
            dfSave["minuteRAM"] = minuteRAM
            dfSave["minuteBrightness"] = minuteBrightness
            dfSave["minuteInteractive"] = minuteInteractive
            #dfSave["minuteDrop"] = minuteDrop
            
            fileNameSave = current_directory + "\\windowFiles\\" + csvFile
            dfSave.to_csv(fileNameSave, ",", index=False) 
            print(f"Done with file: {fileNameSave}")
    print("Done with the window measurements.")

################################## Compute the output ##################################
def dSOC_dt(df):
    initialLevel = df.iloc[0]['minuteLevel']
    finalLevel = df.iloc[-1]['minuteLevel']
    if initialLevel - finalLevel != 0:
        currentRate = (initialLevel - finalLevel) / df["minuteLevel"].size
    else:
        currentRate = 0
    return currentRate

def computeOutput():
    print("Computing the output ...")
    current_directory = os.getcwd()
    test_directory = current_directory + '\\windowFiles'
    currentFileList = os.listdir(test_directory)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        dSOC = dSOC_dt(df)
        if dSOC:
            output = [df["minuteLevel"].iloc[0]]
            
            for i in range(1, df["minuteLevel"].size):
                #currOutput = output[-1] + dSOC * (time[i]-time[i-1]) / 1000.0
                #currOutput = dSOC #* (time[i]-time[i-1]) / 1000.0
                
                currOutput = output[-1] - dSOC
                output.append(currOutput)
            #output[0] = output[-1]
            df['output'] = output
            #df = df[1:]                             # drop first sample => output=0, here or before?
            df.to_csv(fileName, ",", index=False)
            print(f"Done with: {fileName}")
    print("Done with the output.")

################################## Combine the files ##################################
def combineAllUsers(currentFileList, window_directory):
    combined_csv = []
    for f in currentFileList:
        fileName = window_directory + "\\" + f
        df = pandas.read_csv(fileName)
        combined_csv.append(df)
    return combined_csv

def combinePerUser(UserFileList, window_directory):
    combined_csv = []
    for f in UserFileList:
        fileName = window_directory + "\\" + f
        df = pandas.read_csv(fileName)
        combined_csv.append(df)
    return combined_csv

def combine():
    print("Combining the files...")
    current_directory = os.getcwd()
    window_directory = current_directory + '\\windowFiles'
    currentFileList = os.listdir(window_directory)

    combined_csv = combineAllUsers(currentFileList, window_directory)
    combinedAll_csv = pandas.concat(combined_csv)       
    combinedAll_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
    
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        combined_csv = combinePerUser(userFileList, window_directory)
        combinedPer_csv = pandas.concat(combined_csv)       
        combinedPer_csv.to_csv( f"{current_directory}\\combined\\{user}-combined_csv.csv", index=False, encoding='utf-8-sig')
    print("Done combining the files.")

################################## Get the 1 min window ##################################