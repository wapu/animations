import numpy as np
from shapely import geometry as geo
from shapely.affinity import translate

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'truchet_tiles'
width, height = 768, 768
duration = 8

n_patterns = 10
tiles = (21, 21)
tile_size = 30
offset = (width/2 - tile_size*tiles[0]/2, height/2 - tile_size*tiles[1]/2)

np.random.seed(123)
pattern = np.random.choice(a=[-1,1], size=(n_patterns, *tiles))


def draw_tile(x, y, size, surface, odd=False, rotation=1, transition=0.3):
    bg, fg = (1,1,1), (.25,.25,.25)
    buff = size/2 * (1 - transition)
    if odd: fg, bg = bg, fg
    if rotation < 0: fg, bg = bg, fg

    square = geo.Polygon([(x,y), (x+size,y), (x+size,y+size), (x,y+size)])
    gz.polyline(points=square.exterior.coords, fill=bg).translate(offset).draw(surface)

    blob = translate(square, rotation * size/2, -size/2).buffer(-0.9999*buff).buffer(buff).intersection(square)
    gz.polyline(points=blob.exterior.coords, fill=fg).translate(offset).draw(surface)

    blob = translate(square, -rotation * size/2, size/2).buffer(-0.9999*buff).buffer(buff).intersection(square)
    gz.polyline(points=blob.exterior.coords, fill=fg).translate(offset).draw(surface)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration
    p = interval_progresses(progress, 2*n_patterns, ['ease_in', 'ease_out']*n_patterns)
    current_pattern = int(progress * n_patterns)
    current_interval = int(progress * 2*n_patterns)

    for i in range(pattern.shape[2]):
        for j in range(pattern.shape[1]):
            if pattern[current_pattern, i, j] == pattern[(current_pattern+1)%n_patterns, i, j]:
                draw_tile(tile_size*i, tile_size*j, tile_size, surface,
                          odd=((i+j)%2 == 0),
                          rotation=pattern[current_pattern, i, j],
                          transition=0)
            else:
                if current_interval%2 == 0:
                    draw_tile(tile_size*i, tile_size*j, tile_size, surface,
                              odd=((i+j)%2 == 0),
                              rotation=pattern[current_pattern, i, j],
                              transition=p[current_interval])
                else:
                    draw_tile(tile_size*i, tile_size*j, tile_size, surface,
                              odd=((i+j)%2 == 0),
                              rotation=pattern[(current_pattern+1)%n_patterns, i, j],
                              transition=1 - p[current_interval])

    gz.circle(r=.65 * width, stroke_width=.5 * width).translate([width/2, height/2]).draw(surface)
    gz.circle(r=.40 * width, stroke_width=2, stroke=(1,1,1)).translate([width/2, height/2]).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
