import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import time
print("INITIALIZE")
min_mat = [[2048] * 640 for _ in range(480)]
max_mat = [[0] * 640 for _ in range(480)]
noise = [[0] * 640 for _ in range(480)]
xlist = []
ylist = []
init_depth = []
#Calibration Phase 1 : Getting Maximum and Minimum Noise


def depth_calibration():
    (init_depth, _) = get_depth()
    timer = time.time()
    for hd in range(0, 480):
        for wd in range(0, 640):
            if (init_depth[hd][wd] != 2047):
                min_mat[hd][wd] = init_depth[hd][wd]
                max_mat[hd][wd] = init_depth[hd][wd]
    for i in range(0,1):
        print(i)
        (depthc, _) = get_depth()
        for hd in range(0, 480):
            for wd in range(0, 640):
                if(depthc[hd][wd]!=2047):
                    if depthc[hd][wd] < min_mat[hd][wd]:
                        min_mat[hd][wd] = depthc[hd][wd]
                    if depthc[hd][wd] > max_mat[hd][wd]:
                        max_mat[hd][wd] = depthc[hd][wd]
#Noise Calculation : Max - Min matrix
    for hd in range(0, 480):
        for wd in range(0, 640):
            if(abs(max_mat[hd][wd]-min_mat[hd][wd]) < 200):
                noise[hd][wd] = max_mat[hd][wd] - min_mat[hd][wd]
            else:
                noise[hd][wd] = 0
    timer = time.time() - timer
    print('Calibration Time :',timer)
    return(1)
#Screen Region Calibration


def screen_calibration():
    for i in range(0,5):
        (dst, _) = get_video()
        frame = np.array(dst[::1, ::1, ::-1])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 0, 163])
        upper_red = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        dst = cv2.bitwise_and(frame, frame, mask=mask)
        kernel = np.ones((5, 5), np.float32) / 25
        rgb = cv2.filter2D(dst, -1, kernel)
        gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            epsilon = 0.15 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(cnt)
                xlist.append(x)
                xlist.append(x + w)
                ylist.append(y)
                ylist.append(y + h)
        xlist.pop(xlist.index(min(xlist)))
        xlist.pop(xlist.index(max(xlist)))
        ylist.pop(ylist.index(min(ylist)))
        ylist.pop(ylist.index(max(ylist)))
        result=[[min(xlist),min(ylist)],[max(xlist),max(ylist)]]
        return(result)


def get_depth_object():
    result =[]
    (depth, _) = get_depth()
    cv2.rectangle(depth, (min(xlist), min(ylist)), (max(xlist), max(ylist)), (0, 255, 0), 2)
    for wd in range(min(xlist), max(xlist)):
        for hd in range(min(ylist), max(ylist)):
            if (depth[hd][wd]+8 < min_mat[hd][wd]-noise[hd][wd]) and (depth[hd][wd] <2047) and (depth[hd][wd]!= 0)and (depth[hd][wd]!= 255 and (min_mat[hd][wd]<2047)): #8 is the finger width ( approximatively)
                #print(depth[hd][wd],noise[hd][wd],"***",min_mat[hd][wd])
                result.append([hd,wd])
    return(result)
print("Depth Calibration")
depth_calibration()
print("Screen Calibration")
screen_calibration()
