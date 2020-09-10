import pandas
import numpy as np
from sklearn.model_selection import train_test_split
import os

if __name__ == "__main__":
    print("Combining the files...")
    current_directory = os.getcwd()
    window_directory = current_directory + '\\windowFiles'
    currentFileList = os.listdir(window_directory)

    dfFiles = []
    for f in currentFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedAllFiles = pandas.concat(dfFiles)
    dfTrain, dfTest = train_test_split(combinedAllFiles, test_size=0.2)
    
    dfTrain.to_csv("combinedTrain_csv.csv", ",", index=False) 
    dfTest.to_csv("combinedTest_csv.csv", ",", index=False) 