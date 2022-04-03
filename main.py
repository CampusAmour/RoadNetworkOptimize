import time
from utils.model import Simulator
from utils.process_data import parseJsonFile
from utils.genetic_algorithm import GeneticAlgorithm
from utils.build import createGraph, createCars
from utils.method import greedyGenerateCarDepartureTime, writeCarData, writeRoadData


# def main():
#     road_info_path = "./input_data/road_info.xlsx"
#     graph = createGraph(road_info_path)
#     car_info_path = "./input_data/car_info.xlsx"
#     start_time = time.time()
#     cars = createCars(car_info_path, graph)
#     end_time = time.time()
#     print("create cars spend time:", end_time - start_time)
#     road_pipelines, max_length = greedyGenerateCarDepartureTime(graph, cars)
#     simulator = Simulator(graph)
#     print(simulator.action(cars))
#     a = input("ddd")
#     #
#     #
#     json_path = "./config.json"
#     data = parseJsonFile(json_path)
#     population_size = data["population_size"]
#     ga = GeneticAlgorithm(graph, population_size, car_info_path)
#     ga.generatePopulation()
#     # ga.test()
#     ga.execute()
#
#     print("total spend time:", time.time() - start_time)
#
#     ### wirte data ###
#     writeCarData(cars, "./result/car_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
#     writeRoadData(graph.edge_table, road_pipelines, max_length, "./result/road_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")


def way_one():
    """
        遗传算法
    """
    road_info_path = "./input_data/road_info.xlsx"
    car_info_path = "./input_data/car_info.xlsx"
    json_path = "./config.json"
    start_time = time.time()
    graph = createGraph(road_info_path)
    data = parseJsonFile(json_path)
    population_size = data["population_size"]
    epoch = data["epoch"]
    ga = GeneticAlgorithm(graph, population_size, car_info_path, epoch)
    ga.generatePopulation()
    best_chromosome = ga.execute()

    best_cars = best_chromosome[1]
    simulator = Simulator(graph)
    res, road_pipelines, max_time = simulator.action(best_cars)
    if res == True:
        ### wirte data ###
        writeCarData(best_cars, "./result/car_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
        writeRoadData(graph.edge_table, road_pipelines, max_time, "./result/road_result_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
    else:
        print("Error: output wrong...")

    print("total spend time:", time.time() - start_time)


def main():
    road_info_path = "./input_data/road_info.xlsx"
    car_info_path = "./input_data/car_info.xlsx"
    json_path = "./config.json"
    data = parseJsonFile(json_path)
    start_time = time.time()
    graph = createGraph(road_info_path)
    cars = createCars(car_info_path, graph, data["k_path_num"])
    end_time = time.time()
    print("create cars spend time:", end_time - start_time)
    road_pipelines, max_length = greedyGenerateCarDepartureTime(graph, cars, data["road_rate"])

    ### wirte data ###
    writeCarData(cars, "./result/car_result_time_"+str(max_length)+"_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")
    writeRoadData(graph.edge_table, road_pipelines, max_length, "./result/road_result_"+str(max_length)+"_"+time.strftime("%Y-%m-%d-%H-%M",time.localtime())+".xlsx")

    print("total spend time:", time.time() - start_time)


if __name__ == "__main__":
    main()