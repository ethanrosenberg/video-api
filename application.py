from flask import Flask
from pytube import YouTube

from api_test import find_scenes


application = Flask(__name__)

@application.route("/")
def hello():
    return " ".join(find_scenes("sample_video.mp4"))

if __name__ == "__main__":
    application.debug = True
    application.run()
