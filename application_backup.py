from flask import Flask
from pytube import YouTube


application = Flask(__name__)

@application.route("/")
def hello():
    yt = YouTube('https://www.youtube.com/watch?v=BGLTLitLUAo&t=0s')
    return yt.title

if __name__ == "__main__":
    application.debug = True
    application.run()
