import pandas
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

    # Brands with 4000 mAh battery capacity
    validBrands = ['xiaomi-Redmi Note 8T', 'Xiaomi-Mi 9T', 'xiaomi-Redmi Note 5', 'Xiaomi-Mi 9 Lite', 'xiaomi-Redmi Note 7', 'samsung-SM-A307FN']
    
    # For every file in the directory ...
    fileList, usersID = [], []
    for f in currentFileList:
        # Get brand of the phone ...
        raw_directory = current_directory + '\\rawFiles'
        rawFileName = f"{raw_directory}\\{f}"
        df = pandas.read_csv(rawFileName)
        brand = df.brandModel[0]
        
        # check if duration is 5 <= duration <= 30  and brand in valid brand names...
        duration = getDuration(f) 
        if duration >=5 and duration <=30 and brand in validBrands:
            fileList.append( f )                # get file
            usersID.append( f.split('-')[0] )   # and userID
    
    # count number of files ...
    freqFileUpload = Counter(usersID)

    # create a list with the users with more than 20 files
    userList = []
    for pair in freqFileUpload.items():
        if pair[1] >= 20:
            userList.append( pair[0] )
    #print(userList)
    
    # for the valid files ...
    dfFiles=[]
    for f in fileList:
        # and the user have more than 20 files
        if f.split('-')[0] in userList: #280 files
            fileName = f"{output_directory}\\{f}"
            df = pandas.read_csv(fileName)
            dfFiles.append(df)
    # Concat all those files in one Dataset un-labeled!
    combinedAllFiles = pandas.concat(dfFiles)
    combinedAllFiles.to_csv("combinedDataset_sameCap.csv", ",", index=False)
