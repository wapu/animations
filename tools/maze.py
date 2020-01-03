import numpy as np


# states
WALL      = 0
PATH      = 1
TMP_PATH  = 2
RESERVED  = 3


def make_path_from(y, x, L):
    if L[y,x] in (PATH, RESERVED): return None

    h,w = L.shape
    new_path = []
    frontier = [(y,x,y,x)]

    while len(frontier) > 0:
        y_, x_, y, x = frontier.pop()

        if L[y,x] == TMP_PATH: continue
        L[y_,x_] = TMP_PATH
        new_path.append((y_,x_))

        if L[y,x] == PATH: return new_path
        L[y,x] = TMP_PATH
        new_path.append((y,x))

        for d in np.random.permutation(4):
            if d == 0: # up
                if y > 1   and L[y-2,x] not in (TMP_PATH, RESERVED):
                    frontier.append((y-1, x, y-2, x))
            if d == 1: # left
                if x > 1   and L[y,x-2] not in (TMP_PATH, RESERVED):
                    frontier.append((y, x-1, y, x-2))
            if d == 2: # down
                if y < h-2 and L[y+2,x] not in (TMP_PATH, RESERVED):
                    frontier.append((y+1, x, y+2, x))
            if d == 3: # right
                if x < w-2 and L[y,x+2] not in (TMP_PATH, RESERVED):
                    frontier.append((y, x+1, y, x+2))

    return None


def generate_labyrinth(w, h, mask = None):
    assert (h,w) == mask.shape
    L = np.full((2*h-1, 2*w-1), WALL)

    for y in range(h):
        for x in range(w):
            if mask[y,x] == 0:
                L[2*y, 2*x] = RESERVED

    L[2 * (h//2), 2 * (w//2)] = PATH

    # connect all points with odd x and y to the path in a random order
    for i in np.random.permutation(w * h):
        x = 2 * (i % w)
        y = 2 * (i // w)
        new_path = make_path_from(y, x, L)
        if new_path is not None:
            for (y,x) in new_path:
                L[y,x] = PATH

    for y in range(L.shape[0]):
        for x in range(L.shape[1]):
            if L[y,x] == RESERVED: L[y,x] = WALL

    return L


def labyrinth_to_canvas(y, x, L, width, height):
    return ((x - L.shape[1]/2) * 5 + width/2 + 2.5, (y - L.shape[0]/2) * 5 + height/2 + 2.5)









# def rand_perm(n):
# 	p = range(n)
# 	for i in range(n):
# 		j = randint(0, i)
# 		p[i] = p[j]
# 		p[j] = i
# 	return p


# def add_path(G, node, path=None):
# 	if path is None: path = []

# 	# check whether we can go here
# 	if node.data['state'] == ASSIGNED:	return True, path
# 	if node.data['state'] == BLOCKED:	return False, path
# 	if node.data['state'] == TMP:		return False, path

# 	# mark node as visited
# 	node.data['state'] = TMP

# 	# try going to each neighbour
# 	for i in rand_perm(len(node.neighbours)):
# 		neighbour, edge = node.neighbours[i]
# 		success, _ = add_path(G, G.V[neighbour], path=path)
# 		if success:
# 			# mark node as done and add edge to path
# 			node.data['state'] = ASSIGNED
# 			path.append(G.E[edge])
# 			return success, path

# 	# nowhere to go --> fail
# 	return False, path


# def generate_maze(G, start_index, end_index, mask=None):
# 	# allow deeper recursion based on number of vertices
# 	sys.setrecursionlimit(len(G.V)^2)

# 	# init all nodes
# 	G.update_data_all({'state': UNASSIGNED})

# 	G.V[start_index].data['state'] = ASSIGNED

# 	success, path = add_path(G, G.V[end_index])

# 	for i in rand_perm(len(G.V)):
# 		success, p = add_path(G, G.V[i])
# 		if success:
# 			path.extend(p)

# 	maze = Graph(G.V, path)
# 	return maze


# G = make_grid_graph(10, 15)
# maze = generate_maze(G, 0, 8)

# G = make_grid_graph(3, 3)
# for v in G.V:
# 	print v.data
