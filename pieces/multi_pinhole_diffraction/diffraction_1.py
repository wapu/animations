import numpy as np
from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'diffraction_1'
width, height = 768, 768
duration = 8

webm_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
    '-crf': '3',
}

mp4_params = {
    '-b:v': '3500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
}


radius = 330
mask = get_circle_mask(width, height, r=radius, fade=0)


def make_frame(t):
    progress = hermite(t / duration)

    pinholes = 7
    s = 0.15
    pi_ = np.pi * (1 + progress) * (2/pinholes)

    coords = np.mgrid[-width:width, -height:height].transpose([1,2,0]) * s
    I = np.abs(np.sum([ np.exp(np.sum(1j*coords * (np.cos(j * pi_), np.sin(j * pi_)), axis=2))
                           for j in range(pinholes)], axis = 0))

    I -= np.min(I)
    I /= np.max(I)
    I = I**4
    I = np.minimum(1, I*2)
    I *= 255.0

    I = resize(I, (width, height))

    # border
    I *= mask
    I = np.tile(I[:,:,None], (1,1,4))
    surface = gz.Surface.from_image(I.astype(np.uint8))
    gz.circle(xy=(width/2, height/2), r=radius, stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
