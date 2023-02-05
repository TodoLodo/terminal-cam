#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A python script that grabs frames from camera and prints out to the terminal

terminal-cam is a script built on Python language that grabs frames from the integrated webcam, compute the relevant
characters depending on the gray scale value at each pixel of a downscaled frame and prints out to the terminal.
terminal-cam comes with different features/options which can found with more details and usage at,
https://github.com/TodoLodo/terminal-cam#readme
"""

__author__ = "Todo Lodo"
__license__ = "GPL"
__version__ = "1.1.0"
__maintainer__ = "Todo Lodo"
__email__ = "me@todolodo.xyz"

# imports
import time
import warnings
import os
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
import cv2
from math import ceil
import random
import sys
import numpy as np

warnings.filterwarnings('ignore')


class FailedToGrabFrame(Exception):
    def __str__(self):
        return "Failed to grab frame!"


def printE(e):
    print(f"\n\033[0;33m{e}\033[0m")


class Main:
    def __init__(self, option):
        # init
        """
        option:
            0 : default/bw
            1: party/multicolor
            2: random color at bright spot
            3: random color for each line at bright spots
            4: random color on face
        """
        # check if length of option(args) is zero, if so resolve to default option (0)
        if not option:
            option = ['0']
        # print(option)
        os.system('color')
        self.option = int(option[0])

        # data
        self.rawChars = " .,-~:;=!*#$@"
        self.terminalColors = ["\033[0m",
                               "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m",
                               "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
        self.EBGR = ["\033[0m", "\033[0;34m", "\033[0;32m", "\033[0;31m"]
        self.terminalColorsSliced = self.terminalColors[1:]
        # computing the ratio of similar visual distance between height and width when printing characters on terminal
        self.terminal_1_1_Ratio = 11 / 5

        # cam setup
        self.cam: cv2.VideoCapture
        self.camSetup()

        # obtaining max possible resolution
        self.width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.camRatio = self.width / self.height  # computing resolution ratio

        # terminal Ration
        self.terminalRatio = self.camRatio * self.terminal_1_1_Ratio

        self.vCharMapper = np.vectorize(self.charMapper)
        self.vColorMapper = np.vectorize(self.colorMapper)
        self.vRound = np.vectorize(round)

        self.chosenOperator = getattr(self, f"Operator{self.option}")

        # run main function
        self.Terminal()

    # cam setup function
    def camSetup(self):
        self.cam = cv2.VideoCapture(0)
        # using 1e4 to get the max possible value for resolution
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

    #  char mapper
    def charMapper(self, val):
        return self.rawChars[round(val)]

    def colorMapper(self, val):
        print(val)

    # common operator
    def commonOperator(self, gray):
        charArr = (arr := np.c_[arr := np.flip(self.vCharMapper(gray / 255 * 12), 1), ["\n"] * arr.shape[0]]).reshape((arr.size,))
        return np.char.mod('%s', charArr)

    # option 0
    def Operator0(self, frame):
        return "".join(self.commonOperator(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))

    def Operator1(self, frame):
        h, w, c = frame.shape
        colArr = (arr:=np.c_[arr := np.flip(np.array([self.EBGR[rgb.argmax() + 1] for rgb in frame.reshape(h * w, c)]).reshape((h, w)), 1), [self.EBGR[0]] * arr.shape[0]]).reshape((arr.size,))

        return "".join([f"{col}{char}" for char, col in zip(self.commonOperator(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)), colArr)])

    # gets terminal window size
    def terminalScale(self) -> tuple[float, float]:
        w, h = 0, 0
        size = os.get_terminal_size()
        if size.columns / size.lines >= self.terminalRatio:
            h = size.lines
            w = ceil(h * self.terminal_1_1_Ratio * self.camRatio)
        else:
            w = size.columns
            h = ceil(w / (self.terminal_1_1_Ratio * self.camRatio))

        # del data
        del size

        # class attributes
        self.terminalWidth, self.terminalHeight = w, h

        return w, h

    # main function consisting the main loop
    def Terminal(self) -> None:
        try:
            startT = time.time()
            waitTimers = [5, 7, 10, 12, 15, 20]
            waitTimersIndex = 0
            while True:
                # grabs ret and frame from camera where frame is a numpy array
                ret, frame = self.cam.read()
                if ret:
                    # printing out to the terminal of returned string from relevant function
                    print(f"{self.chosenOperator(cv2.resize(frame, (self.terminalScale()), interpolation=cv2.INTER_AREA))[:-1]}", flush=True, end="\n")

                    # fps
                    print(round(1 / ((nowT := time.time()) - startT)))
                    startT = nowT

                # wait if no frame
                else:
                    try:
                        t = waitTimers[waitTimersIndex]
                        maxsl = 0
                        for i in range(t+1):
                            st = time.time()
                            s = f"\033[0;{34 if i == t else 31}mFailed to grab frame! trying again in \033[35m{t-i}s\033[0m"
                            sl = len(s)
                            if maxsl < sl:
                                maxsl = sl
                            elif sl < maxsl:
                                s += ' '
                            print(s, flush=True, end="")
                            time.sleep(1 - (time.time()-st))
                            print("\b"*sl, end="")
                        print()
                        self.camSetup()
                        waitTimersIndex += 1
                    except IndexError:
                        raise FailedToGrabFrame

                # grabbing key events
                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    break
        except KeyboardInterrupt:
            e = "Keyboard Interrupt!"
            printE(e)
        except OSError:
            e = "Unable to find terminal size! Run the script via a terminal"
            printE(e)

        except FailedToGrabFrame as e:
            printE(e)

        self.cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    m = Main(sys.argv[1:])
