import cv2
import numpy as np
import math


class RoadLaneVision:
    # coordinates of corners: order is [top left, top right, bottom right, bottom left]
    def __init__(self, width=640, height=480, top_margin=40, corners=((0, 480), (176, 240), (460, 240), (640, 480))):
        self.__width = width
        self.__height = height
        self.__top_margin = top_margin
        self.__corners = np.array(corners, dtype="float32")
        self.__m = self.__four_point_transform(self.__corners)

    def get_angle(self, gray_img, debug=False):
        gray_img = gray_img[self.__top_margin:, :]
        gray_img = cv2.resize(gray_img, (self.__width, self.__height))
        gray_img = cv2.warpPerspective(gray_img, self.__m, None)
        gray_img = cv2.rotate(gray_img, 2)[:self.__height, :]
        lines_img = None

        if debug:
            lines_img = np.copy(gray_img)
            lines_img = cv2.cvtColor(lines_img, cv2.COLOR_GRAY2BGR)

        lines, lines_img = self.get_road_lines(gray_img, lines_img)

        if lines is not None:
            line_data = self.__compute_lines(lines)
            clustered = self.__cluster_angles(line_data)
            decided_angle = self.__decide_angle(clustered)
        else:
            decided_angle = 0

        return decided_angle, lines_img

    @staticmethod
    def __four_point_transform(pts):
        hwratio = 11 / 8.5  # letter size paper
        scale = 180  # int(maxWidth / 12)

        center_x = 320
        center_y = 240

        dst = np.array([
            [center_x - scale, center_y - scale * hwratio],  # top left
            [center_x + scale, center_y - scale * hwratio],  # top right
            [center_x + scale, center_y + scale * hwratio],  # bottom right
            [center_x - scale, center_y + scale * hwratio],  # bottom left
        ], dtype="float32")

        # compute the perspective transform matrix and then apply it
        m_ = cv2.getPerspectiveTransform(pts, dst)

        return m_

    @staticmethod
    def __line_length(arr):
        return math.sqrt((arr[0, 0] - arr[1, 0]) ** 2 + (arr[0, 1] - arr[1, 1]) ** 2)

    @staticmethod
    def __line_angle(arr):
        dx = arr[1, 0] - arr[0, 0]
        dy = arr[1, 1] - arr[0, 1]
        rads = math.atan2(-dy, dx)
        rads %= 2 * math.pi
        degs = -math.degrees(rads)
        if degs <= -180:
            degs = degs + 180

        degs = degs + 90
        return degs

    def __compute_lines(self, lines):
        from operator import itemgetter

        line_data = []
        for line in lines:
            line_data.append([self.__line_angle(line), self.__line_length(line)])

        sorted(line_data, key=itemgetter(0))
        return line_data

    @staticmethod
    def __cluster_angles(line_data):
        clusters = []
        last_angle = -180
        for a, l in line_data:
            if abs(last_angle - a) > 20:
                clusters.append([(a, l)])
            else:
                clusters[-1].append((a, l))
        return clusters

    @staticmethod
    def __decide_angle(clustered_angles):
        max_length = 0
        max_cluster_id = -1
        for i, c in enumerate(clustered_angles):
            # sum length of lines found in clusters, filter out angles > 80 (likely in horizon)
            cluster_length = sum([l for a, l in c if abs(a) < 80])
            # print('cluster length', cluster_length)
            if cluster_length > max_length:
                max_length = cluster_length
                max_cluster_id = i

        if max_cluster_id > -1:
            angles = [a for a, l in clustered_angles[max_cluster_id]]
            return sum(angles)/len(angles)
        else:
            return 0

    @staticmethod
    def get_road_lines(gray_img, lines_img=None):
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(gray_img, (kernel_size, kernel_size), 0)

        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

        rho = 1  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = 15  # minimum number of votes (intersections in Hough grid cell)
        min_line_length = 50  # minimum number of pixels making up a line
        max_line_gap = 20  # maximum gap in pixels between connectable line segments

        # Run hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)

        if lines is not None:
            if lines_img is not None:
                for line in lines:
                    for x0, y0, x1, y1 in line:
                        cv2.line(lines_img, (x0, y0), (x1, y1), (0, 255, 0), 2)
            lines = lines.reshape((lines.shape[0], 2, 2))
            lines = lines.astype(float)

        return lines, lines_img


if __name__ == "__main__":
    road_vision = RoadLaneVision()
    img_path = './road1.jpg'

    cap = cv2.VideoCapture(0)
    while True:
        _, img = cap.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        angle, lines_ = road_vision.get_angle(img, debug=True)
        print(angle)

        cv2.imshow("Vision", lines_)

        key = cv2.waitKey(1)
        if key == 27:
            break

