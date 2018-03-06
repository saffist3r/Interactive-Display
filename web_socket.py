import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.web import Application, asynchronous, RequestHandler
from tornado.ioloop import IOLoop
from tornado import gen
import tornado.web
import socket
import numpy as np
import cv2
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import time
import toro
from multiprocessing.pool import ThreadPool
print("***INITIALIZING***")
width = 480
height = 640
min_mat = [[2048] * height for _ in range(width)]
max_mat = [[0] * height for _ in range(width)]
noise = [[0] * height for _ in range(width)]
xlist = []
ylist = []
init_depth = []
contour_list = []
depth_list = []
center_list = []
fgbg = cv2.createBackgroundSubtractorMOG2()
_workers = ThreadPool(10)
last_message = "TEST"
marge_noise = 200
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes.
'''
closed = False

#Calibration Phase 1 : Getting Maximum and Minimum Noise


def depth_calibration():
    (init_depth, _) = get_depth()
    timer = time.time()
    for hd in range(0, width):
        for wd in range(0, height):
            if (init_depth[hd][wd] != 2047):
                min_mat[hd][wd] = init_depth[hd][wd]
                max_mat[hd][wd] = init_depth[hd][wd]
    for i in range(0,5):
        print(i)
        (depthc, _) = get_depth()
        for hd in range(0, width):
            for wd in range(0, height):
                if(depthc[hd][wd]!=2047):
                    if depthc[hd][wd] < min_mat[hd][wd]:
                        min_mat[hd][wd] = depthc[hd][wd]
                    if depthc[hd][wd] > max_mat[hd][wd]:
                        max_mat[hd][wd] = depthc[hd][wd]
#Noise Calculation : Max - Min matrix
    for hd in range(0, width):
        for wd in range(0, height):
            if(abs(max_mat[hd][wd]-min_mat[hd][wd]) < marge_noise):
                noise[hd][wd] = max_mat[hd][wd] - min_mat[hd][wd]
            else:
                noise[hd][wd] = 0
    timer = time.time() - timer
    print('Calibration Time :', timer)
    return(1)
#Screen Region Calibration


def screen_calibration():
    for i in range(0, 5):
        (dst, _) = get_video()
        frame = np.array(dst[::1, ::1, ::-1])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 0, 180])
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
        result = [[min(xlist), min(ylist)], [max(xlist), max(ylist)]]
        return result


def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)

class communication_status():
    def __init__(self):
        self.closed = False
    def get_closed(self):
        return self.closed
    def set_closed(self,closed_value):
        self.closed = closed_value
        print(self.closed)

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'STATE : New Connection'

    def on_message(self, message):
        print("STATE : MESSAGE RECIEVED")
        if (message == "edges"):
            self.write_message(str(get_screen_params()))
            print("***Edges Sent ***")
        elif (message == "go"):
            print(status.get_closed())
            while True:
                print("*** sending Contour ***")
                (depth, _) = get_depth()
                (rgb, _) = get_video()
                orig = np.array(rgb[::1, ::1, ::-1])
                fgmask = fgbg.apply(orig)
                ret, thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                kernel = np.ones((5, 5), np.uint8)
                erosion = cv2.erode(thresh, kernel, iterations=1)
                im2, contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                index = 0
                for cnt in contours:
                    for node in cnt:
                        for elem in node:
                            y = elem[0].astype(int)
                            x = elem[1].astype(int)
                            if (y > min(xlist)) and (y < max(xlist)) and (x > min(ylist)) and (x < max(ylist)):
                                if (depth[x][y] + 8 < min_mat[x][y] - noise[x][y]) and (depth[x][y] < 2047) and (
                                            depth[x][y] != 0) and (depth[x][y] != 255 and (min_mat[x][y] < 2047)):
                                    contour_list.append([x, y])
                                    index += 1
                if (len(contour_list) !=0):
                    self.write_message(str(contour_list))

    def on_close(self):
        print 'STATE : Connection Closed'

    def check_origin(self, origin):
        return True
def get_screen_params():
    return([[min(xlist), min(ylist)], [max(xlist), max(ylist)]])
class WSREQHandler(tornado.websocket.WebSocketHandler):
    def on_close(self):
        print("STATE Command : ")
    def on_open(self):
        print("STATE Command : ")
    def on_message(self, message):
        if(message =="open"):
            status.set_closed(False)
        elif(message == "close"):
            status.set_closed(True)
        print(message)

    def check_origin(self, origin):
        return True
application = tornado.web.Application([
    (r'/', WSHandler),
    (r'/command', WSREQHandler),

])
print("*** Depth Calibration ***")
depth_calibration()
print("*** Screen Calibration ***")
screen_calibration()

status = communication_status()
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print '*** Websocket Server Started at %s ***' % myIP
    tornado.ioloop.IOLoop.instance().start()
