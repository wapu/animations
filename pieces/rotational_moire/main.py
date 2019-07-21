import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'rotational_moire'
width, height = 768, 768
duration = 6

rows, cols, dist, radius = 25, 25, 27, 3


webm_params = {
    '-b:v': '3000k',
    '-crf': '0',
}

mp4_params = {
    '-b:v': '3000k',
}


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    color = (.8,.8,.8)

    progress = hermite(t / duration)
    angle0 = 0.5*np.pi * (t / duration)
    angle1 = 0.5*np.pi * progress + angle0
    angle2 = 0.5*np.pi * progress * 2 + angle0

    grid_base = get_grid_coordinates(rows, cols, dist, True)
    grid0 = grid_base.dot(get_rotation_matrix(angle0))
    grid1 = grid_base.dot(get_rotation_matrix(angle1))
    grid2 = grid_base.dot(get_rotation_matrix(angle2))

    center = np.array([width/2, height/2])
    for i in range(grid0.shape[0]):
        gz.circle(r=radius, xy=center + grid0[i], fill=color).draw(surface)
        gz.circle(r=radius, xy=center + grid1[i], fill=color).draw(surface)
        gz.circle(r=radius, xy=center + grid2[i], fill=color).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
