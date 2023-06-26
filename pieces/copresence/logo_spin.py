import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'logo_spin'
width, height = 1920, 1080
duration = 3

cx = width/2
cy = height/2
r = 0.4 * height
n_points = 480


def arc_coords(start, end, n_points=n_points, radius=r, center=(cx,cy)):
    angles = np.linspace(start, end, n_points, endpoint=True)
    X = np.cos(angles) * radius + center[0]
    Y = -np.sin(angles) * radius + center[1]
    return np.stack([X,Y], axis=-1)

def draw_arc(start, end, surface, n_points=n_points, radius=r, center=(cx,cy), c_start=0, c_end=1):
    points = arc_coords(start, end, n_points, r, center)
    for i in range(n_points-1):
        color = [c_start + (c_end - c_start) * i/(n_points-1)]*3
        gz.polyline(points=[center, points[i], points[i+1]],
                    stroke=color, stroke_width=1, line_cap='round',
                    fill=color).draw(surface)


# Times for stage transitions
ts = [0.09, 0.29, 0.42, 0.55, 0.75]


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    # Show logo
    if 0.00 <= progress < ts[0]:
        # back
        draw_arc(0, np.pi, surface, center=(cx - r/2, cy), c_start=0, c_end=.5)
        draw_arc(np.pi, 2*np.pi, surface, center=(cx + r/2, cy), c_start=0, c_end=.5)

        # front
        draw_arc(np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=.5, c_end=1)
        draw_arc(0, np.pi, surface, center=(cx + r/2, cy), c_start=.5, c_end=1)

    # stage 1 - circles pull back 360° into middle line
    if ts[0] <= progress < ts[1]:
        p = interval_progress(progress, (ts[0], ts[1]), 'ease_in')

        if p < 0.5:
            # retracting back
            draw_arc(2*p * np.pi, np.pi, surface, center=(cx - r/2, cy), c_start=0, c_end=.5)
            draw_arc((1 + 2*p) * np.pi, 2*np.pi, surface, center=(cx + r/2, cy), c_start=0, c_end=.5)

            # static front
            draw_arc(np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=.5, c_end=1)
            draw_arc(0, np.pi, surface, center=(cx + r/2, cy), c_start=.5, c_end=1)

        else:
            # only retracting front
            p_ = p - 0.5
            draw_arc((1 + 2*p_) * np.pi, 2*np.pi, surface, center=(cx - r/2, cy), c_start=.5, c_end=1)
            draw_arc(2*p_ * np.pi, np.pi, surface, center=(cx + r/2, cy), c_start=.5, c_end=1)

    # stage 2 - line keeps momentum, rotates 180° and stretches to 2r
    if ts[1] <= progress < ts[2]:
        p = interval_progress(progress, (ts[1], ts[2]), 'none')

        gz.polyline(points=[(cx - (1+p)*r/2, cy), (cx + (1+p)*r/2, cy)],
                    stroke=(1,1,1), stroke_width=2, line_cap='round').rotate(-p*np.pi, center=(cx,cy)).draw(surface)

    # stage 3 - line rotates 180° into shaded circle
    if ts[2] <= progress < ts[3]:
        p = interval_progress(progress, (ts[2], ts[3]), 'none')

        draw_arc(0, p * np.pi, surface, center=(cx, cy), c_start=0, c_end=1)
        draw_arc(np.pi, (p+1) * np.pi, surface, center=(cx, cy), c_start=0, c_end=1)

    # stage 4 - circle rotates on 180° and gets to min 50% opacity
    if ts[3] <= progress < ts[4]:
        p = interval_progress(progress, (ts[3], ts[4]), 'ease_out')

        draw_arc(p * np.pi, (p+1) * np.pi, surface, center=(cx, cy), c_start=0.5*p, c_end=1)
        draw_arc((p+1) * np.pi, (p+2) * np.pi, surface, center=(cx, cy), c_start=0.5*p, c_end=1)

    # stage 5 - circle halves phase apart
    if ts[4] <= progress < 1.00:
        p = interval_progress(progress, (ts[4], 1.00), 'hermite')

        # back
        draw_arc(0, np.pi, surface, center=(cx - p*r/2, cy), c_start=0, c_end=.5)
        draw_arc(np.pi, 2*np.pi, surface, center=(cx + p*r/2, cy), c_start=0, c_end=.5)

        # front
        draw_arc(np.pi, 2*np.pi, surface, center=(cx - p*r/2, cy), c_start=.5, c_end=1)
        draw_arc(0, np.pi, surface, center=(cx + p*r/2, cy), c_start=.5, c_end=1)


    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
