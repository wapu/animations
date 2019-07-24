import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'sine_rings_wandering'
width, height = 768, 768
duration = 10


def modulate_sin(sin, current_angle, peak_angle, radius):
    diff = np.abs(2*radius*np.pi/180 + current_angle - peak_angle) % (2*np.pi)
    diff[diff > np.pi] = 2*np.pi - diff[diff > np.pi]
    factor = np.exp(-np.square(diff)/2) * 2
    return factor * sin + current_angle


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration
    peak_angle = progress * 2*np.pi
    points = []

    # Add sine waves
    domain = np.linspace(0,360,1000)
    sin = (20 - domain/25) * np.sin(domain/7 + 2*np.pi*progress) * np.pi/180
    for i in range(36):
        sin_points = polar_to_cartesian_np(np.stack([domain, modulate_sin(sin, 2*i * np.pi/36, peak_angle, domain)])).T + width/2
        sin_points2 = polar_to_cartesian_np(np.stack([domain, modulate_sin(sin, (2*i+1) * np.pi/36, peak_angle, domain)])).T + width/2
        points.extend(list(sin_points))
        points.extend(list(sin_points2)[::-1])

    # Draw
    gz.polyline(points=points, stroke_width=0, fill=(1,1,1,1), close_path=True).draw(surface)
    gz.circle(xy=(width/2, height/2), r=360, stroke_width=24, stroke=(0,0,0)).draw(surface)
    # gz.circle(xy=(width/2, height/2), r=360-12, stroke_width=2, stroke=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
