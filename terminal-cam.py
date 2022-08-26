import random
from numba import jit, cuda
from numba.core.errors import NumbaPendingDeprecationWarning, NumbaDeprecationWarning, ConstantInferenceError, NumbaWarning
from math import ceil
import sys
import os
import cv2
import warnings
import mediapipe as mp

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
warnings.simplefilter('ignore', category=ConstantInferenceError)
warnings.simplefilter('ignore', category=NumbaWarning)


class Main:
    def __init__(self, option):
        # init
        """
        option:
            0 : default/bw
            1: party/multicolor
        """
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

        # face mesh
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.Terminal()

    def safe_execute(self, default, exception, *args):
        try:
            return self.rawChars[ceil((default / 255) * 12)]
        except Exception:
            return default

    def cudaOperator0(self, gray, frame):
        return "".join(["".join([self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)] for a in range(len(row))]) + "\n" for row in gray])

    def cudaOperator1(self, gray, frame):
        return f"{random.choice(self.terminalColors)}".join(["".join([self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)] for a in range(len(row))]) + "\n" for row in gray])+self.terminalColors[0]

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

    def cudaOperator4(self, gray, result):
        lm = []

        #print(result.multi_face_landmarks)
        if result.multi_face_landmarks:
            for face in result.multi_face_landmarks:
                for pos in face.landmark:
                    #print((ceil(pos.y*49), ceil(pos.x*184)))
                    if (ceil(pos.y*49), ceil(pos.x*184)) not in lm:
                        #print(lm)

                        #print(gray[ceil(pos.y*49), ceil(pos.x*184)])
                        lm.append((ceil(pos.y*49), ceil(pos.x*184)))

                        #gray[ceil(pos.y*49), ceil(pos.x*184)] = random.choice(self.terminalColorsSliced)+self.rawChars[ceil((gray[ceil(pos.y*49), ceil(pos.x*184)] / 255) * 12)]+self.terminalColors[0]

        render = ""

        y = 0
        #print(lm)
        for row in gray:
            x = 0
            for a in range(len(row)):
                #print((x, y))
                if (y, len(row)-x) in lm:
                    render += random.choice(self.terminalColors)+self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)]+self.terminalColors[0]
                else:
                    render += self.rawChars[ceil((row[-1 - (1 * a)] / 255) * 12)]
                x += 1
            render += "\n"
            y += 1


        return render
        #return "".join(["".join([self.safe_execute(row[-1 - (1 * a)], ValueError) for a in range(len(row))]) + "\n" for row in gray])
        #return ""

    def Terminal(self):
        img_counter = 0
        n = True
        with self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            while True:
                ret, frame = self.cam.read()
                if not ret:
                    print("failed to grab frame")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frame = cv2.resize(frame, (128, 72), interpolation=cv2.INTER_AREA)

                result = face_mesh.process(frame)

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                #os.system('cls')
                print(
                    f"{getattr(self, 'cudaOperator'+str(self.option))(cv2.resize(gray, (184, 49), interpolation=cv2.INTER_AREA), result)[:-1]}",
                    flush=True, end="\r")

                k = cv2.waitKey(1)
                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    self.cam.release()
                    cv2.destroyAllWindows()
                    break
                elif k % 256 == 32:
                    # SPACE pressed
                    img_name = f"opencv_frame_{img_counter}.png"
                    cv2.imwrite(img_name, frame)
                    print(f"{img_name} written!")
                    img_counter += 1


if __name__ == '__main__':
    m = Main(sys.argv[1:])
