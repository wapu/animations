

class Graph:

	def __init__(self, V=[], E=[]):
		self.V = []
		self.V.extend(V)
		for v in self.V:
			v.neighbours = []
			v.graph = self
		self.E = []
		for e in E:
			self.add_edge(e)

	def add_node(self, neighbour_indices, data):
		node = Node(data)
		node.graph = self
		self.V.append(node)
		for i in neighbour_indices:
			self.E.append((len(self.V) - 1, i))
			node.neighbours.append((i, len(self.E) - 1))

	def remove_node(self, index):
		node = self.V.pop(index)
		for neighbour in node.neighbours:
			neighbour.neighbours = [(v,e) for (v,e) in neighbour.neighbours if v != index]
		edges = sorted([e for (v,e) in node.neighbours], reverse=True)
		for i in edges:
			del self.E[i]


	def add_edge(self, (index1, index2)):
		self.E.append((index1, index2))
		self.V[index1].neighbours.append((index2, len(self.E)))
		self.V[index2].neighbours.append((index1, len(self.E)))

	def remove_edge(self, index):
		v1, v2 = self.E.pop(index)
		v1.neighbours = [(v,e) for (v,e) in v1.neighbours if v != v2]
		v2.neighbours = [(v,e) for (v,e) in v2.neighbours if v != v1]

	def update_data_all(self, data):
		for v in self.V:
			v.data.update(data)


class Node:

	def __init__(self, data=None):
		self.data = {}
		if data != None: self.data.update(data)
		self.neighbours = []
		self.graph = None


def make_grid_graph(rows, cols, top=0, bottom=1, left=0, right=1):
	G = Graph()
	indices = [[(i * cols + j) for j in range(cols)] for i in range(rows)]

	for i in range(rows):
		for j in range(cols):
			neighbours = []
			if j > 0: neighbours.append(indices[i][j-1])
			if i > 0: neighbours.append(indices[i-1][j])
			data = {'y': top + float(i)/(rows-1) * (bottom - top), 'x': left + float(j)/(cols-1) * (right - left)}
			G.add_node(neighbours, data)

	return G

