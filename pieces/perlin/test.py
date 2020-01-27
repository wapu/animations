import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from perlin import *


name = 'test'
width, height = 768, 768
duration = 3

# noise_x = fractal_perlin((width, height)) + 0.3
noise_x = np.ones((width, height))
noise_y = 2*fractal_perlin((width, height))
noise = np.stack([noise_x, noise_y]).transpose(1,2,0)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    color = np.array([1,1,1])

    progress = t / duration
    p = np.stack([100*np.ones(300), np.linspace(100, height-100, 300)]).T
    v = np.stack([np.ones(300), np.zeros(300)]).T

    for i in range(100):
        p_new = p + v
        for j in range(len(p)):
            gz.polyline(points=(p[j], p_new[j]),
                        stroke=(1,1,1,.2), stroke_width=1).draw(surface)
            try:
                v[j] = v[j] + 0.2 * noise[p[j][0].astype(int), p[j][1].astype(int)]
            except:
                pass
        p = p_new

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
