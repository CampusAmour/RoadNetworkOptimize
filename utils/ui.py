#!/usr/bin/env python
# coding:utf-8
"""
Name   : ui.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/10/5 19:33
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton
from PyQt5.QtGui import QPixmap
from draw import DrawGraph


class TrafficMainWindow():
    def __init__(self, last_window, roadFilePath, carFilePath, ui_path="./traffic_main_window.ui"):
        self.ui = uic.loadUi(ui_path)
        self.last_ui = last_window
        self.ui.backHomeBut.clicked.connect(self.backHome)


        self.roadFilePath = roadFilePath
        self.carFilePath = carFilePath
        self.dw = DrawGraph(self.roadFilePath)
        self.dw.drawRoad()
        self.ui.baseRoadLabel.setPixmap(QPixmap("../temp/base_road_graph.png"))
        self.ui.baseRoadLabel.setText("")
        self.ui.baseRoadLabel.setObjectName("道路信息图")


    def backHome(self):
        self.last_ui.show()
        self.ui.close()
        print("返回成功...")

class TrafficLoadWindow():
    def __init__(self, ui_path="./traffic_load_window.ui"):
        # 从文件中加载UI定义
        self.ui = uic.loadUi(ui_path)

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

        self.main_window = TrafficMainWindow(self.ui, self.roadFilePath, self.carFilePath)
        self.main_window.ui.show()


if __name__ == "__main__":
    app = QApplication([])
    window = TrafficLoadWindow()
    window.ui.show()
    app.exec_()
