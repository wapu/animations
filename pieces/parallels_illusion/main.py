import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'parallels_illusion'
width, height = 768, 768
duration = 5

rows = 11
boxes = 5
size = 0.7 * height / rows


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t/duration
    p_cos = np.cos(2*np.pi*progress)
    amplitude = 0.666*size
    offsets = np.array([0, -amplitude, 0, amplitude, 0, -amplitude, 0, amplitude, 0, -amplitude, 0]) * p_cos

    x_start = width/2 - (2*boxes-1)*size/2 + size/2
    y_start = height/2 - rows*size/2 + size/2

    for i in range(rows):
        y = y_start + i*size
        for j in range(boxes):
            gz.square(l = size, xy = (x_start + offsets[i] + 2*j*size, y), fill = (1,1,1)).draw(surface)
        gz.polyline(points = [(x_start + min(offsets[i-1], offsets[i]) - size/2, y - size/2),
                              (x_start + max(offsets[i-1], offsets[i]) + (2*boxes-1)*size - size/2, y - size/2)],
                    stroke_width = 1, stroke = (.5,.5,.5)).draw(surface)

    gz.polyline(points = [(x_start - size/2, y + size/2), (x_start + (2*boxes-1)*size - size/2, y + size/2)],
                stroke_width = 1, stroke = (.5,.5,.5)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
