import pandas
import numpy as np
import os

def dSOC_dt(df):
    df = pandas.read_csv(fileName)
    batteryStatus = df['status'].unique()
    
    if 3 in batteryStatus and not 2 in batteryStatus:
        initialTime = df.iloc[0]['Timestamp']
        finalTime = df.iloc[-1]['Timestamp'] 
        duration = (finalTime - initialTime) / 1000.0
        
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level']
        
        if initialLevel - finalLevel != 0:
            currentRate = (initialLevel - finalLevel) / duration
        else:
            currentRate = 0
        return currentRate


if __name__ == "__main__":
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        dSOC = dSOC_dt(df)
        if dSOC:
            time = df["Timestamp"]
            output = [0]
            
            for i in range(1, time.size):
                currOutput = output[-1] + dSOC * (time[i]-time[i-1]) / 1000.0
                #currOutput = dSOC * (time[i]-time[i-1]) / 1000.0
                
                output.append(currOutput)
            #output[0] = output[-1]
            df['output'] = output
            df.to_csv(fileName, ",", index=False)
            print(f"Done with: {fileName}")