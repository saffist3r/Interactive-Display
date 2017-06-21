import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
while True:
    (depth,_) = get_depth()
    (dst, _) = get_video()
    kernel = np.ones((4, 4), np.float32) / 25
    rgb = cv2.filter2D(dst, -1, kernel)
    gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        epsilon = 0.15 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.drawContours(rgb, approx, -1, (0, 255, 0), 3)
    print(depth[353][328])
    if (depth[353][328] < 821):
        cv2.circle(rgb, (353, 821), 20, (0, 0, 0), 2, -1)
    cv2.imshow('orig', thresh)
    cv2.imshow('rgb',rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

