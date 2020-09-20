import pandas
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def boxplotAll(current_directory):
    dfTrain = pandas.read_csv(f"{current_directory}\\combinedTrain_csv.csv") 
    dfTest  = pandas.read_csv(f"{current_directory}\\combinedTest_csv.csv")
    levelTrain = dfTrain.level
    levelTest = dfTest.level
    
    fig, axes = plt.subplots(1,2)
    sns.boxplot(levelTrain, ax=axes[0])
    axes[0].set_title("Train dataset")
    axes[0].set_xlabel("Battery level")
    sns.boxplot(levelTest, ax=axes[1])
    axes[1].set_title("Test dataset")
    axes[1].set_xlabel("Battery level")
    plt.show()

def boxplotUser(userFileList, window_directory,):
    dfFiles = []
    for f in userFileList:
        fileName = f"{window_directory}\\{f}"
        df = pandas.read_csv(fileName)
        dfFiles.append(df)
    combinedFiles = pandas.concat(dfFiles)
    level = combinedFiles.level
    
    user = f.split('-')[0]
    sns.boxplot(level)
    plt.title(user)
    plt.xlabel("Battery level")
    plt.show()
    
if __name__ == "__main__":
    current_directory = os.getcwd()
    #boxplotAll(current_directory)

    window_directory = current_directory + "//windowFiles"
    currentFileList = os.listdir(window_directory)
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        if len(userFileList)> 50:
            boxplotUser(userFileList, window_directory) 