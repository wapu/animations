import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'elongated_segments'
width, height = 768, 768
duration = 25

webm_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
    '-crf': '1',
}

mp4_params = {
    '-b:v': '1500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
}


def make_frame(t):
    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    progress = t / duration
    p = interval_progresses(progress, 6, ['hermite'] * 5 + ['ease_in'])
    p[5] = 0.5 * (p[5] + ease_in(p[5]))

    # symmetry = randint(3, 15)
    # n_points = 200 * symmetry
    # harmonics = generate_harmonics(symmetry, 7)

    # Fourier series coefficients
    harmonics = [
            (5,      (p[0] - p[2]),   np.pi/2),
            (10,   2*(p[0] - p[2]),   np.pi/2),
            (15,     (p[0] - p[3]),   np.pi/2),
            (20, 2.3*(p[0] - p[5]),   np.pi/2),
            (25,     (p[1] - p[4]),   np.pi/2),
            (30,   2*(p[1] - p[4]), 3*np.pi/2)
        ]
    n_points = 18000
    segment_length = 130

    # get curve
    points = get_shape_from_harmonics(harmonics, n_points, method='zahn & roskies').T

    # rotate
    points = get_rotation_matrix((4*np.pi / 5) * progress).dot(points - center[:,None]) + center[:,None]

    # scale to canvas
    points -= np.mean(points, axis = 1)[:,None]
    s = 300 / np.max(np.sqrt(np.sum(np.square(points), axis=0)))
    points = center + s * points.T

    # end points of elongated segments
    diffs = np.concatenate([np.diff(points, axis=0), (points[0] - points[-1])[None,:]], axis=0)
    p1 = points - segment_length * diffs
    p2 = points + segment_length * diffs

    # draw
    for i in range(len(points)):
        gz.polyline(points=[p1[i], p2[i]], stroke=(1,1,1,0.02), stroke_width=1).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
