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
    myLabels = ['Mixed', 'Discharging', 'Charging']
    df = pandas.DataFrame.from_dict(freqUsageTypes, orient='index')
    ax = df.plot.bar(rot=0, legend=False)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                             ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_title("Session Type Histrogram", fontweight='bold')
    myLabels = [myLabels[int( label.get_text() )] for label in ax.get_xticklabels()]
    ax.set_xticklabels(myLabels, fontweight='bold')
    ax.set_xlabel("Session type", fontweight='bold')
    ax.set_ylabel("Appearances", fontweight='bold')
    plt.show()

def barFilesUser(usersID):
    freqFileUpload = Counter(usersID)
    df = pandas.DataFrame.from_dict(freqFileUpload, orient='index')
    ax = df.plot.hist(rot=10, bins=10, legend=False)

    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                                ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_title("Files Uploaded Histrogram", fontweight='bold')
    ax.set_xlabel("# of files uploaded bins", fontweight='bold')
    ax.set_ylabel("# of Users", fontweight='bold')
    
    plt.show()

def getUsageDrop(csvFile):
    df = pandas.read_csv(csvFile)
    batteryStatus = df['status'].unique()
    if 3 in batteryStatus and not 2 in batteryStatus:
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level']
        if initialLevel-finalLevel < 0:
            print(csvFile)
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
    ax.set_title("Battery Level Drop Histogram", fontweight='bold')
    ax.set_xlabel("Battery level drop bins", fontweight='bold')
    ax.set_ylabel("Frequency", fontweight='bold')
    
    hist, bin_edges= np.histogram(usageDrops, n)
    cumsum_data = np.cumsum(hist)
    plt.figure()
    plt.title("Distribution of Battery Level Drop", fontweight='bold')
    plt.step(bin_edges[:-1], cumsum_data/cumsum_data[-1])
    plt.xlabel("Battery level drop", fontweight='bold')
    plt.ylabel("Cumulative distribution function (CDF)", fontweight='bold')
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
    n = math.ceil( (max(sessionDuration) - min(sessionDuration)) / 30)              # bins size of 30
    
    ax = df.plot.hist(bins=n, legend=False)
    for p in ax.patches:
        if p.get_height()>0:
            ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), 
                                 ha='center', va='center', xytext=(0, 6), textcoords='offset points')
    ax.set_title("Session Duration Histogram", fontweight='bold')
    ax.set_xlabel("Session Duration bins [mins]", fontweight='bold')
    ax.set_ylabel("Frequency", fontweight='bold')
    
    hist, bin_edges= np.histogram(sessionDuration, n)
    cumsum_data = np.cumsum(hist)
    plt.figure()
    plt.title("Distribution of Session Duration", fontweight='bold')
    plt.step(bin_edges[:-1], cumsum_data/cumsum_data[-1])
    plt.xlabel("Session Duration (Minutes)", fontweight='bold')
    plt.ylabel("Cumulative distribution function (CDF)", fontweight='bold')
    plt.show()

def dataStats(allSessions=False):
    current_directory = os.getcwd()
    csv_directory = current_directory + '\\data\\csvFiles'

    try:
        os.chdir(csv_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    
    
    currentFileList = os.listdir(csv_directory)

    usageTypes = [getTypeOfUsage(csvFile) for csvFile in currentFileList]
    barUsageType(usageTypes) # Uncomment for plot
    
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    barFilesUser(usersID) #Uncomment for plot
    
    #usageDrops = []
    usageDrops = [getUsageDrop(csvFile) for csvFile in currentFileList] #None for non Discharging profiles
    barUsageDrop(usageDrops) #Uncomment for plot

    #sessionDuration = []
    sessionDuration = [getSessionDuration(csvFile) for csvFile in currentFileList] #None for non Discharging profiles
    barSessiontDuration(sessionDuration) #Uncomment for plot    

    try:
        os.chdir(current_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    