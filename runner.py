from pytube import YouTube
from api_test import test_scenes, process_youtube_video
import json

def run(video_url):
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
