from which_pyqt import PYQT_VER
import math

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
# elif PYQT_VER == 'PYQT4':
# 	from PyQt4.QtCore import QLineF, QPointF, QObject
# elif PYQT_VER == 'PYQT6':
# 	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        points = sorted(points, key=lambda point: point.x())

        t2 = time.time()

        t3 = time.time()
        # call function to create hull array
        points = hull_solver(points)
        polygon = [QLineF(points[i], points[(i+1)% len(points)] ) for i in range(len(points))]



        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

def hull_solver(points):
    #base case for dividing
    if len(points) <= 3:
        return points
    #recurse on left and right halves
    left_half = hull_solver(points[0:len(points) // 2])
    right_half = hull_solver(points[len(points) // 2:])
    #stitch the hulls together
    return merge(left_half, right_half)

def merge(left, right):
    #sort both halves in clockwise order
    leftcopy = sortByCW(left)
    rightcopy = sortByCW(right)
    #find the indice to be used for finding tangents
    rLeft_most = 0
    lRight_most = 0
    for i in range(1, len(leftcopy)):
        if (leftcopy[i].x() > leftcopy[lRight_most].x()):
            lRight_most = i
    #find indices of the two tangents
    LU,RU = findUpperTangent(leftcopy,lRight_most,rightcopy,rLeft_most)
    LL,RL = findLowerTangent(leftcopy,lRight_most,rightcopy,rLeft_most)
    #choose which points to keep from left hull
    keep_left = []
    keep_left.append(leftcopy[LL])
    if LL != LU:
        i = LL
        if i != len(leftcopy)-1:
            i+=1
        else:
            i = 0
        while i != LU:
            keep_left.append(leftcopy[i])
            if i != len(leftcopy) - 1:
                i += 1
            else:
                i = 0
        keep_left.append(leftcopy[LU])
    #choose which points to keep from right hull
    keep_right = []
    keep_right.append(rightcopy[RU])
    if RU != RL:
        j = RU
        if j != len(rightcopy)-1:
            j+=1
        else:
            j = 0
        while j != RL:
            keep_right.append(rightcopy[j])
            if j != len(rightcopy) - 1:
                j += 1
            else:
                j = 0
        keep_right.append(rightcopy[RL])
    #append the two keep arrays together
    for item in keep_right:
        keep_left.append(item)
    return keep_left



def findUpperTangent(left, lRight_index, right, rLeft_index):
    cur_slope = calculateSlope(left[lRight_index], right[rLeft_index])
    i = lRight_index
    j = rLeft_index
    done = False
    #compare slopes from points until we have an upper tangent
    while not done:
        done = True
        if (i != 0):
            try_slope = calculateSlope(left[i - 1], right[j])
        else:
            try_slope = calculateSlope(left[len(left) - 1], right[j])
        while try_slope < cur_slope:
            cur_slope = try_slope
            if (i != 0):
                i -= 1
            else:
                i = len(left) - 1
            if i != 0:
                try_slope = calculateSlope(left[i - 1], right[j])
            else:
                try_slope = calculateSlope(left[len(left)-1],right[j])
            done = False

        if (j != len(right) - 1):
            try_slope = calculateSlope(left[i], right[j + 1])
        else:
            try_slope = calculateSlope(left[i], right[0])
        while try_slope > cur_slope:
            cur_slope = try_slope
            if (j != len(right) - 1):
                j += 1
            else:
                j = 0
            if j != len(right)-1:
                try_slope = calculateSlope(left[i], right[j + 1])
            else:
                try_slope = calculateSlope(left[i],right[0])
            done = False

    return i,j

def findLowerTangent(left, lRight_index, right, rLeft_index):
    cur_slope = calculateSlope(left[lRight_index], right[rLeft_index])
    i = lRight_index
    j = rLeft_index
    done = False
    #compare slopes and step through each hull until we find lower tangent
    while not done:
        done = True
        if (i != len(left) - 1):
            try_slope = calculateSlope(left[i + 1], right[j])
        else:
            try_slope = calculateSlope(left[0], right[j])
        while try_slope > cur_slope:
            cur_slope = try_slope
            if (i != len(left) - 1):
                i += 1
            else:
                i = 0
            if(i != len(left)-1):
                try_slope = calculateSlope(left[i + 1], right[j])
            else:
                try_slope = calculateSlope(left[0],right[j])
            done = False

        if (j != 0):
            try_slope = calculateSlope(left[i], right[j - 1])
        else:
            try_slope = calculateSlope(left[i], right[len(right) - 1])
        while try_slope < cur_slope:
            cur_slope = try_slope
            if (j != 0):
                j -= 1
            else:
                j = len(right) - 1
            if (j !=0):
                try_slope = calculateSlope(left[i], right[j - 1])
            else:
                try_slope = calculateSlope(left[i],right[len(right)-1])
            done = False

    return i,j

def calculateSlope(p1, p2):
    #find da slope
    return (p2.y() - p1.y()) / (p2.x() - p1.x())

def sortByCW(points):
    #first sort clockwise to find reference point
    reference_point = sorted(points, key=lambda point: point.x())[0]
    #store rest of points in an array
    rest_of_points = sorted(points, key=lambda point: point.x())[1:]
    sorted_points = []
    #put reference point in the array to return
    sorted_points.append(reference_point)
    #sort the rest of the points cw based on reference point
    rest_sorted = sorted(rest_of_points, key=lambda point: find_angle(point, reference_point))
    #they got sorted ccw so we have to reverse
    rest_sorted_reversed = rest_sorted[::-1]
    #add them to the array to return
    for points in rest_sorted_reversed:
        sorted_points.append(points)
    return sorted_points

def find_angle(point, ref):
    dx = point.x() - ref.x()
    dy = point.y() - ref.y()
    #find arctangent to compare points to sort
    return math.atan2(dy, dx)
