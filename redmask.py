import cv2
import numpy as np
from freenect import sync_get_depth as get_depth, sync_get_video as get_video


def change_BM(value):
    global BM
    BM = value


def change_GM(value):
    global GM
    GM = value


def change_RM(value):
    global RM
    RM = value
def change_BMM(value):
    global BMM
    BMM = value


def change_GMM(value):
    global GMM
    GMM = value


def change_RMM(value):
    global RMM
    RMM = value

BM = 130
GM = 50
RM = 40
BMM = 200
GMM = 190
RMM = 230
while (1):
    (depth, _), (rgb, _) = get_depth(), get_video()
    orig = np.array(rgb[::2,::2,::-1])
    frame = np.array(rgb[::2,::2,::-1])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([BM, GM, RM])
    upper_red = np.array([BMM, GMM, RMM])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('frame', orig)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)
    cv2.createTrackbar('BMin', 'mask', BM, 255, change_BM)
    cv2.createTrackbar('GMin', 'mask', GM, 255, change_GM)
    cv2.createTrackbar('RMin', 'mask', RM, 255, change_RM)
    cv2.createTrackbar('BMax', 'mask', BMM, 255, change_BMM)
    cv2.createTrackbar('GMax', 'mask', GMM, 255, change_GMM)
    cv2.createTrackbar('RMax', 'mask', RMM, 255, change_RMM)
    k = cv2.waitKey(0) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()
