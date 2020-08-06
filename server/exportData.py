from pymongo import MongoClient
import pandas
import os

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]

current_directory = os.getcwd()
csv_directory = current_directory + '\\csvFiles_rasp'
#csv_directory = current_directory + '\\csvFiles_PC'
try:
    os.mkdir(csv_directory)                            # Create target Directory
    print("Directory " , csv_directory ,  " Created ") 
except FileExistsError:
    print("Directory " , csv_directory ,  " already exists")

currentFileList = os.listdir(csv_directory)
print("Number of Files: " + str(len(currentFileList)))

client = MongoClient('localhost', 27017)
db = client.mydb_rasp
#db = client.mydb
''' Export all collections of the database to csv files. If a file already exists, skip it. '''
for col in db.list_collection_names():
    fileName = str(col) + ".csv"
    if fileName in currentFileList:
        continue
    print(fileName)
    
    mongoDocs = list(db[col].find())
    docs = pandas.DataFrame(mongoDocs, columns=columnNames)
    fileName = csv_directory + "\\" + fileName
    docs.to_csv(fileName, ",", index=False)                          # CSV delimited by commas
