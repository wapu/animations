import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'osculating_circles_1'
width, height = 768, 768
duration = 10

webm_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
    '-crf': '1',
}

mp4_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
}


def make_frame(t):
    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    progress = t / duration
    progress = 0.5 * inverse_hermite(progress) + 0.5 * progress
    p = interval_progresses(progress, 3, 'hermite')

    # Fourier series coefficients
    harmonics = [
            (5,  1.5+(p[0] - p[2]), 3*np.pi/2),
            (10, 0.5+(p[0] - p[2]),   np.pi/2),
            (15,     (p[1] - p[0]),   np.pi/2),
            (20,     (p[1] - p[0]),   np.pi/2),
            (25,  -(p[2] - p[1])-0.5, np.pi/2),
            (30,  -(p[2] - p[1])-0.5, np.pi/2)
        ]
    n_points = 27000

    # get curve
    points = get_shape_from_harmonics(harmonics, n_points, method='zahn & roskies').T

    # scale to canvas
    points -= np.mean(points, axis=1)[:,None]
    s = 270 / np.max(np.sqrt(np.sum(np.square(points), axis=0)))
    points = center + s * points.T

    # draw
    for i in range(len(points)):
        p[0] = points[(i-2) % len(points)]
        p[1] = points[ i    % len(points)]
        p[2] = points[(i+2) % len(points)]

        c, r = circle_from_three_points(p[0], p[1], p[2])
        gz.circle(xy=c, r=r, stroke=(1,1,1,0.01), stroke_width=2).draw(surface)

    # outer circle
    gz.circle(xy=center, r=.65 * width, stroke_width=.5 * width, stroke=(0,0,0)).draw(surface)
    gz.circle(xy=center, r=.40 * width, stroke_width=2, stroke=(1,1,1)).draw(surface)

    I = (np.square(surface.get_npimage() / 255) * 255).astype(np.uint8)
    return I


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
