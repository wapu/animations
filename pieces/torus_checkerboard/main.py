import numpy as np
from shapely import geometry as geo
from shapely.affinity import translate

import sys
sys.path.insert(0, '../../tools')
from rendering import *


name = 'torus_checkerboard'
width, height = 768, 768
duration = 1

r_inner, r_outer = 105, 315
n_rings, n_slices = 18, 72


def r_from_alpha(alpha):
    return 0.5 * (r_outer + r_inner) - 0.5 * (r_outer - r_inner) * np.cos(alpha)

def alpha_from_r(r):
    return np.arccos((0.5 * (r_outer + r_inner) - r) / (0.5 * (r_outer - r_inner)))


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t / duration

    alphas = np.linspace(-0.5*np.pi, 1.5*np.pi, 2*n_rings+1)[::-1] + progress * 2 * np.pi/n_rings
    alphas = np.minimum(np.pi, np.maximum(0, alphas))

    rs = r_from_alpha(alphas)
    
    circles = [geo.point.Point(width/2, height/2).buffer(r) for r in rs]
    rings = [circles[i].difference(circles[i+1]) for i in range(len(circles) - 1)]

    slice_angles = np.linspace(0, 2*np.pi, n_slices+1)
    slices = [translate(geo.polygon.Polygon([
                [0,0],
                [width * np.cos(slice_angles[i]), width * np.sin(slice_angles[i])],
                [width * np.cos(slice_angles[i+1]), width * np.sin(slice_angles[i+1])]
              ]), width/2, height/2) for i in range(len(slice_angles) - 1)]

    for i in range(len(rings)):
        for j in range(len(slices)):
            if (i+j) % 2:
                poly = rings[i].intersection(slices[j])
                if poly.area > 0:
                    r = (rs[i] + rs[i+1]) / 2
                    alpha = alpha_from_r(r)
                    opacity = 0.4 + 0.6 * np.sin(alpha)
                    gz.polyline(points=poly.exterior.coords, fill=(1,1,1, opacity)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
