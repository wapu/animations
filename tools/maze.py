
from random import randint
import sys

from Graph import *


# states
UNASSIGNED	= 0
ASSIGNED	= 1
TMP			= 2
BLOCKED		= 3


def rand_perm(n):
	p = range(n)
	for i in range(n):
		j = randint(0, i)
		p[i] = p[j]
		p[j] = i
	return p


def add_path(G, node, path=None):
	if path is None: path = []

	# check whether we can go here
	if node.data['state'] == ASSIGNED:	return True, path
	if node.data['state'] == BLOCKED:	return False, path
	if node.data['state'] == TMP:		return False, path

	# mark node as visited
	node.data['state'] = TMP

	# try going to each neighbour
	for i in rand_perm(len(node.neighbours)):
		neighbour, edge = node.neighbours[i]
		success, _ = add_path(G, G.V[neighbour], path=path)
		if success:
			# mark node as done and add edge to path
			node.data['state'] = ASSIGNED
			path.append(G.E[edge])
			return success, path

	# nowhere to go --> fail
	return False, path


def generate_maze(G, start_index, end_index, mask=None):
	# allow deeper recursion based on number of vertices
	sys.setrecursionlimit(len(G.V)^2)

	# init all nodes
	G.update_data_all({'state': UNASSIGNED})

	G.V[start_index].data['state'] = ASSIGNED

	success, path = add_path(G, G.V[end_index])

	for i in rand_perm(len(G.V)):
		success, p = add_path(G, G.V[i])
		if success:
			path.extend(p)

	maze = Graph(G.V, path)
	return maze


# G = make_grid_graph(10, 15)
# maze = generate_maze(G, 0, 8)

# G = make_grid_graph(3, 3)
# for v in G.V:
# 	print v.data
