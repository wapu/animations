import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'fourier_drawing_xy'
width, height = 768, 768
duration = 10


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


coords = np.load('fourier_drawing_xy_coords.npy')[::8]
coords = 150 * coords/np.max(coords)
coeffs = get_fourier_coeffs(coords)
points = reconstruct_curve(coeffs, 1000)

def prepare_data(coeffs, progress, N=0):
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

    x_data = sorted(x_data, key=lambda tup: tup[0], reverse=True)
    y_data = sorted(y_data, key=lambda tup: tup[0], reverse=True)
    return x_data, y_data


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration
    x_data, y_data = prepare_data(coeffs, progress)
    n_data = len(x_data)

    x_tip = np.array([0, 250])
    for i in range(n_data):
        r, theta = x_data[i]
        x_tip_new = x_tip + r * np.array([np.cos(theta), np.sin(theta)])
        gz.circle(xy=x_tip, r=r, stroke=(1,1,1,.25) if i>0 else (1,0,0,1), stroke_width=1).translate([width/2,height/2]).draw(surface)
        gz.polyline(points=[x_tip, x_tip_new], stroke=(1,1,0,.5), stroke_width=1).translate([width/2, height/2]).draw(surface)
        x_tip = x_tip_new

    y_tip = np.array([-250, 0])
    for i in range(n_data):
        r, theta = y_data[i]
        y_tip_new = y_tip + r * np.array([np.cos(theta), np.sin(theta)])
        gz.circle(xy=y_tip, r=r, stroke=(1,1,1,.25) if i>0 else (1,0,0,1), stroke_width=1).translate([width/2,height/2]).draw(surface)
        gz.polyline(points=[y_tip, y_tip_new], stroke=(1,1,0,.5), stroke_width=1).translate([width/2, height/2]).draw(surface)
        y_tip = y_tip_new

    target = (x_tip[0], y_tip[1])
    gz.polyline(points=[y_tip, target], stroke=(1,1,1,.25), stroke_width=1).translate([width/2,height/2]).draw(surface)
    gz.polyline(points=[x_tip, target], stroke=(1,1,1,.25), stroke_width=1).translate([width/2,height/2]).draw(surface)

    gz.polyline(points=points, stroke=(1,1,1,.5), stroke_width=1).translate([width/2, height/2]).draw(surface)
    gz.circle(xy=target, r=3, fill=(1,1,1)).translate([width/2,height/2]).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, t=0)
    render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)

