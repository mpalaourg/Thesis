from flask import Flask, request
from pymongo import MongoClient
import sys

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
  if not request.is_json:
    return "Request wasn't JSON", 400                         # Request isn't json, DO NOT proceed.

  header = request.headers.get('name')
  if not header:
    return "Empty header", 400                                # Request doesn't have the right header, DO NOT proceed. 
  
  content = request.get_json()
  size = sum([sys.getsizeof(i) for i in content])
  if size < 648:
    return "Something went wrong with the file size", 400     # Request doesn't have the right size, DO NOT proceed.
  
  contentLength = len(content)
  if contentLength == 0:
    return "Empty JSON", 400                                  # Request doesn't have any items, DO NOT proceed.
    
  client = MongoClient('localhost', 27017)
  db = client.mydb
  col = db[header]                                            # Create new collection, if needed
  if col.count() == 0 and contentLength == 1:
    return "Only one item", 400                               # New collection and only one item at json, DO NOT proceed.
    
  # Try to write it to the Database
  try:
    post_id = col.insert_many(content)
    return "JSON received!", 200
  except:
    return "Json received but didn't saved", 406

if __name__ == "__main__":
  # in the virtual environment pip install waitress
  #from waitress import serve
  #serve(app, host="0.0.0.0", port=5000)
  app.run("0.0.0.0", "5000")
