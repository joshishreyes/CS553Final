from pyvis.network import Network
import pandas as pd
import heapq
from collections import defaultdict
import random
import matplotlib.pyplot as plt


# Source: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
class DisjointSet:

  def __init__(self):
    self.forest = set()
    self.parents = {}
    self.sizes = {}

  def make_set(self, x):
    if x not in self.forest:
      self.parents[x] = x
      self.sizes[x] = 1

  def find(self, x):
    if self.parents[x] != x:
      self.parents[x] = self.find(self.parents[x])
      return self.parents[x]
    else:
      return x

  def union(self, x, y):
    x = self.find(x)
    y = self.find(y)
    if x == y:
      return
    if self.sizes[x] < self.sizes[y]:
      temp = x
      x = y
      y = temp
    self.parents[y] = x
    self.sizes[x] = self.sizes[x] + self.sizes[y]


# Source: https://www.sci.utah.edu/~beiwang/publications/PH-GraphDrawing-BeiWang-2019.pdf (Section 4.1)
def kruskals_with_homology(graph):
  forest = []
  mst = DisjointSet()
  barcodes = {}
  for node in graph.get_nodes():
    barcodes[node] = (0, float('inf'))
    mst.make_set(node)
  edges = sorted(graph.get_edges(), key=lambda item: item['value'])
  for edge in edges:
    u = edge['from']
    v = edge['to']
    if mst.find(u) != mst.find(v):
      barcodes[u] = (0, 1 / edge['value'])
      mst.union(u, v)
  return forest, barcodes


def plot_barcodes(barcodes):
  line_segments = []
  counter = 0
  for node, (birth, death) in barcodes.items():
    if death != float('inf'):
      line_segments.append([(birth, counter), (death, counter)])
      counter += 0.1
  for segment in line_segments:
    plt.plot([segment[0][0], segment[1][0]], [segment[0][1], segment[1][1]],
             color='b')
  plt.xlabel('Time')
  plt.ylabel('Node')
  plt.title('PH Barcode')
  plt.show()


net = Network(height="750px",
                  width="100%",
                  bgcolor="#222222",
                  font_color="white")

net.force_atlas_2based(gravity=-100,
                           central_gravity=0.01,
                           spring_length=50,
                           spring_strength=0.5,
                           damping=1,
                           overlap=0)

data = pd.read_csv("book1.csv")

sources = data['Source']
targets = data['Target']
weights = data['weight']

edge_data = zip(sources, targets, weights)

for e in edge_data:
  src = e[0]
  dst = e[1]
  w = e[2]

  net.add_node(src, src, title=src)
  net.add_node(dst, dst, title=dst)
  net.add_edge(src, dst, value=w)

neighbor_map = net.get_adj_list()
for node in net.nodes:
  node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
  node["value"] = len(neighbor_map[node["id"]])

net.show_buttons(filter_=['physics'])
net.write_html("gotbooks.html")

forest, barcodes = kruskals_with_homology(net)
plot_barcodes(barcodes)
