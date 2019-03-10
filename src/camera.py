import cv2
import glob
import numpy as np


"""
    Camera class handles the calibration of the camera itself and then is used to
    create undistorted images.
"""
class Camera:
    @classmethod
    def create(cls, image_path_matcher, checkerboard=(9,5)):
        images = glob.glob(image_path_matcher)

        raw_images = [cv2.imread(image) for image in images]

        return Camera(raw_images, checkerboard)

    def __init__(self, calibration_images, checkerboard):
        self.calibration_images = calibration_images
        self.checkerboard = checkerboard
        self.mtx = None
        self.dist = None


    def calibrate(self):
        grayscale_images = self._convert_to_grayscale()

        objp = np.zeros((self.checkerboard[0]*self.checkerboard[1],3), np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard[0], 0:self.checkerboard[1]].T.reshape(-1, 2)

        objpoints = []
        imgpoints = []

        for image in grayscale_images:
            ret, corners = cv2.findChessboardCorners(image, self.checkerboard, None)
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)


        image_shape = grayscale_images[0].shape
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_shape, None, None)

        self.mtx = mtx
        self.dist = dist


    def undistort(self, img):
        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx)


    def _convert_to_grayscale(self):
        return [cv2.cvtColor(img,  cv2.COLOR_BGR2GRAY) for img in self.calibration_images]
