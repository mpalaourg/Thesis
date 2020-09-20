import pandas
import numpy as np
from sklearn.model_selection import train_test_split
import os

if __name__ == "__main__":
    print("Combining the files...")
    current_directory = os.getcwd()
    norm_directory = current_directory + '\\normFiles'
    currentFileList = os.listdir(norm_directory)

    dfFiles = []
    for f in currentFileList:
        fileName = f"{norm_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedAllFiles = pandas.concat(dfFiles)
    dfTrain, dfTest = train_test_split(combinedAllFiles, test_size=0.2)
    
    dfTrain.to_csv("combinedTrain_csv.csv", ",", index=False) 
    dfTest.to_csv("combinedTest_csv.csv", ",", index=False) 