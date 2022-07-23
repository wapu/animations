
import numpy as np
import subprocess

from geometry import *


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

	points2 = np.zeros(points.shape)
	for i in range(len(points)):
		points2[i,:] = points[cycle[i],:]

	final_points = []
	for i in range(len(cycle)):
		p1 = points[cycle[i],:]
		p2 = points[cycle[(i+1) % len(cycle)],:]

		d = np.sqrt(np.sum(np.square(p1 - p2)))
		subdivisions = int(np.ceil(d / segment_length))

		for j in range(subdivisions):
			t = i + float(j)/subdivisions
			final_points.append(de_boor(t, points2, degree))

	np.save(output_path, np.array(final_points))