import numpy as np
from ortools.graph import pywrapgraph
import glob, os

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from stippling import *



name = 'xr_species'
width, height = 1080, 1080
n_points = 10000
duration = 10 # 300

# np.random.seed(123)
# species_pngs = sorted(glob.glob('species/critically endangered/*.png'))
# species_pngs = list(np.random.permutation(species_pngs))
# species_names = [png.split('\\')[-1].split('.')[0] for png in species_pngs]

species_names = ['Lotus maculatus']
print(f'Stipple image for species {species_names[0]}:')
points = stipple_image_points(f'species/critically endangered/{species_names[0]}.png', n_points=n_points, scale_factor=1, max_iterations=100)
np.save(f'species/np/{species_names[0]}', points)


def dist(A, B):
    BA = np.dot(B, np.transpose(A))
    BB = np.sum(np.square(B), axis=1)
    AA = np.sum(np.square(A), axis=1)
    return np.sqrt(np.transpose(AA - 2 * BA) + BB)


def best_permutation(A, B):
    costs = np.round(np.square(dist(A, B)))
    assignment = pywrapgraph.LinearSumAssignment()
    for a in range(costs.shape[0]):
        for b in range(costs.shape[1]):
            assignment.AddArcWithCost(a, b, int(costs[a, b]))
    status = assignment.Solve()
    return [assignment.RightMate(a) for a in range(costs.shape[0])]


def prepare_data():
    # # Stipple extinction symbol
    # points = stipple_image_points(f'extinction_symbol.png', n_points=n_points, scale_factor=1, max_iterations=100) * 1.5
    # np.save(f'species/np/_xr', points)

    # # Stipple all the species images
    # for png, name in zip(species_pngs, species_names):
    #     if not os.path.isfile(f'species/np/{name}.npy'):
    #         print(f'Stipple file {png} for species {name}:')
    #         points = stipple_image_points(png, n_points=n_points, scale_factor=1, max_iterations=100)
    #         np.save(f'species/np/{name}', points)

    # Find optimal transport between consecutive point clouds
    names = ['_xr', *species_names, '_xr']
    np.save('species/np/_xr_perm.npy', np.load('species/np/_xr.npy'))
    for n in range(len(names) - 1):
        print('Optimizing', names[n], '-->', names[n+1])
        A = np.load(f'species/np/{names[n]}_perm.npy')
        B = np.load(f'species/np/{names[n+1]}.npy')
        perm = best_permutation(A, B)
        np.save(f'species/np/{names[n+1]}_perm.npy', B[perm])


def render_species(forced_names=[], thumbnail_size=(300,300), update_zip=False):
    from PIL import Image
    import zipfile
    import datetime

    stippled = sorted(glob.glob('species/np/*.npy'))
    species_names = [name.split('\\')[-1].split('.')[0] for name in stippled if not '_' in name]
    if forced_names == 'all':
        forced_names = list(species_names)

    for name in species_names + forced_names:
        if os.path.isfile(f'species/gallery/{name}.png') and (name not in forced_names): continue
        print('Rendering', name)
        forced_names.remove(name)

        surface = gz.Surface(width, height)
        gz.rectangle(xy=(width/2, height/2), lx=width, ly=height, fill=(0,0,0)).draw(surface)

        gz.text(name,
                fontfamily='FUCXED CAPS', fontsize=48,
                fill=(.2,.2,.2,1),
                xy=(width/2, height - 35),
                h_align='center', v_align='top').draw(surface)

        coords = np.load(f'species/np/{name}.npy') * height/1500 - (0, 25)
        for i in range(len(coords)):
            gz.circle(xy=coords[i,:], r=1.5, fill=(1,1,1)).draw(surface)

        surface.write_to_png(f'species/gallery/{name}.png')

        # Generate thumbnail
        im = Image.open(f'species/gallery/{name}.png')
        im.thumbnail(thumbnail_size)
        im.save(f'species/gallery/thumbs/{name}.png')

    if update_zip:
        # Update zip file
        with zipfile.ZipFile(f'species/gallery/endangered_species_{datetime.datetime.now():%Y-%m-%d}.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as f:
            for name in species_names:
                f.write(f'species/gallery/{name}.png', f'{name}.png')


# image_paths = ['species/np/_xr.npy'] + [f'species/np/{name}_perm.npy' for name in species_names] + ['species/np/_xr_perm.npy']
# coords = np.array([np.load(path) for path in image_paths]) * height/1500
# coords = coords - (0, 25)
# coords = np.repeat(coords, [3,] + [2] * (len(coords)-2) + [3,], axis=0)
coords = np.load(f'species/np/{species_names[0]}.npy') * height/1500 - (0, 25)

labels = ['', *species_names, '']

# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    # # Species name
    # label_idx = progress * (len(labels) - .5) - .25
    # for i in range(len(labels)):
    #     if np.abs(label_idx - i) < 1:
    #         shade = np.exp(-(2.5*(label_idx - i))**6)
    #         gz.text(labels[i],
    #                 fontfamily='FUCXED CAPS', fontsize=48,
    #                 fill=(.2,.2,.2,shade),
    #                 xy=(width/2, height - 35),
    #                 h_align='center', v_align='top').draw(surface)

    # # Interpolated stipple points
    # for i in range(len(coords[0])):
    #     point = de_boor(progress * (len(coords) - 3) + 3, coords[:,i,:], degree=3)
    #     gz.circle(xy=point, r=1.5, fill=(1,1,1)).draw(surface)

    gz.text(labels[1],
            fontfamily='FUCXED CAPS', fontsize=48,
            fill=(.2,.2,.2,1),
            xy=(width/2, height - 35),
            h_align='center', v_align='top').draw(surface)

    for i in range(len(coords)):
        gz.circle(xy=coords[i,:], r=1.5, fill=(1,1,1)).draw(surface)

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
    save_poster(name, make_frame, t=0)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
    render_species(species_names, update_zip=True)
