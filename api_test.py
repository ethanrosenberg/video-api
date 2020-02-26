from __future__ import print_function

from pytube import YouTube
# Standard PySceneDetect imports:
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
# For caching detection metrics and saving/loading to a stats file
import cv2, pafy


import logging
import os
import time
import math
import random, string
from datetime import datetime

import boto3

# For content-aware scene detection:
from scenedetect.detectors.content_detector import ContentDetector
from scenedetect.platform import get_cv2_imwrite_params

def process_youtube_video(youtube_url):
    #url = "https://www.youtube.com/watch?v=BGLTLitLUAo"

    videoPafy = pafy.new(youtube_url)
    best = videoPafy.getbest(preftype="mp4")

    cap=cv2.VideoCapture(best.url)

    sm = SceneManager()

    sm.add_detector(ContentDetector())

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/video_fps
        dur = FrameTimecode(duration, video_fps)

        num_frames = sm.detect_scenes(frame_source=cap, end_time=dur)

        #base_timecode = FrameTimecode('00:00:05', fps=video_fps)
        scene_list = sm.get_scene_list(dur)
        print("Scene List Count: " + str(len(scene_list)))

        result_urls = generate_images(cap, scene_list, 1, "testvid")


    finally:
        cap.release()

    #return urls
    return result_urls


def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def test_scenes(url):
    cap = cv2.VideoCapture(url)
    sm = SceneManager()

    sm.add_detector(ContentDetector())

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/video_fps
        dur = FrameTimecode(duration, video_fps)

        num_frames = sm.detect_scenes(frame_source=cap, end_time=dur)

        #base_timecode = FrameTimecode('00:00:05', fps=video_fps)
        scene_list = sm.get_scene_list(dur)
        print("Scene List Count: " + str(len(scene_list)))

        result_urls = generate_images(cap, scene_list, 1, "testvid")

        #urls = []

        #s3 = boto3.client(
            #'s3',
            #aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            #aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        #)

        #for key in s3.list_objects(Bucket='motion-snapshots')['Contents']:
            #print(key['Key'])
            #urls.append(str(key['Key']))

        #assert num_frames == duration.get_frames()

    finally:
        cap.release()

    #return urls
    return result_urls
    #return " ".join(str(scene_list))

def find_scenes(video_path):
    # type: (str) -> List[Tuple[FrameTimecode, FrameTimecode]]



    url = "https://www.youtube.com/watch?v=BGLTLitLUAo"
    videoPafy = pafy.new(url)
    best = videoPafy.getbest(preftype="webm")

    video=cv2.VideoCapture(best.url)

    video_manager = VideoManager([video])

    # Construct our SceneManager and pass it our StatsManager.
    scene_manager = SceneManager()

    # Add ContentDetector algorithm (each detector's constructor
    # takes detector options, e.g. threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()



    scene_list = []

    try:

        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        #scene_manager.detect_scenes(frame_source=video_manager)
        scene_manager.detect_scenes(frame_source=video_manager)
        #vcap =

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)

        timecodes = []
        # Each scene is a tuple of (start, end) FrameTimecodes.

        print('List of scenes obtained:')
        for i, scene in enumerate(scene_list):
            timecodes.append(scene[0].get_timecode())
            print(
                'Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))





    finally:
        video_manager.release()

    return timecodes

def get_timestamp_to_milliseconds(time_item):
    hours, minutes, seconds = (["0", "0"] + time_item.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)

    return miliseconds

def generate_images(cap, scene_list, num_images = 1, video_name = "testvid"):
    # type: (List[Tuple[FrameTimecode, FrameTimecode]) -> None

    if not scene_list:
        return

    imwrite_param = []
    imwrite_param = [get_cv2_imwrite_params()['jpg'], None]

    #video_manager = VideoManager([url])
    # Reset video manager and downscale factor.
    #video_manager.release()
    #video_manager.reset()
    #video_manager.set_downscale_factor(1)
    #video_manager.start()

    # Setup flags and init progress bar if available.
    completed = True


    scene_num_format = '%0'
    scene_num_format += str(max(3, math.floor(math.log(len(scene_list), 10)) + 1)) + 'd'
    image_num_format = '%0'
    image_num_format += str(math.floor(math.log(num_images, 10)) + 2) + 'd'

    timecode_list = dict()
    image_filenames = dict()

    for i in range(len(scene_list)):
        timecode_list[i] = []
        image_filenames[i] = []

    if num_images == 1:
        for i, (start_time, end_time) in enumerate(scene_list):
            duration = end_time - start_time
            timecode_list[i].append(start_time + int(duration.get_frames() / 2))

    else:
        middle_images = num_images - 2
        for i, (start_time, end_time) in enumerate(scene_list):
            timecode_list[i].append(start_time)

            if middle_images > 0:
                duration = (end_time.get_frames() - 1) - start_time.get_frames()
                duration_increment = None
                duration_increment = int(duration / (middle_images + 1))
                for j in range(middle_images):
                    timecode_list[i].append(start_time + ((j+1) * duration_increment))

            # End FrameTimecode is always the same frame as the next scene's start_time
            # (one frame past the end), so we need to subtract 1 here.
            timecode_list[i].append(end_time - 1)


    urls = []

    #image_timecode = "00:00:06.480"

    #dt_obj = datetime.strptime(str(image_timecode),'%H:%M:%S.%f')
    #millisec = dt_obj.timestamp() * 1000
    #print(str(image_timecode) + str(millisec))

    # Let's use Amazon S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    #for key in s3.list_objects(Bucket='motion-snapshots')['Contents']:
        #print(key['Key'])
        #urls.append(str(key['Key']))



    try:

        for i in timecode_list:
            for j, image_timecode in enumerate(timecode_list[i]):


                cap.set(cv2.CAP_PROP_POS_MSEC,get_timestamp_to_milliseconds(str(image_timecode)))
                #cap.set(cv2.CAP_PROP_POS_MSEC,image_timecode.get_frames())

                #urls.append(str(image_timecode))
                #video_manager.seek(image_timecode)
                #video_manager.grab()
                #ret_val, frame_im = video_manager.retrieve()
                ret,frame = cap.read()                   # Retrieves the frame at the specified second

                if ret:

                    imageName =  randomword(10) + ".jpg"
                    image_string = cv2.imencode('.jpg', frame)[1].tostring()
                    s3.put_object(Bucket="motion-snapshots", Key = "images/" + imageName, Body=image_string, ACL='public-read', ContentType='image/jpeg')
                    #location = boto3.client('s3').get_bucket_location(Bucket="motion-snapshots")['LocationConstraint']
                    url = "https://s3-%s.amazonaws.com/%s/%s" % ("us-east-2", "motion-snapshots", "images/" + imageName)
                    #url = "https://s3-%s.amazonaws.com/%s/%s" % (location, "motion-snapshots", "images/" + imageName)
                    print("Saved Image: " + str(url))
                    urls.append(url)

                else:
                    completed = False
                    break

        #if not completed:
            #logging.error('Could not generate all output images.')
    #except WritingError as er:
        #logging.error(er)

    finally:
        return urls

    #video_manager.release()

    #return " ".join(str(codes))

    #bucket_location = s3_client.get_bucket_location(Bucket='motion-snapshots')
    #url = "https://s3.{0}.amazonaws.com/{1}/{2}".format(s3.meta.endpoint_url, 'motion-snapshots', "images/" + imageName)
                #cv2.imwrite("images/" + imageName, frame)
    #file_url = '%s/%s/%s' % (s3.meta.endpoint_url, "motion-snapshots", "images/" + imageName)
