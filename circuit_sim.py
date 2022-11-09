from collections import defaultdict
from itertools import product
from typing import Tuple
from functools import reduce
import pandas as pd
import numpy as np

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


# parses a benchfile into a Python dictionary and list of input wires
def createDict(filename: str) -> Tuple[dict, list]:
   benchfile = open(filename)
   # parsing benchfile into dictionary
   # {key : value} = {output_wire : [gate, input1, input2, ... , inputN]}
   bench = benchfile.read().splitlines()
   bench = [line for line in bench if '#' not in line and '' != line]
   inputs = [line for line in bench if 'INPUT' in line]
   circuit = [line for line in bench if (line not in inputs) and 'OUTPUT' not in line]

   gateOut = [line.split(' = ')[0] for line in circuit]
   gate = [line.split(' = ')[1] for line in circuit]
   gate = [[line.split('(')[0]] + line.split('(')[1].replace(')', '').split(', ') for line in gate]
   
   inputs = [line.split('(')[1].replace(')', '') for line in inputs]
   circ = {gateOut[i]: line for i, line in enumerate(gate)}

   return circ, inputs



def createGraphFromDict(circ: dict) -> Graph:
    graph = Graph()

    for gateOut, gate in circ.items():
        for i, component in enumerate(gate):
            if i == 0:
                continue
            graph.addEdge(gateOut, component)
    return graph


# simulates an input combination given a circuit dictionary and list of input wires  
def sim(input_comb: list, circ: dict, inputs: list) -> dict:
   netlist = {i: -1 for i in (inputs + list(circ.keys()))}
   for i, val in enumerate(input_comb):
      netlist[inputs[i]] = val

   for wire in netlist:
      if netlist[wire] == -1:
         visited = set()
         netlist[wire] = simDFS(circ, wire, netlist, visited)
   return netlist # outputs a truth table line with all input, net, and output wires
   

# recursive function for finding the value of each wire 
def simDFS(circ: dict, wire: str, netlist: dict, visited: set) -> int: # circ, wire: G4, netlist: {G1: 0, G2: 1, G3: 0, G4: -1, G5: -1}
   if netlist[wire] != -1:
      return netlist[wire]
   else:
      gate = circ[wire][0]
      wire_in = circ[wire][1:]
      val_in = []
      for wire in wire_in:
         val_in.append(simDFS(circ, wire, netlist, visited))
      return gateSim(gate, val_in)



def gateSim(gate: str, inputs: list) -> int: # gate: 'OR', inputList: [1, 0]
   if gate == 'NOT':
      return 1 - inputs[0]
   elif gate == 'DFF':
      return inputs[0]
   elif gate == 'AND':
      return 0 + all(inputs)
   elif gate == 'NAND':
      return 1 - all(inputs)
   elif gate == 'OR':
      return 0 + any(inputs)
   elif gate == 'NOR':
      return 1 - any(inputs)
   elif gate == 'XOR':
      return inputs.count(1) % 2
   elif gate == 'XNOR':
      return (inputs.count(1) + 1) % 2
   else:
      raise Exception("ERROR: GATE TYPE " + gate + " NOT SUPPORTED")



def getControl(benchfile: str) -> pd.DataFrame:
   circ, wire_in = createDict(benchfile)
   #  df = pd.read_table(testfile, delimiter='\t')

   # generate truth table
   tt_inputs = list(product([0, 1], repeat=len(wire_in)))

   tt = {index: [-1] for index in (wire_in + list(circ.keys()))}

   for line in tt_inputs:
      netlist = sim(line, circ, wire_in)
      for key, val in tt.items():
         val.append(netlist[key])

   df = pd.DataFrame(tt).drop(0).reset_index(drop=True)

   # # sorting truth table
   # wire_in.reverse()
   # for i in wire_in:
   #    df = df.sort_values(by=i)
   # wire_in.reverse()
   # print(df)
   df.to_csv("truthtable.csv", index=False)


   # getting control values
   control_df = pd.DataFrame(np.zeros((len(circ), len(wire_in))), index=circ.keys(), columns=wire_in)
   control = 0

   for input in wire_in:
      df = df.sort_values(by=input).reset_index(drop=True)
      for key in circ:
         # print("control value of " + input + " on wire " + key + ":", end=' ')
         for index in range(len(df) // 2):
            control += df.loc[index, key] ^ df.loc[(index + len(df) // 2), key]
         # print(control)
         control_df.loc[key, input] = control / (2 ** len(input))
         control = 0

   # count = 0
   # for val in wire_in:
   #    count += 1
   #    for key in circ:
   #       for index in range(len(df) // 2):
   #          control += df.loc[index, key] ^ df.loc[(index + (2 ** count))]
   
   return control_df
   







if __name__ == "__main__":
   control_df = getControl('s298.bench')

   control_df.to_csv("output.csv")


   # vals = [[i+4*j for i in range(4)] for j in range(3)]
   # print(vals)
   # print(vals[2][3])


   

