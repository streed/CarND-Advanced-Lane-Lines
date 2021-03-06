import cv2
import numpy as np
import pickle

class ImageProcessingPipeline:

    def __init__(self, camera):
        self.camera = camera

        self.color_thresh = (30, 255)
        self.yellow_thresh = (0, 255)
        self.white_thresh = (0, 255)

        self.sobel_thresh = (20, 120)
        self.sobel_kernel = 15
        self.mag_thresh = (80, 200)
        self.dir_thresh = (0.5, 1.5)

        self.yellow_lower = [15, 100, 0]
        self.yellow_upper = [50, 220, 255]

        self.white_lower = [0, 200, 0]
        self.white_upper = [255, 255, 255]

        self.lane_points = np.float32([(220, 650),
                                       (560, 450),
                                       (720, 450),
                                       (1060, 650)])
        self.lane_dest_points = np.float32([(220, 650),
                                            (60, 0),
                                            (1220, 0),
                                            (1060, 650)])

        self.M = cv2.getPerspectiveTransform(self.lane_points,
                                             self.lane_dest_points)
        self.M_inv = cv2.getPerspectiveTransform(self.lane_dest_points,
                                                 self.lane_points)
            
    def process(self, image):
        undistorted = self.camera.undistort(image)
        color_image = self._color_pipeline(undistorted)
        processed_image =  self._line_pipeline(color_image)
        warped_image = self._warp_image(processed_image)
        return warped_image, undistorted

    def project_lane(self, image, warped, lane):
        warp_zeros = np.zeros_like(warped)
        color_warped = np.dstack((warp_zeros, warp_zeros, warp_zeros))

        plot_y = np.linspace(0, warped.shape[0] - 1, warped.shape[0])

        left_fit_x = lane.left_line.project(plot_y)
        right_fit_x = lane.right_line.project(plot_y)

        pts_left = np.vstack((left_fit_x, plot_y)).astype(np.int32).T
        pts_right = np.vstack((right_fit_x, plot_y)).astype(np.int32).T

        pts = np.vstack((np.mean([left_fit_x, right_fit_x], axis=0), plot_y)).astype(np.int32).T

        cv2.polylines(color_warped, [pts], False, (0, 255, 0), 10)


        cv2.polylines(color_warped, [pts_left], False, (255, 0, 0), 50)
        cv2.polylines(color_warped, [pts_right], False, (0, 0, 255), 50)

        de_warped = cv2.warpPerspective(color_warped, self.M_inv, (image.shape[1], image.shape[0]))
        result = cv2.addWeighted(np.array(image), 1, np.array(de_warped), 2, 0)

        cv2.putText(result,
                    "Curvature: {0:.2f}m".format(lane.curvature()),
                    (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)

        cv2.putText(result,
                    "Center Offset: {0:.2f}m".format(lane.center_offset()),
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)

        cv2.putText(result,
                    "Lane Line Distance: {0:.2f}m".format(lane.lane_line_distance()),
                    (100, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)

        return result



    def _color_pipeline(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

        out = cv2.inRange(hsv, np.array(self.yellow_lower), np.array(self.yellow_upper))
        yellow = cv2.bitwise_and(image, image, mask=out)
        
        out = cv2.inRange(hls, np.array(self.white_lower), np.array(self.white_upper))
        white = cv2.bitwise_and(image, image, mask=out)

        return cv2.bitwise_or(yellow, white)

    def _line_pipeline(self, image):
        return self._combine(image)

    def _abs_sobel(self, image, orient):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobel = gray

        if orient == 'x':
            sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
        elif orient == 'y':
            sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1)

        absolute = np.absolute(sobel)

        scaled = np.uint8(255*absolute / np.max(absolute))

        binary_output = np.zeros_like(scaled)
        binary_output[(scaled >= self.sobel_thresh[0]) & (scaled <= self.sobel_thresh[1])] = 1

        return binary_output

    def _mag_thresh(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel)

        grad = np.sqrt(sobel_x**2 + sobel_y**2)
        scaled = np.uint8(255 * grad / np.max(grad))

        binary_output = np.zeros_like(scaled)
        binary_output[(scaled >= self.mag_thresh[0]) & (scaled <= self.mag_thresh[1])] = 1
        return binary_output

    def _dir_thresh(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel)

        abs_x = np.absolute(sobel_x)
        abs_y = np.absolute(sobel_y)

        dir_xy = np.arctan2(abs_y, abs_x)

        binary_output = np.zeros_like(dir_xy)
        binary_output[(dir_xy >= self.dir_thresh[0]) & (dir_xy <= self.dir_thresh[1])] = 1
        return binary_output

    def _combine(self, image):
        grad_x = self._abs_sobel(image, 'x')
        grad_y = self._abs_sobel(image, 'y')
        mag_binary = self._mag_thresh(image)
        dir_binary = self._dir_thresh(image)

        combined = np.zeros_like(grad_x)
        combined[((grad_x == 1) & (grad_y == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1
        return combined

    def _warp_image(self, image):
        image_size = (image.shape[1], image.shape[0])

        warped = cv2.warpPerspective(image,
                                     self.M,
                                     image_size,
                                     flags=cv2.WARP_FILL_OUTLIERS + cv2.INTER_CUBIC)
        return warped
