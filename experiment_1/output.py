from windowUsage import windowLength, isDischarge
import pandas
import numpy as np
import os

# Compute the energy drain for a session/file
def dSOC_dt(df, start, end):
    initialLevel = df.iloc[start]['level']
    finalLevel = df.iloc[end]['level']
    if initialLevel - finalLevel != 0:
        numberOfWindows = (end-1)-start+1
        duration = numberOfWindows * windowLength
        currentRate = ( (initialLevel - finalLevel) * 100) / duration       # [% change] / [second] - duration in second
    else:
        currentRate = 0 # for safety, if level hasn't change.
    
    # each number of Window has the same share at the changing of the level
    dSOC = [currentRate*windowLength for i in range(numberOfWindows)]      # [% change] / [window] - duration in window
    return dSOC

if __name__ == "__main__":
    print("Computing the output ...")
    current_directory = os.getcwd()
    # normFiles has the same Files as windowFiles, but normalized between [0,1]
    norm_directory = current_directory + '\\normFiles'
    # outputFiles has the same Files as normFiles, but added the column for the output
    output_directory = current_directory + '\\outputFiles'
    currentFileList = os.listdir(norm_directory)
    
    for csvFile in currentFileList:
        fileName = norm_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        if isDischarge(df):
            level = df.level
            uniqueLevels = level.unique()
            prevIdx = 0
            output = []
            # For the unique levels of the battery in the SAME session/file ...
            for i in uniqueLevels[1:]:
                # get the index where value of level is changing ...
                currIdx = level.eq(i).idxmax()
                output = output + dSOC_dt(df, prevIdx, currIdx) 
                prevIdx = currIdx
            df = df[0:currIdx]                  # Throw the last row with same battery

            df["output"] = output
            
            fileNameSave = output_directory + "\\" + csvFile
            df.to_csv(fileNameSave, ",", index=False)
            print(f"Done with: {fileNameSave}")
    print("Done with the output.")
