import numpy as np
import glob, os
from scipy.misc import imread
from skimage.transform import resize
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from xr import *



name = 'xr_species_line_width'
width, height = 1080, 1080
duration = 1


def densify_polyline(coords, max_dist=2):
    # Add extra points between consecutive coordinates if they're too far apart
    all = []
    for i in range(len(coords)):
        start = coords[(i+1)%len(coords)]
        end = coords[i]
        dense = np.array([t * start + (1-t) * end
                         for t in np.linspace(0, 1, max(1, int(round(np.max(np.abs(end-start))/max_dist))))])
        all.append(dense)
    return np.concatenate(all)


# Create required line segments
def prepare_data():
    xr = get_extinction_symbol_contours(radius=0.41*width, center=(width/2, height/2 - 25))
    xr = geo.Polygon(xr[0], holes=xr[1:])

    def collect(b, lines):
        if isinstance(b, geo.Polygon):
            if b.exterior is not None:
                lines.append(densify_polyline(np.array(b.exterior.coords)))
            for it in b.interiors:
                lines.append(densify_polyline(np.array(it.coords)))
        elif isinstance(b, geo.MultiPolygon):
            for poly in b:
                collect(poly, lines)

    lines = []
    for i in range(-10,0):
        b = xr.buffer(5.25*i + 2, resolution=100).buffer(-2).simplify(.5)
        collect(b, lines)
    for i in range(0,35):
        b = xr.buffer(11.4*i + 2 + 2.5, resolution=100).buffer(-2).simplify(.5)
        collect(b, lines)

    segments = []
    for line in lines:
        segments.append(np.stack([line, np.roll(line, -1, axis=0)]).transpose(1,0,2))
    segments = np.concatenate(segments, axis=0)
    np.save(f'{name}_segments.npy', segments)
    np.save(f'{name}_mids.npy', np.mean(segments, axis=1))


def fit_image(img, relative_radius):
    c = img.shape[0]/2
    r_max = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r = ((i-c)**2 + (j-c)**2) / img.shape[0]**2
            if r > r_max:
                if img[i,j] > 0:
                    r_max = r
    scaling = relative_radius / np.sqrt(r_max)
    img_small = resize(img, (int(img.shape[0] * scaling), int(img.shape[1] * scaling)))
    img_new = np.zeros(img.shape)
    offset = (img.shape[0] - img_small.shape[0])//2
    img_new[offset:offset + img_small.shape[0], offset:offset + img_small.shape[1]] = img_small
    return img_new



# Global stuff outside the render function
species = 'Panthera pardus melas'
img = imread(f'species/critically endangered/{species}.png', mode='F') / 255.0
img = fit_image(img, 0.42)

img2 = imread(f'species/critically endangered/Squatina squatina.png', mode='F') / 255.0
img2 = fit_image(img2, 0.42)

xr = get_extinction_symbol_contours(radius=0.42*width, center=(width/2, height/2 - 25))
xr = geo.Polygon(xr[0], holes=xr[1:])

circle_center = np.array([width/2, height/2 - 25])

segments = np.load(f'{name}_segments.npy')
centers = np.load(f'{name}_mids.npy')
valid = [i for i in range(len(segments)) if np.sum(np.square(circle_center - centers[i])) < (0.44*width)**2]
in_symbol = [xr.contains(geo.Point(centers[i])) for i in range(len(segments))]

shades1 = [img[int(centers[i,1] * img.shape[0]/height), int(centers[i,0] * img.shape[1]/height)] for i in valid]
shades2 = [img2[int(centers[i,1] * img2.shape[0]/height), int(centers[i,0] * img2.shape[1]/height)] for i in valid]



# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    for i, idx in enumerate(valid):
        shade = (1 - progress) * shades1[i] + progress * shades2[i]
        if in_symbol[idx]:
            stroke_width = 1 + 3.25*shade
        else:
            stroke_width = 1 + 7*shade
        gz.polyline(points=segments[idx], stroke=(1,1,1), stroke_width=stroke_width, line_cap='round').draw(surface)

    # gz.circle(xy=circle_center, r=0.6*width, stroke_width=0.35*width, stroke=(0,0,0), fill=None).draw(surface)

    gz.text(species,
            fontfamily='FUCXED CAPS', fontsize=48,
            fill=(.2,.2,.2,1),
            xy=(width/2, height - 25),
            h_align='center', v_align='top').draw(surface)

    return surface.get_npimage()



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

# Render animation
if __name__ == '__main__':
    # prepare_data()
    # save_poster(name, make_frame, t=0)
    render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
