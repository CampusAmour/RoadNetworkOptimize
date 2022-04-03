class Simulator():
    def __init__(self, graph, cars):
        self.graph = copy.deepcopy(graph)
        self.cars = copy.deepcopy(cars)
        # random.shuffle(self.cars)
        # Todo: 对car进行一个初始化操作
        # Todo: 是否考虑红绿灯情况


    def _addCarInRoadQueue(self, car, system_time):
        drive_road = self.graph.getEdgeByOriginAndTerminalNodeId(car.current_arrived_node_id, car.getNextPathNodeId())
        edge_id = drive_road.edge_id
        if self.road_capacities[edge_id] == self.graph.edge_table[edge_id].road_max_capacity:
            print("edge: %d, capacity: %d." % (edge_id, self.road_capacities[edge_id]))
            # 车道容量满了
            return False
        # 根据道路容量bpr函数计算车辆通行时间
        pass_time = self.graph.edge_table[edge_id].bprFunc(self.road_capacities[edge_id])
        # 每个item: [car_id, pass_time+system_time, system_time]
        self.road_queues[edge_id].append([car.car_id, pass_time+system_time, system_time])
        self.road_capacities[edge_id] += 1
        return True


    def _driveCarStart(self, cars, system_time):
        if self.carReadyGoNum == 0:
            # 所有车辆均已出发
            return True
        for i in range(len(cars)):
            if (self.carReadyGoNum > 0) and (cars[i].departure_time == system_time):
                if self._addCarInRoadQueue(cars[i], system_time) == False:
                    return False
                self.carReadyGoNum -= 1
        return True


    def _findCarIndexById(self, cars, car_id):
        for i in range(len(cars)):
            if car_id == cars[i].car_id:
                return i
        # Todo: 跑到这里证明car_id不存在,抛异常


    def _moveCar(self, cars, system_time):
        for i in range(1, self.graph.edge_num+1):
            index = 0
            while index < self.road_capacities[i]:
                if self.road_queues[i][index][1] == system_time:
                    # 车辆已经行驶到road尽头
                    car_id = self.road_queues[i][index][0]
                    car_index = self._findCarIndexById(cars, car_id)
                    cars[car_index].current_arrived_node_id = cars[car_index].getNextPathNodeId()
                    cars[car_index].current_arrived_pos += 1
                    # 从当前车道中弹出
                    self.road_queues[i].pop(index)
                    self.road_capacities[i] -= 1
                    # 加入到下一条车道中
                    if cars[car_index].current_arrived_node_id == cars[car_index].terminal_node_id:
                        # 车辆已到达终点
                        self.carArrivedNum += 1
                        # Todo: 记录car行驶总时间
                        # print("car id(%d) is arrived, time is (%d)." % (car_id, system_time))
                    else:
                        if self._addCarInRoadQueue(cars[car_index], system_time) == False:
                            return False
                    continue
                else:
                    index += 1
        return True



    def _initRoadQueues(self):
        # 用队列模拟一个车道大小
        self.road_capacities = [0 for _ in range(self.graph.edge_num+1)]
        self.road_queues = [[] for _ in range(self.graph.edge_num+1)]


    def _sortCarsByDepartureTime(self):
        return sorted(self.cars, key=lambda c: c.departure_time)


    def _checkAllCarsArrived(self):
        return self.carArrivedNum == len(self.cars)


    def action(self):
        # 设置系统时间为0
        system_time = 0
        self._initRoadQueues()
        # 待出发的车辆数量
        self.carReadyGoNum = len(self.cars)
        # 已到达的车辆数量
        self.carArrivedNum = 0
        cars = copy.deepcopy(self._sortCarsByDepartureTime())
        while self._checkAllCarsArrived() == False:
            if (self._driveCarStart(cars, system_time) == False) or (self._moveCar(cars, system_time) == False):
                print("system time is %d." % system_time)
                return False, None
            system_time += 1
        # 返回最后一辆车到达的时间
        return True, system_time-1




"""
def main():
    road_info_path = "./input_data/road_info.xlsx"
    graph = createGraph(road_info_path)
    # print(dijkstra(graph, 4, 2))
    paths = []
    print(graph.getNodeById(6).getConnections())
    visited = [False for _ in range(graph.node_num + 1)]
    findAllPathsBetweenTwoNode(graph, 1, 2, visited, [1], paths)
    print(paths)
    print(len(paths))

    car_info_path = "./input_data/car_info.xlsx"
    cars = createCars(car_info_path, graph)
    print(len(cars))
"""


# def main():
#     road_info_path = "./input_data/road_info.xlsx"
#     graph = createGraph(road_info_path)
#     car_info_path = "./input_data/car_info.xlsx"
#     cars = createCars(car_info_path, graph)
#     for i in range(len(cars)):
#         cars[i].actual_path = cars[i].shortest_path
#     simulator = Simulator(graph, cars[: 250])
#     for _ in range(3):
#         print(simulator.action())


def main():
    road_info_path = "./input_data/road_info.xlsx"
    graph = createGraph(road_info_path)
    car_info_path = "./input_data/car_info.xlsx"
    start_time = time.time()
    cars = createCars(car_info_path, graph)
    end_time = time.time()
    print("create cars spend time:", end_time - start_time)
    road_pipelines, max_length = greedyGenerateCarDepartureTime(cars, graph)
    simulator = Simulator(graph)
    print(simulator.action(cars))

    json_path = "./config.json"
    data = parseJsonFile(json_path)
    population_size = data["population_size"]
    ga = GeneticAlgorithm(graph, population_size, car_info_path)
    # ga.generatePopulation()

    print("total spend time:", time.time() - start_time)

    ### wirte data ###
    # writeCarData(cars, "./result/car_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
    # writeRoadData(graph.edge_table, road_pipelines, max_length, "./result/road_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
