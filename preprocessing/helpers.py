from pymongo import MongoClient
from collections import Counter
import pandas
import numpy as np
import matplotlib.pyplot as plt
import shutil
import os

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]

###################################### EXPORT DATA ####################################
def exportData(VM=False):
    print("Exporting Data ...")
    current_directory = os.getcwd()
    #csv_directory = current_directory + '\\data\\csvFiles_PC'
    csv_directory = current_directory + '\\data\\csvFiles_rasp'
    if VM:
        csv_directory = current_directory + '\\data\\csvFiles_VM'
    
    try:
        os.mkdir(csv_directory)                            # Create target Directory
        print("Directory " , csv_directory ,  " Created ") 
    except FileExistsError:
        print("Directory " , csv_directory ,  " already exists")

    currentFileList = os.listdir(csv_directory)
    print("Number of Files: " + str(len(currentFileList)))

    client = MongoClient('localhost', 27017)
    #db = client.mydb
    db = client.mydb_rasp
    if VM:
        db = client.mydb_VM
    ''' Export all collections of the database to csv files. If a file already exists, skip it. '''
    for col in db.list_collection_names():
        fileName = str(col) + ".csv"
        if fileName in currentFileList:
            continue
        print(fileName)
        
        mongoDocs = list(db[col].find())
        docs = pandas.DataFrame(mongoDocs, columns=columnNames)
        # Some files were written twice. Drop duplicate rows (unique items ALL expect _id)
        docs = docs.drop_duplicates(subset=docs.columns.difference(['_id']))
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

def checkData(VM=False):
    print("Checking Data ...")
    current_directory = os.getcwd()
    #csv_directory = current_directory + '\\data\\csvFiles_PC'
    csv_directory = current_directory + '\\data\\csvFiles_rasp'
    if VM:
        csv_directory = current_directory + '\\data\\csvFiles_VM'

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

###################################### COPY DATA ####################################
def copyData():
    current_directory = os.getcwd()
    # Copy files from PC and rasp to same folder if they does not exist
    for f in os.listdir(current_directory+'\\data\\csvFiles_PC'):
        if not os.path.exists(current_directory+'\\data\\csvFiles\\'+f):
            shutil.copy(current_directory+'\\data\\csvFiles_PC\\'+f, current_directory+'\\data\\csvFiles')
    
    for f in os.listdir(current_directory+'\\data\\csvFiles_rasp'):
        if not os.path.exists(current_directory+'\\data\\csvFiles\\'+f):
            print(f)
            shutil.copy(current_directory+'\\data\\csvFiles_rasp\\'+f, current_directory+'\\data\\csvFiles')
    
    for f in os.listdir(current_directory+'\\data\\csvFiles_VM'):
        if not os.path.exists(current_directory+'\\data\\csvFiles\\'+f):
            print(f)
            shutil.copy(current_directory+'\\data\\csvFiles_VM\\'+f, current_directory+'\\data\\csvFiles')

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
    csv_directory = current_directory + '\\data\\csvFiles'

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
    