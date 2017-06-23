import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
global depth, rgb, initdepth
(initdepth, _) = get_depth()
while True:
    (depth,_) = get_depth()
    (dst, _) = get_video()
    #-----------
    orig = np.array(dst[::1, ::1, ::-1])
    frame = np.array(dst[::1, ::1, ::-1])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([150, 40, 40])
    upper_red = np.array([200, 190, 230])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    dst = cv2.bitwise_and(frame, frame, mask=mask)
    #-----------
    kernel = np.ones((5, 5), np.float32) / 25
    rgb = cv2.filter2D(dst, -1, kernel)
    gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(195, 251):
        for j in range(151, 207):
            if(initdepth[j][i]>depth[j][i]+1):
                print(initdepth[j][i], " - ", depth[j][i])
                cv2.circle(rgb, (i, j), 1, (0, 0, 255), -1)
    for cnt in contours:
        epsilon = 0.15 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.drawContours(rgb, approx, -1, (0, 255, 0), 3)
    cv2.imshow('orig', thresh)
    cv2.imshow('rgb',rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

