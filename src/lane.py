
class LaneLine:
    def __init__(self, fit_x):
        self.fit = fit_x

    def update_fit(self, fit):
        self.fit = fit

    def project(self, plot_y):
        return self.fit[0]*plot_y**2 + self.fit[1]*plot_y + self.fit[2]

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
