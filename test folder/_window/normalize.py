import pandas
import numpy as np
import os

def findMaxBrightness(userFileList, window_directory):
    dfFiles = []
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedFiles = pandas.concat(dfFiles)
    maxBrightness = max(255, combinedFiles.Brightness.max()) # Some phones has different max
    # min = 0 | max = maxBrightness
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        df.Brightness = df.Brightness/maxBrightness #(df-df.min())/(df.max()-df.min())
        df.to_csv(fileName, ",", index=False) 
        print(f"Done with file: {fileName}")
        

if __name__ == "__main__":
    print("Normalizing the files...")
    current_directory = os.getcwd()
    window_directory = current_directory + '\\windowFiles'
    currentFileList = os.listdir(window_directory)

    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        findMaxBrightness(userFileList, window_directory) 
    