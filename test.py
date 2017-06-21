#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv2
import numpy as np

def doloop():
    global depth, rgb
    min = 0
    while True:
        # Get a fresh frame
        (depth, _), (rgb, _) = get_depth(), get_video()
        if(depth[353][167] > min):
            min = depth[353][167]
            print(min)
            cv2.circle(rgb, (353, 328), 20, (0, 0, 0), 2, -1)
        # Build a two panel color image
        d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
        da = np.hstack((d3, rgb))
        # Simple Downsample
        cv2.imshow('both', np.array(da[::2, ::2, ::-1]))
        cv2.waitKey(5)


doloop()
