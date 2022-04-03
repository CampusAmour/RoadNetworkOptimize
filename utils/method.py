#!/usr/bin/env python
# coding:utf-8
"""
Name   : method.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/3/12 21:27
"""
import copy
import math
import time
import random
import pandas as pd
import numpy as np
from utils.logger import Logger


logger = Logger("log").getLogger()


def writeExcel(dictionary, save_excel_path):
    df = pd.DataFrame(dictionary)
    df.to_excel(save_excel_path, index=False)


def dijkstra(graph, start_node_id, terminal_node_id):
    """
        迪杰斯特拉算法: 以自由流时间计算最短路径
    :return:
    """
    if start_node_id == terminal_node_id:
        # Todo: 终点和起点为同一点的情况
        pass

    visited = [False for _ in range(graph.node_num + 1)]
    distance = [-1 for _ in range(graph.node_num + 1)]
    route = [-1 for _ in range(graph.node_num + 1)]

    distance[start_node_id] = 0

    for neighbor_node_id in graph.getNodeById(start_node_id).getConnections():
        distance[neighbor_node_id] = graph.getEdgeByOriginAndTerminalNodeId(start_node_id, neighbor_node_id).free_flow_time
        route[neighbor_node_id] = start_node_id

    for i in range(graph.node_num - 1):
        min_dist = float("inf")
        node_id = -1
        for j in range(1, graph.node_num + 1):
            if not visited[j] and (distance[j] != -1) and (distance[j] < min_dist):
                min_dist = distance[j]
                node_id = j
        if node_id == -1:
            # 说明此时路已经不通了
            break
        visited[node_id] = True
        for v in graph.getNodeById(node_id).getConnections():
            if (distance[v] == -1) or ((graph.getEdgeByOriginAndTerminalNodeId(node_id, v) != None) and (distance[v] > distance[node_id] + graph.getEdgeByOriginAndTerminalNodeId(node_id, v).free_flow_time)):
                distance[v] = distance[node_id] + graph.getEdgeByOriginAndTerminalNodeId(node_id, v).free_flow_time
                route[v] = node_id

    # print(distance)
    # print(route)
    if distance[terminal_node_id] == -1:
        # 说明从起点到该节点未存在路径
        return False, None, None
    # 获取最短路径
    node_id = terminal_node_id
    path = []
    while node_id != -1:
        path.append(node_id)
        node_id = route[node_id]
    return True, distance[terminal_node_id], path[::-1]


# def addLimit(path, start_node_id):
#     result = []
#     for item in path:
#         if start_node_id in item[0]:
#             result.append([start_node_id, item[0][item[0].index(start_node_id) + 1]])
#     # 去重
#     result = [list(r) for r in list(set([tuple(t) for t in result]))]
#     print(result)
#     return result


def findShortestPathWithLimit(graph, start_node_id, terminal_node_id, isolated_node_ids):
    mid_graph = copy.deepcopy(graph)
    for node_id in isolated_node_ids:
        if mid_graph.removeEdgeByNodeId(start_node_id, node_id) == False:
            print("Error: findShortestPathWithLimit.")
            print("start node id: %d, isolated node id %d." % (start_node_id, node_id))
            return False, None, None
    res, dist, mid_path = dijkstra(mid_graph, start_node_id, terminal_node_id)
    if res == False:
        return False, None, None
    return res, dist, mid_path


def addIsolatedPoint(isolated_points, limit_path):
    start_node_id = limit_path[0]
    next_node_id = limit_path[1]
    if isolated_points.get(start_node_id, None) == None:
        isolated_points[start_node_id] = [next_node_id]
    elif next_node_id not in isolated_points[start_node_id]:
        isolated_points[start_node_id].append(next_node_id)
    return isolated_points[start_node_id]


def addPathInAlter(alter_paths, items):
    """
        # 加入到备选路径列表中
    """
    temp_paths = [tuple(p[0]) for p in alter_paths]
    if tuple(items[0]) not in temp_paths:
        alter_paths.append(items)
    # print(alter_paths)


def calcPassTime(graph, path):
    """
        计算path实际用时
    """
    dist = 0.0
    for i in range(len(path)-1):
        dist += graph.getEdgeByOriginAndTerminalNodeId(path[i], path[i+1]).free_flow_time
    return dist


def findKShortestPath(graph, start_node_id, terminal_node_id, k=10):
    k_paths = []
    alter_paths = []
    isolated_points = {}
    res, dist, shortest_path = dijkstra(graph, start_node_id, terminal_node_id)
    if res == False:
        return None
    k_paths.append([shortest_path, dist])

    while True:
        if len(k_paths) == k:
            break
        choice = k_paths[-1][0]
        # print(choice)
        for i in range(len(choice)-1):
            limit_path = [choice[i], choice[i+1]]
            # print(limit_path)
            path = choice[:i]
            isolated_node_ids = addIsolatedPoint(isolated_points, limit_path)
            # print(isolated_node_ids)
            res, _, mid_path = findShortestPathWithLimit(graph, choice[i], terminal_node_id, isolated_node_ids)
            if res == False:
                continue
            path.extend(mid_path)

            dist = calcPassTime(graph, path)

            addPathInAlter(alter_paths, [path, dist])

        if len(alter_paths) == 0:
            print("Only have %d paths." % (len(k_paths)))
            return k_paths

        alter_paths.sort(key=lambda x: x[-1])
        # print(alter_paths)

        k_paths.append(alter_paths.pop(0))
        # print(k_paths)

    return k_paths


def dfs(graph, start_node_id, terminal_node_id, temp, paths):
    """
        Desc: 有向图求AB两点所有路径(无向图中慎用)
    """
    for neighbor_node_id in graph.getNodeById(start_node_id).getConnections():
        if neighbor_node_id == terminal_node_id:
            paths.append(temp + [terminal_node_id])
            return
        dfs(graph, neighbor_node_id, terminal_node_id, temp + [neighbor_node_id], paths)


def findAllPathsBetweenTwoNode(graph, start_node_id, terminal_node_id, max_depth, visited, path, paths):
    """
        Desc: 无向图求AB两点所有路径(每条路径中的每个顶点最多访问一次)
    """
    # print(visited)
    # logging.info("start node %d, end node %d." % (start_node_id, terminal_node_id))
    # print("start node %d, end node %d." % (start_node_id, terminal_node_id))
    if (visited[start_node_id] == True) or (len(path) >= max_depth):
        return
    if start_node_id == terminal_node_id:
        paths.append(path)
        return
    visited[start_node_id] = True
    # print(graph.getNodeById(start_node_id).getConnections())
    for neighbor_node_id in graph.getNodeById(start_node_id).getConnections():
        if not visited[neighbor_node_id]:
            findAllPathsBetweenTwoNode(graph, neighbor_node_id, terminal_node_id, max_depth, visited, path + [neighbor_node_id], paths)
    visited[start_node_id] = False


def getCurrentRoadCapacity(road_pipelines, road_index, road_max_capacity, system_time, fill_amount):
    while len(road_pipelines[road_index]) <= system_time:
        road_pipelines[road_index].extend([0] * fill_amount)
    if road_pipelines[road_index][system_time] == road_max_capacity - 1:
        # 当前时刻车道满了
        return -1
    return road_pipelines[road_index][system_time]


def operateRoadPipeline(road_pipelines, road_index, road_max_capacity, system_time, pass_time, fill_amount, record, rate):
    while len(road_pipelines[road_index]) <= (system_time + pass_time + 3600):
        road_pipelines[road_index].extend([0] * fill_amount)
    # print(pass_time)
    for i in range(system_time, system_time+pass_time+3600):
        if road_pipelines[road_index][i] / road_max_capacity > rate:
            # print("time %d, road index %d, current road %d, road max %d." % (i, road_index, road_pipelines[road_index][i], road_max_capacity))
            # 此时车道已达到拥塞,不允许车辆再进入
        # if road_pipelines[road_index][i] == road_max_capacity - 1:
        #     # 当前时刻车道满了
            return False, i
        road_pipelines[road_index][i] += 1
        record.append((road_index, i))
        # print(road_pipelines[road_index][i])
    return True, None


def removeLimitedEdges(graph, road_pipelines, time, rate):
    delete_node_pairs = []
    for node_id, node in graph.node_table.items():
        for neighbor_node_id, edge_id in node.connectedTo.items():
            if len(road_pipelines[edge_id]) > time:
                if road_pipelines[edge_id][time] / graph.edge_table[edge_id].road_max_capacity > rate:
                    delete_node_pairs.append((node_id, neighbor_node_id))
                else:
                    pass_time = graph.edge_table[edge_id].bprFunc(road_pipelines[edge_id][time])
                    graph.edge_table[edge_id].updateRoadActualPassTime(pass_time)
            else:
                pass_time = graph.edge_table[edge_id].bprFunc(road_pipelines[edge_id][-1])
                graph.edge_table[edge_id].updateRoadActualPassTime(pass_time)

            # if (len(road_pipelines[edge_id]) > time) and (road_pipelines[edge_id][time] / graph.edge_table[edge_id].road_max_capacity > rate):
            #     delete_node_pairs.append((node_id, neighbor_node_id))

    for node_id, neighbor_node_id in delete_node_pairs:
        if graph.removeEdgeByNodeId(node_id, neighbor_node_id) == False:
                print("Error: addLimitedEdges.")
                print("start node id: %d, isolated node id %d." % (node_id, neighbor_node_id))
                return False
    return True


def changePath(graph, road_pipelines, time, start_node_id, terminal_node_id, rate):
    if time == 0:
        return False, None, None
    mid_graph = copy.deepcopy(graph)
    if removeLimitedEdges(mid_graph, road_pipelines, time, rate) == False:
        return False, None, None
    res, dist, mid_path = dijkstra(mid_graph, start_node_id, terminal_node_id)
    if res == False:
        return False, None, None
    return res, dist, mid_path


def greedyGenerateCarDepartureTime(graph, cars, rate):
    """
        Desc: 贪心算法生成车辆离开的时间
    """
    all_car_pass_max_time = 0
    fill_amount = 100
    random.shuffle(cars)
    operate_graph = copy.deepcopy(graph)
    road_pipelines = [[0]*fill_amount for _ in range(operate_graph.edge_num + 1)]
    system_time = 1
    carReadyGoNum = len(cars)
    is_departure = [False] * (len(cars) + 1)

    while carReadyGoNum > 0:
        print("system time: %d, car ready go number: %d." % (system_time, carReadyGoNum))

        last_carReadyGoNum = carReadyGoNum
        is_full_lane = False
        lanes = graph.getRoadLaneNum()

        for i in range(len(cars)):
            if carReadyGoNum == 0:
                break
            car_id = cars[i].car_id
            if is_departure[car_id] == True:
                continue
            time = system_time
            cars[i].actual_path = cars[i].shortest_path

            while is_departure[car_id] == False:
                block_time = 0
                record = []

                for j in range(len(cars[i].actual_path)-1):
                    # print(cars[i].actual_path[j], cars[i].actual_path[j+1])
                    drive_road = graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[j], cars[i].actual_path[j+1])
                    drive_road_index = drive_road.edge_id
                    if (j == 0) and (lanes[drive_road_index] == 0):
                        is_full_lane = True
                        break
                    # 根据道路容量bpr函数计算车辆通行时间
                    # Todo: 信号灯
                    drive_road_capacity = getCurrentRoadCapacity(road_pipelines, drive_road_index, drive_road.road_max_capacity, time, fill_amount)
                    if drive_road_capacity == -1:
                        break
                    pass_time = graph.edge_table[drive_road_index].bprFunc(drive_road_capacity)
                    ok, block_time = operateRoadPipeline(road_pipelines, drive_road_index, drive_road.road_max_capacity, time, pass_time, fill_amount, record, rate)
                    if ok == False:
                        break
                    # print("road_index %d, pass_time %d." % (drive_road_index, pass_time))
                    time += pass_time
                else:
                    is_departure[car_id] = True
                    cars[i].departure_time = system_time
                    cars[i].arrived_time = time
                    if all_car_pass_max_time < time:
                        all_car_pass_max_time = time
                    carReadyGoNum -= 1
                    lanes[graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[0], cars[i].actual_path[1]).edge_id] -= 1
                    # print("    car id: %d, departure time: %d, arrived time: %d, number %d short path" % (cars[i].car_id, system_time, time, k+1), end=", ")
                    # print("drive path:", cars[i].actual_path)
                    break

                if is_full_lane == True:
                    break

                # 拿到了time和road_pipeline
                res, _, mid_path = changePath(graph, road_pipelines, block_time, cars[i].start_node_id, cars[i].terminal_node_id, rate)

                # 回退处理
                for (a, b) in record:
                    road_pipelines[a][b] -= 1

                if res == True:
                    print("carReadyGoNum:", carReadyGoNum, end=", ")
                    print("success to change path", end=", ")
                    print("car id: %d, strat node: %d, terminal node: %d" % (cars[i].car_id, cars[i].start_node_id, cars[i].terminal_node_id), end=", ")
                    print("path:", mid_path)
                    cars[i].actual_path = mid_path
                else:
                    print("time: %d, car id: %d no road to go." % (system_time, cars[i].car_id))
                    break

        if last_carReadyGoNum == carReadyGoNum:
            print("equal!!!")
            print("%d cars could not go." % (carReadyGoNum))
            break

        system_time += 1

    # print(road_pipelines)
    print("max time: %d." % all_car_pass_max_time)
    # cars.sort(key=lambda car: car.car_id)
    return road_pipelines, all_car_pass_max_time


def floatNumberRoundUp(num):
    if num < 0:
        # Todo: 输入小于0时，特殊处理
        logger.error("Input number is negative.")
    return math.ceil(num)


def writeRoadData(roads, road_pipelines, max_length, save_excel_path="../result/road_esult.xlsx"):
    road_ids = []
    road_capacities = []
    for index in sorted(roads.keys()):
        road_ids.append(roads[index].edge_id)
        road_capacities.append(roads[index].road_max_capacity)

    for i in range(1, len(road_pipelines)):
        if len(road_pipelines[i]) < max_length:
            road_pipelines[i].extend([0]*(max_length-len(road_pipelines[i])))
        elif len(road_pipelines[i]) > max_length:
            road_pipelines[i] = road_pipelines[i][:max_length]
    dictionary = {
        "道路序号": road_ids,
        "道路最大容量": road_capacities
    }
    pipelines = np.array(road_pipelines[1:])
    for i in range(1, max_length):
        dictionary[str(i)] = list(pipelines[:, i])
    writeExcel(dictionary, save_excel_path)


def writeCarData(cars, save_excel_path="../result/car_result.xlsx"):
    sorted_cars = sorted(cars, key=lambda car: car.car_id)
    ids = []
    departure_times = []
    arrived_times = []
    drive_times = []
    drive_routes = []
    for car in sorted_cars:
        ids.append(car.car_id)
        departure_times.append(car.departure_time)
        arrived_times.append(car.arrived_time)
        drive_times.append(car.arrived_time-car.departure_time)
        drive_routes.append("->".join(str(x) for x in car.actual_path))
    dictionary = {
        "车辆序号": ids,
        "车辆出发时间": departure_times,
        "车辆到达时间": arrived_times,
        "车辆行驶时间": drive_times,
        "车辆行驶路线": drive_routes
    }
    writeExcel(dictionary, save_excel_path)


if __name__ == "__main__":
    pass