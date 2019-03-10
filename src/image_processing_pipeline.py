import cv2
import numpy as np
import pickle

class ImageProcessingPipeline:

    def __init__(self, camera):
        self.camera = camera

        self.color_thresh = (90, 255)

        self.sobel_thresh = (10, 100)
        self.sobel_kernel = 15
        self.mag_thresh = (20, 120)
        self.dir_thresh = (0.5, 1.5)

        self.lane_points = [(0, 0), (400, 620), (400, 720), (720, 1280)]
            
    def process(self, image):
        processed_image =  self._line_pipeline(self._color_pipeline(self.camera.undistort(image)))
        warped_image = self._warp_image(processed_image)
        return processed_image

    def _color_pipeline(self, image):
        hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

        S = hls[:, :, 2] 

        binary_mask = np.zeros_like(S)
        binary_mask[(S > self.color_thresh[0]) & (S <= self.color_thresh[1])] = 1
        return cv2.bitwise_and(image, image, mask = binary_mask)

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

        combined = np.zeros_like(dir_binary)
        combined[((grad_x == 1) & (grad_y == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1
        return combined

    def _warp_image(self, image):
        points = np.float32(self.lane_points)
        dest_points = np.float32([(0, 0), (image.shape[0], 0), image.shape, (0, image.shape[1])])

        lined = cv2.polylines(image,np.int32([points]),True,(255,255,255))

        M = cv2.getPerspectiveTransform(points, dest_points)
        warped = cv2.warpPerspective(image, M, image.shape)

        return lined
