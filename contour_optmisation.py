# author : Safwene Ladhari
# The purpose of this module is to create an api to manipulate the Kinect Sensor
#
#
#
import numpy as np
import cv2
from freenect import sync_get_video as get_video
import json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
while True:
    (rgb, _) = get_video()
    orig = np.array(rgb[::1, ::1, ::-1])
    fgmask = fgbg.apply(orig)
    cv2.imshow('backgrondeliminated', fgmask)
    ret, thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    im2, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    index = 0
    f = open("output.json", "w")
    for cnt in contours:
        f.write(index+"")
        if(cv2.arcLength(cnt, True)<250):
            contours.pop(index)
        else:
            index += 1
            hull = cv2.convexHull(cnt)
            for item in cnt:
                f.write(json.dumps(item.tolist()))
            f.close()
            cv2.drawContours(rgb, [hull], -1, (0,255,0),1)
            M = cv2.moments(cnt)
            if(M['m00']!=0):
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.circle(rgb, (cx, cy), 3, (0, 0, 255), -1)
    cv2.imshow('orig', rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break