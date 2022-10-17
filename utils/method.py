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


def getCurrentRoadCapacity(road_pipelines, road_index, road_max_capacity, system_time):
    # while len(road_pipelines[road_index]) <= system_time:
    #     road_pipelines[road_index].extend([0] * fill_amount)
    if len(road_pipelines[road_index]) <= system_time:
        return 0
    if road_pipelines[road_index][system_time] >= road_max_capacity:
        # 当前时刻车道满了
        return -1
    return road_pipelines[road_index][system_time]


def operateRoadPipeline(road_pipelines, road_index, road_max_capacity, system_time, pass_time, record, rate):
    if len(road_pipelines[road_index]) < (system_time + pass_time):
        road_pipelines[road_index].extend([road_pipelines[road_index][-1]] * (system_time + pass_time - len(road_pipelines[road_index])))
    # print(pass_time)
    for i in range(system_time, system_time+pass_time):
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


def removeLimitedEdges(graph, road_pipelines, road_current_accumulate, time, rate):
    delete_node_pairs = []
    for node_id, node in graph.node_table.items():
        for neighbor_node_id, edge_id in node.connectedTo.items():
            if len(road_pipelines[edge_id]) > time:
                if road_pipelines[edge_id][time] / road_current_accumulate[edge_id] > rate:
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


def changeDrivePath(graph, road_pipelines, road_current_accumulate, time, start_node_id, terminal_node_id, rate):
    if time == 0:
        return False, None, None
    mid_graph = copy.deepcopy(graph)
    if removeLimitedEdges(mid_graph, road_pipelines, road_current_accumulate, time, rate) == False:
        return False, None, None
    res, dist, mid_path = dijkstra(mid_graph, start_node_id, terminal_node_id)
    if res == False:
        return False, None, None
    return res, dist, mid_path


def updateTotalRoadPipelines(graph, system_time, current_road_pipelines, actual_path):
    time = system_time
    for i in range(len(actual_path) - 1):
        edge = graph.getEdgeByOriginAndTerminalNodeId(actual_path[i], actual_path[i+1])
        road_index = edge.edge_id
        # print("length: %d, time: %d" % (len(current_road_pipelines[road_index]), time))
        if len(current_road_pipelines[road_index]) <= time:
            capacity = 0
        else:
            capacity = current_road_pipelines[road_index][time]
        pass_time = edge.bprFunc(capacity)
        # print("    actual node[%d]->node[%d] pass time: %d" % (actual_path[i], actual_path[i+1], pass_time))

        if len(current_road_pipelines[road_index]) < (time + pass_time):
            current_road_pipelines[road_index].extend([0] * (time + pass_time - len(current_road_pipelines[road_index])))
        for t in range(time, time+pass_time):
            current_road_pipelines[road_index][t] += 1
        time += pass_time
    # print("time:", time)


def roadAccumulate(road_current_accumulate, road_acc_amount):
    for i in range(1, len(road_current_accumulate)):
        road_current_accumulate[i] += road_acc_amount[i]


def calcUncrowdedDriveTime(graph, actual_path):
    uncrowded_drive_time = 0
    for i in range(len(actual_path)-1):
        edge = graph.getEdgeByOriginAndTerminalNodeId(actual_path[i], actual_path[i+1])
        uncrowded_drive_time += edge.free_flow_time
    return uncrowded_drive_time

"""
def greedyGenerateCarDepartureTime(graph, cars, rate, system_time, start_time, total_road_pipelines=None, current_road_pipelines=None, is_departure=None):
    all_car_pass_max_time = 0
    # fill_amount = 100
    if system_time == 1:
        random.shuffle(cars)
    operate_graph = copy.deepcopy(graph)
    # 记录累计道路容量
    if total_road_pipelines == None:
        total_road_pipelines = [[0] for _ in range(operate_graph.edge_num + 1)]
    # 记录当前道路容量
    if current_road_pipelines == None:
        current_road_pipelines = [[0] for _ in range(operate_graph.edge_num + 1)]

    road_current_accumulate = [.0] * (operate_graph.edge_num + 1)
    road_acc_amount = [0] * (operate_graph.edge_num + 1)
    for _, edge in operate_graph.edge_table.items():
        road_acc_amount[edge.edge_id] = edge.road_max_capacity / 3600
    for _ in range(system_time-1):
        roadAccumulate(road_current_accumulate, road_acc_amount)

    if is_departure == None:
        carReadyGoNum = len(cars)
        is_departure = [False] * (len(cars) + 1)
    else:
        carReadyGoNum = 0
        for i in range(1, len(cars)+1):
            if is_departure[i] == False:
                carReadyGoNum += 1
        print("carReadyGoNum:", carReadyGoNum)

    while carReadyGoNum > 0:
        print("system time: %d, car ready go number: %d." % (system_time, carReadyGoNum))

        # road acc
        roadAccumulate(road_current_accumulate, road_acc_amount)
        # print(road_current_accumulate)

        # last_carReadyGoNum = carReadyGoNum
        is_full_lane = False
        lanes = graph.getRoadLaneNum()

        for i in range(len(cars)):
            if carReadyGoNum == 0:
                break
            car_id = cars[i].car_id
            if is_departure[car_id] == True:
                continue
            cars[i].actual_path = cars[i].shortest_path
            cars[i].retry_times = 0

            while is_departure[car_id] == False:
                car_drive_time = system_time
                cars[i].retry_times += 1
                if cars[i].retry_times > 5:
                    break

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
                    drive_road_capacity = getCurrentRoadCapacity(current_road_pipelines, drive_road_index, road_current_accumulate[drive_road_index], car_drive_time)
                    if drive_road_capacity == -1:
                        block_time = car_drive_time
                        break
                    pass_time = graph.edge_table[drive_road_index].bprFunc(drive_road_capacity)
                    # print("    simulate node[%d]->node[%d] pass time: %d" % (cars[i].actual_path[j], cars[i].actual_path[j+1], pass_time))

                    ok, block_time = operateRoadPipeline(total_road_pipelines, drive_road_index, road_current_accumulate[drive_road_index], car_drive_time, pass_time, record, rate)
                    if ok == False:
                        break
                    # print("road_index %d, pass_time %d." % (drive_road_index, pass_time))
                    car_drive_time += pass_time
                else:
                    is_departure[car_id] = True
                    cars[i].departure_time = system_time
                    cars[i].arrived_time = car_drive_time
                    cars[i].uncrowded_drive_time = calcUncrowdedDriveTime(graph, cars[i].actual_path)
                    # print("departure_time:", cars[i].departure_time)
                    # print("arrived_time:", cars[i].arrived_time)
                    # print("drive time:", cars[i].arrived_time - cars[i].departure_time)
                    # print("uncrowded_drive_time:", cars[i].uncrowded_drive_time)

                    # 更新累计道路容量
                    updateTotalRoadPipelines(graph, system_time, current_road_pipelines, cars[i].actual_path)

                    if all_car_pass_max_time < car_drive_time:
                        all_car_pass_max_time = car_drive_time
                    carReadyGoNum -= 1
                    lanes[graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[0], cars[i].actual_path[1]).edge_id] -= 1
                    # print("    car id: %d, departure time: %d, arrived time: %d, number %d short path" % (cars[i].car_id, system_time, time, k+1), end=", ")
                    # print("drive path:", cars[i].actual_path)
                    break

                if is_full_lane == True:
                    break
                # 拿到了time和road_pipeline
                res, _, mid_path = changeDrivePath(graph, current_road_pipelines, road_current_accumulate, block_time, cars[i].start_node_id, cars[i].terminal_node_id, rate)

                # 回退处理
                for (a, b) in record:
                    total_road_pipelines[a][b] -= 1

                if res == True:
                    # print("    carReadyGoNum:", carReadyGoNum, end=", ")
                    # print("success to change path", end=", ")
                    # print("car id: %d, strat node: %d, terminal node: %d" % (cars[i].car_id, cars[i].start_node_id, cars[i].terminal_node_id), end=", ")
                    # print("path:", mid_path)
                    cars[i].actual_path = mid_path
                else:
                    # print("    time: %d, car id: %d no road to go." % (system_time, cars[i].car_id))
                    break

        # if last_carReadyGoNum == carReadyGoNum:
        #     print("equal!!!")
        #     print("%d cars could not go." % (carReadyGoNum))
        #     break

        system_time += 1
        if system_time % 50 == 0:
            writeData(graph, cars, total_road_pipelines, current_road_pipelines, system_time)

        print("simulate spend time:", time.time() - start_time)
    # print(current_road_pipelines)
    print("max time: %d." % all_car_pass_max_time)
    # cars.sort(key=lambda car: car.car_id)
    return current_road_pipelines, total_road_pipelines, all_car_pass_max_time
"""

def floatNumberRoundUp(num):
    if num < 0:
        # Todo: 输入小于0时，特殊处理
        logger.error("Input number is negative.")
    return math.ceil(num)


def writeRoadAccumulateData(roads, road_pipelines, max_length, save_excel_path="../result/road_result.xlsx"):
    road_ids = []
    road_capacities = []
    for index in sorted(roads.keys()):
        road_ids.append(roads[index].edge_id)
        road_capacities.append(roads[index].road_max_capacity)

    for i in range(1, len(road_pipelines)):
        if len(road_pipelines[i]) <= max_length:
            road_pipelines[i].extend([road_pipelines[i][-1]] * (max_length + 1 - len(road_pipelines[i])))
        else:
            road_pipelines[i] = road_pipelines[i][: max_length + 1]
    dictionary = {
        "道路序号": road_ids,
        "道路最大容量": road_capacities
    }
    pipelines = np.array(road_pipelines[1:])
    for i in range(1, max_length):
        dictionary[str(i)] = list(pipelines[:, i])
    writeExcel(dictionary, save_excel_path)


def writeRoadData(roads, road_pipelines, max_length, save_excel_path="../result/road_result.xlsx"):
    road_ids = []
    road_left_nodes = []
    road_right_nodes = []
    road_capacities = []
    for index in sorted(roads.keys()):
        road_ids.append(roads[index].edge_id)
        road_left_nodes.append(roads[index].origin_node_id)
        road_right_nodes.append(roads[index].terminal_node_id)
        road_capacities.append(roads[index].road_max_capacity)

    for i in range(1, len(road_pipelines)):
        if len(road_pipelines[i]) <= max_length:
            road_pipelines[i].extend([0] * (max_length + 1 - len(road_pipelines[i])))
        else:
            road_pipelines[i] = road_pipelines[i][: max_length + 1]
    dictionary = {
        "道路序号": road_ids,
        "源点": road_left_nodes,
        "终点": road_right_nodes,
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
    uncrowded_drive_times = []
    drive_routes = []
    for car in sorted_cars:
        ids.append(car.car_id)
        departure_times.append(car.departure_time)
        arrived_times.append(car.arrived_time)
        drive_times.append(car.arrived_time-car.departure_time)
        uncrowded_drive_times.append(car.uncrowded_drive_time)
        drive_routes.append("->".join(str(x) for x in car.actual_path))

    dictionary = {
        "车辆序号": ids,
        "车辆出发时间": departure_times,
        "车辆到达时间": arrived_times,
        "车辆行驶时间": drive_times,
        "车辆(无拥堵)行驶时间": uncrowded_drive_times,
        "车辆行驶路线": drive_routes
    }
    writeExcel(dictionary, save_excel_path)


def writeData(graph, cars, total_road_pipelines, current_road_pipelines, system_time):
    writeCarData(cars, "./result/car_result_system_time_" + str(system_time) + ".xlsx")
    writeRoadAccumulateData(graph.edge_table, total_road_pipelines, system_time,
                  "./result/road_capacity_result_system_time_" + str(system_time) + ".xlsx")
    writeRoadData(graph.edge_table, current_road_pipelines, system_time,
                  "./result/road_cars_result_system_time_" + str(system_time) + ".xlsx")


def fillCarInfo(path, cars):
    df = pd.read_excel(path)
    is_departure = [False] * (len(cars) + 1)
    car_ids = list(df.loc[:, "车辆序号"].values)
    car_departure_time_times = list(df.loc[:, "车辆出发时间"].values)
    car_arrived_times = list(df.loc[:, "车辆到达时间"].values)
    uncrowded_drive_times = list(df.loc[:, "车辆(无拥堵)行驶时间"].values)
    car_drive_paths = list(df.loc[:, "车辆行驶路线"].values)
    cars.sort(key=lambda car: car.car_id)
    for i in range(len(cars)):
        if cars[i].car_id != car_ids[i]:
            print("Error!")
            return None
        cars[i].departure_time = car_departure_time_times[i]
        if cars[i].departure_time != 0:
            is_departure[cars[i].car_id] = True
        cars[i].arrived_time = car_arrived_times[i]
        cars[i].uncrowded_drive_time = uncrowded_drive_times[i]
        cars[i].actual_path = [int(val) for val in car_drive_paths[i].split("->")]
    return is_departure


def fillPipeline(pipeline, df, i):
    line = list(df.loc[i - 1].values)
    if i != line[0]:
        return False
    pipeline.extend(line[2:])
    return True

def fillRoadInfo(road_accumulate_capacity_path, road_current_capacity_path, edge_num):
    total_road_pipelines = [[0] for _ in range(edge_num + 1)]
    current_road_pipelines = [[0] for _ in range(edge_num + 1)]

    df1 = pd.read_excel(road_accumulate_capacity_path)
    df2 = pd.read_excel(road_current_capacity_path)
    for i in range(1, edge_num+1):
        if not(fillPipeline(total_road_pipelines[i], df1, i) and fillPipeline(current_road_pipelines[i], df2, i)):
            print("Fill road info error!")
            return None, None
    return current_road_pipelines, total_road_pipelines

def uniformDistribute(displayEdges: list, t: int, factor: int) -> (list, list):
    edgeSize, edgeColor = [], []
    for de in displayEdges:
        crowdRate = de.capacity_with_time[t - 1] / de.capacity
        edgeSize.append(crowdRate * factor + 1)
        if crowdRate > 0.7:
            edgeColor.append("red")
        elif crowdRate > 0.35:
            edgeColor.append("yellow")
        else:
            edgeColor.append("green")
    return edgeSize, edgeColor

if __name__ == "__main__":
    pass
