import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from chladni import *
from geometry import *


name = 'chladni_kaleidoscope_6'
width, height = 768, 768
duration = 10

radius = 300
mask = get_circle_mask(width, height, radius, fade=150)


def make_frame(t):
    progress = t / duration
    p = np.mean(interval_progresses(progress, 4, 'hermite')) * 2*np.pi

    # Overlayed wave patterns
    n = 3 + np.sin(p)
    m = 4 + np.cos(p)
    I = np.mean([np.exp(-np.abs(get_chladni_pattern(n, m, width, height, lim=1.5, angle=i * 2*np.pi/6)))**8 for i in range(6)], axis=0)
    I = np.minimum(1, 3*I)**3

    # Border fade
    I *= mask

    I = np.tile(I[:,:,None], (1,1,3)) * 255
    return I.astype(np.uint8)


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, type='png')
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
