import numpy as np
from scipy.spatial.distance import pdist, squareform

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'blinking_dots'
width, height = 1024, 1024
duration = 6



def circle_packing(r_max=0.35 * width):
    dots = []
    area_max = np.pi * r_max*r_max
    area_covered = 0
    while area_covered < 0.7 * area_max:
        x = width * np.random.rand()
        y = height * np.random.rand()
        d_center = np.sqrt((x - width/2)**2 + (y - height/2)**2)
        if d_center + 3 < r_max:
            if len(dots) == 0:
                d_min = r_max - d_center
            else:
                d_min = min([np.sqrt((x - xi)**2 + (y - yi)**2) - r for (xi,yi,r) in dots])
            if d_min >= 3:
                r = 3 + np.random.rand() * min(min(d_min - 3, r_max - d_center - 3), 0.2 * r_max)
                dots.append((x,y,r))
                area_covered += np.pi*r*r
                print(area_covered/area_max)
    return dots


# dots = circle_packing()
# np.save(f'{name}.npy', dots)
dots = np.load(f'{name}.npy')

# Create spiral pattern around center
dots[:,0] -= width/2
dots[:,1] -= height/2
phase = np.pi * np.sin(np.arctan2(dots[:,1], dots[:,0]) + 2*np.pi * np.sqrt(np.sum(np.square(dots[:,:2]), axis=1)) / (0.35*width))
dots[:,0] += width/2
dots[:,1] += height/2



# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    for i,(x,y,r) in enumerate(dots):
        r_ = (r-2) * (np.sin(progress*2*np.pi + phase[i]) + 1)/2

        # Empty bubbles variant
        gz.circle(xy=(x,y), r=r_, stroke_width=.5 + (r_**2)/(r**2), stroke=(1,1,1), fill=None).draw(surface)

        # Filled circles variant
        # gz.circle(xy=(x,y), r=0.9*r_ + 1, stroke_width=0, fill=[1 - 0.95*((r_+2)**1.5)/(r**1.5)]*3).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
