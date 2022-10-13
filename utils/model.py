#!/usr/bin/env python
# coding:utf-8
"""
Name   : graph.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/3/1 0:17
Desc   : 图用邻接表形式表示
"""
import math
import copy
import random
from utils.logger import Logger
from utils.method import getCurrentRoadCapacity, operateRoadPipeline

logger = Logger("log").getLogger()
random.seed(7)


class Car():
    def __init__(self, car_id, start_node_id, terminal_node_id, shortest_distance, short_path, actual_path, departure_time):
        self.car_id = car_id
        self.start_node_id = start_node_id
        self.terminal_node_id = terminal_node_id
        self.shortest_distance = shortest_distance
        self.shortest_path = short_path
        # # 当前所行驶在的道路id
        # self.current_drive_road = -1
        # Todo:
        # 车辆出发时间(由遗传算法给出)
        # self.departure_time = departure_time
        self.departure_time = departure_time
        # 车辆到达时间
        self.arrived_time = 0
        # 实际路线(节点组成)
        self.actual_path = actual_path
        # 实际路线(边组成)
        self.edge_actual_path = []
        # 记录car当前所处于的结点的索引(初始为start_node)
        self.current_arrived_pos = 0
        # 记录car当前所处于的node id
        self.current_arrived_node_id = start_node_id

        # # 实际路线用时(由遗传算法给出)
        # self.actual_distance = actual_distance

        # 确定路线后,车辆在无拥挤下的行驶时间
        self.uncrowded_drive_time = -1

        self.retry_times = 0


    def getNextPathNodeId(self):
        """
            Desc: 返回path路径中的下一个结点id
        """
        if self.current_arrived_pos < len(self.actual_path) - 1:
            return self.actual_path[self.current_arrived_pos + 1]
        # 当前结点已是最后一个结点(终点)
        # Todo: 错误处理
        return


class Edge():
    def __init__(self, input_item):
        self.edge_id = input_item.edge_id
        self.origin_node_id = input_item.origin_node_id
        self.terminal_node_id = input_item.terminal_node_id
        self.free_flow_time = input_item.free_flow_time
        self.road_length = input_item.road_length
        # self.desired_travel_time = input_item.desired_travel_time
        # self.max_travel_time = input_item.max_travel_time
        self.free_flow_speed = input_item.free_flow_speed
        # self.desired_speed = input_item.desired_speed
        # self.min_speed = input_item.min_speed
        self.road_max_capacity = input_item.road_max_capacity
        self.lane_num = input_item.lane_num
        self.car_interval = None    # 车辆在该条路上出发的间隔，

        self.alpha = 0.61
        self.beta = 1.653


    def bprFunc(self, road_capacity):
        """
            Desc: BPR函数,当车道中车辆大于30%时,车辆行驶速度会下降,具体为公式xxx
        """
        # print("road_capacity:", road_capacity)
        t = self.free_flow_time * (1 + self.alpha * math.pow((road_capacity / self.road_max_capacity), self.beta))
        if t < 0:
            # Todo: 异常处理
            pass
        # 向上取整返回
        return math.ceil(t)


    def updateRoadActualPassTime(self, pass_time):
        self.free_flow_time = pass_time


class Node():
    def __init__(self, node_id):
        self.node_id = node_id
        self.connectedTo = {}

    def addNeighborNode(self, neighbor_node_id, edge_id):
        self.connectedTo[neighbor_node_id] = edge_id

    # 返回该结点连接的所有节点id
    def getConnections(self):
        return self.connectedTo.keys()

    def getNodeId(self):
        return self.node_id

    # 根据相连结点的id返回边的信息
    def getEdgeIdByNeighborNodeId(self, neighbor_node_id):
        return self.connectedTo.get(neighbor_node_id, None)

    def removeNeighborNode(self, neighbor_node_id):
        if self.connectedTo.get(neighbor_node_id, None) == None:
            return False
        _ = self.connectedTo.pop(neighbor_node_id)
        return True

    def __str__(self):
        pass


class Graph():
    def __init__(self):
        self.node_table = {}
        self.node_num = 0
        self.edge_table = {}
        self.edge_num = 0

    def getNodeById(self, node_id):
        return self.node_table.get(node_id, None)

    def _addNode(self, node_id):
        if self.getNodeById(node_id) != None:
            return
        self.node_table[node_id] = Node(node_id)
        self.node_num += 1

    def getEdgeById(self, edge_id):
        return self.edge_table.get(edge_id, None)

    def addEdge(self, edge):
        self._addNode(edge.origin_node_id)
        self._addNode(edge.terminal_node_id)

        if self.edge_table.get(edge.edge_id, None) != None:
            # Todo: 边已存在后的处理
            raise Exception("This edge(id: %d) is existed." % (edge.edge_id))
        self.edge_num += 1
        self.edge_table[edge.edge_id] = edge
        self.node_table[edge.origin_node_id].addNeighborNode(edge.terminal_node_id, edge.edge_id)

    def getNodes(self):
        return self.node_table.keys()

    def getEdgeByOriginAndTerminalNodeId(self, origin_node_id, next_node_id):
        # logger.debug("Start to get edge by origin node(%d), terminal node(%d)." % (origin_node_id, next_node_id))
        edge = self.getEdgeById(self.getNodeById(origin_node_id).getEdgeIdByNeighborNodeId(next_node_id))
        if edge == None:
            logger.error("Failed to get edge id by origin node(%d), terminal node(%d)." % (origin_node_id, next_node_id))
            return
        # logger.debug("Succeed to get edge id(%d) by origin node(%d), terminal node(%d)." % (edge.edge_id, origin_node_id, next_node_id))
        return edge

    def removeEdgeByNodeId(self, node_id, remove_node_id):
        # print("node id: %d, remove node id: %d." % (node_id, remove_node_id))
        edge = self.getEdgeById(self.getNodeById(node_id).getEdgeIdByNeighborNodeId(remove_node_id))
        if (edge == None) or (self.edge_table.get(edge.edge_id, None) == None):
            return False
        if self.getNodeById(node_id).removeNeighborNode(remove_node_id) == False:
            return False
        _ = self.edge_table.pop(edge.edge_id)
        self.edge_num -= 1
        return True

    def getRoadLaneNum(self):
        lanes = [0] * (self.edge_num + 1)
        for edge_id, edge in self.edge_table.items():
            lanes[edge_id] = edge.lane_num * 2
        return lanes


class InputItem():
    def __init__(self, row_item):
        # 0-边id, 1-路段, 2-自由流时间, 3-道路容量
        self.edge_id = int(row_item[0])
        nodes = row_item[1].split('-')
        self.origin_node_id = int(nodes[0])
        self.terminal_node_id = int(nodes[1])
        self.free_flow_time = float(row_item[2])
        self.road_max_capacity = int(row_item[3])
        self.road_length = float(row_item[4])
        # self.desired_travel_time = float(row_item[5])
        # self.max_travel_time = float(row_item[6])
        # self.free_flow_speed = float(row_item[7])
        # self.desired_speed = float(row_item[8])
        # self.min_speed = float(row_item[9])
        self.free_flow_speed = float(row_item[5])
        self.lane_num = int(row_item[6])


class Simulator():
    def __init__(self, graph):
        self.graph = copy.deepcopy(graph)
        # random.shuffle(self.cars)
        # Todo: 对car进行一个初始化操作
        # Todo: 是否考虑红绿灯情况


    def action(self, input_cars):
        # 设置系统时间为0
        system_time = 1
        cars = copy.deepcopy(input_cars)
        carReadyGoNum = len(cars)
        is_departure = [False] * len(cars)
        fill_amount = 8
        road_pipelines = [[0] * fill_amount for _ in range(self.graph.edge_num + 1)]

        while carReadyGoNum > 0:
            # print("system time: %d, car ready go number: %d." % (system_time, carReadyGoNum))
            for i in range(len(cars)):
                if carReadyGoNum == 0:
                    break
                if (is_departure[i] == True) or (cars[i].departure_time != system_time):
                    continue
                time = system_time
                for j in range(len(cars[i].actual_path) - 1):
                    # print(cars[i].actual_path[j], cars[i].actual_path[j+1])
                    drive_road = self.graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[j],
                                                                        cars[i].actual_path[j + 1])
                    drive_road_index = drive_road.edge_id
                    # 根据道路容量bpr函数计算车辆通行时间
                    # Todo: 信号灯
                    drive_road_capacity = getCurrentRoadCapacity(road_pipelines, drive_road_index,
                                                                 drive_road.road_max_capacity, time, fill_amount)
                    if drive_road_capacity == -1:
                        return False, None, None
                    pass_time = self.graph.edge_table[drive_road_index].bprFunc(drive_road_capacity)
                    if operateRoadPipeline(road_pipelines, drive_road_index, drive_road.road_max_capacity, time,
                                           pass_time, fill_amount) == False:
                        return False, None, None
                    # print("road_index %d, pass_time %d." % (drive_road_index, pass_time))
                    time += pass_time
                is_departure[i] = True
                cars[i].arrived_time = time
                carReadyGoNum -= 1
                continue
            system_time += 1

        max_time = 0
        # print(road_pipelines)
        for road in road_pipelines:
            for index in range(len(road)):
                if (road[index] != 0) and (max_time < index):
                    max_time = index
        print("max time: %d." % max_time)
        return True, road_pipelines, max_time

class DisplayEdge():
    def __init__(self, edge_id, origin_node_id, terminal_node_id, capacity_with_time):
        # 0-边id, 1-路段, 2-自由流时间, 3-道路容量
        self.edge_id = edge_id
        self.origin_node_id = origin_node_id
        self.terminal_node_id = terminal_node_id
        self.capacity_with_time = [int(item) for item in capacity_with_time]

    def __str__(self):
        return "edge id: %s, origin node id: %s, terminal node id: %s" %\
               (self.edge_id, self.origin_node_id, self.terminal_node_id)


if __name__ == "__main__":
    pass
