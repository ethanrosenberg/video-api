from flask import Flask, request
from pytube import YouTube
from api_test import test_scenes, process_youtube_video

import json



application = Flask(__name__)

@application.route("/")
def welcome():
    return "Please request /process to get started."

@application.route("/error")
def error():
    return "Error"

@application.route("/process")
def hello():
    #return " ".join(find_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/sample_video.mp4"))
    #return YouTube('https://youtu.be/9bZkp7q19f0').streams.first()

    try:

        video_url = request.args.get('video_url').strip()
        print("Submitted video url: " + video_url)

        if video_url is "":
            return "Please submit a video url to process! eg. /process?video_url=http://youtube.com/play?id=9bZkp"
        elif "youtube" in video_url or "youtu.be" in video_url:
            print("Processing youtube video...")
            my_json_string = json.dumps(process_youtube_video(video_url))
            return my_json_string
        else:
            print("Processing normal video...")
            my_json_string = json.dumps(test_scenes(video_url))
            return my_json_string
    except Exception as e:
        return "We encountered a problem... error_message => " + str(e)
    #return "Working!!"

    #return test_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/calamity.mp4")
    #return test_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/sample_video.mp4")
    #return test_youtube()
#@application.route("/youtube")
#def youtube():
    #return " ".join(find_scenes("https://motion-snapshots.s3.us-east-2.amazonaws.com/sample_video.mp4"))
    #return YouTube('https://youtu.be/9bZkp7q19f0').streams.first()
    #https://www.youtube.com/watch?v=CeC199GPwqs

    #my_json_string = json.dumps(process_youtube_video("https://www.youtube.com/watch?v=CeC199GPwqs"))
    #return my_json_string


if __name__ == "__main__":
    application.debug = True
    application.run()
