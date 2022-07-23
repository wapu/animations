import numpy as np
from ortools.graph import pywrapgraph

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from stippling import *



name = 'skull_and_brain'
width, height = 768, 768
duration = 4


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
    # Stipple images
    skull = stipple_image_points(f'skull_and_brain/skull.png', n_points=5000, scale_factor=2, max_iterations=100)
    np.save(f'skull_and_brain/skull', skull)
    brain = stipple_image_points(f'skull_and_brain/brain.png', n_points=5000, scale_factor=2, max_iterations=100)
    np.save(f'skull_and_brain/brain', brain)

    # Optimal transport
    skull = np.load('skull_and_brain/skull.npy')
    brain = np.load('skull_and_brain/brain.npy')
    perm = best_permutation(skull, brain)
    np.save('skull_and_brain/brain', brain[perm])


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    skull = np.load('skull_and_brain/skull.npy') * width / 3000
    brain = np.load('skull_and_brain/brain.npy') * width / 3000

    progress = t / duration
    p = interval_progresses(progress, 2, 'hermite')

    for i in range(len(skull)):
        point = (1 - p[0] + p[1]) * skull[i] + (p[0] - p[1]) * brain[i]
        gz.circle(xy=point, r=1.5, fill=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
