import cv2
import picamera
import picamera.array

class Vision:
    def __init__(self, resolution=(640,480)):
        self.__camera = picamera.PiCamera()
        self.__stream = picamera.array.PiRGBArray(self.__camera)
        self.__camera.resolution = resolution
        self.__camera.color_effects = (128,128) # gray

    def get_gray_image(self):
        self.__camera.capture(self.__stream, 'bgr', use_video_port=True)
        img = self.__stream.array
        self.__stream.seek(0)
        self.__stream.truncate()
        return img

    def __del__(self):
        self.__camera.close()
        self.__stream.close()
