import os
import glob
import pandas as pd

def combineAllUsers(currentFileList):
    combined_csv = []
    for f in currentFileList:
        fileName = test_directory + "\\" + f
        df = pd.read_csv(fileName)
        batteryStatus = df['status'].unique()
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        if 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0:
            combined_csv.append(df)
    return combined_csv

def combinePerUser(UserFileList):
    combined_csv = []
    for f in UserFileList:
        fileName = test_directory + "\\" + f
        df = pd.read_csv(fileName)
        batteryStatus = df['status'].unique()
        initialLevel = df.iloc[0]['level']
        finalLevel = df.iloc[-1]['level'] 
        if 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0:
            combined_csv.append(df)
    return combined_csv

if __name__ == "__main__":
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)

    combined_csv = combineAllUsers(currentFileList)
    combinedAll_csv = pd.concat(combined_csv)       
    combinedAll_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
    
    usersID = [csvFile.split('-')[0] for csvFile in currentFileList]
    usersID = list( set(usersID) ) # Keep the IDs only once
    for user in usersID:
        userFileList = [csvFile for csvFile in currentFileList if user in csvFile]
        combined_csv = combinePerUser(userFileList)
        combinedPer_csv = pd.concat(combined_csv)       
        combinedPer_csv.to_csv( f"{current_directory}\\combined\\{user}-combined_csv.csv", index=False, encoding='utf-8-sig')
