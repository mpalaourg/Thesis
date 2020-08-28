from pymongo import MongoClient
from collections import Counter
import pandas
import numpy as np
import matplotlib.pyplot as plt
import shutil
import os

# Initialize Range Dictionaries #
levelRange = {"min" : 0, "max" : 100}
temperatureRange = {"min" : 0, "max" : 100}
voltageRange = {"min" : 0, "max" : 100}
usageRange = {"min" : 0, "max" : 100}
ramRange = {"min" : 0, "max" : 100}
brightnessRange = {"min" : 0, "max" : 100}
capacityRange = {"min" : 0, "max" : 100}

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]

###################################### EXPORT DATA ####################################
def exportData():
    print("Exporting Data ...")
    current_directory = os.getcwd()
    csv_directory = current_directory + '\\data\\csvFiles_rasp'
    #csv_directory = current_directory + '\\data\\csvFiles_PC'
    try:
        os.mkdir(csv_directory)                            # Create target Directory
        print("Directory " , csv_directory ,  " Created ") 
    except FileExistsError:
        print("Directory " , csv_directory ,  " already exists")

    currentFileList = os.listdir(csv_directory)
    print("Number of Files: " + str(len(currentFileList)))

    client = MongoClient('localhost', 27017)
    db = client.mydb_rasp
    #db = client.mydb
    ''' Export all collections of the database to csv files. If a file already exists, skip it. '''
    for col in db.list_collection_names():
        fileName = str(col) + ".csv"
        if fileName in currentFileList:
            continue
        print(fileName)
        
        mongoDocs = list(db[col].find())
        docs = pandas.DataFrame(mongoDocs, columns=columnNames)
        fileName = csv_directory + "\\" + fileName
        docs.to_csv(fileName, ",", index=False)                          # CSV delimited by commas
    print("Export Data: DONE!\n")

###################################### CHECK DATA ####################################
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

def checkData():
    print("Checking Data ...")
    current_directory = os.getcwd()
    csv_directory = current_directory + '\\data\\csvFiles_rasp'
    #csv_directory = current_directory + '\\data\\csvFiles_PC'
    try:
        os.chdir(csv_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    

    if checkDiffLevel(csv_directory):
        print("All Good with the Battery level dropping.")
    
    if samplingPeriod(csv_directory):
        print("All Good with the Sampling Frequency")
    
    try:
        os.chdir(current_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    
    print("Check Data: DONE!\n")

###################################### NORMALIZE DATA ####################################
def findMinimum(field, userFileList, csv_directory):
    userFileMin = []
    for csvFile in userFileList:
        fileName = csv_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        userFileMin.append( df[field].min() )
        if df[field].min() < 0:
            print(fileName)
    return max( min(userFileMin), 0)

def findMaximum(field, userFileList, csv_directory):
    userFileMax = []
    for csvFile in userFileList:
        fileName = csv_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        userFileMax.append( df[field].max() )
    return max(userFileMax)

def normalize(userFileList, csv_directory, csvNorm_directory):
    for csvFile in userFileList:
        fileNameRead = csv_directory + "\\" + csvFile
        df = pandas.read_csv(fileNameRead)
        df["level"] = (df["level"] - levelRange["min"]) / (levelRange["max"] - levelRange["min"])        
        df["temperature"] = (df["temperature"] - temperatureRange["min"]) / (temperatureRange["max"] - temperatureRange["min"])
        df["voltage"] = (df["voltage"] - voltageRange["min"]) / (voltageRange["max"] - voltageRange["min"])
        df["usage"] = (df["usage"] - usageRange["min"]) / (usageRange["max"] - usageRange["min"])
        df["RAM"] = (df["RAM"] - ramRange["min"]) / (ramRange["max"] - ramRange["min"])
        df["Brightness"] = (df["Brightness"] - brightnessRange["min"]) / (brightnessRange["max"] - brightnessRange["min"])
        df["availCapacityPercentage"] = (df["availCapacityPercentage"] - capacityRange["min"]) / (capacityRange["max"] - capacityRange["min"])
        
        fileNameSave = csvNorm_directory + "\\" + csvFile
        df.to_csv(fileNameSave, ",", index=False)                          # CSV delimited by commas

def normData():
    print("Normalizing Data ...")
    current_directory = os.getcwd()
    # Copy files from PC and rasp to same folder if they does not exist
    for f in os.listdir(current_directory+'\\data\\csvFiles_PC'):
        if not os.path.exists(current_directory+'\\data\\csvFiles\\'+f):
            shutil.copy(current_directory+'\\data\\csvFiles_PC\\'+f, current_directory+'\\data\\csvFiles')
    
    for f in os.listdir(current_directory+'\\data\\csvFiles_rasp'):
        if not os.path.exists(current_directory+'\\data\\csvFiles\\'+f):
            print(f)
            shutil.copy(current_directory+'\\data\\csvFiles_rasp\\'+f, current_directory+'\\data\\csvFiles')
  
    csvNorm_directory = current_directory + '\\data\\csvFiles_norm'
    if os.path.exists(csvNorm_directory):
        shutil.rmtree(csvNorm_directory)
        print("Previous normalized folder was deleted!")
    else:
        print("Nothing there to delete!")
    
    try:
        os.mkdir(csvNorm_directory)                            # Create target Directory
        print("Directory " , csvNorm_directory ,  " Created ") 
    except FileExistsError:
        print("Directory " , csvNorm_directory ,  " already exists")

    csv_directory = current_directory + '\\data\\csvFiles'
    currentFileList = os.listdir(csv_directory)
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        
        temperatureRange["min"] = findMinimum('temperature', userFileList, csv_directory)
        voltageRange["min"] = findMinimum('voltage', userFileList, csv_directory)
        usageRange["min"] = findMinimum('usage', userFileList, csv_directory)
        
        temperatureRange["max"] = findMaximum('temperature', userFileList, csv_directory)
        voltageRange["max"] = findMaximum('voltage', userFileList, csv_directory)
        brightnessRange["max"] = findMaximum('Brightness', userFileList, csv_directory)
        
        normalize(userFileList, csv_directory, csvNorm_directory)
        print("The data of " + user + " was normalized successfully!")
    print("Normalize Data: DONE!\n")
    
###################################### SPLIT MIXED SESSIONS ####################################
TYPE_MIXED = 0
TYPE_DISCHARGING = 1
TYPE_CHARGING = 2

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

def splitMixedSessions():
    print("Spliting Mixed Sessions ...")
    current_directory = os.getcwd()
    csv_directory = current_directory + '\\data\\csvFiles_norm'

    try:
        os.chdir(csv_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()    
    
    currentFileList = os.listdir(csv_directory)
    for csvFile in currentFileList:
        if getTypeOfUsage(csvFile) == TYPE_MIXED:
            df = pandas.read_csv(csvFile)
            ''' https://towardsdatascience.com/pandas-dataframe-group-by-consecutive-same-values-128913875dba
                Create a new column shift down the original values by 1 row
                Compare the shifted values with the original values. True if they are equal, otherwise False
                Using cumsum() on the boolean column, the resulted column can be used for grouping by
            '''
            for k, v in df.groupby( (df['status'].shift() != df['status']).cumsum() ):
                batteryStatus = v['status'].unique()
                initialLevel = df.iloc[0]['level']
                finalLevel = df.iloc[-1]['level'] 

                if (batteryStatus == 3) and (finalLevel - initialLevel < 0):
                    fileNameSave = f"{csvFile.split('.')[0]}_v{k}.{csvFile.split('.')[1]}" 
                    #print(fileNameSave)
                    v.to_csv(fileNameSave, ",", index=False)                          # CSV delimited by commas
    try:
        os.chdir(current_directory)
        print("Current Working Directory " , os.getcwd())
    except OSError:
        print("Can't change the Current Working Directory")
        exit()
    print("Split Mixed Sessions: DONE!\n")
    