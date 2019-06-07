import os, sys, re, time, random
import threading
import signal
import ntpath
import socket


FPS = 30
SIZE_X = 2048
SIZE_Y = 2048
EXPORT_FORMAT = ".mp4"
EXPORT_NAME = "test"
CODEC = "libx264"
COMPRESSION_QUALITY = 25
IMAGE_FORMAT = "pic%04d.png"  #looking for images with 4 digit padding.  e.g. pic0001, pic0002, etc.


# This video conversion source file will take in an n x n series of .png images and convert it to an .mp4
# file used for viewing on DHMx as well as save on the file system.

# Convert a series of frames at variable fps (default 30) to a lossy *.mp4 format
#os.system("ffmpeg -r 60 -f image2 -s 1920x1080 -i pic%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4")
def img_to_mp4(fps=FPS, size_x=SIZE_X, size_y=SIZE_Y, export_format=EXPORT_FORMAT, export_name=EXPORT_NAME, codec=CODEC, compression_quality=COMPRESSION_QUALITY,image_format=IMAGE_FORMAT):

   os.system("ffmpeg -r {0} -f image2 -s {1}x{2} -i {3} -vcodec {4} -crf {5}  -pix_fmt yuv420p {6}.{7}".format(\
        fps,\
        size_x, \
        size_y, \
        image_format, \
        codec, \
        compression_quality, \
        export_name, \
        export_format))
