import cv2
import numpy as np


"""
    Camera class handles the calibration of the camera itself and then is used to
    create undistorted images.
"""
class Camera
    def __int__(self, calibration_images, checkerboard=(9,5)):
        self.calibration_images = calibration_images

        self.mtx = None
        self.dist = None

    def calibrate(self):
        grayscale_images = self._convert_to_grayscale()

        objp = np.zeros((heckerboard[0]*checkerboard[1]*3), np.float32)
        objp[:, :2] = np.mgrid([0:checkerboard[0], 0:checkerboard[1]].T.reshape(-1, 2)

        objpoints = []
        imgpoints = []

        for image in grayscale_images:
            ret, corners = cv2.findChessboardCorners(gray, checkerboard, None)
            if ret == True:
                objpoints.append(objp)
                imgpoints.append(corners)


        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, grayscale_images[0][::-1], None, None)

        self.mtx = mtx
        self.dist = dist


    def undistort(self, img):
        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx)


    def _convert_to_grayscale(self):
        return [cv2.cvtColor(img,  cv2.COLOR_BGR2GRAY) for img in self.calibration_images]
