from flask import Flask, request
from runner import run


application = Flask(__name__)

@application.route("/")
def welcome():
    return "Please request /process to get started."

@application.route("/error")
def error():
    return "Error"

@application.route("/process")
def hello():

    try:
        video_url = request.args.get('video_url').strip()
        runner(video_url)

    except Exception as e:
        return "We encountered a problem... error_message => " + str(e)

if __name__ == "__main__":
    application.debug = True
    application.run()
