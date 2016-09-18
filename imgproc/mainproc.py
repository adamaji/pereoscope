import sys
import cv2
import math
import numpy as np

import requests
import json
import codecs
import subprocess


BROADCAST_ID_ONE = "1DXxyLaBBpWJM"
BROADCAST_ID_TWO = ""
SCALE = 500.0

WIDTH = 640 # Width of a frame
HEIGHT = 480 # Height of a frame

# FFMPEG Handlers

#
#
#
def get_stream_url(broadcast_id):
    url_to_get = "https://api.periscope.tv/api/v2/accessVideoPublic"
    payload = {"broadcast_id": broadcast_id}
    r = requests.get(url_to_get, params=payload)
    print(r.url)
    # print(r.content)
    #content = str(r.content, 'utf-8')
    content = unicode(r.content, 'utf-8')
    jsondict = json.loads(content)
    print(content)
    return jsondict['hls_url']

#
#
#
def send_stream(url1, url2):
    args = [
        'ffmpeg',
        '-i',
        url1,
        '-i',
        url2,
        '-filter_complex'
        ' "[0:v:0]pad=iw*2:ih[bg]; [bg][1:v:0]overlay=w" ',
        '-map',
        '[vid]',
        '-c:v',
        'libx264',
        '-crf',
        '23',
        '-preset',
        'veryfast',
        'output.mp4'
        ]
    p = subprocess.Popen(args)
    print(" ".join(args))

#
# Returns a frame from the stream
#
def read_stream(url1, url2):
    command1 = [
        'ffmpeg',
        '-i',
        url1,
        '-f', 'image2pipe',
        '-vf',
        'scale={width}:{height}'.format(width=WIDTH, height=HEIGHT),
        '-pix_fmt',
        'rgb24',
        '-vcodec',
        'rawvideo',
        '-']

    command2 = [
        'ffmpeg',
        '-i',
        url2,
        '-f', 'image2pipe',
        '-vf',
        'scale={width}:{height}'.format(width=WIDTH, height=HEIGHT),
        '-pix_fmt',
        'rgb24',
        '-vcodec',
        'rawvideo',
        '-']
    
    pipe1 = subprocess.Popen(command1, stdout=subprocess.PIPE, bufsize=10**8)
    # pipe2 = subprocess.Popen(command2, stdout = subprocess.PIPE, bufsize=10**8)

    while True:


        raw_image = pipe1.stdout.read(WIDTH*HEIGHT*3)
        # print(raw_image)
        # transform the byte read into a numpy array
        image =  np.fromstring(raw_image, dtype='uint8')
        image = image.reshape((WIDTH,HEIGHT,3))

        # TODO: get the other image from the other stream...
        # Use image for both for the moment.
        output_frames(image, image)

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # throw away the data in the pipe's buffer.
    # cv2.imshow('original',image)asdf
    pipe1.stdout.flush()
    pipe1.kill()

    return image

def output_frames(frame, frame2):
    #frame = np.rot90(read_stream(hls_url1, ""), 3)
    #frame2 = np.rot90(read_stream(hls_url2, ""), 3)

    common_shape = find_common_shape(frame, frame2)

    frame = frame[0:common_shape[0], 0:common_shape[1]]
    frame2 = frame2[0:common_shape[0], 0:common_shape[1]] 

    r = SCALE / frame.shape[1]
    dim = (int(SCALE), int(frame.shape[0] * r))

    r2 = SCALE / frame2.shape[1]
    dim2 = (int(SCALE), int(frame2.shape[0] * r2))
     
    # perform the actual resizing of the frame and show it
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    frame2 = cv2.resize(frame2, dim2, interpolation = cv2.INTER_AREA)

    stich = np.concatenate((frame, frame2), axis=1)

    cv2.imshow('frame',stich)

###----------------------------------####

# Frame handlers

#
#
#
def find_common_shape(frame1, frame2):
    # rows, cols, channels
    s1 = frame1.shape
    s2 = frame2.shape

    return (min(s1[0],s2[0]), min(s1[1],s2[1]), min(s1[2],s2[2]))

#
#
#
def resize_streams(frame1, frame2):
    r = 100.0 / frame.shape[1]
    dim = (100, int(frame.shape[0] * r))
     
    # perform the actual resizing of the frame and show it
    resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

#
# align video
#
def align_streams(frame1, frame2):
    print "TODO"

#
# distort each
#
def distort_stream(stream):
    print "TODO"

#
# stich together
#
def stich_streams(frame1, frame2):
    print "TODO"

#
#
#
if __name__ == "__main__":

    hls_url1 = get_stream_url(BROADCAST_ID_ONE) # Me
    hls_url2 = get_stream_url(BROADCAST_ID_ONE) # Adam
    # send_stream(hls_url1, hls_url2)
    # frame = np.rot90(read_stream(hls_url1, ""))
    # frame2 = np.rot90(read_stream(hls_url2, ""))

    read_stream(hls_url1, hls_url2)
    # cap = cv2.VideoCapture("../../local/hackmit3.mp4")
    # cap2 = cv2.VideoCapture("../../local/test3.mp4")

    # ret, frame = cap.read()
    # ret2, frame2 = cap2.read()



    cv2.destroyAllWindows()

    # aligned = False  

    # while(cap.isOpened() and cap2.isOpened()):
    #     ret, frame = cap.read()
    #     ret2, frame2 = cap2.read()

    #     frame = frame[0:common_shape[0], 0:common_shape[1]]
    #     frame2 = frame2[0:common_shape[0], 0:common_shape[1]]
         
    #     # perform the actual resizing of the frame and show it
    #     frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    #     frame2 = cv2.resize(frame2, dim2, interpolation = cv2.INTER_AREA)

    #     stich = np.concatenate((frame, frame2), axis=1)

    #     cv2.imshow('frame',stich)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cap.release()
    # cv2.destroyAllWindows() 
