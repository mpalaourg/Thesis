from pymongo import MongoClient
from collections import Counter
import pandas
import numpy as np
import matplotlib.pyplot as plt
import os

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]

def checkDiffLevel(csv_directory):
    allGood = True
    currentFileList = os.listdir(csv_directory)
    for csvFile in currentFileList:
        df = pandas.read_csv(csvFile)
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        if (finalLevel - initialLevel == 0):
            # I must check for > 0 -> Charging
            # I must check for < 0 -> Discharging 
            allGood = False
            print(csvFile)
    return allGood

def samplingPeriod(csv_directory):
    allGood = True
    currentFileList = os.listdir(csv_directory)
    for csvFile in currentFileList:
        df = pandas.read_csv(csvFile)
        firstSample = df.iloc[0]['Timestamp']
        finalSample = df.iloc[-1]['Timestamp']
        samplingPeriod = ( (finalSample - firstSample) / (len(df.axes[0]) - 1) ) / 1000
        samplingStep = df.iloc[-1]['SampleFreq']
        if (samplingStep - round(samplingPeriod) != 0):
            # I must check for different sample sizes
            allGood = False
            print(csvFile + " - - " + str(samplingStep - round(samplingPeriod)) + " - - " + str(samplingPeriod))
    return allGood

def checkBatteryOnlyDropping(csv_directory):
    allGood = True
    currentFileList = os.listdir(csv_directory)
    for csvFile in currentFileList:
        df = pandas.read_csv(csvFile)
        length = len(df.axes[0])
        for i in range(0, length):
            batteryStatus = df.iloc[i]['status']
            if (batteryStatus != 0 and batteryStatus != 3):
                # I must check for > 0 -> Charging
                # I must check for < 0 -> Discharging 
                allGood = False
                print(csvFile)
                break
    return allGood

if __name__ == "__main__":
    current_directory = os.getcwd()
    print("Current Working Directory " , current_directory)
    csv_directory = current_directory + '\\csvFiles_rasp'
    #csv_directory = current_directory + '\\csvFiles_PC'
    try:
        os.chdir(csv_directory)
        print("Directory changed")
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    
    print("Current Working Directory " , os.getcwd())

    if checkDiffLevel(csv_directory):
        print("All Good with the Battery level dropping.")
    
    if samplingPeriod(csv_directory):
        print("All Good with the Sampling Frequency")
    #if checkBatteryOnlyDropping(csv_directory):
    #    print("All samples are Discharging")