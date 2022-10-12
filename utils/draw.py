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
from utils.process import readRoadInfo

class DrawGraph():
    def __init__(self, base_path, road_path="../input_data/road_info.xlsx"):
        self.base_path = base_path
        road_info = readRoadInfo(road_path)
        self.name_to_id = {}
        index = 0
        self.edges = []
        edge_id = 1
        for item in road_info:
            if self.name_to_id.get(item.origin_node_id, None) == None:
                self.name_to_id[item.origin_node_id] = index
                index += 1
            if self.name_to_id.get(item.terminal_node_id, None) == None:
                self.name_to_id[item.terminal_node_id] = index
                index += 1
            self.edges.append((edge_id, self.name_to_id[item.origin_node_id], self.name_to_id[item.terminal_node_id]))
            edge_id += 1
        self.id_to_name = dict(zip(self.name_to_id.values(), self.name_to_id.keys()))
        print("name_to_id:", self.name_to_id)
        print("id_to_name", self.id_to_name)
        print("edges:", self.edges)
        # print(sorted(self.id_to_name.items(), key=lambda x: x[0]))
        # print([v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])])

        # Construct graph
        self.graph = ig.Graph(len(self.name_to_id), [edge[1:] for edge in self.edges], directed=True)

    def drawBaseRoad(self):
        self.graph.es["color"] = "black"
        self.graph.es["width"] = 1.2

        # Plot graph
        fig, ax = plt.subplots()
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.6,
            vertex_color="lightblue",
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])],
            edge_lty="solid",
            edge_curved=0.3,
            layout=self.graph.layout("kk")
        )
        # plt.show()
        if not os.path.exists(self.base_path + "/temp"):
            os.mkdir(self.base_path + "/temp")

        fig.savefig(self.base_path + "/temp/base_road_graph.png", bbox_inches='tight', pad_inches=-0.1)

    def drawDriveRoadByCar(self, car):
        print(car.actual_path)
        print(car.edge_actual_path)
        self.graph.es["color"] = "black"
        self.graph.es["width"] = 1.2

        # print("vertex count:", self.graph.vcount())

        walk_node_list = [0] * self.graph.vcount() # 节点数量
        color_dict = {0: "lightblue", 1: "red"}


        for node_id in car.actual_path:
            # print("node_id = %d, id = %d" % (node_id, self.name_to_id[node_id]))
            walk_node_list[self.name_to_id[node_id]] = 1
        # print(walk_node_list)


        for edge_id in car.edge_actual_path:
            self.graph.es[edge_id-1]["color"] = "red"

        # Plot graph
        fig, ax = plt.subplots()
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.6,
            vertex_color=[color_dict[val] for val in walk_node_list],
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])],
            edge_lty="solid",
            edge_curved=0.3,
            layout=self.graph.layout("kk")
        )
        # plt.show()
        if not os.path.exists(self.base_path + "/temp"):
            os.mkdir(self.base_path + "/temp")

        fig.savefig(self.base_path + "/temp/carid_%s_trace_graph.png" % (str(car.car_id)), bbox_inches='tight', pad_inches=-0.1)

if __name__ == "__main__":
    pass
