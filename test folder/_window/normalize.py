import pandas
import numpy as np
import os

def normalize(userFileList, window_directory, norm_directory):
    dfFiles = []
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedFiles = pandas.concat(dfFiles)
    
    maxBrightness = max(255, combinedFiles.Brightness.max())  # Some phones has different max
    maxVoltage = max(4.2, combinedFiles.voltage.max())        # 4.2 seems good
    maxTemperature = max(45, combinedFiles.temperature.max()) # 45 is already to high
    
    minVoltage = min(3.4, combinedFiles.voltage.min())        # 4.2 seems good
    minTemperature = min(25, combinedFiles.temperature.min()) # 25 seems good
    
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        df.level = df.level/100                                                                 #(df-df.min())/(df.max()-df.min())
        df.usage = df.usage/100                                                                 #(df-df.min())/(df.max()-df.min())
        df.RAM = df.RAM/100                                                                     #(df-df.min())/(df.max()-df.min())
        
        df.Brightness = df.Brightness/maxBrightness                                             #(df-df.min())/(df.max()-df.min())
        df.voltage = (df.voltage - minVoltage) / (maxVoltage -  minVoltage)                     #(df-df.min())/(df.max()-df.min())
        df.temperature = (df.temperature - minTemperature) / (maxTemperature -  minTemperature) #(df-df.min())/(df.max()-df.min())
        
        fileNameSave = f"{norm_directory}\\{f}"
        df.to_csv(fileNameSave, ",", index=False) 
        print(f"Done with file: {fileNameSave}")
        

if __name__ == "__main__":
    print("Normalizing the files...")
    current_directory = os.getcwd()
    window_directory = current_directory + '\\windowFiles'
    norm_directory = current_directory + '\\normFiles'
    currentFileList = os.listdir(window_directory)

    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        normalize(userFileList, window_directory, norm_directory) 
    