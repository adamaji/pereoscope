import sys
import cv2
import math
import numpy as np
import os

import requests
import json
import codecs
import subprocess
import Queue as queue
import m3u8

from threading import Thread
from time import sleep

import utils

BROADCAST_ID_LEFT = "1zqKVVOoEXwKB" 
BROADCAST_ID_RIGHT = "1ZkKzWkoErwGv" 

SCALE = 500.0

WIDTH = 1024 # Width of a frame
HEIGHT = 600 # Height of a frame

def main_loop(l_queue, r_queue):

    hls_pl_url_l = utils.get_stream_url(BROADCAST_ID_LEFT) # Me
    hls_pl_url_r = utils.get_stream_url(BROADCAST_ID_LEFT) # Me

    thread1 = Thread(target = read_pl, args = (l_queue, hls_pl_url_l))
    thread1.start()

    # thread1.join()

    thread2 = Thread(target = read_pl, args = (r_queue, hls_pl_url_r))
    thread2.start()

def display_loop(l_queue, r_queue):

    frame_l, t_l = l_queue.get()
    frame_r, t_r = r_queue.get()

    while True:
        # print("OUTPUT\n\n")
        print(r_queue.qsize())


        print(t_r, t_l)

        if t_r < t_l:
            output_frames(frame_l, frame_r)
            frame_r, t_r = r_queue.get()
            sleep(0.05)
        else:
            output_frames(frame_l, frame_r)
            frame_l, t_l = l_queue.get()
            sleep(0.05)

    cv2.destroyAllWindows()

def read_pl(q, pl_uri):

    last_frame = 0

    while True:

        m3obj = m3u8.load(pl_uri)

        devnull = open(os.devnull, 'wb') #python >= 2.4

        for segment in m3obj.segments:

            # print(segment.uri)

            # chunk_1474163371949391788_1430.ts\n <- segment.uri
            frame_number = int(segment.uri.split(".")[0].split("_")[-1])

            if frame_number > last_frame:
                last_frame = frame_number
                print(frame_number)
            else:
                break

            fullpath = segment.base_uri + segment.uri

            #open the segment for reading.
            command = [
                'ffmpeg',
                '-i',
                fullpath,
                '-f', 'image2pipe',
                '-vf',
                'scale={width}:{height}'.format(width=WIDTH, height=HEIGHT),
                '-pix_fmt',
                'rgb24',
                '-vcodec',
                'rawvideo',
                '-']

            pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=devnull, bufsize=10**8)

            while True:

                raw_image = pipe.stdout.read(WIDTH*HEIGHT*3)

                if raw_image == b'':
                    print("Done")
                    break
                
                # print(len(raw_image))
                # transform the byte read into a numpy array
                image = np.fromstring(raw_image, dtype='uint8')
                image = image.reshape((HEIGHT,WIDTH,3))

                # TODO: get the other image from the other stream...
                # Use image for both for the moment.
                timestamp = segment.uri[6:19]
                q.put((image, int(timestamp)))
                # print("Image read")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                pipe.stdout.flush()


        # cv2.imshow('original',image)asdf
        pipe.kill()


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

    # print("RAN\n")

def find_common_shape(frame1, frame2):
    # rows, cols, channels
    s1 = frame1.shape
    s2 = frame2.shape

    return (min(s1[0],s2[0]), min(s1[1],s2[1]), min(s1[2],s2[2]))


if __name__ == "__main__":

    l_queue = queue.Queue()
    r_queue = queue.Queue()

    main_loop(l_queue, r_queue)
    display_loop(l_queue, r_queue)

    thread.join()