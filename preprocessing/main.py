import pandas
import numpy as np
import os

from helpers import exportData, checkData, normData, splitMixedSessions 
from dataStats import dataStats

if __name__ == "__main__":
    #exportData()
    #checkData()
    #normData()
    splitMixedSessions()
    #dataStats()

    '''
    rateOfChangeSOC = []
    current_directory = os.getcwd()
    csv_directory = current_directory + '\\csvFiles_norm'
    currentFileList = os.listdir(csv_directory)
    for csvFile in currentFileList:
        fileName = csv_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        batteryStatus = df['status'].unique()
        if 3 in batteryStatus and not 2 in batteryStatus:
            initialTime = df.iloc[0]['Timestamp']
            finalTime = df.iloc[-1]['Timestamp'] 
            duration = (finalTime - initialTime) / 60000.0

            initialLevel = df.iloc[0]['level']
            finalLevel = df.iloc[-1]['level']
            # Per 10 seconds (or 5) is too small
            #currentRate = (initialLevel - finalLevel) / df["level"].size
            currentRate = (initialLevel - finalLevel) / duration
            rateOfChangeSOC.append(currentRate)
    print(rateOfChangeSOC)
    '''