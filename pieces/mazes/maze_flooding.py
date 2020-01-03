import numpy as np
from scipy.misc import imread
from collections import deque
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from maze import *


name = 'maze_flooding'
width, height = 768, 768
duration = 12

cols, rows = 70, 70


def prepare_area():
    surface = gz.Surface(width=cols, height = rows)
    gz.rectangle(lx=cols, ly=rows, xy=(cols/2, rows/2), fill=(0,0,0)).draw(surface)
    gz.circle(xy=(cols/2, rows/2), r=cols/2 - 1, fill=(1,1,1)).draw(surface)
    surface.write_to_png('maze_area.png')
    L = generate_labyrinth(cols, rows, imread('maze_area.png', mode="F") / 255)
    np.save('maze.npy', L)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    gz.circle(xy=(width/2, height/2), r=0.465*width, fill=(.1,.1,.1)).draw(surface)

    progress = t / duration
    # p = interval_progresses(progress, 10, 'hermite')

    L = np.load('maze.npy')
    h, w = L.shape

    n_starts = 5
    starts = 2 * np.round([(35 + 25*np.sin(i * 2*np.pi / n_starts),
                            35 + 25*np.cos(i * 2*np.pi / n_starts)) for i in range(n_starts)]).astype(np.int)
    max_steps = 370 * progress
    frontier = deque([(max_steps, None, starts[i]) for i in range(n_starts)])

    while len(frontier) > 0:
        steps, direction, (x,y) = frontier.popleft()
        if L[y,x] != PATH: continue
        L[y,x] = RESERVED
        if steps < 0:   color = [0,0,0]
        elif steps > 75: color = [.1,.1,.1]
        else:            color = [(.95 - steps/75)**2 + .1] * 3

        for d in range(4):
            if direction is not None and d == (direction + 2) % 4: continue
            if d == 0: # up
                if y > 1   and L[y-1,x] == PATH:
                    frontier.append((steps - 1, d, (x,y-2)))
                    if color is not None:
                        gz.polyline(points=[labyrinth_to_canvas(y, x, L, width, height), labyrinth_to_canvas(y-2, x, L, width, height)],
                                    stroke=color, stroke_width=5, line_cap='round').draw(surface)
            if d == 1: # left
                if x > 1   and L[y,x-1] == PATH:
                    frontier.append((steps - 1, d, (x-2,y)))
                    if color is not None:
                        gz.polyline(points=[labyrinth_to_canvas(y, x, L, width, height), labyrinth_to_canvas(y, x-2, L, width, height)],
                                    stroke=color, stroke_width=5, line_cap='round').draw(surface)
            if d == 2: # down
                if y < h-2 and L[y+1,x] == PATH:
                    frontier.append((steps - 1, d, (x,y+2)))
                    if color is not None:
                        gz.polyline(points=[labyrinth_to_canvas(y, x, L, width, height), labyrinth_to_canvas(y+2, x, L, width, height)],
                                    stroke=color, stroke_width=5, line_cap='round').draw(surface)
            if d == 3: # right
                if x < w-2 and L[y,x+1] == PATH:
                    frontier.append((steps - 1, d, (x+2,y)))
                    if color is not None:
                        gz.polyline(points=[labyrinth_to_canvas(y, x, L, width, height), labyrinth_to_canvas(y, x+2, L, width, height)],
                                    stroke=color, stroke_width=5, line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_area()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
