import pandas
import os
import numpy as np
from math import floor
from collections import Counter
import pickle

#windowLength = 30   #seconds
#windowDist   = 15   # seconds

# Check if a file is a Discharge Session and battery has drop
def isDischarge(df):
    batteryStatus = df['status'].unique()
    initialLevel = df.iloc[0]['level']
    finalLevel = df.iloc[-1]['level'] 
    return 3 in batteryStatus and not 2 in batteryStatus and finalLevel-initialLevel < 0
    
# Return the index of the sample that is 'distance' seconds away
def getIndex(start, time, distance):
    for idx in range(start, time.size):
        deltaT = round( (time[idx] - time[start]) / 1000.0 )
        if deltaT >= distance:
            return idx
    # for the last elements window won't be 'distance' seconds long
    return idx      

# Check the percentage of True and return the round value of the percentage.
def isEnable(column):
    enable = column.sum()/column.size
    enable = round(enable)
    return bool(enable)

# Return the category with most appearances in the window
def majorityVote(votes):
    vote_count = Counter(votes)
    majority = vote_count.most_common(1)
    return majority[0][0]

if __name__ == "__main__":
    print("Gettting the window measurements ...")
    current_directory = os.getcwd()
    raw_directory = current_directory + '\\rawFiles'
    currentFileList = os.listdir(raw_directory)

    allStdUsage, allStdRAM = [], []
    allStdDiffUsage, allStdDiffRAM = [], []
    allStdDiff2Usage, allStdDiff2RAM = [], []
    allRoughnessUsage, allRoughnessRAM = [], []
    lengths = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for windowLength in lengths:

        stdUsage, stdRAM = [], []
        stdDiffUsage, stdDiffRAM = [], []
        stdDiff2Usage, stdDiff2RAM = [], []
        roughnessUsage, roughnessRAM = [], []
        for csvFile in currentFileList:
            fileName = raw_directory + "\\" + csvFile
            df = pandas.read_csv(fileName)

            if isDischarge(df):
                level = df.level
                voltage = df.voltage
                temperature = df.temperature 
                status = df.status
                health = df.health
                usage = df.usage
                wifi = df.WiFi
                GPS = df.GPS 
                cellular = df.Cellular
                hotspot = df.Hotspot
                interactive = df.isInteractive 
                bluetooth = df.Bluetooth
                RAM = df.RAM
                brightness = df.Brightness
                time = df.Timestamp
                
                start = 0 # start of first window
                windowTemperature, windowVoltage, windowUsage, windowRAM = [], [], [], []
                windowLevel, windowStatus, windowHealth, windowBrightness = [], [], [], []
                windowWiFi, windowCellular, windowHotspot, windowGPS, windowBluetooth, windowInteractive  = [], [], [], [], [], []
                while start != time.size-1:
                    end = getIndex(start=start, time=time, distance=windowLength)
                    # voltage, temperature, usage, RAM -> mean | boolean -> percentage of true - round to 0 or 1 - False or True
                    # status and heath -> majority vote - Categorical data 
                    windowLevel.append( floor(level[start:end].mean()) )
                    windowVoltage.append( round(voltage[start:end].mean(), 4) )
                    windowTemperature.append( round(temperature[start:end].mean(), 4) )
                    windowStatus.append( majorityVote(status[start:end]) )
                    windowHealth.append( majorityVote(health[start:end]) )
                    windowUsage.append( round(usage[start:end].mean(), 4) )
                    windowWiFi.append( isEnable(wifi[start:end]) )
                    windowCellular.append( isEnable(cellular[start:end]) )
                    windowHotspot.append( isEnable(hotspot[start:end]) )
                    windowGPS.append( isEnable(GPS[start:end]) )
                    windowBluetooth.append( isEnable(bluetooth[start:end]) )
                    windowRAM.append( round(RAM[start:end].mean(), 4) )
                    windowBrightness.append( round(brightness[start:end].mean(), 0) )
                    windowInteractive.append( isEnable(interactive[start:end]) )
                    
                    #start = getIndex(start=start, time=time, distance=windowDist)
                    prev_start = start
                    start = end
                # Create the new dataframe
                dfSave = pandas.DataFrame()
                dfSave["level"] = windowLevel
                dfSave["temperature"] = windowTemperature
                dfSave["voltage"] = windowVoltage
                dfSave["status"] = windowStatus
                dfSave["health"] = windowHealth
                dfSave["usage"] = windowUsage
                dfSave["WiFi"] = windowWiFi
                dfSave["Cellular"] = windowCellular
                dfSave["Hotspot"] = windowHotspot
                dfSave["GPS"] = windowGPS
                dfSave["Bluetooth"] = windowBluetooth
                dfSave["RAM"] = windowRAM
                dfSave["Brightness"] = windowBrightness
                dfSave["isInteractive"] = windowInteractive
                
                fileNameSave = f"{current_directory}\\windowFiles_{windowLength}\\{csvFile}"
                dfSave.to_csv(fileNameSave, ",", index=False) 
                print(f"Done with file: {fileNameSave}")

                # Get the std of the variables
                stdUsage.append( np.std(windowUsage) )
                stdRAM.append( np.std(windowRAM) )
                # Get the std of the diff of the variables
                windowUsage = pandas.Series(windowUsage)
                diffUsage = windowUsage.diff().fillna(value=0)
                stdDiffUsage.append( np.std(diffUsage) )

                windowRAM = pandas.Series(windowRAM)
                diffRAM = windowRAM.diff().fillna(value=0)
                stdDiffRAM.append( np.std(diffRAM) )
        
                # Get the std of the second diff of the variables
                diff2Usage = diffUsage.diff().fillna(value=0)
                stdDiff2Usage.append( np.std(diff2Usage) )
                
                diff2RAM = diffRAM.diff().fillna(value=0)
                stdDiff2RAM.append( np.std(diff2RAM) )

                #Get roughness
                roughnessUsage.append( np.sum( np.square(diff2Usage)/4 ) )
                roughnessRAM.append( np.sum( np.square(diff2RAM)/4 ) )
        allStdUsage.append(stdUsage)
        allStdRAM.append(stdRAM)
        allStdDiffUsage.append(stdDiffUsage)
        allStdDiffRAM.append(stdDiffRAM)
        allStdDiff2Usage.append(stdDiff2Usage)
        allStdDiff2RAM.append(stdDiff2RAM)
        allRoughnessUsage.append(roughnessUsage)
        allRoughnessRAM.append(roughnessRAM)

        print(f"Done with length = {windowLength}")
    with open("stdUsage.pickle","wb") as f:
        pickle.dump(allStdUsage, f)
    with open("stddiffUsage.pickle","wb") as f:
        pickle.dump(allStdDiffUsage, f)
    with open("stddiff2Usage.pickle","wb") as f:
        pickle.dump(allStdDiff2Usage, f)
    with open("roughUsage.pickle","wb") as f:
        pickle.dump(allRoughnessUsage, f)
    
    with open("stdRAM.pickle","wb") as f:
        pickle.dump(allStdRAM, f)
    with open("stddiffRAM.pickle","wb") as f:
        pickle.dump(allStdDiffRAM, f)
    with open("stddiff2RAM.pickle","wb") as f:
        pickle.dump(allStdDiff2RAM, f)
    with open("roughRAM.pickle","wb") as f:
        pickle.dump(allRoughnessRAM, f)
        