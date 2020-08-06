from pymongo import MongoClient
from collections import Counter
import pandas
import numpy as np
import math
import matplotlib.pyplot as plt
import os

TYPE_MIXED = 0
TYPE_DISCHARGING = 1
TYPE_CHARGING = 2

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]


def getTypeOfUsage(csvFile):
    df = pandas.read_csv(csvFile)
    batteryStatus = df['status'].unique()
    if 0 in batteryStatus:
        print("Found 0 in status: " + csvFile)
    if 3 in batteryStatus and 2 in batteryStatus:
        return TYPE_MIXED       # Mixed Usage
    if 3 in batteryStatus:
        return TYPE_DISCHARGING # Discharging
    if 2 in batteryStatus:
        return TYPE_CHARGING    # Charging

def barUsageType(usageTypes):
    freqUsageTypes = Counter(usageTypes)
    df = pandas.DataFrame.from_dict(freqUsageTypes, orient='index')
    ax = df.plot.bar(rot=0, legend=False)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                             ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_xticklabels(['Discharging', 'Charging', 'Mixed'])
    ax.set_xlabel("Type of Session")
    ax.set_ylabel("Appearances")
    plt.show()

def barFilesUser(usersID):
    freqFileUpload = Counter(usersID)
    df = pandas.DataFrame.from_dict(freqFileUpload, orient='index')
    ax = df.plot.bar(rot=15, legend=False)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                             ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_xticklabels(freqFileUpload.keys(), fontsize=7)
    ax.set_xlabel("User Unique ID")
    ax.set_ylabel("# of Files Uploaded")
    plt.show()

def getUsageDrop(csvFile):
    df = pandas.read_csv(csvFile)
    batteryStatus = df['status'].unique()
    if 3 in batteryStatus and not 2 in batteryStatus:
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        return initialLevel-finalLevel
    
def barUsageDrop(usageDrops):
    Not_none_values = filter(None.__ne__, usageDrops)
    usageDrops = list(Not_none_values)
    df = pandas.DataFrame(usageDrops)
    n = math.ceil( (max(usageDrops) - min(usageDrops)) / 5)              # bins size of 5
    ax = df.plot.hist(bins=n, legend=False)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                             ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_xlabel("Battery level drop bins")
    ax.set_ylabel("Frequency")
    plt.show()

def getSessionDuration(csvFile):
    df = pandas.read_csv(csvFile)
    batteryStatus = df['status'].unique()
    if 3 in batteryStatus and not 2 in batteryStatus:
        initialTime = df.iloc[0]['Timestamp']
        finalTime = df.iloc[-1]['Timestamp'] 
        return (finalTime-initialTime)/60000.0

def barSessiontDuration(sessionDuration):
    Not_none_values = filter(None.__ne__, sessionDuration)
    sessionDuration = list(Not_none_values)
    df = pandas.DataFrame(sessionDuration)
    n = math.ceil( (max(sessionDuration) - min(sessionDuration)) / 20)              # bins size of 20
    ax = df.plot.hist(bins=n, legend=False)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                             ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_xlabel("Session Duration bins [mins]")
    ax.set_ylabel("Frequency")
    plt.show()

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

    currentFileList = os.listdir(csv_directory)

    usageTypes = [getTypeOfUsage(csvFile) for csvFile in currentFileList]
    barUsageType(usageTypes) # Uncomment for plot

    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    barFilesUser(usersID) #Uncomment for plot

    usageDrops = [getUsageDrop(csvFile) for csvFile in currentFileList] #None for non Discharging profiles
    barUsageDrop(usageDrops) #Uncomment for plot

    sessionDuration = [getSessionDuration(csvFile) for csvFile in currentFileList] #None for non Discharging profiles
    barSessiontDuration(sessionDuration) #Uncomment for plot    