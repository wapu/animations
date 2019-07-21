import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'lineart_flower'
width, height = 768, 768
duration = 12


webm_params = {
    '-speed': '0',
    '-b:v': '5000k',
    '-minrate': '50k',
    '-maxrate': '15000k',
    '-crf': '0',
}

mp4_params = {
    '-b:v': '5000k',
    '-minrate': '50k',
    '-maxrate': '15000k',
}


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t / duration
    p = interval_progresses(progress, 2, 'none')

    n_points, n_seeds = 486, 6
    radius = 330
    C = get_circle_coordinates(n_points, radius, (width/2, height/2))
    # rotate_positions_around(C, -6*pi * progress, (h/2, w/2))

    min_lines_per_seed = int(p[1] * n_points)
    max_lines_per_seed = int(p[0] * n_points)

    # draw lines starting from each seed
    for j in range(min_lines_per_seed, max_lines_per_seed):
        opacity = 0.3 * ((j - min_lines_per_seed)**2 + (max_lines_per_seed - j)**2) / (max_lines_per_seed - min_lines_per_seed)**2
        for i in range(n_seeds):
            i_seed = i * (n_points // n_seeds)
            i_seed -= int(round(1.5 * (min_lines_per_seed + max_lines_per_seed))) # imitates rotation
            gz.polyline(points=[C[(i_seed + (j+1)) % n_points], C[(i_seed + 2*(j+1)) % n_points]],
                        stroke=(1,1,1,opacity), stroke_width=1).draw(surface)

    # draw outer circle
    gz.circle(r=radius, xy=(width/2, height/2), stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
