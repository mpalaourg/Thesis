from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
  if request.is_json:
    header  = request.headers.get('name')
    content = request.get_json()
    if content:
      client = MongoClient('localhost', 27017)
      db = client.mydb
      col = db[header]   # Create new collection
      
      post_id = col.insert_many(content)
      return "JSON received!", 200
    else:
      return "Empty JSON", 400
  else:
    return "Request wasn't JSON", 400

if __name__ == "__main__":
  app.run("0.0.0.0", "5000")
