# Just For Exposing a specific Port
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Done"