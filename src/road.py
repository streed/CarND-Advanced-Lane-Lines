import cv2
import numpy as np
import matplotlib.pyplot as plt

from .lane import Lane

class Road:

    def __init__(self):
        self.n_windows = 10
        self.sliding_margin = 100
        self.poly_margin = 100
        self.minpix = 50

        self.lane = None

    """
        Assume the image is warped and has been thresholded
    """
    def process(self, image):
        if not self.lane:
            left_fit, right_fit, out_image = self.find_lanes_sliding_window(image)
            self.lane = Lane(left_fit, right_fit)
        else:
            left_fit, right_fit, out_image = self.find_lanes_sliding_window(image)
            if self.lane.validate_new_fit(left_fit, right_fit):
                self.lane.update_fit(left_fit, right_fit)
            else:
                left_fit, right_fit, out_image = self.find_lanes_sliding_window(image)
                self.lane.update_fit(left_fit, right_fit)

        return out_image

    def find_lanes_from_existing_lanes(self, image):
        left = self.lane.left_line
        right = self.lane.right_line
        nonzero = image.nonzero()
        nonzero_x = np.array(nonzero[1])
        nonzero_y = np.array(nonzero[0])

        left_lane_inds = ((nonzerox > (left.project(nonzeroy) - self.poly_margin)) &
                          (nonzerox < (left.project(nonzeroy) + self.poly_margin)))
        right_lane_inds = ((nonzerox > (right.project(nonzeroy) - self.poly_margin)) &
                           (nonzerox < (right.project(nonzeroy) + self.poly_margin)))

        left_x = nonzero_x[left_lane_inds]
        left_y = nonzero_y[left_lane_inds]
        right_x = nonzero_x[right_lane_inds]
        right_y = nonzero_y[right_lane_inds]

        out_image = np.dstack((image, image, image)) * 255
        out_image[lefty, leftx] = [255, 0, 0]
        out_image[righty, rightx] = [0, 0, 255]

        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        return left_fit, right_fit, out_image


    def find_lanes_sliding_window(self, image):
        bottom_half = image[image.shape[0] // 2:, :]
        histogram = np.sum(bottom_half, axis=0)

        out_image = np.dstack((image, image, image)) * 255

        midpoint = np.int(histogram.shape[0] // 2)
        left_base_x = np.argmax(histogram[:midpoint])
        right_base_x = np.argmax(histogram[midpoint:]) + midpoint

        left_lane_inds = []
        right_lane_inds = []

        window_height = np.int(image.shape[0] // self.n_windows)

        nonzero = image.nonzero()

        nonzero_x = np.array(nonzero[1])
        nonzero_y = np.array(nonzero[0])

        left_x_current = left_base_x
        right_x_current = right_base_x


        for window in range(self.n_windows):
            window_y_low = image.shape[0] - (window + 1) * window_height
            window_y_high = image.shape[0] - window * window_height
            
            window_x_left_low = left_x_current - self.sliding_margin
            window_x_left_high = left_x_current + self.sliding_margin

            window_x_right_low = right_x_current - self.sliding_margin
            window_x_right_high = right_x_current + self.sliding_margin

            cv2.rectangle(out_image,
                          (window_x_left_low, window_y_low),
                          (window_x_left_high, window_y_high),
                          (0,255,0),
                          2) 

            cv2.rectangle(out_image,
                          (window_x_right_low, window_y_low),
                          (window_x_right_high, window_y_high),
                          (0,255,0),
                          2) 
                        
            good_left_inds = ((nonzero_y >= window_y_low) &
                              (nonzero_y < window_y_high) &
                              (nonzero_x >= window_x_left_low) &
                              (nonzero_x < window_x_left_high)).nonzero()[0]

            good_right_inds = ((nonzero_y >= window_y_low) &
                               (nonzero_y < window_y_high) & 
                               (nonzero_x >= window_x_right_low) &
                               (nonzero_x < window_x_right_high)).nonzero()[0]

            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            if len(good_left_inds) > self.minpix:
                left_x_current = np.int(np.mean(nonzero_x[good_left_inds]))

            if len(good_right_inds) > self.minpix:
                right_x_current = np.int(np.mean(nonzero_x[good_right_inds]))

        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        leftx = nonzero_x[left_lane_inds]
        lefty = nonzero_y[left_lane_inds] 
        rightx = nonzero_x[right_lane_inds]
        righty = nonzero_y[right_lane_inds]

        out_image[lefty, leftx] = [255, 0, 0]
        out_image[righty, rightx] = [0, 0, 255]

        if len(leftx) > 0:
            left_fit = np.polyfit(lefty, leftx, 2)
        else:
            left_fit = [False, False, False]

        if len(rightx) > 0:
            right_fit = np.polyfit(righty, rightx, 2)
        else:
            right_fit = [False, False, False]

        return  left_fit, right_fit, out_image
