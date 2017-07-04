import numpy as np
import cv2
from freenect import sync_get_depth as get_depth
import time
(init_depth, _) = get_depth()
#Calibration Phase 1
timer = time.time()
min_mat = [[9999] * 640 for _ in range(480)]
max_mat = [[0] * 640 for _ in range(480)]
noise = [[0] * 640 for _ in range(480)]
for i in range(0,2):
    (depthc, _) = get_depth()
    for hd in range(0, 480):
        for wd in range(0, 640):
            #print(i,wd,hd)
            if depthc[hd][wd] < min_mat[hd][wd]:
                min_mat[hd][wd] = depthc[hd][wd]
            if depthc[hd][wd] > max_mat[hd][wd]:
                max_mat[hd][wd] = depthc[hd][wd]
#Noise Calculation
for hd in range(0, 480):
    for wd in range(0, 640):
        noise[hd][wd] = max_mat[hd][wd] - min_mat[hd][wd]
timer = time.time() - timer
print('Calibration Time :',timer)

while True:
    (depth, _) = get_depth()
    cv2.rectangle(depth, (230, 100), (440, 300), (255, 0, 0), 2)
    for wd in range(230,440):
        for hd in range(100,300):
            if (depth[hd][wd]+noise[hd][wd] < init_depth[hd][wd]+8) and (depth[hd][wd] <2047): #8 is the finger width ( approximatively)
                #and(depth[hd][wd]+noise[hd][wd] < max_mat[hd][wd]+1500)
                print(depth[hd][wd],noise[hd][wd],"***",min_mat[hd][wd]-12)
                cv2.circle(depth, (wd, hd), 1, (0, 255, 0), -1)
    d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
    cv2.imshow('Depth', d3)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
