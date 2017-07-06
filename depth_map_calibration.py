import numpy as np
import cv2
from freenect import sync_get_depth as get_depth
import time

def rawDepthToMeters(depthValue):
    if depthValue < 2047:
      return float(1.0 / (depthValue * -0.0030711016 + 3.3309495161))

(init_depth, _) = get_depth()
#Calibration Phase 1
timer = time.time()
min_mat = [[2048] * 640 for _ in range(480)]
max_mat = [[0] * 640 for _ in range(480)]
for hd in range(0, 480):
    for wd in range(0, 640):
        if (init_depth[hd][wd] != 2047):
            min_mat[hd][wd] = init_depth[hd][wd]
            max_mat[hd][wd] = init_depth[hd][wd]
noise = [[0] * 640 for _ in range(480)]
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

while True:
    (depth, _) = get_depth()
    cv2.rectangle(depth, (230, 100), (440, 300), (255, 0, 0), 2)
    for wd in range(230,440):
        for hd in range(100,300):
            if (depth[hd][wd]+8 < min_mat[hd][wd]-noise[hd][wd]) and (depth[hd][wd] <2047) and (depth[hd][wd]!= 0)and (depth[hd][wd]!= 255 and (min_mat[hd][wd]!=2047)): #8 is the finger width ( approximatively)
                #and(depth[hd][wd]+noise[hd][wd] < max_mat[hd][wd]+1500)
                print(depth[hd][wd],noise[hd][wd],"***",min_mat[hd][wd])
                cv2.circle(depth, (wd, hd), 8, (0, 255, 0), 1)
    d3 = np.dstack((depth, depth, depth)).astype(np.uint8)
    cv2.imshow('Depth', d3)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
