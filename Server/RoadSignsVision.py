import cv2
import numpy as np
import math

'''
    find_stop_sign(gray_img, debug=False) --- finding stop signs
'''


class RoadSignsVision:
    def __init__(self):
        self.__stop_sign_cascade = cv2.CascadeClassifier('stop_sign.xml')

    def find_stop_sign(self, gray_img, debug=False):
        found = False
        img = gray_img

        stop_signs = self.__stop_sign_cascade.detectMultiScale(gray_img, 1.1, 4)

        if len(stop_signs) > 0:
            found = True
            if debug:
                img = cv2.cvtColor(np.copy(gray_img), cv2.COLOR_GRAY2BGR)
                for x, y, w, h in stop_signs:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(img, 'STOP', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        return found, img

    @staticmethod
    def __get_distance(p1, p2):
        return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))


if __name__ == '__main__':
    sign_vision = RoadSignsVision()
    cap = cv2.VideoCapture(0)
    while True:
        _, img_ = cap.read()
        img_ = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
        found_, img_ = sign_vision.find_stop_sign(img_, debug=True)

        print('STOP' if found_ else '')
        cv2.imshow("Vision", img_)
        key = cv2.waitKey(1)
        if key == 27:
            break
