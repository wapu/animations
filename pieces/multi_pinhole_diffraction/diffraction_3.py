import numpy as np
from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'diffraction_3'
width, height = 768, 768
duration = 4

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
    progress = t / duration

    exposures = 5
    s = 0.5
    wavelength = 30 * 0.442 # 442 nanometers
    theta = 19.8 * (np.pi/180)
    pi_ = 2*np.pi * np.sin(theta) / wavelength

    angles = [0]
    for i in range(exposures):
        angles.append(angles[i] + (72*progress if i%2==0 else 72*(1-progress)) * (np.pi/180))
    angles = angles[1:]

    coords = np.mgrid[-width:width, -height:height].transpose([1,2,0]) * s
    I = np.sum([
            np.square(
                np.sin(pi_ * np.sum(coords * (-np.sin(angles[i]), np.cos(angles[i])), axis=2)))
                    for i in range(exposures)], axis=0)

    I -= np.min(I)
    I /= np.max(I)
    I = I**4
    I = np.maximum(0, np.minimum(1,  I * 2 - 0.25))
    I *= 255

    I = resize(I, (width, height))

    # border
    I *= mask
    I = np.tile(I[:,:,None], (1,1,4))
    surface = gz.Surface.from_image(I.astype(np.uint8))
    gz.circle(xy=(width/2, height/2), r=radius, stroke=(1,1,1), stroke_width=3).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
