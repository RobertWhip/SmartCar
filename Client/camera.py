import cv2


class Vision:
    def __init__(self):
        self.__cap = cv2.VideoCapture(0)

    def get_gray_image(self, width=640, height=480):
        return cv2.resize(cv2.cvtColor(self.__cap.read()[1], cv2.COLOR_BGR2GRAY), (width, height))

    def __del__(self):
        self.__cap.release()

