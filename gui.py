#!/usr/bin/python3
import threading
import Tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
from Tkinter import *


def ok_callback():
    root.destroy()
    print ("Closing")
    sys.exit(1)

def mainfuncstart():
    import squareDetection
    squareDetection.mainfunc()


def config_callback():
    t = threading.Thread(target=mainfuncstart, name='Config_wizard')
    t.start()


root = Tkinter.Tk()
frame = Frame(root)
root.title("ENVAST AR SOLUTION - GUI")
frame.pack()
toplabel = StringVar()
HeightLabel = StringVar()
WidthLabel = StringVar()
MarginLabel = StringVar()
frametop = Frame(frame)
frametop.pack(side = TOP)
framebot = Frame(frame)
framebot_1 = Frame(framebot)
framebot_2 = Frame(framebot_1)
framebot_3 = Frame(framebot_2)
framebot_4 = Frame(framebot_1)
framebot.pack(side = TOP)
framebot_1.pack(side = TOP)
framebot_2.pack(side = TOP)
framebot_3.pack(side = TOP)
frame_buttom = Frame(frame)
frame_buttom.pack(side = BOTTOM)
label_top = Label( frametop, textvariable = toplabel, relief = RAISED )
ok_button = Button( frame_buttom, text = "Confirm" ,command = ok_callback)
config_button = Button( frame_buttom, text = "Configuration", command = config_callback)
label_width = Label( framebot_1, textvariable = WidthLabel, relief = RAISED )
Entry_width = Entry(framebot_1, bd = 5)
label_height = Label( framebot_2, textvariable = HeightLabel, relief = RAISED )
Entry_height = Entry(framebot_2, bd = 5)
label_margin = Label( framebot_3, textvariable = MarginLabel, relief = RAISED )
Entry_margin = Entry(framebot_3, bd = 5)
toplabel.set("ENVAST AR BOX Configuration GUI")
HeightLabel.set("Height :")
WidthLabel.set("Width :")
MarginLabel.set("Margin :")
label_top.pack(side = TOP)
label_height.pack(side = LEFT)
label_width.pack(side = LEFT)
label_margin.pack(side = LEFT)
Entry_width.pack(side = RIGHT)
Entry_height.pack(side = RIGHT)
Entry_margin.pack(side = RIGHT)
ok_button.pack(side = RIGHT)
config_button.pack(side = LEFT)
Entry_height.insert(0,"10")

root.mainloop()