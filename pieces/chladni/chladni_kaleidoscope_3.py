import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from chladni import *
from geometry import *


name = 'chladni_kaleidoscope_3'
width, height = 768, 768
duration = 10

radius = 300
mask = get_circle_mask(width, height, radius, fade=150)


def make_frame(t):
    progress = t / duration
    p = np.mean(interval_progresses(progress, 4, 'hermite')) * 2*np.pi

    # Overlayed wave patterns
    n = 7 + 2*np.sin(p)
    m = 9 + np.cos(p)
    I = np.mean([np.exp(-np.abs(get_chladni_pattern(n, m, width, height, lim=1.5, angle=i * 2*np.pi/3)))**8 for i in range(3)], axis=0)
    I = np.minimum(1, 2*I)**2

    # Border fade
    I *= mask

    I = np.tile(I[:,:,None], (1,1,3)) * 255
    return I.astype(np.uint8)


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, type='png')
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
