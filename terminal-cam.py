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
__version__ = "1.0.2dev"
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

    # common operator
    def commonOperator(self, gray):
        charArr = np.c_[arr := np.flip(self.vCharMapper(gray / 255 * 12), 1), ["\n"] * arr.shape[0]]
        return charArr

    # option 0
    def Operator0(self, gray):
        return "".join(["".join(row) for row in self.commonOperator(gray)])

    # option 1
    def Operator1(self, gray):
        return f"{random.choice(self.terminalColors)}".join(["".join(row) for row in self.commonOperator(gray)]) + \
               self.terminalColors[0]

    # option 2
    def Operator2(self, gray):
        c = random.choice(self.terminalColorsSliced)
        return "".join(
            ["".join(
                [(c
                  if ceil((row[-1 - (1 * a)] / 255) * 12) >= 10
                     and (ceil((row[-1 - (1 * (a - 1))] / 255) * 12) < 10 if a != 0 else True)
                  else
                  self.terminalColors[0]
                  if ceil((row[-1 - (1 * a)] / 255) * 12) < 10
                     and (ceil((row[-1 - (1 * (a - 1))] / 255) * 12) >= 10 if a != 0 else True)
                  else
                  "")
                 +
                 self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)]
                 for a in range(len(row))
                 ]) + "\n" for row in gray]) + self.terminalColors[0]

    # option 3
    def Operator3(self, gray):
        return "".join(
            ["".join(
                [(random.choice(self.terminalColorsSliced)
                  if ceil((row[-1 - (1 * a)] / 255) * 12) >= 10 and (
                    ceil((row[-1 - (1 * (a - 1))] / 255) * 12) < 10 if a != 0 else True)
                  else
                  self.terminalColors[0]
                  if ceil((row[-1 - (1 * a)] / 255) * 12) < 10 and (
                      ceil((row[-1 - (1 * (a - 1))] / 255) * 12) >= 10 if a != 0 else True)
                  else
                  "")
                 +
                 self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)]
                 for a in range(len(row))
                 ]) + "\n" for row in gray]) + self.terminalColors[0]

    # terminal scaler
    def terminalScale(self):
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
    def Terminal(self):
        try:
            startT = time.time()
            waitTimers = [5, 7, 10, 12, 15, 20]
            waitTimersIndex = 0
            while True:
                # grabs ret and frame from camera where frame is numpy array
                ret, frame = self.cam.read()
                if ret:
                    # creating a gray scale frame to find the relevant character to print later on
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # setting frames flags writeable to false and changing colour-space
                    frame.flags.writeable = False
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # downscaling frame array
                    frame = cv2.resize(frame, (128, 72), interpolation=cv2.INTER_AREA)

                    # setting frames flags writeable to back to true and changing colour-space back
                    frame.flags.writeable = True
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # printing out to the terminal of returned string from relevant function
                    print(f"{self.chosenOperator(cv2.resize(gray, (self.terminalScale()), interpolation=cv2.INTER_AREA))[:-1]}", flush=False, end="\n")
                    nowT = time.time()
                    print(round(1 / (nowT - startT)))
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
        except FailedToGrabFrame as e:
            printE(e)

        self.cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    m = Main(sys.argv[1:])
