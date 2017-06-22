import cv2
import numpy as np
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
while (1):
    (depth, _), (rgb, _) = get_depth(), get_video()
    orig = np.array(rgb[::2,::2,::-1])
    frame = np.array(rgb[::2,::2,::-1])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([150, 40, 40])
    upper_red = np.array([200, 190, 230])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('frame', orig)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()