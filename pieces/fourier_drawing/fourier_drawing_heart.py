import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'fourier_drawing_heart'
width, height = 768, 768
duration = 5


def get_fourier_coeffs(points, N=0):
    if N == 0: N = len(points)
    z = np.array(points)[None, :, :]
    m = np.arange(-(N//2), N//2+1)[:, None, None]
    k = np.arange(len(points))[None, :, None]
    return np.sum(z * np.exp(-2*np.pi * 1j * m * k/N), axis=1) / N

def reconstruct_curve(coeffs, N):
    t = np.linspace(0, 1, N)[:, None, None]
    m = np.arange(-(len(coeffs)//2), len(coeffs)//2+1)[None, :, None]
    return np.sum(coeffs[None, :, :] * np.exp(2*np.pi * 1j * m * t), axis=1)


# Prepare heart shape
t = np.linspace(-np.pi, np.pi, 500)
x = 16 * np.sin(t)**3
y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
coords = np.stack([x, -y]).T
coords = 270 * coords/np.max(coords)
coeffs = get_fourier_coeffs(coords)
points = reconstruct_curve(coeffs, 1000)


def prepare_circles(coeffs, progress, N=0):
    if N == 0: N = len(coeffs)//2
    coeffs = coeffs[len(coeffs)//2-N:len(coeffs)//2+N+1,:]
    m = np.arange(-N, N+1)

    x_data, y_data = [], []
    for i in range(len(coeffs)):
        re, im = coeffs[i].real, coeffs[i].imag
        r = np.sqrt(im*im + re*re)
        theta = np.arctan2(im, re) + progress * m[i] * 2*np.pi + np.array([0, np.pi/2])
        x_data.append((r[0], theta[0]))
        y_data.append((r[1], theta[1]))

    data = x_data + y_data
    data = sorted(data, key=lambda tup: tup[0], reverse=True)
    return data


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    offset = (width/2, height/2 - 20)
    progress = t / duration

    # Trace arm and draw circles
    data = prepare_circles(coeffs, progress)
    n_data = len(data)
    tip = np.array([0,0])
    arm = [tip]
    for i in range(n_data):
        r, theta = data[i]
        tip_new = tip + r * np.array([np.cos(theta), np.sin(theta)])
        if i > 0:
            gz.circle(xy=tip, r=r, stroke=(.3,.3,.3), stroke_width=1, fill=(1,1,1,.05)).translate(offset).draw(surface)
        tip = tip_new
        arm.append(tip)

    # Draw outline with trailing highlight
    gz.polyline(points=points, stroke_width=0, fill=(1,1,1,.07)).translate(offset).draw(surface)
    head = int(round(len(points) * progress))
    tail_length = len(points)/5
    for i in list(range(head+1,len(points))) + list(range(head+1)):
        i_ = i if (i < head) else (i - len(points))
        segment_color =  [1 - .8 * min(1, (head - i_) / tail_length)]*3
        gz.polyline(points=(points[i,:], points[(i+1) % len(points),:]),
                    stroke=segment_color, stroke_width=3, line_cap='round').translate(offset).draw(surface)

    # Draw arm and endpoints
    gz.polyline(points=arm, stroke=(.8,.8,.8), stroke_width=1).translate(offset).draw(surface)
    gz.circle(xy=(0,0), r=1, fill=(1,1,1)).translate(offset).draw(surface)
    gz.circle(xy=tip, r=2, fill=(1,1,1)).translate(offset).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, t=0)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)

