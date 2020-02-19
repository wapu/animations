import numpy as np
import gizeh as gz
from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'modulus_cosine'
width, height = 768, 768
duration = 7


coords = np.mgrid[:2*width,:2*height].transpose([1,2,0])
d = coords / (2*width, 2*height)
c0 = np.prod(1 - d, axis=2)
c1 = np.prod(d * (-1,1) + (1,0), axis=2)
c2 = np.prod(d * (1,-1) + (0,1), axis=2)
c3 = np.prod(d, axis=2)
cosine_sum = np.sum(np.cos(0.1 * (0.5 + np.abs(d - 0.5)) * (coords - (width, height))), axis=2)

outer_radius = 330
mask = get_circle_mask(width, height, outer_radius)


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 4, 'none')
    ph = interval_progresses(progress, 4, 'hermite')

    I = (p[2] - p[0])/2 + (1 + (p[1] - p[3])/2) * cosine_sum
    
    corners = np.array([ [np.sin(2*np.pi * progress), np.sin(2*np.pi * (progress + 0.25))],
                         [np.sin(2*np.pi * (progress + 0.75)), np.sin(2*np.pi * (progress + 0.5))] ]) * 0.4 + 0.6
    modulus = (corners[0,0] * c0 +
               corners[0,1] * c1 +
               corners[1,0] * c2 +
               corners[1,1] * c3)
    I = np.mod(I, modulus)

    I = resize(I, (width, height))
    I *= mask

    I -= np.min(I)
    I /= np.max(I)
    I = np.tile(I[:,:,np.newaxis], (1,1,4)) * 255

    surface = gz.Surface.from_image(I.astype(np.uint8))
    gz.circle(xy=(width/2, height/2), r=outer_radius, stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
