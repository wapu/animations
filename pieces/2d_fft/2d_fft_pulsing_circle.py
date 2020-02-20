import numpy as np
import gizeh as gz

from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = '2d_fft_pulsing_circle'
width, height = 768, 768
duration = 10


def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 2, 'hermite')
    p = interval_progresses(p[0], 2, 'none') + interval_progresses(p[1], 2, 'none')

    # circle
    surface = gz.Surface(2*width, 2*height)
    gz.circle(xy=(width, height),
              r=40 + 3*(p[0] - p[1] - p[2] + p[3]),
              stroke_width=8 + 4*(p[0] + p[1] - p[2] - p[3]),
              stroke=(1,1,1)).draw(surface)

    # FFT
    I = np.fft.fft2(surface.get_npimage()[:,:,0]/255)
    I = np.log(np.abs(I) + 0.00001).astype(np.float32)
    I = 1 - np.minimum(1, np.maximum(0, I))
    I = resize(I, (width, height))

    # border
    radius = (300 + 15 * (p[0] + p[1] - p[2] - p[3]))
    I *= get_circle_mask(width, height, radius)
    I = np.tile(I[:,:,np.newaxis], (1,1,4)) * 255
    surface = gz.Surface.from_image(I.astype(np.uint8))
    gz.circle(xy=(width/2, height/2), r=radius, stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
