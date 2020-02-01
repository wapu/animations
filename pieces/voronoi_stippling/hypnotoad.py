import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from stippling import *


name = 'hypnotoad'
width, height = 768, 768
duration = 3


def prepare_data():
    points = stipple_image_points('hypnotoad.png', n_points=1500, scale_factor=2, max_iterations=100)
    np.save('hypnotoad', points)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration
    points = np.load('hypnotoad.npy') * height/3000

    n_circles = 5
    for j in range(n_circles + 1):
        for i in range(len(points)):
            radius = 3 * (n_circles - j + 2*progress)
            color = [((j+1)%2) * ((1-progress) if j==0 else 1)]*3
            gz.circle(xy=points[i,:], r=radius, fill=color).draw(surface)

            # Innermost white circle
            if j == n_circles and progress > 0.5:
                gz.circle(xy=points[i,:], r=(2*progress - 0.5)*2, fill=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
