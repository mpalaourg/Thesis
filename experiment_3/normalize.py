import pandas
import numpy as np
import os

# Read the files of each user from 'window_directory', find the [per user]
# min and maxs for the variables and normalize the variables between [0,1].
# Then, saved the files at 'norm_directory'.
# For the variables, that min and/or max value weren't calculated, 0 and 100
# were used respectively.
def normalize(userFileList, window_directory, norm_directory):
    dfFiles = []
    # Concat all files of a user, at one dataframe, for finding easily mins and maxs.
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedFiles = pandas.concat(dfFiles)
    
    maxBrightness = max(255, combinedFiles.Brightness.max())  # Some phones has different max Brightness (1023, 2047, 4095)
    maxVoltage = max(4.2, combinedFiles.voltage.max())        # 4.2 is a typical value for a fully charged phone
    maxTemperature = max(45, combinedFiles.temperature.max()) # 45 Celcius is a typical value for high Temperature
    
    minVoltage = min(3.4, combinedFiles.voltage.min())        # 3.4 is a typical value for a fully discharged phone
    minTemperature = min(25, combinedFiles.temperature.min()) # 25 Celcius is a typical value for low Temperature
    
    # Read again each file, normalize the values between [0,1] and save them.
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
    # windowFiles has the same Files as rawFiles, but grouped at time Windows for smoothing
    window_directory = current_directory + '\\windowFiles'
    # normFiles has the same Files as windowFiles, but normalized between [0,1]
    norm_directory = current_directory + '\\normFiles'
    currentFileList = os.listdir(window_directory)

    # Get the user IDs
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        # Get all the files of a user in the directory
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        normalize(userFileList, window_directory, norm_directory) 
    