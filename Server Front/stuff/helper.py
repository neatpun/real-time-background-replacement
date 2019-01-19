

import datetime
import cv2
import threading
import time
import tensorflow as tf
import json

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    import Queue
elif PY3:
    import queue as Queue


    
class FPS2:
    def __init__(self, interval):
        self._glob_start = None
        self._glob_end = None
        self._glob_numFrames = 0
        self._local_start = None
        self._local_numFrames = 0
        self._interval = interval
        self.curr_local_elapsed = None
        self.first = False

    def start(self):
        self._glob_start = datetime.datetime.now()
        self._local_start = self._glob_start
        return self

    def stop(self):
        self._glob_end = datetime.datetime.now()

    def update(self):
        self.first = True
        curr_time = datetime.datetime.now()
        self.curr_local_elapsed = (curr_time - self._local_start).total_seconds()
        self._glob_numFrames += 1
        self._local_numFrames += 1
        if self.curr_local_elapsed > self._interval:
          print("> FPS: {}".format(self.fps_local()))
          self._local_numFrames = 0
          self._local_start = curr_time

    def elapsed(self):
        return (self._glob_end - self._glob_start).total_seconds()

    def fps(self):
        return self._glob_numFrames / self.elapsed()
    
    def fps_local(self):
        if self.first:
            return round(self._local_numFrames / self.curr_local_elapsed,1)
        else:
            return 0.0
    
    
class WebcamVideoStream:
# with modifications from https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
    def __init__(self, src, width, height):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.frame_counter = 1
        self.width = width
        self.height = height
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        #Debug stream shape
        self.real_width = int(self.stream.get(3))
        self.real_height = int(self.stream.get(4))
        print("> Start video stream with shape: {},{}".format(self.real_width,self.real_height))
    
    def start(self):
        # start the thread to read frames from the video stream
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            self.frame_counter += 1

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        
    def isActive(self):
        # check if VideoCapture is still Opened
        return self.stream.isOpened

    def resize(self):
        try:
            self.frame = cv2.resize(self.frame, (self.width, self.height)) 
        except:
            print("> Error resizing video stream")
        



