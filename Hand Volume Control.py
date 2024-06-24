import cv2
import math
import numpy as np
import HandTrackerModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
wcam = 720
hcam = 640
pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)

detector = htm.handDetector(detectionCon = 0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume. GetMute()
#volume. GetMasterVolumeLevel()
volRange = volume. GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 400
volPer = 0

while True:
    ret, frame = cap.read()

    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)
    detector.get_fps(frame, color = (0, 255, 0))
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        cv2.circle(frame , (x1, y1), 7, (0, 255, 255), cv2.FILLED)
        cv2.circle(frame , (x2, y2), 7, (0, 255, 255), cv2.FILLED)
        cv2.circle(frame , (cx, cy), 7, (0, 255, 255), cv2.FILLED)
        cv2.line(frame , (x1, y1), (x2, y2), (255, 255, 204), 3)

        length = math.hypot(x2-x1, y2-y1)

        vol = np.interp(length, (45, 250), (minVol, maxVol))
        volBar = np.interp(length, (45, 250), (400, 150))
        volPer = np.interp(length, (45, 250), (0, 100))
        print(length, vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length < 45:
            cv2.circle(frame , (cx, cy), 7, (0, 165, 255), cv2.FILLED)

    cv2.rectangle(frame , (50,150),(85,400) , (0, 255, 255))
    cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 255), -1)
    cv2.putText(frame, f' {int(volPer)} %', (10, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


