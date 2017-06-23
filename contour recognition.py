import numpy as np
import cv2
from freenect import sync_get_video as get_video
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
while True:
    (rgb, _) = get_video()
    fgmask = fgbg.apply(rgb)
    cv2.imshow('backgrondeliminated', fgmask)
    ret, thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    im2, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(rgb, contours, -1, (0,255,0), 3)
    cv2.imshow('orig', rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    #cv2.imshow('final',im)
    #cv2.waitKey(0)

