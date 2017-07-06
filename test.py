#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2
import numpy as np

def doloop():
    global depth, rgb, initdepth
    min = 0
    (initdepth, _) = get_depth()
    while True:
        # Get a fresh frame
        (depth, _), (rgb, _) = get_depth(), get_video()
        #cv2.rectangle(rgb, (230, 100), (440, 300), (255, 0, 0), 2)
        test = np.array(rgb[::2,::2,::-1])
        cv2.imshow('FIRST',test)
        # Build a two panel color image
        d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
        da = np.hstack((d3, rgb))
        # Simple Downsample
        cv2.imshow('both', np.array(da[::2, ::2, ::-1]))
        cv2.waitKey(5)
doloop()
