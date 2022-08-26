import random
from math import ceil
import sys
import os
import cv2
import mediapipe as mp


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

        # cam setup
        self.cam = cv2.VideoCapture(0)

        # face mesh (used for creating face_mesh object to detect faces)
        self.mp_face_mesh = mp.solutions.face_mesh

        # run main function
        self.Terminal()

    # option 0
    def cudaOperator0(self, gray, frame):
        return "".join(
            ["".join([self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)] for a in range(len(row))]) + "\n" for row in
             gray])

    # option 1
    def cudaOperator1(self, gray, frame):
        return f"{random.choice(self.terminalColors)}".join(
            ["".join([self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)] for a in range(len(row))]) + "\n" for row in
             gray]) + self.terminalColors[0]

    # option 2
    def cudaOperator2(self, gray, frame):
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
    def cudaOperator3(self, gray, frame):
        return "".join(
            ["".join(
                [(random.choice(self.terminalColorsSliced)
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

    # option 4
    def cudaOperator4(self, gray, result):
        lm = []

        if result.multi_face_landmarks:  # check if list length is > 0
            for face in result.multi_face_landmarks:  # for every face detected
                for pos in face.landmark:
                    if (ceil(pos.y * 49), ceil(pos.x * 184)) not in lm:
                        # appending if mesh point isn't computed before
                        lm.append((ceil(pos.y * 49), ceil(pos.x * 184)))

    # initiate rendering string
        render = ""

        y = 0
        for row in gray:  # looping through each row in gray numpy array
            x = 0
            for a in range(len(row)):  # iterating through elements in a row with the length of row
                if (y, len(row) - x) in lm:
                    # if point is point on face add a coloured string to be printed
                    render += random.choice(self.terminalColors) + self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)] + \
                              self.terminalColors[0]
                else:
                    # if not will add a default colour string
                    render += self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)]
                x += 1  # increment x throw row
            # adding \n to go to next line after each row
            render += "\n"
            y += 1  # increment x throw rows

        return render

    # main function consisting the main loop
    def Terminal(self):
        # opening up a face_mesh object to detect up-to 2 faces
        with self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            while True:
                # grabs ret and frame from camera where frame is numpy array
                ret, frame = self.cam.read()
                if not ret:
                    print("failed to grab frame")
                    continue

                # creating a gray scale frame to find the relevant character to print later on
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # setting frames flags writeable to false and changing colour-space
                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # downscaling frame array
                frame = cv2.resize(frame, (128, 72), interpolation=cv2.INTER_AREA)

                # processing to find faces in frame
                result = face_mesh.process(frame)

                # setting frames flags writeable to back to true and changing colour-space back
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # printing out to the terminal of returned string from relevant function
                print(
                    f"{getattr(self, 'cudaOperator' + str(self.option))(cv2.resize(gray, (184, 49), interpolation=cv2.INTER_AREA), result)[:-1]}",
                    flush=True, end="\r")

                # grabbing key events
                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    self.cam.release()
                    cv2.destroyAllWindows()
                    break


if __name__ == '__main__':
    m = Main(sys.argv[1:])
