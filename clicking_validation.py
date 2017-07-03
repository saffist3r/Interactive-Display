# author : Safwene Ladhari
# The purpose of this module is to create an api to manipulate the Kinect Sensor
#
#
#
import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import json

fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
(init_depth, _) = get_depth()
while True:
    (depth, _), (rgb, _) = get_depth(), get_video()
    orig = np.array(rgb[::1, ::1, ::-1])
    fgmask = fgbg.apply(orig)
    cv2.imshow('No Background', fgmask)
    ret, thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    im2, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    index = 0
    for cnt in contours:
        if cv2.arcLength(cnt, True) < 250:
            contours.pop(index)
        else:
            index += 1
            hull = cv2.convexHull(cnt)
            for item in cnt:
                #cont.add_item(item[0][1],item[0][0],depth[item[0][1]][item[0][0]])
                #print(json.dumps(item.tolist()))
                #print(depth[item[0][1]][item[0][0]])
                if(depth[item[0][1]][item[0][0]] < init_depth[item[0][1]][item[0][0]]):
                    print("Clicked")
            cv2.drawContours(orig, [hull], -1, (0, 255, 0), 3)
            M = cv2.moments(cnt)
            if M['m00']!= 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                print(depth[cy][cx])
                cv2.circle(orig, (cx, cy), 3, (0, 0, 255), -1)
    cv2.imshow('orig', orig)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
