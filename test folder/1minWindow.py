import pandas
from statistics import mean
import os

if __name__ == "__main__":
    current_directory = os.getcwd()
    test_directory = current_directory + '\\testFiles'
    currentFileList = os.listdir(test_directory)
    
    for csvFile in currentFileList:
        fileName = test_directory + "\\" + csvFile
        df = pandas.read_csv(fileName)
        batteryStatus = df['status'].unique()
        if 3 in batteryStatus and not 2 in batteryStatus:
            sampleFreq = df["SampleFreq"]
            windowFreqs = []
            
            usage, voltage, temperature = df["usage"], df["voltage"], df["temperature"]
            windowUsage, windowVoltage, windowTemperature = [usage[0]], [voltage[0]], [temperature[0]]
            minuteUsage, minuteVoltage, minuteTemperature = [], [], []
            
            timeUntilNow = 0
            for index in range(1, sampleFreq.size):
                timeUntilNow += sampleFreq[index]
                windowFreqs.append( sampleFreq[index] )
                windowUsage.append( usage[index] )
                windowVoltage.append( voltage[index] )
                windowTemperature.append( temperature[index] )
                
                if timeUntilNow >= 60:
                    # Window has the values inside the 1min Window
                    minuteUsage.append( mean(windowUsage) )
                    minuteVoltage.append( mean(windowVoltage) )
                    minuteTemperature.append( mean(windowTemperature) )

                    timeUntilNow -= windowFreqs[0]
                    del windowUsage[0], windowVoltage[0], windowTemperature[0], windowFreqs[0]
            # Create the new dataframe
            df = pandas.DataFrame()
            df["minuteTemperature"] = minuteTemperature
            df["minuteVoltage"] = minuteVoltage
            df["minuteUsage"] = minuteUsage
            
            fileNameSave = current_directory + "\\windowFiles\\" + csvFile
            df.to_csv(fileNameSave, ",", index=False) 
            print(f"Done with file: {fileNameSave}")