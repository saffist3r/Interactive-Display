# author : Safwene Ladhari
# The purposeof this module is to create an api to manipulate the Kinect Sensor
#
#
#
import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import time
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
min_mat = [[2048] * 640 for _ in range(480)]
max_mat = [[0] * 640 for _ in range(480)]
noise = [[0] * 640 for _ in range(480)]
xlist = []
ylist = []
init_depth = []
def screen_calibration():
    for i in range(0,5):
        (dst, _) = get_video()
        frame = np.array(dst[::1, ::1, ::-1])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 0, 240])
        upper_red = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        dst = cv2.bitwise_and(frame, frame, mask=mask)
        kernel = np.ones((5, 5), np.float32) / 25
        rgb = cv2.filter2D(dst, -1, kernel)
        gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        index = 0
        for cnt in contours:
            epsilon = 0.15 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if cv2.arcLength(approx, True) < 15:
                contours.pop(index)
            else:
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    xlist.append(x)
                    xlist.append(x + w)
                    ylist.append(y)
                    ylist.append(y + h)
                    index += 1
        xlist.pop(xlist.index(min(xlist)))
        xlist.pop(xlist.index(max(xlist)))
        ylist.pop(ylist.index(min(ylist)))
        ylist.pop(ylist.index(max(ylist)))
        result = [[min(xlist), min(ylist)], [max(xlist), max(ylist)]]
        return result


def depth_calibration():
    (init_depth, _) = get_depth()
    timer = time.time()
    for hd in range(0, 480):
        for wd in range(0, 640):
            if (init_depth[hd][wd] != 2047):
                min_mat[hd][wd] = init_depth[hd][wd]
                max_mat[hd][wd] = init_depth[hd][wd]
    for i in range(0, 5):
        print(i)
        (depthc, _) = get_depth()
        for hd in range(0, 480):
            for wd in range(0, 640):
                if (depthc[hd][wd] != 2047):
                    if depthc[hd][wd] < min_mat[hd][wd]:
                        min_mat[hd][wd] = depthc[hd][wd]
                    if depthc[hd][wd] > max_mat[hd][wd]:
                        max_mat[hd][wd] = depthc[hd][wd]
                        # Noise Calculation : Max - Min matrix
    for hd in range(0, 480):
        for wd in range(0, 640):
            if (abs(max_mat[hd][wd] - min_mat[hd][wd]) < 200):
                noise[hd][wd] = max_mat[hd][wd] - min_mat[hd][wd]
            else:
                noise[hd][wd] = 0
    timer = time.time() - timer
    print('Calibration Time :', timer)
    return (1)


screen_calibration()
depth_calibration()
while True:
    (rgb, _) = get_video()
    (depth, _) = get_depth()
    orig = np.array(rgb[::1, ::1, ::-1])
    fgmask = fgbg.apply(orig)
    cv2.imshow('backgrondeliminated', fgmask)
    ret, thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    im2, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    index = 0
    result = []
    curr = time.time();
    for cnt in contours:
        for node in cnt:
            for elem in node:
                result.append(elem)
                y = elem[0].astype(int)
                x = elem[1].astype(int)
                if (y > min(xlist)) and (y < max(xlist)) and (x > min(ylist)) and (x < max(ylist)):
                    if (depth[x][y] + 8 < min_mat[x][y] - noise[x][y]) and (depth[x][y] < 2047) and (
                                depth[x][y] != 0) and (depth[x][y] != 255 and (min_mat[x][y] < 2047)):
                        result.append([x, y])
                        index += 1
                        hull = cv2.convexHull(cnt)
                        cv2.drawContours(rgb, [hull], -1, (0, 255, 0), -1)
                        M = cv2.moments(cnt)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            cv2.circle(rgb, (cx, cy), 3, (0, 0, 255), -1)
    print(int(round((time.time()-curr) * 1000)))
    cv2.imshow('orig', rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
