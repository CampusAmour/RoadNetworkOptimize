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
from matplotlib import font_manager

import utils.model
from utils import method
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
        self.graph.es["width"] = 1

        # Plot graph
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.3,
            vertex_color="lightblue",
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])],
            # edge_label=[str(edge[0]) for edge in self.edges],
            edge_lty="solid",
            edge_curved=0.1,
            layout=self.graph.layout("kk")
        )
        # plt.show()
        if not os.path.exists(self.base_path + "/temp"):
            os.mkdir(self.base_path + "/temp")

        fig.savefig(self.base_path + "/temp/base_road_graph.png", bbox_inches='tight', pad_inches=-0.1)

    def drawDriveRoadByCar(self, car):
        self.graph.es["color"] = "black"
        self.graph.es["width"] = 1

        walk_node_list = [0] * self.graph.vcount() # 节点数量
        color_dict = {0: "lightblue", 1: "red"}

        for node_id in car.actual_path:
            walk_node_list[self.name_to_id[node_id]] = 1

        for edge_id in car.edge_actual_path:
            self.graph.es[edge_id-1]["color"] = "red"

        # Plot graph
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.3,
            vertex_color=[color_dict[val] for val in walk_node_list],
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])],
            # edge_label=[edge[0] for edge in self.edges],
            edge_lty="solid",
            edge_curved=0.1,
            layout=self.graph.layout("kk")
        )
        # plt.show()
        if not os.path.exists(self.base_path + "/temp"):
            os.mkdir(self.base_path + "/temp")

        fig.savefig(self.base_path + "/temp/carid_%s_trace_graph.png" % (str(car.car_id)), bbox_inches='tight', pad_inches=-0.1)

    def drawDriveRoadByTime(self, displayEdges, t):
        edgeSize, edgeColor = method.uniformDistribute(displayEdges, t, 5)
        print("edgeSize:", edgeSize)
        print(len(displayEdges[0].capacity_with_time))
        self.graph.es["color"] = "black"
        self.graph.es["width"] = 6

        # walk_node_list = [0] * self.graph.vcount()  # 节点数量
        # color_dict = {0: "lightblue", 1: "red"}
        #
        # for node_id in car.actual_path:
        #     walk_node_list[self.name_to_id[node_id]] = 1
        #
        # for edge_id in car.edge_actual_path:
        #     self.graph.es[edge_id - 1]["color"] = "red"

        # Plot graph
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
        ig.plot(
            self.graph,
            target=ax,
            vertex_size=0.3,
            vertex_color="lightblue",
            vertex_label=[v[1] for v in sorted(self.id_to_name.items(), key=lambda x: x[0])],
            edge_width=edgeSize,
            edge_color=edgeColor,
            edge_lty="solid",
            edge_curved=0.1,
            layout=self.graph.layout("kk")
        )
        # plt.show()
        if not os.path.exists(self.base_path + "/temp"):
            os.mkdir(self.base_path + "/temp")

        fig.savefig(self.base_path + "/temp/road_capacity_time_%s_graph.png" % (str(t)), bbox_inches='tight',
                    pad_inches=-0.1)


def drawEdgeCapacityWithTime(de: utils.model.DisplayEdge, base_path):
    y = de.capacity_with_time
    x = [i+1 for i in range(len(de.capacity_with_time))]

    mf = font_manager.FontProperties(fname=base_path+"/material/simsun.ttc")

    # 设置标题
    plt.title(u"道路编号%d[%d->%d]流量变化图" % (de.edge_id, de.origin_node_id, de.terminal_node_id), fontproperties=mf, fontsize=16)
    # 设置x轴标注
    plt.xlabel(u"时间(秒)", fontproperties=mf)
    # 设置y轴标注
    plt.ylabel(u"道路流量(辆)", fontproperties=mf)
    plt.xlim((0, len(x)+1))
    plt.ylim((0, max(y)+1))

    plt.plot(x, y)
    plt.savefig(base_path + "/temp/edge_id_%d" % (de.edge_id) + ".png")
    plt.clf()

if __name__ == "__main__":
    pass
