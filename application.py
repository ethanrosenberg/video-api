from flask import Flask
from pytube import YouTube

from api_test import test_scenes

import json


application = Flask(__name__)

@application.route("/")
def hello():
    #return " ".join(find_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/sample_video.mp4"))
    #return YouTube('https://youtu.be/9bZkp7q19f0').streams.first()


    my_json_string = json.dumps(test_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/calamity.mp4"))
    return my_json_string
    #return "Working!!"

    #return test_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/calamity.mp4")
    #return test_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/sample_video.mp4")
    #return test_youtube()


if __name__ == "__main__":
    application.debug = True
    application.run()
