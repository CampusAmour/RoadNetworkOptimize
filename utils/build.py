from utils.method import dijkstra, findKShortestPath
from utils.model import Edge, Graph, Car
from utils.process_data import readRoadInfo, readCarInfo
from utils.logger import Logger


logger = Logger("log").getLogger()


def createGraph(path):
    input_items = readRoadInfo(path)
    graph = Graph()
    for item in input_items:
        edge = Edge(item)
        graph.addEdge(edge)
    return graph


# def createCars(path, graph):
# #     create_car_info = readCarInfo(path)
# #     cars = []
# #     car_id = 1
# #     for info in create_car_info:
# #         ok, shortest_distance, short_path = dijkstra(graph, info[0], info[1])
# #         if ok == False:
# #             # 求最短路径失败
# #             logger.error("Calculate short path failed, start node(%d), terminal node(%d)." % (info[0], info[1]))
# #             continue
# #
# #         paths = []
# #         visited = [False for _ in range(graph.node_num + 1)]
# #         findAllPathsBetweenTwoNode(graph, info[0], info[1], len(short_path) + 10, visited, [info[0]], paths)
# #         # print(paths)
# #         for _ in range(info[2]):
# #             # 调参
# #             departure_time = random.randint(0, 45)
# #             # paths = findAllPathsBetweenTwoNode(graph, info[0], info[1], [])
# #             actual_path = random.choice(paths)
# #             cars.append(Car(car_id, info[0], info[1], shortest_distance, short_path, actual_path, departure_time))
# #             car_id += 1
# #             # print("car_id:", car_id)
# #     return cars


def createCars(path, graph, k_path_num):
    create_car_info = readCarInfo(path)
    cars = []
    car_id = 1
    for info in create_car_info:
        ok, shortest_distance, short_path = dijkstra(graph, info[0], info[1])
        # k_paths = findKShortestPath(graph, info[0], info[1], k_path_num)
        if ok == False:
            # 求最短路径失败
            logger.error("Calculate short path failed, start node(%d), terminal node(%d)." % (info[0], info[1]))
            continue
        for _ in range(info[2]):
            # 调参
            departure_time = 0
            actual_path = short_path
            cars.append(Car(car_id, info[0], info[1], shortest_distance, short_path, actual_path, departure_time))
            car_id += 1
    return cars