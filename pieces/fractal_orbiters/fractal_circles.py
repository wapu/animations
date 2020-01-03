import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'fractal_circles'
width, height = 768, 768
duration = 3

n = 5
max_depth = 4


def find_subcircles(X, Y, R, depth, offset):
    r = float(R) * np.sin(np.pi/n) / (1 + np.sin(np.pi/n))
    subcircles = []
    for i in range(n):
        angle = i * 2*np.pi/n
        if (depth%2):
            angle += offset
        else:
            angle -= offset
        # angle += (max_depth + 1 - depth) * offset
        x = X + np.sin(angle) * (R - r)
        y = Y + np.cos(angle) * (R - r)
        subcircles.append((x, y, r))
    return subcircles

def draw_circles(X, Y, R, depth, surface, offset):
    # gz.circle(r = R, xy = [X, Y], stroke = (1,1,1), stroke_width = 1).draw(surface)
    color = [1 - float(depth)/(max_depth+1)]*3
    gz.circle(r = R, xy = [X, Y], fill = color, stroke_width = 0, stroke = (0,0,0)).draw(surface)
    if depth > 0:
        for (x, y, r) in find_subcircles(X, Y, R, depth, offset):
            draw_circles(x, y, r, depth - 1, surface, offset)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t/duration
    offset = progress * 2*np.pi / n

    X, Y, R = width/2, height/2, 0.86*width/2
    draw_circles(X, Y, R, max_depth, surface, offset)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
