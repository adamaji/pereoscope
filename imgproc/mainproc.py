import sys
import cv2
import math
import numpy as np

SCALE = 500.0

def find_common_shape(frame1, frame2):
    # rows, cols, channels
    s1 = frame1.shape
    s2 = frame2.shape

    return (min(s1[0],s2[0]), min(s1[1],s2[1]), min(s1[2],s2[2]))

def resize_streams(frame1, frame2):
    r = 100.0 / frame.shape[1]
    dim = (100, int(frame.shape[0] * r))
     
    # perform the actual resizing of the frame and show it
    resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)


# align video
def align_streams(frame1, frame2):
    print "TODO"

# distort each
def distort_stream(stream):
    print "TODO"

# stich together
def stich_streams(frame1, frame2):
    print "TODO"

#
#
#
if __name__ == "__main__":
    cap = cv2.VideoCapture("../../local/hackmit3.mp4")
    cap2 = cv2.VideoCapture("../../local/test3.mp4")

    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

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

    while(cap.isOpened() and cap2.isOpened()):
        ret, frame = cap.read()
        ret2, frame2 = cap2.read()

        frame = frame[0:common_shape[0], 0:common_shape[1]]
        frame2 = frame2[0:common_shape[0], 0:common_shape[1]]
         
        # perform the actual resizing of the frame and show it
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        frame2 = cv2.resize(frame2, dim2, interpolation = cv2.INTER_AREA)

        stich = np.concatenate((frame, frame2), axis=1)

        cv2.imshow('frame',stich)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()    
