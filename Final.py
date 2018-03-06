import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import time


xlist = []
ylist = []
(init_depth, _) = get_depth()
#Calibration Phase 1
timer = time.time()
min_mat = [[2048] * 640 for _ in range(480)]
max_mat = [[0] * 640 for _ in range(480)]
noise = [[0] * 640 for _ in range(480)]
for hd in range(0, 480):
    for wd in range(0, 640):
        if (init_depth[hd][wd] != 2047):
            min_mat[hd][wd] = init_depth[hd][wd]
            max_mat[hd][wd] = init_depth[hd][wd]
for i in range(0,10):
    (depthc, _) = get_depth()
    for hd in range(0, 480):
        for wd in range(0, 640):
            if(depthc[hd][wd]!=2047):
                if depthc[hd][wd] < min_mat[hd][wd]:
                    min_mat[hd][wd] = depthc[hd][wd]
                if depthc[hd][wd] > max_mat[hd][wd]:
                    max_mat[hd][wd] = depthc[hd][wd]
#Noise Calculation
for hd in range(0, 480):
    for wd in range(0, 640):
        if(abs(max_mat[hd][wd]-min_mat[hd][wd]) < 200):
            noise[hd][wd] = max_mat[hd][wd] - min_mat[hd][wd]
        else:
            noise[hd][wd] = 0
timer = time.time() - timer
print('Calibration Time :',timer)
#Screen Region Calibration
for i in range(0,5):
    (dst, _) = get_video()
    # -----------
    orig = np.array(dst[::1, ::1, ::-1])
    frame = np.array(dst[::1, ::1, ::-1])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 0, 183])
    upper_red = np.array([255, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    dst = cv2.bitwise_and(frame, frame, mask=mask)
    # -----------
    kernel = np.ones((5, 5), np.float32) / 25
    rgb = cv2.filter2D(dst, -1, kernel)
    gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for cnt in contours:
        epsilon = 0.15 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(rgb, (x, y), (x + w, y + h), (0, 255, 255), 2)
            xlist.append(x)
            xlist.append(x + w)
            ylist.append(y)
            ylist.append(y + h)
            # cv2.drawContours(rgb, approx, -1, (210, 255, 0), 3)
    xlist.pop(xlist.index(min(xlist)))
    xlist.pop(xlist.index(max(xlist)))
    ylist.pop(ylist.index(min(ylist)))
    ylist.pop(ylist.index(max(ylist)))
while True:
    (depth, _) = get_depth()
    cv2.rectangle(depth, (min(xlist), min(ylist)), (max(xlist), max(ylist)), (0, 255, 0), 2)
    for wd in range(min(xlist), max(xlist)):
        for hd in range(min(ylist), max(ylist)):
            print(wd,hd)
            if (depth[hd][wd]+8 < min_mat[hd][wd]-noise[hd][wd]) and (depth[hd][wd] <2047) and (depth[hd][wd]!= 0)and (depth[hd][wd]!= 255 and (min_mat[hd][wd]<2047)): #8 is the finger width ( approximatively)
                print(depth[hd][wd],noise[hd][wd],"***",min_mat[hd][wd])
                cv2.circle(depth, (wd, hd), 8, (0, 255, 0), 1)
    d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
    cv2.imshow('Depth', d3)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
