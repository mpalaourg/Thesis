from pymongo import MongoClient
import pandas
import os

columnNames = [ "_id", "ID", "level", "temperature", "voltage", "technology", "status", "health", "usage",
                "WiFi", "Cellular", "Hotspot", "GPS", "Bluetooth", "RAM", "Brightness", "isInteractive",
                "SampleFreq", "brandModel", "androidVersion", "availCapacityPercentage", "Timestamp" ]

current_directory = os.getcwd()
csv_directory = current_directory + '\\csvFiles'
try:
    os.mkdir(csv_directory)                            # Create target Directory
    print("Directory " , csv_directory ,  " Created ") 
except FileExistsError:
    print("Directory " , csv_directory ,  " already exists")

client = MongoClient('localhost', 27017)
db = client.mydb

for col in db.list_collection_names():
    mongoDocs = list(db[col].find())

    docs = pandas.DataFrame(columns=columnNames)
    for num, doc in enumerate(mongoDocs):
        doc["_id"] = str(doc["_id"])                    # convert ObjectId() to str
        doc_id = doc["_id"]                             # get document _id from dict
        series_obj = pandas.Series( doc, name=doc_id )  # create a Series obj from the MongoDB dict
        docs = docs.append(series_obj)                  # append the MongoDB Series obj to the DataFrame obj
    
    fileName = csv_directory + "\\" + str(col) + ".csv"
    docs.to_csv(fileName, ",")                   # CSV delimited by commas