#!/usr/bin/env python
# coding:utf-8
"""
Name   : ui.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/10/5 19:33
"""

import os
import time
import threading
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton
from PyQt5.QtGui import QPixmap, QTextCursor
from utils.draw import DrawGraph
from utils.process import parseJsonFile
from utils.build import createGraph, createCars
from utils.method import *



class TrafficMainWindow():
    def __init__(self, last_window, base_path, roadFilePath, carFilePath):
        self.base_path = base_path
        self.ui = uic.loadUi(base_path + "/utils/traffic_main_window.ui")
        self.last_ui = last_window
        self.ui.backHomeBut.clicked.connect(self.backHome)


        self.roadFilePath = roadFilePath
        self.carFilePath = carFilePath
        self.dw = DrawGraph(self.base_path, self.roadFilePath)
        self.dw.drawRoad()
        self.ui.baseRoadLabel.setPixmap(QPixmap(self.base_path + "/temp/base_road_graph.png"))
        self.ui.baseRoadLabel.setText("")
        self.ui.baseRoadLabel.setObjectName("道路信息图")

        self.ui.runBut.clicked.connect(self.switchThread)

        self.isRunFinish = False

    def sendMsgToRuntimeText(self, msg="\n"):
        self.ui.showRuntimeText.moveCursor(QTextCursor.End)
        self.ui.showRuntimeText.insertPlainText(msg)

    def switchThread(self):
        self.t = threading.Thread(target=self.calc())
        self.t.start()
        self.isRunFinish = False

    def _greedyGenerateCarDepartureTime(self, graph, cars, rate, system_time, start_time, total_road_pipelines=None,
                                       current_road_pipelines=None, is_departure=None):
        """
            Desc: 贪心算法生成车辆离开的时间
        """
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
        for _ in range(system_time - 1):
            roadAccumulate(road_current_accumulate, road_acc_amount)

        if is_departure == None:
            carReadyGoNum = len(cars)
            is_departure = [False] * (len(cars) + 1)
        else:
            carReadyGoNum = 0
            for i in range(1, len(cars) + 1):
                if is_departure[i] == False:
                    carReadyGoNum += 1
            print("carReadyGoNum:", carReadyGoNum)

        while carReadyGoNum > 0:
            # print("system time: %d, car ready go number: %d." % (system_time, carReadyGoNum))
            self.sendMsgToRuntimeText("system time: %d, car ready go number: %d.\n" % (system_time, carReadyGoNum))

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

                    for j in range(len(cars[i].actual_path) - 1):
                        # print(cars[i].actual_path[j], cars[i].actual_path[j+1])
                        drive_road = graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[j],
                                                                            cars[i].actual_path[j + 1])
                        drive_road_index = drive_road.edge_id
                        if (j == 0) and (lanes[drive_road_index] == 0):
                            is_full_lane = True
                            break
                        # 根据道路容量bpr函数计算车辆通行时间
                        # Todo: 信号灯
                        drive_road_capacity = getCurrentRoadCapacity(current_road_pipelines, drive_road_index,
                                                                     road_current_accumulate[drive_road_index],
                                                                     car_drive_time)
                        if drive_road_capacity == -1:
                            block_time = car_drive_time
                            break
                        pass_time = graph.edge_table[drive_road_index].bprFunc(drive_road_capacity)
                        # print("    simulate node[%d]->node[%d] pass time: %d" % (cars[i].actual_path[j], cars[i].actual_path[j+1], pass_time))

                        ok, block_time = operateRoadPipeline(total_road_pipelines, drive_road_index,
                                                             road_current_accumulate[drive_road_index], car_drive_time,
                                                             pass_time, record, rate)
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
                        lanes[graph.getEdgeByOriginAndTerminalNodeId(cars[i].actual_path[0],
                                                                     cars[i].actual_path[1]).edge_id] -= 1
                        # print("    car id: %d, departure time: %d, arrived time: %d, number %d short path" % (cars[i].car_id, system_time, time, k+1), end=", ")
                        # print("drive path:", cars[i].actual_path)
                        break

                    if is_full_lane == True:
                        break
                    # 拿到了time和road_pipeline
                    res, _, mid_path = changeDrivePath(graph, current_road_pipelines, road_current_accumulate,
                                                       block_time, cars[i].start_node_id, cars[i].terminal_node_id,
                                                       rate)

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
        # print("max time: %d." % all_car_pass_max_time)
        self.sendMsgToRuntimeText("max time: %d.\n" % all_car_pass_max_time)
        # cars.sort(key=lambda car: car.car_id)
        return current_road_pipelines, total_road_pipelines, all_car_pass_max_time


    def calc(self):
        road_info_path = self.roadFilePath
        car_info_path = self.carFilePath
        json_path = self.base_path + "/config.json"
        data = parseJsonFile(json_path)
        start_time = time.time()
        graph = createGraph(road_info_path)
        cars = createCars(car_info_path, graph, data["k_path_num"])
        end_time = time.time()
        self.sendMsgToRuntimeText("create cars spend time: %d\n" % (end_time - start_time))
        current_road_pipelines, total_road_pipelines, max_length = self._greedyGenerateCarDepartureTime(graph, cars,
                                                                                                  data["road_rate"], 1,
                                                                                                  start_time)
        print("max_length:", max_length)
        # ### wirte data ###
        # writeCarData(cars, "./result/car_result_time_" + str(max_length) + "_" + time.strftime("%Y-%m-%d-%H-%M",
        #                                                                                        time.localtime()) + ".xlsx")
        # writeRoadAccumulateData(graph.edge_table, total_road_pipelines, max_length,
        #                         "./result/road_capacity_result_" + str(max_length) + "_" + time.strftime(
        #                             "%Y-%m-%d-%H-%M", time.localtime()) + ".xlsx")
        # writeRoadData(graph.edge_table, current_road_pipelines, max_length,
        #               "./result/road_cars_result_" + str(max_length) + "_" + time.strftime("%Y-%m-%d-%H-%M",
        #                                                                                    time.localtime()) + ".xlsx")

        print("total spend time:", time.time() - start_time)
        self.isRunFinish = True

    def backHome(self):
        self.last_ui.show()
        self.ui.close()
        print("返回成功...")

class TrafficLoadWindow():
    def __init__(self, base_path):
        # 从文件中加载UI定义
        self.base_path = base_path
        self.ui = uic.loadUi(base_path + "/utils/traffic_load_window.ui")

        self.roadFilePath = ""
        self.carFilePath = ""
        self.ui.chooseRoadFileBut.clicked.connect(self.chooseRoadFilePath)
        self.ui.chooseCarFileBut.clicked.connect(self.chooseCarFilePath)
        self.ui.clearFileBut.clicked.connect(self.clearFilePath)
        self.ui.submitFileBut.clicked.connect(self.submitFilePath)

    def chooseRoadFilePath(self):
        self.roadFilePath, _ = QFileDialog.getOpenFileName(None, "选取文件", os.getcwd(),
                                                                 "All Files(*);;Excel Files(*.xlsx;*.xls);;Csv Files(*.csv)")
        self.ui.chooseRoadFileText.setText(self.roadFilePath)

    def chooseCarFilePath(self):
        self.carFilePath, _ = QFileDialog.getOpenFileName(None, "选取文件", os.getcwd(),
                                                                 "All Files(*);;Excel Files(*.xlsx;*.xls);;Csv Files(*.csv)")
        self.ui.chooseCarFileText.setText(self.carFilePath)

    def clearFilePath(self):
        self.roadFilePath = ""
        self.ui.chooseRoadFileText.setText("")
        self.ui.chooseCarFileText.setText("")

    def _checkFilePath(self, isRoad=True):
        suffix = ("xlsx", "xls", "csv")
        for str in suffix:
            if ((isRoad == True) and (self.roadFilePath.endswith(str) == True)):
                return True
            if ((isRoad == False) and (self.carFilePath.endswith(str) == True)):
                return True
        if (isRoad == True):
            text = "道路"
            path = self.roadFilePath
        else:
            text = "车辆"
            path = self.carFilePath
        msgBox = QMessageBox()
        msgBox.setWindowTitle("提示")
        msgBox.setText("{0}信息文件路径[{1}]有误!".format(text, path))
        msgBox.addButton(QPushButton("确定"), QMessageBox.YesRole)
        msgBox.exec_()
        return False

    def submitFilePath(self):
        if ((self._checkFilePath(True) == False) or (self._checkFilePath(False) == False)):
            return

        # 进入下一级菜单
        print("提交成功...")
        self.ui.hide()

        self.main_window = TrafficMainWindow(self.ui, self.base_path, self.roadFilePath, self.carFilePath)
        self.main_window.ui.show()


if __name__ == "__main__":
    # app = QApplication([])
    # window = TrafficLoadWindow()
    # window.ui.show()
    # app.exec_()
    pass
