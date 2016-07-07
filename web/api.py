import json
from flask import Flask
from flask_pymongo import PyMongo

app = Flask('topsecret')
mongo = PyMongo(app)

@app.route('/')
def home():
    return json.dumps({"foo": "bar"})

@app.route('/emails/<id>', methods=['GET'])
def emails_all(id):
    email = mongo.db.email.find_one_or_404({'_id': id})
    return json.dumps(email)

if __name__ == "__main__":
    app.run()