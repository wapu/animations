import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *


name = 'fractal_lines'
width, height = 768, 768
duration = 4

max_depth = 8
lengths = [180 * (1/2)**i for i in range(max_depth)]
angles = [(0*np.pi/3, 2*np.pi/3, 4*np.pi/3)] * max_depth
speeds = [1/3, -2/3, 2/3, -2/3, 2/3, -2/3, 2/3, -2/3, 2/3, -2/3, 2/3, -2/3, 2/3, -2/3]
alpha = [((i+2)/8)**1.5 for i in range(max_depth)]
widths = [(i+1)/2 for i in range(max_depth,0,-1)]


def draw_recursive(surface, depth, start, angular_offset, progress):
    for a in angles[depth]:
        angle = a + angular_offset + speeds[depth] * progress * 2*np.pi
        end = start + lengths[depth] * np.array([np.sin(angle), -np.cos(angle)])
        gz.polyline(points=[start + 0.1*(end-start), end - 0.1*(end-start)], stroke_width=widths[depth], stroke=(1,1,1,alpha[depth]), line_cap='round').draw(surface)
        if depth+1 < max_depth:
            draw_recursive(surface, depth+1, end, angle, progress)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = hermite(t/duration)

    draw_recursive(surface, 0, np.array([width/2, height/2]), 0, progress)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)

