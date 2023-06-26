# Code reused from Yawei Liu
# https://yaweiliu.github.io/research_notes/notes/20210301_Creating%20an%20icosphere%20with%20Python.html


import numpy as np



def vertex(x, y, z): 
    """ Return vertex coordinates fixed to the unit sphere """ 
    length = np.sqrt(x**2 + y**2 + z**2) 
    return [i / length for i in (x,y,z)] 


def middle_point(verts,middle_point_cache,point_1, point_2): 
    """ Find a middle point and project to the unit sphere """ 
    # We check if we have already cut this edge first 
    # to avoid duplicated verts 
    smaller_index = min(point_1, point_2) 
    greater_index = max(point_1, point_2) 
    key = '{0}-{1}'.format(smaller_index, greater_index) 
    if key in middle_point_cache: return middle_point_cache[key] 
    # If it's not in cache, then we can cut it 
    vert_1 = verts[point_1] 
    vert_2 = verts[point_2] 
    middle = [sum(i)/2 for i in zip(vert_1, vert_2)] 
    verts.append(vertex(*middle)) 
    index = len(verts) - 1 
    middle_point_cache[key] = index 
    return index


def icosphere(subdiv, return_faces=False):
    # verts for icosahedron
    r = (1.0 + np.sqrt(5.0)) / 2.0;
    verts = np.array([[-1.0, r, 0.0],[ 1.0, r, 0.0],[-1.0, -r, 0.0],
                      [1.0, -r, 0.0],[0.0, -1.0, r],[0.0, 1.0, r],
                      [0.0, -1.0, -r],[0.0, 1.0, -r],[r, 0.0, -1.0],
                      [r, 0.0, 1.0],[ -r, 0.0, -1.0],[-r, 0.0, 1.0]]);
    # rescale the size to radius of 0.5
    verts /= np.linalg.norm(verts[0])
    verts = list(verts)

    faces = [[0, 11, 5],[0, 5, 1],[0, 1, 7],[0, 7, 10],
             [0, 10, 11],[1, 5, 9],[5, 11, 4],[11, 10, 2],
             [10, 7, 6],[7, 1, 8],[3, 9, 4],[3, 4, 2],
             [3, 2, 6],[3, 6, 8],[3, 8, 9],[5, 4, 9],
             [2, 4, 11],[6, 2, 10],[8, 6, 7],[9, 8, 1],];

    for i in range(subdiv):
        middle_point_cache = {}
        faces_subdiv = []
        for tri in faces: 
            v1  = middle_point(verts,middle_point_cache,tri[0], tri[1])
            v2  = middle_point(verts,middle_point_cache,tri[1], tri[2])
            v3  = middle_point(verts,middle_point_cache,tri[2], tri[0])
            faces_subdiv.append([tri[0], v1, v3]) 
            faces_subdiv.append([tri[1], v2, v1]) 
            faces_subdiv.append([tri[2], v3, v2]) 
            faces_subdiv.append([v1, v2, v3]) 
        faces = faces_subdiv

    if return_faces:
        return np.array(verts), np.array(faces)
    else:
        return np.array(verts)



# own code from here

class Node():
    def __init__(self, pos, neighbors=[], edges=[]):
        self.pos = pos
        self.neighbors = neighbors
        self.edges = edges

class Edge():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

def split_node(node):
    splits = []
    for e in node.edges:
        split = Node(Node.pos)
        split.neighbors = list(splits)
        split.edges = [Edge(split, n) for n in split.neighbors]
        split.edges.append(e)
        splits.append(split)


def adjacency_from_faces(size, faces):
    A = np.zeros((size, size), dtype=int)
    for (i1, i2, i3) in faces:
        A[i1, i2] = 1
        A[i2, i1] = 1
        A[i1, i3] = 1
        A[i3, i1] = 1
        A[i2, i3] = 1
        A[i3, i2] = 1
    return A

def index_edges_from_A(A):
    index_edges = []
    for i in range(A.shape[0]):
        for j in range(i):
            if A[i,j] == 1:
                index_edges.append((i,j))
    return index_edges

def icosphere_graph(verts, faces):
    nodes = [Node(v) for v in verts]
    A = adjacency_from_faces(len(nodes), faces)
    index_edges = index_edges_from_A(A)

    edges = []
    for (i,j) in index_edges:
        e = Edge(nodes[i], nodes[j])
        edges.append(e)
        nodes[i].neighbors.append(nodes[j])
        nodes[j].neighbors.append(nodes[i])
        nodes[i].edges.append(e)
        nodes[j].edges.append(e)

    return nodes, edges


# n, e = icosphere_graph(*icosphere(0, return_faces=True))
# print(len(n), len(e))