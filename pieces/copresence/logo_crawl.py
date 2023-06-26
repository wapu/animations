import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'logo_crawl'
width, height = 1920, 1080
duration = 8

cx = width/2
cy = height/2
r = 0.4 * height
n_points = 360


def arc_coords(start, end, n_points=n_points, radius=r, center=(cx,cy)):
    angles = np.linspace(start, end, n_points, endpoint=True)
    X = np.cos(angles) * radius + center[0]
    Y = -np.sin(angles) * radius + center[1]
    return np.stack([X,Y], axis=-1)

def draw_arc(start, end, surface, n_points=n_points, radius=r, center=(cx,cy), c_start=0, c_end=1):
    points = arc_coords(start, end, n_points, r, center)
    for i in range(n_points-1):
        color = c_start + (c_end - c_start) * i/(n_points-1)
        color = [hermite(color)]*3
        gz.polyline(points=[center, points[i], points[i+1]],
                    stroke=color, stroke_width=2, line_cap='round',
                    fill=color).draw(surface)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    if progress < 0.5:
        p = interval_progress(progress, (0, 0.5))
        pp = interval_progresses(p, 2, [None])

        # left
        draw_arc(p * 2*np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=0, c_end=1 - p)
        draw_arc(0, p * 2*np.pi, surface, center=(cx - r/2, cy), c_start=p, c_end=0)

        # right
        draw_arc(np.pi, (3 - 2*p)*np.pi, surface, center=(cx + r/2, cy), c_start=p, c_end=1)
        draw_arc((3 - 2*p)*np.pi, 3*np.pi, surface, center=(cx + r/2, cy), c_start=1, c_end=1 - p)

        # front (lower half of left circle)
        draw_arc(np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=0.5 - 0.5*pp[0] + 0.5*pp[1], c_end=1 - p)

    else:
        p = interval_progress(progress, (0.5, 1))
        pp = interval_progresses(p, 2, [None])

        # left
        draw_arc(p * 2*np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=1, c_end=p)
        draw_arc(0, p * 2*np.pi, surface, center=(cx - r/2, cy), c_start=1 - p, c_end=1)

        # right
        draw_arc(np.pi, (3 - 2*p)*np.pi, surface, center=(cx + r/2, cy), c_start=1 - p, c_end=0)
        draw_arc((3 - 2*p)*np.pi, 3*np.pi, surface, center=(cx + r/2, cy), c_start=0, c_end=p)

        # front (lower half of left circle)
        draw_arc(np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=0.5 + 0.5*pp[0] - 0.5*pp[1], c_end=p)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
