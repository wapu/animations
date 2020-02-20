import numpy as np


# https://www.scratchapixel.com/lessons/3d-basic-rendering/computing-pixel-coordinates-of-3d-point/
#     mathematics-computing-2d-coordinates-of-3d-points
from math import sin, cos, pi
def x_rot(t):
    return np.matrix(
        [[1, 0, 0, 0],
         [0, cos(t), -sin(t), 0],
         [0, sin(t), cos(t), 0],
         [0, 0, 0, 1]])
def y_rot(t):
    return np.matrix(
        [[cos(t), 0, sin(t), 0],
         [0, 1, 0, 0],
         [-sin(t), 0, cos(t), 0],
         [0, 0, 0, 1]])
def z_rot(t):
    return np.matrix(
        [[cos(t), -sin(t), 0, 0],
         [sin(t), cos(t), 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]])
def trans(x,y,z):
    return np.matrix(
        [[1, 0, 0, x],
         [0, 1, 0, y],
         [0, 0, 1, z],
         [0, 0, 0, 1]])

def get_camera_matrix(t_x=0, t_y=0, t_z=0, x=0, y=0, z=1):
    # apply translation, then rotations around x, y and z axis in that order
    camera_to_world = z_rot(t_z) * y_rot(t_y) * x_rot(t_x) * trans(x,y,z)
    # invert and drop last row
    return np.linalg.inv(camera_to_world)[:3]

def project(C, points, screen_size):
    points = np.array(C * points)
    z = points[2,:]
    points = points / -z
    center = (screen_size[0]/2, screen_size[1]/2)
    points = points[:2,:].T * (1,-1) * center + center
    return points, z
