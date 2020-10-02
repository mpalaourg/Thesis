import pandas
import numpy as np
from sklearn.model_selection import train_test_split
import os

if __name__ == "__main__":
    print("Creating dataset...")
    current_directory = os.getcwd()
    # outputFiles has the same Files as normFiles, but added the column for the output
    output_directory = current_directory + '\\outputFiles'
    currentFileList = os.listdir(output_directory)

    dfFiles = []
    # For every file in the directory ...
    for f in currentFileList:
        # check if belongs to user-1 ...
        if 'fcd4594565a94482bd5b18c6e01ca2a3' in f:
            print(f)
            fileName = f"{output_directory}\\{f}"
            df = pandas.read_csv(fileName)
            dfFiles.append(df)
    # Concat all those files in one Dataset un-labeled!
    combinedAllFiles = pandas.concat(dfFiles)
    combinedAllFiles.to_csv("combinedDataset_user_1.csv", ",", index=False)