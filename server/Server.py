from flask import Flask, request
from pymongo import MongoClient
import sys
import datetime

def myPrintWaitress(IP, msg, code):
  BOLD  = '\033[1m'
  RED   = '\033[91m'
  GREEN = '\033[92m' 
  END   = '\033[0m'

  fileOutput = open("output.log", "a")
  dateTimeNow = datetime.datetime.now()
  date = dateTimeNow.strftime("%d/%b/%Y %H:%M:%S")
  if code == 200:
    msg = IP + " - - " + "[" + date + "] " + BOLD + GREEN + msg + END + " - " + str(code) + " -"
  else:
    msg = IP + " - - " + "[" + date + "] " + BOLD + RED + msg + END + " - " + str(code) + " -"

  print(msg)
  fileOutput.write(msg+"\n")
  fileOutput.close()

app = Flask(__name__)
@app.route("/")
def hello():
  return "Hello World!"

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
  if not request.is_json:
    myPrintWaitress(request.remote_addr, "Request wasn't JSON", 400)
    return "Request wasn't JSON", 400                         # Request isn't json, DO NOT proceed.

  header = request.headers.get('name')
  if not header:
    myPrintWaitress(request.remote_addr, "Empty header", 400)
    return "Empty header", 400                                # Request doesn't have the right header, DO NOT proceed. 
  
  content = request.get_json()
  
  contentLength = len(content)
  if contentLength == 0:
    myPrintWaitress(request.remote_addr, "Empty JSON", 400)
    return "Empty JSON", 400                                  # Request doesn't have any items, DO NOT proceed.

#  size = sum([sys.getsizeof(i) for i in content]) / len(content) # 648 bytes 
#  if size < 600:
#    myPrintWaitress(request.remote_addr, "Something went wrong with the file size", 417)
#    return "Something went wrong with the file size", 417     # Request doesn't have the right size, DO NOT proceed. (not exactly 417)
    
  #client = MongoClient('localhost', 27017)
  client = MongoClient('192.168.100.9', 27017)
  db = client.mydb
  col = db[header]                                            # Create new collection, if needed
  if col.count() == 0 and contentLength == 1:
    myPrintWaitress(request.remote_addr, "Only one item", 400)
    return "Only one item", 400                               # New collection and only one item at json, DO NOT proceed.
    
  # Try to write it to the Database
  try:
    post_id = col.insert_many(content)
    myPrintWaitress(request.remote_addr, "JSON received!", 200)
    return "JSON received!", 200
  except:
    myPrintWaitress(request.remote_addr, "Json received but didn't saved", 406)
    return "Json received but didn't saved", 406

if __name__ == "__main__":
  # in the virtual environment pip install waitress
  from waitress import serve
  serve(app, host="0.0.0.0", port=5000, expose_tracebacks=True)
  #app.run("0.0.0.0", "5000")
