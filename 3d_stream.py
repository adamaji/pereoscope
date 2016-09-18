import httplib2
import os
import sys
import datetime
import subprocess
from datetime import datetime

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "client_secrets.json"))

def get_service(args):

	flow = flow_from_clientsecrets("client_secrets.json",
    	scope="https://www.googleapis.com/auth/youtube",
    	message=MISSING_CLIENT_SECRETS_MESSAGE)

	print "WORKS"
	storage = Storage("%s-oauth2.json" % sys.argv[0])
	credentials = storage.get()

	print credentials

	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

	youtube_service = build('youtube', 'v3', http=credentials.authorize(httplib2.Http()))
	return youtube_service


def insert_stream(service, title):

	response = service.liveStreams().insert(

		part="snippet,cdn",
		body=dict(
			snippet=dict(
				title = title
			),
			cdn=dict(
				format="720p",
				ingestionType="rtmp"
			)
		)

	).execute()

	snippet = response["snippet"]
	print "NAME: " + response['cdn']['ingestionInfo']['streamName']
	print "URL: " + response["cdn"]["ingestionInfo"]["ingestionAddress"]

	url_to_send = response["cdn"]["ingestionInfo"]["ingestionAddress"]

	return url_to_send, response['cdn']['ingestionInfo']['streamName']

def create_broadcast(service, args, title):

	print args.start_time
	response = service.liveBroadcasts().insert(

		part = "snippet, status",
		body = dict(
			snippet = dict(
				title = title,
				scheduledStartTime=args.start_time,

			),
			status=dict(
				privacyStatus=args.privacy_status
			)
		)

	).execute()

	print "BROADCAST WORKS"

	snippet = response["snippet"]

	return response["id"]


def bind_broadcast(service, broadcast_id, stream_id):

	response = service.liveBroadcasts().bind(

		part="id, contentDetails",
		id=broadcast_id,
		streamId=stream_id
	).execute()

def send_stream(url):

    args = [
        'ffmpeg',
        '-re',
        '-i',
        'test.mp4',
        '-vcodec',
        'libx264',
        '-preset',
        'veryfast',
        '-maxrate',
        '3000k',
        '-bufsize',
        '6000k',
        '-pix_fmt',
        'yuv420p',
        '-g',
        '50',
        '-tune',
        'zerolatency',
        '-b:v',
        '900k',
        '-f',
        'flv',
        url
        ]

    print "CALLED"
    subprocess.call(args)

if __name__ == "__main__":

	argparser.add_argument("--broadcast-title", help="Broadcast title",
    	default="Stream")
  	argparser.add_argument("--privacy-status", help="Broadcast privacy status",
    	default="public")
  	argparser.add_argument("--start-time", help="Scheduled start time",
    	default='2016-09-18T08:00:00.0Z')
  	argparser.add_argument("--end-time", help="Scheduled end time",
    	default='2017-01-31T00:00:00.000Z')
  	argparser.add_argument("--stream-title", help="Stream title",
    	default="Stream")
  	args = argparser.parse_args()

	service = get_service(args)

	print "WORKS"

	print type(datetime.now())
	url = None
	try:
		#broadcast_id = create_broadcast(service, args, "Stream")
		print "WORKS"
		url, stream_name = insert_stream(service, "Stream3")

		#bind_broadcast(service, broadcast_id, stream_id)
		send_stream(url+"/surf-z5b1-4utp-e6cw")

	except HttpError, e:
		print e.content

	

