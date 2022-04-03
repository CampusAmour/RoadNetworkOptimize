#!/usr/bin/env python
# coding:utf-8
"""
Name   : genetic_algorithm.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/3/9 0:51
"""

import copy
import random
import numpy as np
from utils.build import createCars
from utils.model import Simulator
from utils.method import greedyGenerateCarDepartureTime
from utils.logger import Logger


logger = Logger("log").getLogger()


class GeneticAlgorithm:
    def __init__(self, graph, population_size, car_info_path, epoch):
        self.graph = copy.deepcopy(graph)
        self.population = []
        self.population_size = population_size
        self.car_info_path = car_info_path
        self.crossRate = 0.5
        # 遗传算法迭代次数
        self.epoch = epoch


    def _generateChromosome(self):
        cars = createCars(self.car_info_path, self.graph)
        # simulator = Simulator(self.graph)
        # res, _, spend_time = simulator.action(cars)
        _, spend_time = greedyGenerateCarDepartureTime(self.graph, cars)
        return spend_time, cars


    def generatePopulation(self):
        i = 0
        while len(self.population) < self.population_size:
            i += 1
            spend_time, cars = self._generateChromosome()
            self.population.append((spend_time, cars))
            logger.info("第%d次生成染色体成功,最后一辆车到达时间:%d" % (i, spend_time))


    def _getFitnessValue(self):
        """
            计算适应性函数
        """
        spend_times = np.array([1 / p[0] for p in self.population])
        probability = spend_times / np.sum(spend_times)
        # print(probability)
        cum_probability = np.cumsum(probability)
        # print(cum_probability)
        return cum_probability

    # # 轮盘赌方式1-直接产生population_size个染色体
    # def _selectNewPopulation(self, cum_probability):
    #     ms = []
    #     # 存活的种群
    #     for i in range(self.population_size):
    #         ms.append(random.random())
    #     ms.sort()
    #     print(ms)
    #     # 存活的种群排序
    #     fitin = 0
    #     newin = 0
    #     newPopulation = self.population
    #
    #     while newin < self.population_size and fitin < self.population_size:
    #         if (ms[newin] < cum_probability[fitin]):
    #             newPopulation[newin] = self.population[fitin]
    #             newin += 1
    #         else:
    #             fitin += 1
    #     print(newPopulation)
    #     return newPopulation


    # 轮盘赌方式2-每次产生1个染色体
    def _selectNewPopulation(self, cum_probability):
        val = random.random()
        left = 0
        for index, right in enumerate(cum_probability):
            if (val >= left) and (val <= right):
                return index
            left = right
        return -1


    def _crossoverTwoCarPath(self, car_one, car_two):
        # Todo: 交叉出发时间
        length1 = len(car_one.actual_path)
        length2 = len(car_two.actual_path)
        combinations = []
        for i in range(length1):
            for j in range(length2):
                if car_one.actual_path[i] == car_two.actual_path[j]:
                    for k in range(i + 1, length1):
                        for l in range(j + 1, length2):
                            if (car_one.actual_path[k] == car_two.actual_path[l]):
                                combinations.append((i, k, j, l))
                                break
                    break
        # print(combinations)
        # print(car_one.actual_path)
        # print(car_two.actual_path)
        c = random.choice(combinations)

        path_one = car_one.actual_path[: c[0]]
        path_one.extend(car_two.actual_path[c[2]: c[3]])
        path_one.extend(car_one.actual_path[c[1]:])

        path_two = car_two.actual_path[: c[2]]
        path_two.extend(car_one.actual_path[c[0]: c[1]])
        path_two.extend(car_two.actual_path[c[3]:])

        car_one.actual_path = path_one
        car_two.actual_path = path_two


    def _crossover(self, chromosome_one, chromosome_two):
        """
            染色体交叉
            交叉出发时间和实际路径
        """
        for j in range(len(chromosome_one)):
            if (random.random() < self.crossRate):
                # car = chromosome_one[j]
                # print(chromosome_one[j].car_id)
                # print(chromosome_two[j].car_id)
                self._crossoverTwoCarPath(chromosome_one[j], chromosome_two[j])


    def _mutation(self):
        """
            染色体变异
            随机选点后走最短路径
        """
        pass


    def chooseBestChromosome(self):
        """
            选择最佳染色体(最大适应度的染色体)
        """
        choose_index = 0
        min_time = self.population[0][0]
        for i in range(1, self.population_size):
            if min_time > self.population[i][0]:
                min_time = self.population[i][0]
                choose_index = i
        # print(choose_index)
        return choose_index


    def execute(self):
        simulator = Simulator(self.graph)
        points = []

        for e in range(self.epoch):
            print("交叉迭代第 %d 轮." % (e + 1))
            # 保留最佳染色体
            best_chromosome_index = self.chooseBestChromosome()
            # 画图需要
            best_point = self.population[best_chromosome_index][0]
            points.append(best_point)

            new_population = [copy.deepcopy(self.population[best_chromosome_index])]

            # 计算
            cum_probability = self._getFitnessValue()
            # print(cum_probability)

            # 交叉变异补齐种群
            while len(new_population) < self.population_size:
                # 轮盘赌选
                choose_one = self._selectNewPopulation(cum_probability)
                choose_two = self._selectNewPopulation(cum_probability)
                # 深拷贝
                chromosome_one = copy.deepcopy(self.population[choose_one][1])
                chromosome_two = copy.deepcopy(self.population[choose_two][1])
                # 交叉
                self._crossover(chromosome_one, chromosome_two)

                # 变异

                # 计算可行
                res, _, max_time = simulator.action(chromosome_one)
                if (res == True) and (max_time <= best_point):
                    new_population.append([max_time, chromosome_one])
                res, _, max_time = simulator.action(chromosome_two)
                if (res == True) and (max_time <= best_point) and (len(new_population) < self.population_size):
                    new_population.append([max_time, chromosome_one])

            self.population = new_population
            # print(self.population)
        print(points)
        # 迭代完成后选择最优染色体
        return self.population[self.chooseBestChromosome()]


if __name__ == "__main__":
    pass
