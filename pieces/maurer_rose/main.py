import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *


name = 'maurer_rose'
width, height = 768, 768
duration = 10
radius = 330

webm_params = {
    '-framerate': '25',
    '-speed': '0',
    '-b:v': '5000k',
    '-minrate': '1000k',
    '-maxrate': '15000k',
    '-crf': '0',
}

mp4_params = {
    '-tune': 'animation',
    '-b:v': '5000k',
    '-minrate': '1000k',
    '-maxrate': '15000k',
}


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    
    progress = t/duration
    p = 0.75 + 0.25 * np.sin(progress * 2*np.pi)
    
    points = []
    n, d = 6, 71
    segments = int(round(360 * p / 2)) * 2
    if segments % d == 0: segments += 2

    for k in range(segments):
        theta = k*d * (2*np.pi/segments)
        r = np.sin(n*theta)
        x = radius * r * np.cos(theta)
        y = radius * r * np.sin(theta)
        points.append((x,y))

    gz.text(f'{segments} segments',
            fontfamily='Impact', fontsize=24,
            fill=(.3,.3,.3),
            xy=(width - 70, height - 50),
            h_align='right', v_align='top').draw(surface)

    angle = progress * 2*np.pi / 3
    if len(points) > 0:
        gz.polyline(
            points=points,
            stroke=(1,1,1),
            stroke_width=5,
            close_path=True
        ).rotate(angle).translate([width/2, height/2]).draw(surface)

        gz.polyline(
            points=points,
            stroke=(0.5,0.5,0.5),
            stroke_width=3,
            close_path=True
        ).rotate(angle).translate([width/2, height/2]).draw(surface)

        gz.polyline(
            points=points,
            stroke=(0,0,0),
            stroke_width=1,
            close_path=True
        ).rotate(angle).translate([width/2, height/2]).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)