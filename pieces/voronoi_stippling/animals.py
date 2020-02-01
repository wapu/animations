import numpy as np
from ortools.graph import pywrapgraph

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from stippling import *



name = 'animals'
width, height = 768, 768
duration = 15


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
    # Stipple all the animal images
    animals = ['eagle', 'grizzly', 'lion', 'owl', 'shark', 'spider', 'tiger', 'wolf', 'snake']
    for animal in animals:
        points = stipple_image_points(f'animals/{animal}.png', n_points=4900, scale_factor=2, max_iterations=150)
        np.save(f'animals/{animal}', points)

    # Create neutral grid pattern as starting point
    grid = np.mgrid[-35:35, -35:35].transpose(1,2,0).reshape(-1,2).astype(np.float32)
    grid *= 90 * (3000/256) / (35 * np.sqrt(2))
    rotate_around(grid, pi/4, np.array([0,0]))
    grid = grid + (1500, 1500)
    np.save('animals/grid.npy', grid)

    # Find optimal transport between consecutive point clouds
    names = ['grid', 'eagle', 'grizzly', 'lion', 'owl', 'shark', 'spider', 'tiger', 'wolf', 'snake', 'grid']
    np.save('animals/grid_perm.npy', np.load('animals/grid.npy'))
    for n in range(len(names) - 1):
        print('Optimizing', names[n], '-->', names[n+1])
        A = np.load(f'animals/{names[n]}_perm.npy')
        B = np.load(f'animals/{names[n+1]}.npy')
        perm = best_permutation(A, B)
        np.save(f'animals/{names[n+1]}_perm.npy', B[perm])


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    image_paths = [f'animals/{name}.npy' for name in
                    ['grid', 'lion_perm', 'tiger_perm', 'grizzly_perm',
                     'wolf_perm', 'shark_perm', 'snake_perm', 'spider_perm',
                     'owl_perm', 'eagle_perm', 'grid_perm']]
    coords = np.array([np.load(path) for path in image_paths]) * width / 3000

    progress = t / duration
    coords = np.repeat(coords, [3,] + [2] * (len(coords)-2) + [3,], axis=0)

    for i in range(len(coords[0])):
        point = de_boor(progress * (len(coords) - 3.4) + 3, coords[:,i,:], degree=3)
        gz.circle(xy=point, r=1.5, fill=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
