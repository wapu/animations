import numpy as np
import gizeh as gz
from scipy.ndimage import gaussian_filter
from scipy.misc import imsave, imread

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from xr import *


name = 'xr_dot_size'
width, height = 768, 768
duration = 10
r_min = .5
r_max = 5

def prepare_data():
    surface = gz.Surface(width,height)
    offset = np.array((width/2,height/2))
    gz.square(l=width, xy=offset, fill=(0,0,0)).draw(surface)

    radius, corners, stroke_width = get_extinction_symbol_params(0.35*width)
    gz.circle(r=radius, xy=offset, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    gz.polyline(points=corners + offset, close_path=True, fill=None, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)

    img = surface.get_npimage()[:,:,0]
    img = gaussian_filter(img, sigma=width/50, truncate=10)
    imsave(f'extinction_symbol_soft_{width}.png', img)


xr = imread(f'extinction_symbol_soft_{width}.png').T


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    points = np.mgrid[:width:16,:height:12].astype(float)
    points[0,:,::2] = (points[0,:,::2] + 8 + 160 * progress) % width
    points[0,:,1::2] = (points[0,:,1::2] - 160 * progress) % width
    points = points.reshape(2,-1).T
    rotate_around(points, 2*np.pi*progress, (width/2, height/2))

    for x,y in points:
        d = np.sqrt((x-width/2)**2 + (y-height/2)**2)
        if d < width/2-30:
            r = r_min + (r_max - r_min) * xr[int(x), int(y)]/255
            gz.circle(xy=(x,y), r=r, fill=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
