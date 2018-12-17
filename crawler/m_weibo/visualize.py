import csv
import math
import networkx as nx
from pyecharts import Graph

def read_network(csv_file):
    network = nx.Graph()
    with open(csv_file, 'r') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            source, target = row
            network.add_edge(source, target)
    dc = nx.centrality.degree_centrality(network)
    n = len(dc)
    dc = {k:v*(n-1) for k, v in dc.items()}
    return dc

def gen_graph(csv_file):
    dc = read_network(csv_file)
    max_degree = max(dc.values())
    nodes = [node for node in dc.keys() if dc[node] != 1]
    links = []
    with open(csv_file, 'r') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            source, target = row
            if source not in nodes or target not in nodes:
                continue
            else:
                link = {'source': source, 'target': target}
                links.append(link)
    nodes = [{'name': node, 'symbolSize': math.log10(dc[node]) / math.log10(max_degree) * 20, 'value': dc[node]} for node in nodes]

    graph = Graph(
        title='微博传播网络图',
        width=1080,
        height=800
    )

    graph.add(
        '',
        nodes,
        links,
        is_label_show=True,
        line_curve=0.2
    )
    graph.render()

if __name__ == '__main__':
    gen_graph('test.csv')
