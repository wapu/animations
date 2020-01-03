import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *


name = 'lissajous_interpolation'
width, height = 768, 768
duration = 20


def lissajous_points(a=1, b=1, c=0, delta=np.pi/2, gamma=0, N=1000):
    t = np.linspace(0, 2*np.pi, N)
    return np.stack([np.sin(a*t), np.sin(b*t + delta), np.sin(c*t + gamma)], axis=1)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t/duration

    lines = [
        lissajous_points(1, 1, 1,  np.pi/2, np.pi/2),
        lissajous_points(3, 4, 1, -np.pi/4, np.pi/2),
        lissajous_points(5, 4, 1,     0.74, np.pi/2),
        lissajous_points(5, 6, 1,  np.pi/4, np.pi/2),
        lissajous_points(7, 6, 1, -np.pi/4, np.pi/2),
        lissajous_points(7, 3, 1,     5.79, np.pi/2),
        lissajous_points(5, 3, 1,     1.11, np.pi/2),
        lissajous_points(5, 6, 1,     5.18, np.pi/2),
        lissajous_points(1, 6, 1,     3.70, np.pi/2),
        lissajous_points(1, 2, 1,     0.89, np.pi/2),
        lissajous_points(3, 2, 1, -np.pi/4, np.pi/2),
    ]
    lines.append(lines[0])
    lines = np.array(lines) * 225 + (width/2, height/2, 0)

    weights = equidistant_weight_functions(progress, len(lines), 'hermite')
    points = np.sum([weights[j] * lines[j] for j in range(len(weights))], axis=0)
    
    # Switch from points to lines and sort by depth
    lines = np.array([(points[i,:2], points[(i+1)%len(points),:2]) for i in range(len(points))])
    z_lines = np.array([(points[i,2] + points[(i+1)%len(points),2]) / 2 for i in range(len(points))])
    sort_indices = np.argsort(z_lines)
    lines = lines[sort_indices]
    z_lines = z_lines[sort_indices]

    # Relative depth for shading
    z_min, z_max = z_lines.min(), z_lines.max()
    z_ratios = (z_lines - z_min) / (z_max - z_min)

    # Draw lines
    for i in range(len(lines)):
        gz.polyline(points = lines[i],
                    stroke_width = 5 + 5 * z_ratios[i],
                    stroke = (0,0,0),
                    line_cap = 'butt').draw(surface)
        gz.polyline(points = lines[i],
                    stroke_width = 4 + 2 * z_ratios[i],
                    stroke = [0.33 + 0.67 * z_ratios[i]]*3,
                    line_cap = 'round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
