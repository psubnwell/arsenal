import csv
import networkx as nx
from pyecharts import Bar

def read_network(csv_file):
    network = nx.Graph()
    with open(csv_file, 'r') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            source, target = row
            network.add_edge(source, target)
    return network

def hierarchical_analyze(network, source_node):
    max_repost_distance = nx.eccentricity(network, source_node)
    length = nx.single_source_shortest_path_length(network, source_node)
    hier = {}
    for i in range(1, max_repost_distance + 1):
        hier[i] = len([k for k, v in length.items() if v == i])
    return hier

def plot(data):
    bar = Bar('层级转发量统计')
    bar.add('', list(data.keys()), list(data.values()))
    bar.render()



if __name__ == '__main__':
    network = read_network('./test.csv')
    hier = hierarchical_analyze(network, '@法制日报')
    plot(hier)
