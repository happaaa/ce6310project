from collections import defaultdict
import re
import pandas as pd

# This class represents a directed graph using
# adjacency list representation
class Graph:

	# Constructor
	def __init__(self):
		# default dictionary to store graph
		self.graph = defaultdict(list)

	def addEdge(self, u, v):
		self.graph[u].append(v)

	# A function used by DFS
	def DFSUtil(self, v, visited):
		visited.add(v)
		print(v, end=' ')
		# Recur for all the vertices
		# adjacent to this vertex
		for neighbour in self.graph[v]:
			if neighbour not in visited:
				self.DFSUtil(neighbour, visited)

	def DFS(self, v):

		# Create a set to store visited vertices
		visited = set()
		self.DFSUtil(v, visited)





# def createGraph(filename):
#     benchfile = open(filename)
#     bench = benchfile.read().splitlines()
#     bench = [line for line in bench if '#' not in line and '' is not line]
#     inputs = [line for line in bench if 'INPUT' in line]
#     outputs = [line for line in bench if 'OUTPUT' in line]
#     circuit = [line for line in bench if (line not in inputs) and (line not in outputs)]


#     # inputs = [re.findall(r'G\d+', line)  for line in inputs]
#     inputs = [line.split('(')[1].replace(')', '') for line in inputs]
#     # outputs = [re.findall(r'G\d+', line)  for line in outputs]
#     circuit = [re.findall(r'G\d+', line) for line in circuit]

#     graph = Graph()
#     for gate in circuit:
#         for i, wire in enumerate(gate):
#             if i == 0:
#                 continue
#             graph.addEdge(gate[0], wire)
#     return graph, inputs


def createDict(filename):
    benchfile = open(filename)
    bench = benchfile.read().splitlines()
    bench = [line for line in bench if '#' not in line and '' != line]
    inputs = [line for line in bench if 'INPUT' in line]
    # outputs = [line for line in bench if 'OUTPUT' in line]
    circuit = [line for line in bench if (line not in inputs) and 'OUTPUT' not in line]

    gateOut = [line.split(' = ')[0] for line in circuit]
    gate = [line.split(' = ')[1] for line in circuit]
    gate = [[line.split('(')[0]] + line.split('(')[1].replace(')', '').split(', ') for line in gate]

    inputs = [line.split('(')[1].replace(')','') for line in inputs]
    circDict = {gateOut[i]: line for i, line in enumerate(gate)}

    return circDict, inputs



def createGraphFromDict(circDict):
    graph = Graph()

    for gateOut, gate in circDict.items():
        for i, component in enumerate(gate):
            if i == 0:
                continue
            graph.addEdge(gateOut, component)
    return graph



def getFanIn(graph, inputs, gate):

    path = graph.DFS(gate)


    return


def getControl(benchfile, testfile):
    circ, wire_in = createDict(benchfile)
    df = pd.read_table(testfile, delimiter='\t')

    wire_in.reverse()
    for i in wire_in:
        df = df.sort_values(by=i)
    wire_in.reverse()

    control  = 0
    for input in wire_in:
        df = df.sort_values(by=input)
        df = df.reset_index(drop=True)
        for key in circ:
            print("control value of " + input + " on wire " + key + ":", end=' ')
            for index in range(len(df) // 2):
                control += df.loc[index, key] ^ df.loc[(index + len(df) // 2), key]
            print(control)
            control = 0
                



if __name__ == "__main__":

    # circ,i = createDict("adder.txt")
    # graph = createGraphFromDict(circ)
    # graph.DFS('G9')
    # circ.DFS('G9')
    # for line in circ:
    #     print(line)
    # print(circ)
    # print(i)

    getControl('adder.txt', 'adder_benchtest.txt')

    # string = "THIS IS A STRING"
    
    # print (string.split("T")[2])






    

