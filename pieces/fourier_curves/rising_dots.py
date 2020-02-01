import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'rising_dots'
width, height = 768, 768
duration = 5


# Render frame at time t
duration_4 = 10

# Fourier series coefficients
harmonics = [
        ( 3,  0.9 + 1.2,   np.pi/2),
        ( 6,  0.2 + 0.0, 3*np.pi/2),
        (12, -0.4 + 0.4, 3*np.pi/2),
        (15, -0.1 + 1.0,   np.pi/2),
        (21,  1.3 + 1.5, 3*np.pi/2)
    ]

# Get curve
n_points = 3000
points = np.array(get_shape_from_harmonics(harmonics, n_points, method='zahn & roskies')).T

# Scale to canvas
points -= np.mean(points, axis=1)[:,None]
s = 90*3 / np.max(np.sqrt(np.sum(np.square(points), axis=0)))
center = np.array((width/2, height/2))
points = center + s * points.T
points = np.concatenate([points, points])


def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t / duration

    # Draw
    for j in range(50):
        color = [((j+1)/50)**2] * 3
        w = ((j+1)/50)**2
        for i in range(30):
            start = 100*i+j + int(progress*n_points/30)
            gz.polyline(points=points[start:start+2,:], stroke_width=3*w+4, stroke=(0,0,0), line_cap='butt').draw(surface)
            if j==18:
                gz.circle(xy=points[start+1,:], r=3.5*w, fill=(0,0,0)).draw(surface)
            gz.polyline(points=points[start:start+2,:], stroke_width=3*w, stroke=color, line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
