import numpy as np

MAX_HISTORY = 3
ym_per_pix = 3.048/76 # One line dash is 10ft or 3.048m and was 80 pixels tall
xm_per_pix = 3.7/676 # The lane lines are roughly 3.7m apart of 700 pixels apart.

class LaneLine:
    def __init__(self, fit_x):
        self.fits = [fit_x]
        self.diffs = [[0, 0, 0]]

    def update_fit(self, fit):
        self.fits.append(fit)
        if len(self.diffs) > 0:
            self.diffs.append(np.subtract(self.diff, fit))
        else:
            self.diffs.append(np.array([0, 0, 0]))

        if len(self.fits) > MAX_HISTORY:
            self.fits = self.fits[-MAX_HISTORY:]
            self.diffs = self.diffs[-MAX_HISTORY:]

    @property
    def fit(self):
        return np.mean(self.fits, axis=0)

    @property
    def diff(self):
        return np.mean(self.diffs, axis=0)


    def project(self, plot_y):
        fit = self.fit
        return fit[0]*plot_y**2 + fit[1]*plot_y + fit[2]

    def base_x(self):
        return self.project(720*ym_per_pix)

    def curvature(self):

        y_eval = 720

        fit = self.fit

        return((1 + (2*fit[0]*y_eval*ym_per_pix + fit[1])**2)**1.5) / np.absolute(2*fit[0])

class Lane:

    def __init__(self, left_fit_x, right_fit_x):
        self.left_line = LaneLine(left_fit_x)
        self.right_line = LaneLine(right_fit_x)

    def update_fit(self, left_fit_x, right_fit_x):
        self.set_left(left_fit_x)
        self.set_right(right_fit_x)

    def set_left(self, fit_x):
        if not self.left_line:
            self.left_line = LaneLine(fit_x)
        else:
            self.left_line.update_fit(fit_x)

    def set_right(self, fit_x):
        if not self.right_line:
            self.right_line = LaneLine(fit_x)
        else:
            self.right_line.update_fit(fit_x)

    def center_offset(self):
        left_fit_x = self.left_line.fit
        right_fit_x = self.right_line.fit

        mid_fit_x = np.mean([left_fit_x, right_fit_x], axis=0)

        mid_lane = LaneLine(mid_fit_x)
        mid_x = mid_lane.project(720)*xm_per_pix

        offset = ((1280/2)*xm_per_pix) - mid_x

        return offset

    def lane_line_distance(self):
        return self._lane_line_distance(self.left_line, self.right_line)

    def _lane_line_distance(self, left, right):
        left_base_x = self.left_line.base_x()
        right_base_x = self.right_line.base_x()

        return (right_base_x - left_base_x) * xm_per_pix

    def validate_new_fit(self, left_fit, right_fit):
        temp_left = LaneLine(left_fit)
        temp_right = LaneLine(right_fit)

        new_distance = self._lane_line_distance(temp_left, temp_right)

        if new_distance < 3 or new_distance > 4.4:
            return False

        return True

    def curvature(self):
        return (self.left_line.curvature() + self.right_line.curvature()) / 2.0
