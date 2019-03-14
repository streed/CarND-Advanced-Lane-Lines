**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[distorted_undistorted]: ./output_images/distorted_undistorted.png "Distorted and Undistorted"
[checkerboard]: ./output_images/checkerboard.png "Checkerboard"
[output_example]: ./output_images/output_example.png "Output example"
[polynomial]: ./output_images/polynomial.png "Polynomial"
[sliding_window]: ./output_images/sliding_window.png "Sliding Window"
[thresholded_warped]: ./output_images/thresholded_warped.png "Thresholded Warped"
[white_mask]: ./output_images/white_mask.png "White Mask"
[yellow_mask]: ./output_images/yellow_mask.png "Yellow Mask"
[color_mask]: ./output_images/color_mask.png "Color Mask"
[combined_thresholds]: ./output_images/combined_thresholds.png "Combined Thresholds"
[before_warp]: ./output_images/before_warp.png "Before Warp"
[warped_image]: ./output_images/warped_image.png "Warped Image"
[video]: ./output_movie/project_video.mp4

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

To calibrate the camera I wrote a Camera class located in "./src/camera.py". This class does the following things. It lets you use the factory method to create a raw camera that has access to the set of calibration images used to calibrate this camera.

After the camera is created with the calibration images the camera is calibrated. In this project we used a 9x6 checkerboard pattern. During the calibration steps I mapped where the points should be in object space and then found the corrosponding checkerboard points in image space. Then after using all of the passed in camera calibration images I was able to produce the calibration matrix and coefficients. 

Once the camera is calibrated if the parameter to save the matrix and coefficients is `True` then they are saved into a pickle file called "camera_calibration.npz", this greatly sped up my work as you should only have to do this once for a new camera.

The image below shows one of the undistorted checkerboard images.

![alt text][checkerboard]

The following image is a little harder to see the change, but it is a undistorted image of the road.

![alt_text][distorted_undistorted]

### Pipeline (single images)

The pipeline was broken up into two parts. The first is in the class called `ImageProcessingPipeline` which handles a bulk of the color and edge thresholding as well as warping the road image into a birds eye view. The second part is handled in the class called `Road`. This `Road` class handles actually finding and analyizing the images that are passed to it, it assumes that it receives a warped birds eye view binary image.


#### 1. Provide an example of a distortion-corrected image.

The first step in the pipeline contained in the `ImageProcessingPipeline` is to use the calibrated camera from above to
undistorted the image, this is handled at line 40 in `./src/image_processing_pipeline.py`. Below is an example.
![alt text][distorted_undistorted]

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

The second step of the `ImageProcessingPipeline` is to mask out the lane colors from the image. Through various experimentation
as well as referring to the first lane finding project I decided to use the HSV color space for the yellow lane lines and HLS 
for the white lane lines. This gave me the best overall picture.


I used a combination of color and gradient thresholds to generate a binary image (thresholding steps at lines # through # in `another_file.py`).  Here's an example of my output for this step.  (note: this is not actually from one of the test images)

White Mask:

![alt_text][white_mask]

Yellow Mask:

![alt_text][yellow_mask]

Combined Color Mask:

![alt_text][color_mask]

Once this was completed I used the ideas from the `Advanced Computer Vision` lab to use the absolute sobel, magnitude thresholding, and direction thresholding.

Combined Abolsute Sobel, Magnitude, Direction thresholds:

![alt_text][combined_thresholds]

Both filtering and thresholding is below:

![alt_text][before_warp]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

Through experimentation I was able to find a reasonable bounding box that when warped gave parallel lines and gave a large enough area to examine tighter turns. The source and destination points are hard coded in `ImageProcessingPipeline` from lines 25 through 32.

The image below shows the unwarped box and the second image shows the first image warped:

![alt_text][warped_image]


#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

For finding the actual pixels I used two methods. The first method was the sliding window method as described in the lab. The second method was using the previously found polynomial and building up a bounding area surrounding the polynomial. 

How the process works is contained in the `Road` class in `./src/road.py`. When the first image comes in we do not know of a lane and we proceed with the sliding window method. Once we find the lane lines we instantiate a `Lane` object. This will hold the polynomial and various other information of the left and right lane lines.

The image below shows the sliding window method running:

![alt_text][sliding_window]

After this is successful or it gives us a reasonable acceptable result we then use the polynomial masking method from lines 34 through 77 in `./src/road.py`. 

The image below shows the polynomial window method running:

![alt_text][polynomial]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in lines # through # in my code in `my_other_file.py`

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

The lane lines are warped back down onto the original image in `ImageProcessingPipeline` on likes 47 through 64.

The image below shows the result of this method:

![alt_text][output_example]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a link to the video [Youtube Link](https://www.youtube.com/watch?v=hfM-DkZHoPM)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

The one issue that my implementation faces on the project_video and the challenge video are the areas with low contrast with the lane lines. For example in the project_video the road right on the bridge gave me the most trouble because the image gets washed out. I experimented with trying to even out the image by leveling the histogram, but I couldn't get it to work. Another way to improve the process would be having multiple sets of thresholds for differing lightness levels of the images, this would make the rest of the image processing better.

The other area it fails in, especially in the harder challenge video, are very tight turns. My algorithm loses the lanes completely. Along with the constant changing of light and dark throws off all of my threshholds and the lane lines go through trees rather than on the road.
