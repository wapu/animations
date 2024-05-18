import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'trailing_shades'
width, height = 768, 768
duration = 10

webm_params = {
    '-b:v': '3000k',
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
    progress = (progress + 0.125) % 1

    n_shades = 300
    shade_interval = .25
    for i in range(n_shades):
        progress_shifted = (progress + shade_interval*(i+1)/n_shades - shade_interval) % 1
        #progress_shifted = hermite(progress_shifted)
        p = interval_progresses(progress_shifted, 4, 'hermite')

        # Fourier series coefficients
        harmonics = [
                ( 3, 0.9*(p[0] - p[3]) + 1.2,   np.pi/2),
                ( 6, 0.2*(p[0] - p[2]) + 0.0, 3*np.pi/2),
                ( 9, 0.9*(p[1] - p[2]) + 1.0,   np.pi/2),
                (12, 0.4*(p[1] - p[0]) + 0.4, 3*np.pi/2),
                (15, 0.1*(p[3] - p[0]) + 1.0,   np.pi/2),
                (18, 0.1*(p[3] - p[1]) + 0.2,   np.pi/2),
                (21, 1.3*(p[0] - p[3]) + 1.5, 3*np.pi/2)
            ]

        # get curve
        n_points = 2000
        points = get_shape_from_harmonics(harmonics, n_points, method='zahn & roskies').T

        # rotate
        points = get_rotation_matrix(2*np.pi * progress_shifted/3).dot(points - center[:,None]) + center[:,None]

        # scale to canvas
        points -= np.mean(points, axis=1)[:,None]
        s = 270 / np.max(np.sqrt(np.sum(np.square(points), axis=0)))
        points = center + s * points.T

        # draw
        if i+1 < n_shades:
            color = (1,1,1, 0.05 * np.square((i+1)/n_shades))
        else:
            color = (1,1,1, 0.25)
        gz.polyline(points=points, close_path=True, stroke=color, stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
