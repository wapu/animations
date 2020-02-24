
import numpy as np
from cmath import exp
from random import randint

from rendering import hermite


def norm(v, axis=None):
    return v / np.sqrt(np.sum(np.square(v), axis=axis))

def get_rotation_matrix(angle, homogeneous=False):
    c = np.cos(angle)
    s = np.sin(angle)
    if homogeneous:
        R = np.array([
                [ c, s, 0],
                [-s, c, 0],
                [ 0, 0, 1]
            ])
    else:
        R = np.array([
                [ c, s],
                [-s, c]
            ])
    return R


def divide_line(p_start, p_end, n_points):
    return np.stack([np.linspace(p_start[0], p_end[0], n_points),
                     np.linspace(p_start[1], p_end[1], n_points)], axis=-1)


def rotate_around(points, angle, center):
    points[:] = (points - center).dot(get_rotation_matrix(angle)) + center


# TODO: proper numpy
def get_grid_coordinates(rows, cols, dist, clip=False):
    points = []

    radius = dist * min(rows, cols) // 2
    radius2 = radius*radius

    for i in range(rows):
        for j in range(cols):
            y = (i - rows//2) * dist
            x = (j - cols//2) * dist

            d = y*y + x*x
            if (d < radius2) or (clip == False):
                points.append((x,y))

    return np.array(points)


def get_circle_coordinates(n_points, radius=1, center=(0,0)):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    X = np.cos(angles) * radius + center[0]
    Y = np.sin(angles) * radius + center[1]
    return np.stack([X,Y], axis=-1)


def get_circle_mask(width, height, r=0, fade=0):
    coords = np.mgrid[:width,:height].transpose([1,2,0])
    dists = np.sqrt(np.sum(np.square(coords - (width/2, height/2)), axis=2))
    if fade <= 1:
        return np.maximum(0, np.minimum(1, (r - dists)))
    else:
        return hermite(np.maximum(0, np.minimum(1, (r - dists - 0.5) / np.abs(fade) + 0.5)))


def circle_from_three_points(p1, p2, p3):
    d = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])
    if d == 0:
        return None, None
    u = 0.5 * (p1[0]*p1[0] - p2[0]*p2[0] + p1[1]*p1[1] - p2[1]*p2[1])
    v = 0.5 * (p2[0]*p2[0] - p3[0]*p3[0] + p2[1]*p2[1] - p3[1]*p3[1])

    x = (u * (p2[1] - p3[1]) - v * (p1[1] - p2[1])) / d
    y = (v * (p1[0] - p2[0]) - u * (p2[0] - p3[0])) / d
    radius = sqrt((p1[0] - x)**2 + (p1[1] - y)**2)
    return (x,y), radius


# TODO: proper numpy
def polar_to_cartesian(r, theta):
    y = r * np.sin(theta)
    x = r * np.cos(theta)
    return y, x

def polar_to_cartesian_np(polar):
    return (polar[:,0] * np.array([np.cos(polar[:,1]), np.sin(polar[:,1])])).T


# TODO: proper numpy
def cartesian_to_polar(y, x):
    r = np.sqrt(x*x + y*y)
    theta = np.arctan2(y,x)
    return r, theta

def cartesian_to_polar_np(cartesian):
    r = np.sqrt(np.sum(np.square(cartesian), axis=1))
    t = np.arctan2(cartesian[:,1], cartesian[:,0])
    return np.vstack([r, t]).T


def generate_harmonics(symmetry, n_harmonics):
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

    harmonics = []
    evenHarmonic = True
    m = 1

    for i in range(n_harmonics):
        k = 1

        if (i != 0):
            k = m * symmetry
            if evenHarmonic:
                k = k + 1
                m = m + 1
            else:
                k = k - 1

        a_x = float(fibonacci[n_harmonics - i]) / float(fibonacci[n_harmonics])
        p_x = 2*np.pi * float(fibonacci[randint(0, n_harmonics)]) / float(fibonacci[n_harmonics])
        a_y = a_x

        if ((k-1) % symmetry == 0):
            p_y = p_x - np.pi/2
        else:
            p_y = p_x + np.pi/2

        harmonics.append([k, a_x, p_x, a_y, p_y])

        evenHarmonic = not evenHarmonic

    return harmonics


# TODO: proper numpy
def get_shape_from_harmonics(harmonics, n_points=512, method='lopez'):
    if method == 'lopez':
        points = []
        t_delta = (2*np.pi) / (n_points - 1)

        for i in range(n_points):
            x, y = 0, 0
            t = t_delta * i

            for j in range(len(harmonics)):
                k, a_x, p_x, a_y, p_y = harmonics[j]
                x += a_x * np.cos(t * k + p_x)
                y += a_y * np.cos(t * k + p_y)

            points.append(np.array([x, y]))

        return points

    elif method == 'zahn & roskies':
        if len(harmonics[0]) == 5:
            harmonics = [(k, a_x, p_x) for (k, a_x, p_x, a_y, p_y) in harmonics]

        points = []
        t_delta = (2*np.pi) / (n_points - 1)

        mu_0 = sum([a * np.cos(p) for (k, a, p) in harmonics])

        Z = 0 + 0j
        for i in range(n_points):
            t = i * t_delta

            theta = -t + mu_0 + sum([a * np.cos(k*t - p) for (k, a, p) in harmonics])

            Z += exp(1j * theta)

            points.append(np.array([Z.imag, Z.real]))

        return points


def center_and_scale(points, center, radius):
    avg = np.mean(points, axis=0)
    center = np.array(center)
    max_dist = np.sqrt(np.max(np.sum(np.square(points - avg), axis=1)))
    scale = radius / max_dist

    points[:] -= avg
    points[:] *= scale
    points[:] += center

    return avg, scale, center


# De Boor's algorithm for B-Spline interpolation at location 0 <= t <= len(points)
def de_boor(t, points, degree, i=None, n=None):
    if degree == 0:
        return points[i % len(points), :]

    if i is None: i = int(t)
    if n is None: n = degree

    alpha = float(t - i) / (n + 1 - degree)
    return (1 - alpha) * de_boor(t, points, degree - 1, i = i - 1, n = n) + alpha * de_boor(t, points, degree - 1, i = i, n = n)


# TODO: use shapely
# adapted from https://gist.github.com/danieljfarrell/faf7c4cafd683db13cbc
def line_ray_intersection(r_origin, r_dir, p1, p2, norm=True):
    r_origin = np.array(r_origin, dtype=np.float)
    r_dir = np.array(r_dir, dtype=np.float)
    if norm: r_dir /= np.linalg.norm(r_dir)
    p1 = np.array(p1, dtype=np.float)
    p2 = np.array(p2, dtype=np.float)

    v1 = r_origin - p1
    v2 = p2 - p1
    v3 = np.array([-r_dir[1], r_dir[0]])
    t1 = np.cross(v2, v1) / np.dot(v2, v3)
    t2 = np.dot(v1, v3) / np.dot(v2, v3)

    if t1 >= 0.0 and t2 >= 0.0 and t2 <= 1.0:
        return (r_origin + t1 * r_dir, t1)
    else:
        return None
