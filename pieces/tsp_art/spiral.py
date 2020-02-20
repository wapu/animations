import numpy as np
import gizeh as gz

from scipy.linalg import norm
from math import sin, cos, pi

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from stippling import *
from tsp import *


name = 'spiral_tsp'
width, height = 768, 768
duration = 60


def prepare():
    surface = gz.Surface(width, height)
    gz.rectangle(lx=width, ly=height, xy=(width/2, height/2), fill=(0,0,0)).draw(surface)
    gz.circle(xy=(width/2, height/2), r=width/2 - 10, fill=(1,1,1)).draw(surface)
    gz.circle(xy=(width/2, height/2), r=width/2 - 40, fill=(0,0,0)).draw(surface)
    surface.write_to_png('spiral_ring.png')

    points = stipple_image_points('spiral_ring.png', n_points=5000, scale_factor=2, max_iterations=50)
    np.save('spiral_ring.npy', points)
    write_tsp('spiral_ring.tsp', points)

    run_linkern('spiral_ring.tsp', 'spiral_ring.cyc', '../../tools/linkern.exe')
    postprocess_cyc('spiral_ring.npy', 'spiral_ring.cyc',
                    'spiral_ring_processed.npy', (256, 256), segment_length=5, degree=3, normalize_points=False)


def cartesian_to_polar_slow(x_y):
    r = []
    t = []
    for i in range(len(x_y)):
        r.append( np.sqrt(np.sum(np.square(x_y[i]))) )
        t.append( np.arctan2(x_y[i,1], x_y[i,0]) )
        if i > 0:
            if t[-1] > (t[-2] + np.pi):
                t[-1] -= 2*np.pi
            if t[-1] < (t[-2] - np.pi):
                t[-1] += 2*np.pi
    return np.vstack([r, t]).T - (0, min(t))


center = (width/2, height/2)
points_c = np.load('spiral_ring_processed.npy') / 2
points_p = cartesian_to_polar_slow(points_c - center)
r_min, r_max = points_p[:,0].min(), points_p[:,0].max()
r = (r_min + r_max) / 2

stretch = 2.6
n_reps = 5
points_ = np.concatenate([points_p + (0, 2*i*np.pi) for i in range(n_reps)][::-1])[::-1]


def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    cut = int(progress * len(points_p)) + 430
    points = np.concatenate([points_[cut:], points_[:cut] + (0, 2*np.pi*n_reps)])
    points[:,1] -= 2*np.pi * progress
    points[:,1] *= stretch

    r_coefficients = np.power(points[:,1] / (2*np.pi*n_reps*stretch), 3)
    points[:,0] *= r_coefficients

    mean_rs = r * r_coefficients
    points[:,0] = (points[:,0] - mean_rs) * stretch + mean_rs

    points[:,0] *= 0.8
    points[:,1] += 2*np.pi * progress - 0.5 * np.pi
    points = polar_to_cartesian_np(points) + center

    surface = gz.Surface(width, height)
    n_segments = 50
    for i in range(10,n_segments):
        color = [1,1,1,((i+1)/n_segments)**2]
        gz.polyline(points=points[len(points)*i//n_segments : len(points)*(i+1)//n_segments + 1],
                    stroke_width=2*(i+1)/n_segments, stroke=color).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
