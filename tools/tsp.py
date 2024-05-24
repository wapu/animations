import numpy as np
import subprocess
import fast_tsp
from scipy.spatial.distance import pdist, squareform
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from geometry import *


def solve_tsp_fast(points, duration_seconds=2.0):
    distance_matrix = (squareform(pdist(points)) * 10000).astype(int)
    route = fast_tsp.find_tour(distance_matrix, duration_seconds)
    return route


# See https://developers.google.com/optimization/routing/tsp
def solve_tsp_ortools(points):
    print('Solving TSP using OR-Tools...', end=' ')
    distance_matrix = (squareform(pdist(points)) * 10000).astype(int)

    # Setup for ortools
    manager = pywrapcp.RoutingIndexManager(distance_matrix.shape[1], 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    # More setup
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem and extract route as list of indices
    solution = routing.SolveWithParameters(search_parameters)
    index = routing.Start(0)
    route = [manager.IndexToNode(index)]
    while not routing.IsEnd(index):
        index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))

    print('done.\n')
    return route[:-1]


def write_cyc(route, output_path):
    with open(output_path, 'w') as f:
        f.write(f'{len(route)} {len(route)}\n')
        for i in range(len(route) - 1):
            f.write(f'{route[i]} {route[i+1]}\n')
        f.write(f'{route[-1]} {route[0]}\n')


# Remaining functions are for calling linkern.exe solver under Windows
def write_tsp(output_path, coordinates):
    with open(output_path, 'w') as f:
        f.write('NAME: output\n')
        f.write('TYPE: TSP\n')
        f.write(f'DIMENSION: {len(coordinates)}\n')
        f.write('EDGE_WEIGHT_TYPE: EUC_2D\n')
        f.write('NODE_COORD_SECTION\n')
        for i in range(len(coordinates)):
            f.write('{i} {coordinates[i,1]} {coordinates[i,0]}\n')
        f.write('EOF')


def write_tsp_dist(output_path, distance_matrix):
    with open(output_path, 'w') as f:
        f.write('NAME: output\n')
        f.write('TYPE: TSP\n')
        f.write(f'DIMENSION: {distance_matrix.shape[0]}\n')
        f.write('EDGE_WEIGHT_TYPE: EXPLICIT\n')
        f.write('EDGE_WEIGHT_FORMAT: FULL_MATRIX\n')
        f.write('EDGE_WEIGHT_SECTION\n')
        for i in range(distance_matrix.shape[0]):
            for j in range(distance_matrix.shape[1]):
                f.write(f' {int(distance_matrix[i][j])}')
            f.write('\n')
        f.write('EOF')


def run_linkern(input_path, output_path, linkern_path='linkern.exe'):
    subprocess.call([linkern_path, '-o', output_path, input_path])


def read_cyc(input_path):
    lines = open(input_path, 'r').read().split('\n')
    indices = [int(line.split()[0]) for line in lines[1 : len(lines) - 1]]
    return indices


def postprocess_cyc(input_path, cycle_path, output_path, size, segment_length=4, degree=4, radius=15./16., normalize_points=True):
    points = np.load(input_path)
    cycle = read_cyc(cycle_path)

    if normalize_points:
        height, width = size
        center_and_scale(points, (height/2, width/2), min(height, width)/2 * radius)

    points_ordered = points[cycle]

    points_equal = []
    for i in range(len(points_ordered)):
        p1 = points_ordered[i]
        p2 = points_ordered[(i+1) % len(points_ordered)]

        d = np.sqrt(np.sum(np.square(p1 - p2)))
        subdivisions = int(np.ceil(d / segment_length))

        for j in np.arange(subdivisions)/subdivisions:
            points_equal.append((1-j)*p1 + j*p2)

    final_points = de_boor_np(np.arange(len(points_equal)), np.array(points_equal), degree)

    # final_points = []
    # for i in range(len(cycle)):
    #     p1 = points_ordered[i]
    #     p2 = points_ordered[(i+1) % len(points_ordered)]

    #     d = np.sqrt(np.sum(np.square(p1 - p2)))
    #     subdivisions = int(np.ceil(d / segment_length))

    #     for j in range(subdivisions):
    #         t = i + float(j)/subdivisions
    #         final_points.append(de_boor(t, points_ordered, degree))

    np.save(output_path, np.array(final_points))
