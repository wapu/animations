
import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
from scipy.ndimage import zoom
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.ndimage.filters import gaussian_filter
from math import pi, ceil, sqrt


def rejection_sampling(density, n_samples):
	h, w = density.shape[:2]
	density = density * (1. / np.max(density))

	samples = []
	while len(samples) < n_samples:
		y, x, s = np.random.rand(), np.random.rand(), np.random.rand()
		if s <= density[int(y*h), int(x*w)]:
			samples.append((y,x))

	return samples


# Taken from https://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping
def clip(subject_polygon, clip_polygon):
	def point_inside_clip_edge(point, edge_point_1, edge_point_2):
		return(edge_point_2[0] - edge_point_1[0]) * (point[1] - edge_point_1[1]) > (edge_point_2[1] - edge_point_1[1]) * (point[0] - edge_point_1[0])

	def compute_intersection():
		dc = [ edge_point_1[0] - edge_point_2[0], edge_point_1[1] - edge_point_2[1] ]
		dp = [ s[0] - e[0], s[1] - e[1] ]
		n1 = edge_point_1[0] * edge_point_2[1] - edge_point_1[1] * edge_point_2[0]
		n2 = s[0] * e[1] - s[1] * e[0] 
		n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
		return [(n1*dp[0] - n2*dc[0]) * n3, (n1*dp[1] - n2*dc[1]) * n3]

	output_list = subject_polygon

	edge_point_1 = clip_polygon[-1]
	for clip_vertex in clip_polygon:

		edge_point_2 = clip_vertex
		input_list = output_list
		output_list = []

		s = input_list[-1]
		for subject_vertex in input_list:

			e = subject_vertex
			if point_inside_clip_edge(e, edge_point_1, edge_point_2):
				if not point_inside_clip_edge(s, edge_point_1, edge_point_2):
					output_list.append(compute_intersection())
				output_list.append(e)
			elif point_inside_clip_edge(s, edge_point_1, edge_point_2):
				output_list.append(compute_intersection())
			s = e

		edge_point_1 = edge_point_2

	return output_list


def find_centroid(P, Q, region, p, attractor=None, repulsor=None):
	X, Y = 0, 0
	denominator = 0
	area = 0

	if (attractor is None) and (repulsor is None):
		attractor = np.array(P.shape) * 0.5
	step_size = P.shape[0] * 0.002

	n_points = len(region)
	min_y = min([point[0] for point in region])
	max_y = max([point[0] for point in region])

	# Get all edges and sort them by maximum y coordinate
	edges = []
	for i in range(n_points):
		p1, p2 = region[i], region[(i+1) % n_points]
		if   p1[0] < p2[0]: edges.append((p1, p2))
		elif p1[0] > p2[0]: edges.append((p2, p1))
	edges.sort(key=lambda edge: (edge[0][0], edge[1][0]))

	# Sweep line
	active_edges = []
	next_edge_index = 0
	for y in range(int(min_y), int(max_y) + 1):

		# Add newly crossed edges
		while True:
			if next_edge_index >= len(edges): break
			edge = edges[next_edge_index]
			if y >= edge[0][0]:
				active_edges.append(edge)
				next_edge_index += 1
			else: break

		# Remove no longer crossed edges
		pop_indices = []
		for i in range(len(active_edges)):
			if active_edges[i][1][0] <= y:
				pop_indices.append(i)
		for i in pop_indices[::-1]:
			active_edges.pop(i)

		if (len(active_edges) % 2) != 0:
			print(y)
			print(pop_indices)
			for edge in active_edges:
				print(edge)

		# Get x coordinates
		x_coordinates = []
		for edge in active_edges:
			ratio = (y - edge[0][0]) / (edge[1][0] - edge[0][0])
			x = edge[0][1] + ratio * (edge[1][1] - edge[0][1])
			x_coordinates.append(x)
		assert 0 == (len(x_coordinates) % 2), 'line sweep error at y=%d: got %d edge intersections (even number expected)' % (y, len(x_coordinates))

		# Integrate
		x_coordinates.sort()
		for i in range(int(len(x_coordinates) // 2)):
			x1, x2 = x_coordinates[2*i], x_coordinates[2*i + 1]
			x1_, x2_ = int(round(x1)), int(round(x2))

			denominator += P[y, x2_] - P[y, x1_]
			Y += y * (P[y, x2_] - P[y, x1_])
			X += (x2_ * P[y, x2_] - Q[y, x2_]) - (x1_ * P[y, x1_] - Q[y, x1_])
			area += (x2 - x1)

	if denominator >= 0.01:
		centroid = (Y / denominator, X / denominator + 0.5)
	else:
		# TODO: FIND BETTER HEURISTIC!
		# Dumb heuristic when not enough probability mass to work with:
		# 	  Take a small step towards image center, things should become clearer there
		if repulsor is not None:
			direction = p - repulsor
			direction_norm = sqrt(direction[0]*direction[0] + direction[1]*direction[1])
			centroid = p + direction * (step_size / direction_norm)
		else:
			direction = attractor - p
			direction_norm = sqrt(direction[0]*direction[0] + direction[1]*direction[1])
			centroid = p + direction * (step_size / direction_norm)

	return centroid, area


def precompute_integrands(density):
	print('Precomputing integrands...')
	P, Q = np.zeros(density.shape), np.zeros(density.shape)
	for i in range(P.shape[0]):
		for j in range(P.shape[1]):
			P[i,j] = P[i,j-1] + density[i,j]
			Q[i,j] = Q[i,j-1] + P[i,j]
	return P, Q


def find_center_of_weight(P, Q):
	denominator, Y, X = 0, 0, 0
	for y in range(P.shape[0]):
		denominator += P[y, -1] - P[y, 0]
		Y += y * (P[y, -1] - P[y, 0])
		X += (P.shape[1] - 1) * P[y, -1] - Q[y, -1]
	mid = (Y / denominator, X / denominator + 0.5)
	return mid


def get_initial_points(density, n_points=100, init=None):
	if init is None:
		samples = rejection_sampling(density, n_points)
	else:
		samples = [(init[i,0] / density.shape[0], init[i,1] / density.shape[1]) for i in range(init.shape[0])]
	# Additional outside points to get finite Voronoi regions inside the image
	samples.extend([(-1., -1.), (-1., 2.), (2., -1.), (2., 2.)])
	points = np.array(samples) * density.shape
	return points


def lloyds_method(points, P, Q, clip_polygon, max_iterations, attractors=None, repulsor=None, verbose=True):
	if verbose:
		print('Generating centroidal voronoi diagram...')
	it, max_d, std_prev, std_diff = 0, P.shape[0], 1, 1
	# while std_diff > 5e-8 and max_d > (P.shape[0] * 1e-3) and it < max_iterations:
	while it < max_iterations and max_d > 0.05:
		it += 1
		v = Voronoi(points)

		# Push points to centroids of voronoi regions
		max_d = 0
		# Areas = []
		for i in range(len(points) - 4):
			# Prepare region polygon
			region = v.regions[v.point_region[i]]
			region = [(v.vertices[region[j]][0], v.vertices[region[j]][1]) for j in range(len(region))]
			region = clip(region, clip_polygon)

			# Find centroid
			if attractors is None:
				centroid, area = find_centroid(P, Q, region, points[i,:])
			else:
				centroid, area = find_centroid(P, Q, region, points[i,:], attractor=attractors[i,:], repulsor=repulsor)
			max_d = max(max_d, sqrt((points[i,0] - centroid[0])**2 + (points[i,0] - centroid[0])**2))
			# areas.append(area / (P.shape[0] * P.shape[1]))
			points[i,:] = centroid

		# std = np.std(areas)
		# std_diff = abs(std_prev - std)
		# std_prev = std
		if verbose:
			print(f'Iteration {it: 4}: maximum centroid shift = {round(max_d, 2)}')


# Following http://mrl.nyu.edu/~ajsecord/npar2002/npar2002_ajsecord_preprint.pdf
def stipple_image_points(input_image_path, n_points=5000, max_iterations=50, init=None, scale_factor=1, invert=False, attractors=None, repulsor=None):
	print('GENERATING STIPPLE IMAGE')

	# Read density from image file
	density = imread(input_image_path, mode='F') / 255
	if invert:
		density = 1 - density
	if scale_factor != 1:
		density = zoom(density, zoom=scale_factor, order=2, mode='mirror')

	# Precompute stuff
	P, Q = precompute_integrands(density)
	mid = find_center_of_weight(P, Q)
	clip_polygon = ((0, 0), (P.shape[0] - 1, 0), (P.shape[0] - 1, P.shape[1] - 1), (0, P.shape[1] - 1))
	points = get_initial_points(density, n_points=n_points, init=init)

	# # Get attractors
	# print 'placing attractors...'
	# points_sparse = get_initial_points(density, n_points=100)
	# lloyds_method(points_sparse, P, Q, clip_polygon, 50, verbose=False)

	# attractors = np.zeros((len(points) - 4, 2))
	# for i in range(len(points) - 4):
	# 	d_min = 2*P.shape[0]*P.shape[0]
	# 	for j in range(len(points_sparse) - 4):
	# 		d = np.sum(np.square(points[i,:] - points_sparse[j,:]))
	# 		if d < d_min:
	# 			d_min = d
	# 			attractors[i,:] = points_sparse[j,:]

	# Distribute points
	lloyds_method(points, P, Q, clip_polygon, max_iterations, attractors=attractors, repulsor=repulsor)

	# # Show Voronoi plot
	# voronoi_plot_2d(v)
	# plt.show()

	return points[:-4, ::-1]