#!/usr/bin/env python
# coding:utf-8
"""
Name   : draw.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/10/5 19:10
"""
import os
import igraph as ig
import matplotlib.pyplot as plt
from process_data import readRoadInfo

class DrawGraph():
    def __init__(self, road_path="../input_data/road_info.xlsx"):
        road_info = readRoadInfo(road_path)
        self.name_to_id = {}
        index = 0
        edges = []
        for item in road_info:
            if self.name_to_id.get(item.origin_node_id, None) == None:
                self.name_to_id[item.origin_node_id] = index
                index += 1
            if self.name_to_id.get(item.terminal_node_id, None) == None:
                self.name_to_id[item.terminal_node_id] = index
                index += 1
            edges.append((self.name_to_id[item.origin_node_id], self.name_to_id[item.terminal_node_id]))
        self.id_to_name = dict(zip(self.name_to_id.values(), self.name_to_id.keys()))
        print(self.name_to_id)
        print(self.id_to_name)
        print(edges)
        print(sorted(self.id_to_name.items(), key=lambda x: x[0]))
        print([v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])])

        # Construct graph
        self.graph = ig.Graph(len(self.name_to_id), edges, directed=True)

    def drawRoad(self):
        bridges = self.graph.bridges()
        self.graph.es["color"] = "black"
        self.graph.es[bridges]["color"] = "red"
        self.graph.es["width"] = 1.0
        self.graph.es[bridges]["width"] = 1.2

        # Plot graph
        fig, ax = plt.subplots(figsize=(5, 5))
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.6,
            vertex_color="lightblue",
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])]
        )
        # plt.show()
        if not os.path.exists("../temp"):
            os.mkdir("../temp")

        fig.savefig("../temp/base_road_graph.png", bbox_inches='tight', pad_inches=-0.1)


if __name__ == "__main__":
    dg = DrawGraph()
    dg.drawRoad()
