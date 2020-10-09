import pandas
import numpy as np
from sklearn.model_selection import train_test_split
import os
from collections import Counter

def getDuration(f):
    # rawFiles has the Timestamp
    raw_directory = current_directory + '\\rawFiles'
    rawFileName = f"{raw_directory}\\{f}"
    df = pandas.read_csv(rawFileName)

    initialTime = df.iloc[0]['Timestamp']
    finalTime = df.iloc[-1]['Timestamp'] 
    return (finalTime-initialTime)/60000.0

if __name__ == "__main__":
    print("Creating dataset...")
    current_directory = os.getcwd()
    # outputFiles has the same Files as normFiles, but added the column for the output
    output_directory = current_directory + '\\outputFiles'
    currentFileList = os.listdir(output_directory)

    # For every file in the directory ...
    fileList, usersID = [], []
    for f in currentFileList:
        # check if duration is 5 <= duration <= 30 ...
        duration = getDuration(f) 
        if duration >=5 and duration <=30:
            fileList.append( f )                # get file
            usersID.append( f.split('-')[0] )   # and userID

    # count number of files ...
    freqFileUpload = Counter(usersID)
    # create a list with the users with more than 20 files
    userList = []
    for pair in freqFileUpload.items():
        if pair[1] >= 20:
            userList.append( pair[0] )
    print(userList)
    
    # for the files that is 5 <= duration <= 30 ...
    dfFiles=[]
    for f in fileList:
        # and the user have more than 20 files
        if f.split('-')[0] in userList: #371 files
            fileName = f"{output_directory}\\{f}"
            df = pandas.read_csv(fileName)
            dfFiles.append(df)
    # Concat all those files in one Dataset un-labeled!
    combinedAllFiles = pandas.concat(dfFiles)
    combinedAllFiles.to_csv("combinedDataset_allUsers.csv", ",", index=False)