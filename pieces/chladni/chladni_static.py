import numpy as np
import gizeh as gz

from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from chladni import *
from geometry import *


name = 'chladni_static'
width, height = 768, 768
duration = 8

radius = 300
mask = get_circle_mask(width, height, radius, fade=150)


def make_frame(t):
    progress = t / duration
    # p = interval_progresses(progress, 4, 'hermite')
    # Squircle path for phase space
    theta = 2*np.pi * progress
    y,x = polar_to_cartesian(1/(np.abs(np.cos(theta))**5 + np.abs(np.sin(theta))**5)**(1/5), theta)

    # Wave pattern with changing phase offset
    # I = get_wolfram_chladni_pattern(5, 4, 2*width, 2*height, lim=2.5, xphase=(p[0] - p[2]) * 4*np.pi, yphase=(p[1] - p[3]) * 4*np.pi)
    I = get_wolfram_chladni_pattern(5, 4, 2*width, 2*height, lim=2.5, xphase=x * 2*np.pi, yphase=y * 2*np.pi)

    I = I%1.0
    I = resize(I, (width, height))
    # I = (np.tanh(I*30) + 1) / 2
    # I = np.minimum(1, 1*np.exp(-np.abs(I)))**4

    # Border fade
    # I *= mask

    I = np.tile(I[:,:,None], (1,1,3)) * 255
    return I.astype(np.uint8)


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
